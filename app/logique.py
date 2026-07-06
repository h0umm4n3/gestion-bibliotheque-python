from datetime import date, timedelta
import models


DUREE_EMPRUNT_JOURS = 14
DUREE_PROLONGATION_JOURS = 7
TARIF_RETARD_PAR_JOUR = 2
SEUIL_PERTE_JOURS = 30
FRAIS_ADMINISTRATIFS = 20


def _aujourdhui():
    """Renvoie la date du jour au format AAAA-MM-JJ (texte)."""
    return date.today().isoformat()


def _ajouter_jours(date_texte, nb_jours):
    """Ajoute un nombre de jours à une date texte et renvoie la nouvelle date texte."""
    date_obj = date.fromisoformat(date_texte)
    nouvelle_date = date_obj + timedelta(days=nb_jours)
    return nouvelle_date.isoformat()


def calculer_jours_retard(date_retour_prevue, date_reference=None):
    """Calcule le nombre de jours de retard entre la date prévue et une date de référence."""
    if date_reference is None:
        date_reference = _aujourdhui()
    prevue = date.fromisoformat(date_retour_prevue)
    reference = date.fromisoformat(date_reference)
    ecart = (reference - prevue).days
    return ecart if ecart > 0 else 0


def mettre_a_jour_statuts_retard():
    """Parcourt les emprunts actifs et met à jour leur statut (EnRetard ou Perdu)."""
    emprunts = models.lister_emprunts_actifs()
    for emprunt in emprunts:
        retard = calculer_jours_retard(emprunt["date_retour_prevue"])
        if retard > SEUIL_PERTE_JOURS:
            models.modifier_statut_emprunt(emprunt["id_emprunt"], "Perdu")
        elif retard > 0:
            models.modifier_statut_emprunt(emprunt["id_emprunt"], "EnRetard")


def compte_eligible(adherent):
    """Vérifie RG04 : compte non Suspendu/Bloqué et sans pénalité impayée."""
    if adherent["statut"] in ("Suspendu", "Bloque"):
        return False, "Compte non éligible : l'adhérent est " + adherent["statut"] + "."
    if models.compter_penalites_impayees(adherent["id_adherent"]) > 0:
        return False, "Compte non éligible : pénalité(s) impayée(s)."
    return True, ""


def quota_respecte(adherent):
    """Vérifie RG01 : le nombre d'emprunts en cours est inférieur au quota de l'adhérent."""
    nb_en_cours = models.compter_emprunts_en_cours(adherent["id_adherent"])
    if nb_en_cours >= adherent["max_emprunts"]:
        return False, "Quota atteint (" + str(adherent["max_emprunts"]) + " emprunts maximum)."
    return True, ""


def emprunter_livre(id_adherent, id_exemplaire):
    """Réalise le workflow d'emprunt : RG04 -> RG01 -> RG06 -> création de l'emprunt."""
    adherent = models.obtenir_adherent(id_adherent)
    if adherent is None:
        return False, "Adhérent introuvable."

    eligible, message = compte_eligible(adherent)
    if not eligible:
        return False, message

    quota_ok, message = quota_respecte(adherent)
    if not quota_ok:
        return False, message

    exemplaire = models.obtenir_exemplaire(id_exemplaire)
    if exemplaire is None:
        return False, "Exemplaire introuvable."
    if exemplaire["disponible"] != 1:
        return False, "Exemplaire indisponible : aucun exemplaire empruntable."

    date_emprunt = _aujourdhui()
    date_retour = _ajouter_jours(date_emprunt, DUREE_EMPRUNT_JOURS)
    id_emprunt = models.creer_emprunt(id_adherent, id_exemplaire, date_emprunt, date_retour)
    models.modifier_disponibilite_exemplaire(id_exemplaire, 0)

    message = (
        "Emprunt n°" + str(id_emprunt) + " enregistré. "
        + "Date de retour prévue : " + date_retour + "."
    )
    return True, message


def retourner_livre(id_exemplaire, id_emplacement=None):
    """Réalise le workflow de retour : enregistrement, calcul du retard, pénalité, remise en rayon."""
    emprunt = models.obtenir_emprunt_en_cours_par_exemplaire(id_exemplaire)
    if emprunt is None:
        return False, "Aucun emprunt en cours pour cet exemplaire."

    date_du_jour = _aujourdhui()
    models.enregistrer_retour(emprunt["id_emprunt"], date_du_jour)

    jours_retard = calculer_jours_retard(emprunt["date_retour_prevue"], date_du_jour)
    message_penalite = ""
    if jours_retard > 0:
        montant = jours_retard * TARIF_RETARD_PAR_JOUR
        models.creer_penalite(emprunt["id_emprunt"], "Retard", montant, "EnAttente", date_du_jour)
        message_penalite = (
            " Retard de " + str(jours_retard) + " jour(s) : "
            + "pénalité de " + str(montant) + " DH."
        )

    models.modifier_disponibilite_exemplaire(id_exemplaire, 1)
    if id_emplacement is not None:
        models.modifier_emplacement_exemplaire(id_exemplaire, id_emplacement)

    exemplaire = models.obtenir_exemplaire(id_exemplaire)
    emplacement = models.obtenir_emplacement(exemplaire["id_emplacement"])
    code_emp = emplacement["code_emplacement"] if emplacement else "non défini"

    notification = notifier_prochaine_reservation(exemplaire["id_livre"])

    message = (
        "Retour enregistré. Exemplaire rangé à l'emplacement " + code_emp + "."
        + message_penalite
        + notification
    )
    return True, message


def reserver_livre(id_adherent, id_livre):
    """Réalise le workflow de réservation : emprunt direct possible ou mise en file d'attente."""
    adherent = models.obtenir_adherent(id_adherent)
    if adherent is None:
        return False, "Adhérent introuvable."

    nb_disponibles = models.compter_exemplaires_disponibles(id_livre)
    if nb_disponibles > 0:
        return True, "Un exemplaire est disponible : emprunt direct possible (pas besoin de réserver)."

    nb_attente = models.compter_reservations_en_attente(id_livre)
    priorite = nb_attente + 1
    models.creer_reservation(id_adherent, id_livre, _aujourdhui(), "EnAttente", priorite)
    message = "Réservation enregistrée. Vous êtes en position " + str(priorite) + " dans la file d'attente."
    return True, message


def notifier_prochaine_reservation(id_livre):
    """Notifie le prochain réservataire (statut Disponible) au retour d'un exemplaire (extend)."""
    reservation = models.prochaine_reservation(id_livre)
    if reservation is None:
        return ""
    models.modifier_statut_reservation(reservation["id_reservation"], "Disponible")
    adherent = models.obtenir_adherent(reservation["id_adherent"])
    return (
        " Notification : l'adhérent "
        + adherent["prenom"] + " " + adherent["nom"]
        + " est informé que le livre est désormais disponible."
    )


def prolonger_emprunt(id_emprunt):
    """Prolonge un emprunt une seule fois de +7 jours (RG02)."""
    emprunt = models.obtenir_emprunt(id_emprunt)
    if emprunt is None:
        return False, "Emprunt introuvable."
    if emprunt["date_retour_effective"] is not None:
        return False, "Emprunt déjà retourné : prolongation impossible."
    if emprunt["prolonge"] == 1:
        return False, "Cet emprunt a déjà été prolongé une fois."

    nouvelle_date = _ajouter_jours(emprunt["date_retour_prevue"], DUREE_PROLONGATION_JOURS)
    models.modifier_date_retour_prevue(id_emprunt, nouvelle_date)
    models.marquer_prolonge(id_emprunt)
    if emprunt["statut"] == "EnRetard":
        models.modifier_statut_emprunt(id_emprunt, "EnCours")
    return True, "Emprunt prolongé. Nouvelle date de retour : " + nouvelle_date + "."


def payer_penalite(id_penalite):
    """Marque une pénalité comme payée et débloque le compte si plus rien n'est dû."""
    penalite = models.obtenir_penalite(id_penalite)
    if penalite is None:
        return False, "Pénalité introuvable."
    if penalite["statut_paiement"] == "Paye":
        return False, "Cette pénalité est déjà payée."

    models.modifier_statut_paiement(id_penalite, "Paye")
    return True, _debloquer_si_solde(penalite)


def exonerer_penalite(id_penalite):
    """Exonère une pénalité (montant annulé) et débloque le compte si plus rien n'est dû."""
    penalite = models.obtenir_penalite(id_penalite)
    if penalite is None:
        return False, "Pénalité introuvable."
    models.modifier_statut_paiement(id_penalite, "Exonere")
    return True, _debloquer_si_solde(penalite)


def _debloquer_si_solde(penalite):
    """Débloque l'adhérent s'il n'a plus aucune pénalité impayée (helper interne)."""
    emprunt = models.obtenir_emprunt(penalite["id_emprunt"])
    id_adherent = emprunt["id_adherent"]
    if models.compter_penalites_impayees(id_adherent) == 0:
        adherent = models.obtenir_adherent(id_adherent)
        if adherent["statut"] in ("Suspendu", "Bloque"):
            models.modifier_statut_adherent(id_adherent, "Actif")
            return "Pénalité réglée. Compte réactivé (plus aucune pénalité due)."
        return "Pénalité réglée. Aucune pénalité restante."
    return "Pénalité réglée. Il reste des pénalités impayées sur ce compte."


def declarer_perte_ou_vol(id_emprunt, type_penalite):
    """Déclare une perte ou un vol : pénalité (prix + frais), blocage du compte (RG04)."""
    if type_penalite not in ("Perte", "Vol"):
        return False, "Type invalide : utiliser 'Perte' ou 'Vol'."
    emprunt = models.obtenir_emprunt(id_emprunt)
    if emprunt is None:
        return False, "Emprunt introuvable."

    exemplaire = models.obtenir_exemplaire(emprunt["id_exemplaire"])
    livre = models.obtenir_livre(exemplaire["id_livre"])
    montant = (livre["prix"] or 0) + FRAIS_ADMINISTRATIFS

    models.creer_penalite(id_emprunt, type_penalite, montant, "EnAttente", _aujourdhui())
    statut_emprunt = "Perdu" if type_penalite == "Perte" else "Vole"
    models.modifier_statut_emprunt(id_emprunt, statut_emprunt)
    models.modifier_etat_exemplaire(emprunt["id_exemplaire"], "Perdu")
    models.modifier_disponibilite_exemplaire(emprunt["id_exemplaire"], 0)
    if emprunt["date_retour_effective"] is None:
        models.cloturer_emprunt(id_emprunt, _aujourdhui(), statut_emprunt)
    models.modifier_statut_adherent(emprunt["id_adherent"], "Bloque")

    return True, (
        type_penalite + " déclaré(e). Pénalité de " + str(montant) + " DH créée. "
        + "Compte bloqué jusqu'au règlement."
    )


def donnees_tableau_de_bord():
    """Rassemble les indicateurs du tableau de bord (livres populaires, retards, pertes/vols)."""
    return {
        "populaires": models.livres_les_plus_empruntes(),
        "retards": models.emprunts_en_retard(),
        "pertes_vols": models.compter_pertes_vols(),
    }

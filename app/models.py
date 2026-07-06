from database import obtenir_connexion


def _executer(requete, parametres=()):
    """Exécute une requête d'écriture (INSERT/UPDATE/DELETE) et renvoie l'id inséré."""
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    curseur.execute(requete, parametres)
    connexion.commit()
    dernier_id = curseur.lastrowid
    connexion.close()
    return dernier_id


def _lire_tous(requete, parametres=()):
    """Exécute une requête de lecture et renvoie toutes les lignes trouvées."""
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    curseur.execute(requete, parametres)
    lignes = curseur.fetchall()
    connexion.close()
    return lignes


def _lire_un(requete, parametres=()):
    """Exécute une requête de lecture et renvoie la première ligne (ou None)."""
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    curseur.execute(requete, parametres)
    ligne = curseur.fetchone()
    connexion.close()
    return ligne


def verifier_connexion(email, mot_de_passe):
    """Vérifie les identifiants et renvoie l'utilisateur correspondant (ou None)."""
    return _lire_un(
        "SELECT * FROM utilisateur WHERE email = ? AND mot_de_passe = ?",
        (email, mot_de_passe),
    )


def lister_utilisateurs():
    """Renvoie la liste de tous les comptes utilisateurs."""
    return _lire_tous("SELECT * FROM utilisateur ORDER BY id_utilisateur")


def obtenir_utilisateur(id_utilisateur):
    """Renvoie un utilisateur d'après son identifiant."""
    return _lire_un("SELECT * FROM utilisateur WHERE id_utilisateur = ?", (id_utilisateur,))


def modifier_role_utilisateur(id_utilisateur, role):
    """Modifie le rôle d'un utilisateur."""
    _executer("UPDATE utilisateur SET role = ? WHERE id_utilisateur = ?", (role, id_utilisateur))


def creer_utilisateur(email, mot_de_passe, role):
    """Crée un compte de connexion (email + mot de passe + rôle) et renvoie son identifiant."""
    return _executer(
        "INSERT INTO utilisateur (email, mot_de_passe, role) VALUES (?, ?, ?)",
        (email, mot_de_passe, role),
    )


def obtenir_utilisateur_par_email(email):
    """Renvoie le compte ayant cet email (ou None) — sert à éviter les doublons."""
    return _lire_un("SELECT * FROM utilisateur WHERE email = ?", (email,))


def supprimer_utilisateur(id_utilisateur):
    """Supprime un compte de connexion."""
    _executer("DELETE FROM utilisateur WHERE id_utilisateur = ?", (id_utilisateur,))


def creer_adherent(id_utilisateur, nom, prenom, cin, email, telephone, type_adherent, statut, max_emprunts):
    """Crée un nouvel adhérent et renvoie son identifiant."""
    return _executer(
        """INSERT INTO adherent
           (id_utilisateur, nom, prenom, cin, email, telephone, type_adherent, statut, max_emprunts)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (id_utilisateur, nom, prenom, cin, email, telephone, type_adherent, statut, max_emprunts),
    )


def obtenir_adherent(id_adherent):
    """Renvoie un adhérent d'après son identifiant."""
    return _lire_un("SELECT * FROM adherent WHERE id_adherent = ?", (id_adherent,))


def obtenir_adherent_par_utilisateur(id_utilisateur):
    """Renvoie l'adhérent lié à un compte utilisateur (pour le rôle Adherent)."""
    return _lire_un("SELECT * FROM adherent WHERE id_utilisateur = ?", (id_utilisateur,))


def lister_adherents():
    """Renvoie la liste de tous les adhérents."""
    return _lire_tous("SELECT * FROM adherent ORDER BY nom, prenom")


def modifier_adherent(id_adherent, nom, prenom, cin, email, telephone, type_adherent, statut, max_emprunts):
    """Met à jour les informations d'un adhérent existant."""
    _executer(
        """UPDATE adherent
           SET nom = ?, prenom = ?, cin = ?, email = ?, telephone = ?,
               type_adherent = ?, statut = ?, max_emprunts = ?
           WHERE id_adherent = ?""",
        (nom, prenom, cin, email, telephone, type_adherent, statut, max_emprunts, id_adherent),
    )


def modifier_statut_adherent(id_adherent, statut):
    """Modifie uniquement le statut d'un adhérent (Actif/Suspendu/Bloque)."""
    _executer("UPDATE adherent SET statut = ? WHERE id_adherent = ?", (statut, id_adherent))


def modifier_quota_adherent(id_adherent, max_emprunts):
    """Modifie uniquement le quota d'emprunts d'un adhérent (RG01 configurable)."""
    _executer("UPDATE adherent SET max_emprunts = ? WHERE id_adherent = ?", (max_emprunts, id_adherent))


def supprimer_adherent(id_adherent):
    """Supprime un adhérent de la base."""
    _executer("DELETE FROM adherent WHERE id_adherent = ?", (id_adherent,))


def creer_livre(titre, auteur, editeur, categorie, prix, nb_exemplaires, isbn):
    """Crée un nouveau livre et renvoie son identifiant."""
    return _executer(
        """INSERT INTO livre (titre, auteur, editeur, categorie, prix, nb_exemplaires, isbn)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (titre, auteur, editeur, categorie, prix, nb_exemplaires, isbn),
    )


def obtenir_livre(id_livre):
    """Renvoie un livre d'après son identifiant."""
    return _lire_un("SELECT * FROM livre WHERE id_livre = ?", (id_livre,))


def lister_livres():
    """Renvoie la liste de tous les livres du catalogue."""
    return _lire_tous("SELECT * FROM livre ORDER BY titre")


def modifier_livre(id_livre, titre, auteur, editeur, categorie, prix, nb_exemplaires, isbn):
    """Met à jour les informations d'un livre existant."""
    _executer(
        """UPDATE livre
           SET titre = ?, auteur = ?, editeur = ?, categorie = ?, prix = ?, nb_exemplaires = ?, isbn = ?
           WHERE id_livre = ?""",
        (titre, auteur, editeur, categorie, prix, nb_exemplaires, isbn, id_livre),
    )


def supprimer_livre(id_livre):
    """Supprime un livre du catalogue."""
    _executer("DELETE FROM livre WHERE id_livre = ?", (id_livre,))


def creer_emplacement(salle, etagere, rangee, position, code_emplacement):
    """Crée un nouvel emplacement et renvoie son identifiant."""
    return _executer(
        """INSERT INTO emplacement (salle, etagere, rangee, position, code_emplacement)
           VALUES (?, ?, ?, ?, ?)""",
        (salle, etagere, rangee, position, code_emplacement),
    )


def obtenir_emplacement(id_emplacement):
    """Renvoie un emplacement d'après son identifiant."""
    return _lire_un("SELECT * FROM emplacement WHERE id_emplacement = ?", (id_emplacement,))


def lister_emplacements():
    """Renvoie la liste de tous les emplacements."""
    return _lire_tous("SELECT * FROM emplacement ORDER BY code_emplacement")


def modifier_emplacement(id_emplacement, salle, etagere, rangee, position, code_emplacement):
    """Met à jour les informations d'un emplacement existant."""
    _executer(
        """UPDATE emplacement
           SET salle = ?, etagere = ?, rangee = ?, position = ?, code_emplacement = ?
           WHERE id_emplacement = ?""",
        (salle, etagere, rangee, position, code_emplacement, id_emplacement),
    )


def supprimer_emplacement(id_emplacement):
    """Supprime un emplacement de la base."""
    _executer("DELETE FROM emplacement WHERE id_emplacement = ?", (id_emplacement,))


def creer_exemplaire(id_livre, id_emplacement, code_barre, etat, disponible=1):
    """Crée un nouvel exemplaire et renvoie son identifiant."""
    return _executer(
        """INSERT INTO exemplaire (id_livre, id_emplacement, code_barre, etat, disponible)
           VALUES (?, ?, ?, ?, ?)""",
        (id_livre, id_emplacement, code_barre, etat, disponible),
    )


def obtenir_exemplaire(id_exemplaire):
    """Renvoie un exemplaire d'après son identifiant."""
    return _lire_un("SELECT * FROM exemplaire WHERE id_exemplaire = ?", (id_exemplaire,))


def lister_exemplaires_par_livre(id_livre):
    """Renvoie tous les exemplaires d'un livre donné (avec le code de leur emplacement)."""
    return _lire_tous(
        """SELECT e.*, emp.code_emplacement
           FROM exemplaire e
           LEFT JOIN emplacement emp ON e.id_emplacement = emp.id_emplacement
           WHERE e.id_livre = ?
           ORDER BY e.id_exemplaire""",
        (id_livre,),
    )


def lister_exemplaires_disponibles():
    """Renvoie tous les exemplaires actuellement disponibles (pour l'écran d'emprunt)."""
    return _lire_tous(
        """SELECT e.id_exemplaire, e.code_barre, l.titre
           FROM exemplaire e
           JOIN livre l ON e.id_livre = l.id_livre
           WHERE e.disponible = 1
           ORDER BY l.titre""",
    )


def compter_exemplaires_disponibles(id_livre):
    """Compte les exemplaires disponibles d'un livre (utile pour la réservation, RG06)."""
    ligne = _lire_un(
        "SELECT COUNT(*) AS n FROM exemplaire WHERE id_livre = ? AND disponible = 1",
        (id_livre,),
    )
    return ligne["n"]


def trouver_exemplaire_disponible(id_livre):
    """Renvoie un exemplaire disponible d'un livre, ou None s'il n'y en a aucun."""
    return _lire_un(
        "SELECT * FROM exemplaire WHERE id_livre = ? AND disponible = 1 LIMIT 1",
        (id_livre,),
    )


def modifier_disponibilite_exemplaire(id_exemplaire, disponible):
    """Modifie la disponibilité d'un exemplaire (1 = dispo, 0 = emprunté)."""
    _executer("UPDATE exemplaire SET disponible = ? WHERE id_exemplaire = ?", (disponible, id_exemplaire))


def modifier_etat_exemplaire(id_exemplaire, etat):
    """Modifie l'état d'un exemplaire (Bon, Use, Endommage, Perdu)."""
    _executer("UPDATE exemplaire SET etat = ? WHERE id_exemplaire = ?", (etat, id_exemplaire))


def modifier_emplacement_exemplaire(id_exemplaire, id_emplacement):
    """Affecte ou met à jour l'emplacement d'un exemplaire."""
    _executer("UPDATE exemplaire SET id_emplacement = ? WHERE id_exemplaire = ?", (id_emplacement, id_exemplaire))


def creer_emprunt(id_adherent, id_exemplaire, date_emprunt, date_retour_prevue, statut="EnCours"):
    """Crée un nouvel emprunt et renvoie son identifiant."""
    return _executer(
        """INSERT INTO emprunt
           (id_adherent, id_exemplaire, date_emprunt, date_retour_prevue, date_retour_effective, prolonge, statut)
           VALUES (?, ?, ?, ?, NULL, 0, ?)""",
        (id_adherent, id_exemplaire, date_emprunt, date_retour_prevue, statut),
    )


def obtenir_emprunt(id_emprunt):
    """Renvoie un emprunt d'après son identifiant."""
    return _lire_un("SELECT * FROM emprunt WHERE id_emprunt = ?", (id_emprunt,))


def obtenir_emprunt_en_cours_par_exemplaire(id_exemplaire):
    """Renvoie l'emprunt en cours (non rendu) d'un exemplaire donné."""
    return _lire_un(
        """SELECT * FROM emprunt
           WHERE id_exemplaire = ? AND date_retour_effective IS NULL
           ORDER BY id_emprunt DESC LIMIT 1""",
        (id_exemplaire,),
    )


def compter_emprunts_en_cours(id_adherent):
    """Compte les emprunts en cours d'un adhérent (pour le quota RG01)."""
    ligne = _lire_un(
        """SELECT COUNT(*) AS n FROM emprunt
           WHERE id_adherent = ? AND date_retour_effective IS NULL
           AND statut IN ('EnCours', 'EnRetard')""",
        (id_adherent,),
    )
    return ligne["n"]


def lister_emprunts_en_cours():
    """Renvoie tous les emprunts non rendus, avec les infos adhérent et livre (pour le retour)."""
    return _lire_tous(
        """SELECT em.*, a.nom, a.prenom, l.titre, ex.code_barre
           FROM emprunt em
           JOIN adherent a ON em.id_adherent = a.id_adherent
           JOIN exemplaire ex ON em.id_exemplaire = ex.id_exemplaire
           JOIN livre l ON ex.id_livre = l.id_livre
           WHERE em.date_retour_effective IS NULL
           ORDER BY em.date_retour_prevue""",
    )


def lister_emprunts_par_adherent(id_adherent):
    """Renvoie l'historique complet des emprunts d'un adhérent (pour son historique)."""
    return _lire_tous(
        """SELECT em.*, l.titre, ex.code_barre
           FROM emprunt em
           JOIN exemplaire ex ON em.id_exemplaire = ex.id_exemplaire
           JOIN livre l ON ex.id_livre = l.id_livre
           WHERE em.id_adherent = ?
           ORDER BY em.date_emprunt DESC""",
        (id_adherent,),
    )


def lister_tous_emprunts():
    """Renvoie tous les emprunts (pour les calculs du tableau de bord)."""
    return _lire_tous("SELECT * FROM emprunt")


def lister_emprunts_actifs():
    """Renvoie les emprunts non rendus (utilisé pour recalculer les retards)."""
    return _lire_tous(
        "SELECT * FROM emprunt WHERE date_retour_effective IS NULL AND statut IN ('EnCours', 'EnRetard')"
    )


def modifier_date_retour_prevue(id_emprunt, date_retour_prevue):
    """Modifie la date de retour prévue d'un emprunt (utilisé lors d'une prolongation)."""
    _executer(
        "UPDATE emprunt SET date_retour_prevue = ? WHERE id_emprunt = ?",
        (date_retour_prevue, id_emprunt),
    )


def marquer_prolonge(id_emprunt):
    """Marque un emprunt comme prolongé (RG02 : une seule fois)."""
    _executer("UPDATE emprunt SET prolonge = 1 WHERE id_emprunt = ?", (id_emprunt,))


def enregistrer_retour(id_emprunt, date_retour_effective):
    """Enregistre la date de retour effective et passe le statut à Retourne."""
    _executer(
        "UPDATE emprunt SET date_retour_effective = ?, statut = 'Retourne' WHERE id_emprunt = ?",
        (date_retour_effective, id_emprunt),
    )


def modifier_statut_emprunt(id_emprunt, statut):
    """Modifie le statut d'un emprunt (EnCours, EnRetard, Perdu, Vole, Retourne)."""
    _executer("UPDATE emprunt SET statut = ? WHERE id_emprunt = ?", (statut, id_emprunt))


def cloturer_emprunt(id_emprunt, date_retour_effective, statut):
    """Clôt un emprunt en fixant la date de retour effective et un statut final (Perdu/Vole)."""
    _executer(
        "UPDATE emprunt SET date_retour_effective = ?, statut = ? WHERE id_emprunt = ?",
        (date_retour_effective, statut, id_emprunt),
    )


def creer_reservation(id_adherent, id_livre, date_reservation, statut, priorite):
    """Crée une nouvelle réservation et renvoie son identifiant."""
    return _executer(
        """INSERT INTO reservation (id_adherent, id_livre, date_reservation, statut, priorite)
           VALUES (?, ?, ?, ?, ?)""",
        (id_adherent, id_livre, date_reservation, statut, priorite),
    )


def obtenir_reservation(id_reservation):
    """Renvoie une réservation d'après son identifiant."""
    return _lire_un("SELECT * FROM reservation WHERE id_reservation = ?", (id_reservation,))


def compter_reservations_en_attente(id_livre):
    """Compte les réservations en attente pour un livre (pour calculer la priorité)."""
    ligne = _lire_un(
        "SELECT COUNT(*) AS n FROM reservation WHERE id_livre = ? AND statut = 'EnAttente'",
        (id_livre,),
    )
    return ligne["n"]


def prochaine_reservation(id_livre):
    """Renvoie la prochaine réservation en attente (priorité la plus haute = la plus petite)."""
    return _lire_un(
        """SELECT * FROM reservation
           WHERE id_livre = ? AND statut = 'EnAttente'
           ORDER BY priorite ASC LIMIT 1""",
        (id_livre,),
    )


def lister_reservations_par_adherent(id_adherent):
    """Renvoie les réservations d'un adhérent (pour son historique et ses notifications)."""
    return _lire_tous(
        """SELECT r.*, l.titre
           FROM reservation r
           JOIN livre l ON r.id_livre = l.id_livre
           WHERE r.id_adherent = ?
           ORDER BY r.date_reservation DESC""",
        (id_adherent,),
    )


def lister_notifications_adherent(id_adherent):
    """Renvoie les réservations devenues Disponible (notifications de mise à disposition)."""
    return _lire_tous(
        """SELECT r.*, l.titre
           FROM reservation r
           JOIN livre l ON r.id_livre = l.id_livre
           WHERE r.id_adherent = ? AND r.statut = 'Disponible'
           ORDER BY r.date_reservation DESC""",
        (id_adherent,),
    )


def modifier_statut_reservation(id_reservation, statut):
    """Modifie le statut d'une réservation (EnAttente, Disponible, Annulee)."""
    _executer("UPDATE reservation SET statut = ? WHERE id_reservation = ?", (statut, id_reservation))


def creer_penalite(id_emprunt, type_penalite, montant, statut_paiement, date_creation):
    """Crée une nouvelle pénalité et renvoie son identifiant."""
    return _executer(
        """INSERT INTO penalite (id_emprunt, type_penalite, montant, statut_paiement, date_creation)
           VALUES (?, ?, ?, ?, ?)""",
        (id_emprunt, type_penalite, montant, statut_paiement, date_creation),
    )


def obtenir_penalite(id_penalite):
    """Renvoie une pénalité d'après son identifiant."""
    return _lire_un("SELECT * FROM penalite WHERE id_penalite = ?", (id_penalite,))


def compter_penalites_impayees(id_adherent):
    """Compte les pénalités impayées (EnAttente) d'un adhérent (RG04)."""
    ligne = _lire_un(
        """SELECT COUNT(*) AS n
           FROM penalite p
           JOIN emprunt em ON p.id_emprunt = em.id_emprunt
           WHERE em.id_adherent = ? AND p.statut_paiement = 'EnAttente'""",
        (id_adherent,),
    )
    return ligne["n"]


def lister_toutes_penalites():
    """Renvoie toutes les pénalités avec les infos adhérent et livre (pour la gestion)."""
    return _lire_tous(
        """SELECT p.*, a.id_adherent, a.nom, a.prenom, l.titre
           FROM penalite p
           JOIN emprunt em ON p.id_emprunt = em.id_emprunt
           JOIN adherent a ON em.id_adherent = a.id_adherent
           JOIN exemplaire ex ON em.id_exemplaire = ex.id_exemplaire
           JOIN livre l ON ex.id_livre = l.id_livre
           ORDER BY p.date_creation DESC""",
    )


def lister_penalites_par_adherent(id_adherent):
    """Renvoie les pénalités d'un adhérent (pour son historique)."""
    return _lire_tous(
        """SELECT p.*, l.titre
           FROM penalite p
           JOIN emprunt em ON p.id_emprunt = em.id_emprunt
           JOIN exemplaire ex ON em.id_exemplaire = ex.id_exemplaire
           JOIN livre l ON ex.id_livre = l.id_livre
           WHERE em.id_adherent = ?
           ORDER BY p.date_creation DESC""",
        (id_adherent,),
    )


def modifier_statut_paiement(id_penalite, statut_paiement):
    """Modifie le statut de paiement d'une pénalité (Paye, EnAttente, Exonere)."""
    _executer(
        "UPDATE penalite SET statut_paiement = ? WHERE id_penalite = ?",
        (statut_paiement, id_penalite),
    )


def livres_les_plus_empruntes(limite=5):
    """Renvoie les livres classés par nombre d'emprunts décroissant."""
    return _lire_tous(
        """SELECT l.titre, COUNT(em.id_emprunt) AS nb_emprunts
           FROM emprunt em
           JOIN exemplaire ex ON em.id_exemplaire = ex.id_exemplaire
           JOIN livre l ON ex.id_livre = l.id_livre
           GROUP BY l.id_livre
           ORDER BY nb_emprunts DESC
           LIMIT ?""",
        (limite,),
    )


def emprunts_en_retard():
    """Renvoie les emprunts actuellement en retard (pour le tableau de bord)."""
    return _lire_tous(
        """SELECT em.*, a.nom, a.prenom, l.titre
           FROM emprunt em
           JOIN adherent a ON em.id_adherent = a.id_adherent
           JOIN exemplaire ex ON em.id_exemplaire = ex.id_exemplaire
           JOIN livre l ON ex.id_livre = l.id_livre
           WHERE em.statut = 'EnRetard'
           ORDER BY em.date_retour_prevue""",
    )


def compter_pertes_vols():
    """Compte le nombre d'emprunts marqués Perdu ou Vole (pour le tableau de bord)."""
    ligne = _lire_un("SELECT COUNT(*) AS n FROM emprunt WHERE statut IN ('Perdu', 'Vole')")
    return ligne["n"]

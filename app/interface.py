import tkinter as tk
from tkinter import ttk, messagebox

import models
import logique


class ApplicationBibliotheque:
    """Classe principale gérant toute l'interface graphique de l'application."""

    def __init__(self, racine):
        """Initialise l'application avec la fenêtre racine."""
        self.racine = racine
        self.utilisateur = None
        self.adherent = None
        self.emprunts_courants = {}

        self.racine.title("Système de Gestion des Emprunts - Bibliothèque")
        self.racine.geometry("980x620")
        self.racine.minsize(820, 560)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=24)
        style.configure("Titre.TLabel", font=("Segoe UI", 14, "bold"))

        self.afficher_connexion()


    def _vider(self, conteneur):
        """Supprime tous les widgets enfants d'un conteneur donné."""
        for widget in conteneur.winfo_children():
            widget.destroy()

    def _creer_tableau(self, parent, colonnes, hauteur=12):
        """Crée un tableau ttk.Treeview avec barre de défilement et renvoie le tableau."""
        cadre = ttk.Frame(parent)
        cadre.pack(fill="both", expand=True, padx=5, pady=5)
        identifiants = [c[0] for c in colonnes]
        tableau = ttk.Treeview(cadre, columns=identifiants, show="headings", height=hauteur)
        for cle, libelle, largeur in colonnes:
            tableau.heading(cle, text=libelle)
            tableau.column(cle, width=largeur, anchor="w")
        barre = ttk.Scrollbar(cadre, orient="vertical", command=tableau.yview)
        tableau.configure(yscrollcommand=barre.set)
        tableau.pack(side="left", fill="both", expand=True)
        barre.pack(side="right", fill="y")
        return tableau

    def _selection_id(self, tableau):
        """Renvoie l'identifiant (iid) de la ligne sélectionnée, ou None avec un avertissement."""
        selection = tableau.selection()
        if not selection:
            messagebox.showwarning("Sélection requise", "Veuillez d'abord sélectionner une ligne.")
            return None
        return int(selection[0])

    def _ouvrir_formulaire(self, titre, champs, valeurs, callback):
        """Ouvre une fenêtre modale de formulaire et appelle callback(valeurs) à la validation."""
        fenetre = tk.Toplevel(self.racine)
        fenetre.title(titre)
        fenetre.transient(self.racine)
        fenetre.grab_set()
        fenetre.resizable(False, False)

        saisies = {}
        for i, champ in enumerate(champs):
            ttk.Label(fenetre, text=champ["libelle"]).grid(row=i, column=0, sticky="w", padx=10, pady=6)
            if champ["type"] == "choix":
                widget = ttk.Combobox(fenetre, values=champ["options"], state="readonly", width=28)
                widget.set(valeurs.get(champ["cle"], champ["options"][0]))
            else:
                widget = ttk.Entry(fenetre, width=30)
                widget.insert(0, str(valeurs.get(champ["cle"], "")))
            widget.grid(row=i, column=1, padx=10, pady=6)
            saisies[champ["cle"]] = (champ, widget)

        def valider():
            """Lit les saisies, contrôle les nombres, ferme la fenêtre et appelle le callback."""
            resultat = {}
            for cle, (champ, widget) in saisies.items():
                valeur = widget.get().strip()
                if champ["type"] == "nombre":
                    try:
                        valeur = float(valeur) if "." in valeur else int(valeur)
                    except ValueError:
                        messagebox.showerror("Erreur", champ["libelle"] + " doit être un nombre.")
                        return
                resultat[cle] = valeur
            fenetre.destroy()
            callback(resultat)

        cadre_boutons = ttk.Frame(fenetre)
        cadre_boutons.grid(row=len(champs), column=0, columnspan=2, pady=12)
        ttk.Button(cadre_boutons, text="Valider", command=valider).pack(side="left", padx=6)
        ttk.Button(cadre_boutons, text="Annuler", command=fenetre.destroy).pack(side="left", padx=6)


    def afficher_connexion(self):
        """Construit et affiche l'écran de connexion (email + mot de passe)."""
        self._vider(self.racine)
        self.utilisateur = None
        self.adherent = None

        cadre = ttk.Frame(self.racine, padding=40)
        cadre.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(cadre, text="Connexion", style="Titre.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(cadre, text="Email :").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.champ_email = ttk.Entry(cadre, width=30)
        self.champ_email.grid(row=1, column=1, padx=6, pady=6)
        self.champ_email.insert(0, "admin@biblio.ma")

        ttk.Label(cadre, text="Mot de passe :").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.champ_mdp = ttk.Entry(cadre, width=30, show="*")
        self.champ_mdp.grid(row=2, column=1, padx=6, pady=6)
        self.champ_mdp.insert(0, "admin123")

        ttk.Button(cadre, text="Se connecter", command=self.traiter_connexion).grid(
            row=3, column=0, columnspan=2, pady=16
        )

        self.racine.bind("<Return>", lambda evenement: self.traiter_connexion())

        aide = (
            "Comptes de test :\n"
            "Admin : admin@biblio.ma / admin123\n"
            "Bibliothécaire : biblio@biblio.ma / biblio123\n"
            "Adhérent (étudiant) : sara@biblio.ma / sara123\n"
            "Adhérent (enseignant) : karim@biblio.ma / karim123"
        )
        ttk.Label(cadre, text=aide, foreground="#555555", justify="left").grid(
            row=4, column=0, columnspan=2, pady=(10, 0)
        )

    def traiter_connexion(self):
        """Vérifie les identifiants saisis et ouvre l'application si la connexion réussit."""
        email = self.champ_email.get().strip()
        mot_de_passe = self.champ_mdp.get().strip()
        utilisateur = models.verifier_connexion(email, mot_de_passe)
        if utilisateur is None:
            messagebox.showerror("Échec", "Email ou mot de passe incorrect.")
            return

        self.utilisateur = utilisateur
        if utilisateur["role"] == "Adherent":
            self.adherent = models.obtenir_adherent_par_utilisateur(utilisateur["id_utilisateur"])
            if self.adherent is None:
                messagebox.showerror("Erreur", "Aucune fiche adhérent liée à ce compte.")
                return

        self.racine.unbind("<Return>")
        self.afficher_application()

    def deconnexion(self):
        """Déconnecte l'utilisateur et revient à l'écran de connexion."""
        self.afficher_connexion()


    def _navigation(self):
        """Renvoie la liste des entrées de menu (libellé, méthode) selon le rôle connecté."""
        role = self.utilisateur["role"]
        if role == "Admin":
            return [
                ("Rôles utilisateurs", self.ecran_roles),
                ("Configuration", self.ecran_configuration),
                ("Emplacements", self.ecran_emplacements),
                ("Tableau de bord", self.ecran_tableau_bord),
            ]
        if role == "Bibliothecaire":
            return [
                ("Catalogue", self.ecran_catalogue),
                ("Adhérents", self.ecran_adherents),
                ("Emprunter", self.ecran_emprunter),
                ("Retours / Prolong.", self.ecran_retours),
                ("Vol / Perte", self.ecran_vol_perte),
                ("Pénalités", self.ecran_penalites),
            ]
        return [
            ("Catalogue", self.ecran_catalogue),
            ("Mon historique", self.ecran_historique),
            ("Mes notifications", self.ecran_notifications),
        ]

    def afficher_application(self):
        """Construit la disposition principale après connexion."""
        self._vider(self.racine)

        entete = ttk.Frame(self.racine, padding=10)
        entete.pack(fill="x")
        ttk.Label(entete, text="Système de Gestion des Emprunts", style="Titre.TLabel").pack(side="left")
        infos = self.utilisateur["email"] + "  (" + self.utilisateur["role"] + ")"
        ttk.Label(entete, text=infos, foreground="#555555").pack(side="left", padx=20)
        ttk.Button(entete, text="Déconnexion", command=self.deconnexion).pack(side="right")

        ttk.Separator(self.racine, orient="horizontal").pack(fill="x")

        corps = ttk.Frame(self.racine)
        corps.pack(fill="both", expand=True)

        self.cadre_nav = ttk.Frame(corps, padding=10)
        self.cadre_nav.pack(side="left", fill="y")
        self.cadre_contenu = ttk.Frame(corps, padding=10)
        self.cadre_contenu.pack(side="left", fill="both", expand=True)

        entrees = self._navigation()
        for libelle, methode in entrees:
            ttk.Button(self.cadre_nav, text=libelle, width=18, command=methode).pack(fill="x", pady=4)

        entrees[0][1]()

    def _titre_section(self, texte):
        """Affiche un titre de section en haut du cadre de contenu."""
        ttk.Label(self.cadre_contenu, text=texte, style="Titre.TLabel").pack(anchor="w", pady=(0, 10))


    def ecran_catalogue(self):
        """Affiche le catalogue des livres avec les actions adaptées au rôle."""
        self._vider(self.cadre_contenu)
        self._titre_section("Catalogue des livres")

        colonnes = [
            ("id", "ID", 40),
            ("titre", "Titre", 200),
            ("auteur", "Auteur", 150),
            ("categorie", "Catégorie", 110),
            ("prix", "Prix (DH)", 80),
            ("dispo", "Disponibles", 90),
            ("isbn", "ISBN", 120),
        ]
        self.tableau_livres = self._creer_tableau(self.cadre_contenu, colonnes)
        self._remplir_catalogue()

        barre_actions = ttk.Frame(self.cadre_contenu)
        barre_actions.pack(fill="x", pady=8)

        if self.utilisateur["role"] == "Bibliothecaire":
            ttk.Button(barre_actions, text="Ajouter", command=self._ajouter_livre).pack(side="left", padx=4)
            ttk.Button(barre_actions, text="Modifier", command=self._modifier_livre).pack(side="left", padx=4)
            ttk.Button(barre_actions, text="Supprimer", command=self._supprimer_livre).pack(side="left", padx=4)
            ttk.Button(barre_actions, text="Exemplaires", command=self._gerer_exemplaires).pack(side="left", padx=4)
        else:
            ttk.Button(barre_actions, text="Réserver le livre", command=self._reserver_livre).pack(side="left", padx=4)

    def _remplir_catalogue(self):
        """Vide puis remplit le tableau du catalogue avec les livres de la base."""
        for ligne in self.tableau_livres.get_children():
            self.tableau_livres.delete(ligne)
        for livre in models.lister_livres():
            disponibles = models.compter_exemplaires_disponibles(livre["id_livre"])
            self.tableau_livres.insert(
                "", "end", iid=str(livre["id_livre"]),
                values=(
                    livre["id_livre"], livre["titre"], livre["auteur"],
                    livre["categorie"], livre["prix"], disponibles, livre["isbn"],
                ),
            )

    def _champs_livre(self):
        """Renvoie la définition des champs du formulaire d'un livre."""
        return [
            {"cle": "titre", "libelle": "Titre", "type": "texte"},
            {"cle": "auteur", "libelle": "Auteur", "type": "texte"},
            {"cle": "editeur", "libelle": "Éditeur", "type": "texte"},
            {"cle": "categorie", "libelle": "Catégorie", "type": "texte"},
            {"cle": "prix", "libelle": "Prix (DH)", "type": "nombre"},
            {"cle": "nb_exemplaires", "libelle": "Nb exemplaires", "type": "nombre"},
            {"cle": "isbn", "libelle": "ISBN", "type": "texte"},
        ]

    def _ajouter_livre(self):
        """Ouvre le formulaire de création d'un livre."""
        def enregistrer(valeurs):
            models.creer_livre(
                valeurs["titre"], valeurs["auteur"], valeurs["editeur"], valeurs["categorie"],
                valeurs["prix"], valeurs["nb_exemplaires"], valeurs["isbn"],
            )
            self._remplir_catalogue()
            messagebox.showinfo("Succès", "Livre ajouté.")
        valeurs_init = {"prix": 0, "nb_exemplaires": 0}
        self._ouvrir_formulaire("Ajouter un livre", self._champs_livre(), valeurs_init, enregistrer)

    def _modifier_livre(self):
        """Ouvre le formulaire de modification du livre sélectionné."""
        id_livre = self._selection_id(self.tableau_livres)
        if id_livre is None:
            return
        livre = models.obtenir_livre(id_livre)
        valeurs_init = dict(livre)

        def enregistrer(valeurs):
            models.modifier_livre(
                id_livre, valeurs["titre"], valeurs["auteur"], valeurs["editeur"], valeurs["categorie"],
                valeurs["prix"], valeurs["nb_exemplaires"], valeurs["isbn"],
            )
            self._remplir_catalogue()
            messagebox.showinfo("Succès", "Livre modifié.")
        self._ouvrir_formulaire("Modifier le livre", self._champs_livre(), valeurs_init, enregistrer)

    def _supprimer_livre(self):
        """Supprime le livre sélectionné après confirmation."""
        id_livre = self._selection_id(self.tableau_livres)
        if id_livre is None:
            return
        if messagebox.askyesno("Confirmation", "Supprimer ce livre ?"):
            models.supprimer_livre(id_livre)
            self._remplir_catalogue()

    def _reserver_livre(self):
        """Réserve le livre sélectionné pour l'adhérent connecté (workflow réservation)."""
        id_livre = self._selection_id(self.tableau_livres)
        if id_livre is None:
            return
        succes, message = logique.reserver_livre(self.adherent["id_adherent"], id_livre)
        if succes:
            messagebox.showinfo("Réservation", message)
        else:
            messagebox.showerror("Refus", message)


    def _gerer_exemplaires(self):
        """Ouvre une fenêtre listant les exemplaires du livre sélectionné et permet d'en ajouter."""
        id_livre = self._selection_id(self.tableau_livres)
        if id_livre is None:
            return
        livre = models.obtenir_livre(id_livre)

        fenetre = tk.Toplevel(self.racine)
        fenetre.title("Exemplaires - " + livre["titre"])
        fenetre.geometry("640x420")
        fenetre.transient(self.racine)

        colonnes = [
            ("id", "ID", 40),
            ("code", "Code-barres", 120),
            ("etat", "État", 100),
            ("dispo", "Disponible", 90),
            ("emp", "Emplacement", 160),
        ]
        tableau = self._creer_tableau(fenetre, colonnes, hauteur=10)

        def rafraichir():
            for ligne in tableau.get_children():
                tableau.delete(ligne)
            for ex in models.lister_exemplaires_par_livre(id_livre):
                dispo = "Oui" if ex["disponible"] == 1 else "Non"
                code_emp = ex["code_emplacement"] if ex["code_emplacement"] else "-"
                tableau.insert(
                    "", "end", iid=str(ex["id_exemplaire"]),
                    values=(ex["id_exemplaire"], ex["code_barre"], ex["etat"], dispo, code_emp),
                )
        rafraichir()

        def ajouter_exemplaire():
            emplacements = models.lister_emplacements()
            if not emplacements:
                messagebox.showwarning("Impossible", "Créez d'abord un emplacement (menu Admin).")
                return
            options_emp = [e["code_emplacement"] for e in emplacements]
            champs = [
                {"cle": "code_barre", "libelle": "Code-barres", "type": "texte"},
                {"cle": "etat", "libelle": "État", "type": "choix", "options": ["Bon", "Use", "Endommage", "Perdu"]},
                {"cle": "emplacement", "libelle": "Emplacement", "type": "choix", "options": options_emp},
            ]

            def enregistrer(valeurs):
                emp = next(e for e in emplacements if e["code_emplacement"] == valeurs["emplacement"])
                models.creer_exemplaire(id_livre, emp["id_emplacement"], valeurs["code_barre"], valeurs["etat"], 1)
                rafraichir()
                self._remplir_catalogue()
            self._ouvrir_formulaire("Ajouter un exemplaire", champs, {}, enregistrer)

        ttk.Button(fenetre, text="Ajouter un exemplaire", command=ajouter_exemplaire).pack(pady=8)


    def ecran_adherents(self):
        """Affiche la liste des adhérents et les actions de gestion."""
        self._vider(self.cadre_contenu)
        self._titre_section("Gestion des adhérents")

        colonnes = [
            ("id", "ID", 40),
            ("nom", "Nom", 120),
            ("prenom", "Prénom", 120),
            ("type", "Type", 100),
            ("statut", "Statut", 90),
            ("quota", "Quota", 60),
            ("tel", "Téléphone", 110),
        ]
        self.tableau_adherents = self._creer_tableau(self.cadre_contenu, colonnes)
        self._remplir_adherents()

        barre = ttk.Frame(self.cadre_contenu)
        barre.pack(fill="x", pady=8)
        ttk.Button(barre, text="Ajouter", command=self._ajouter_adherent).pack(side="left", padx=4)
        ttk.Button(barre, text="Modifier", command=self._modifier_adherent).pack(side="left", padx=4)
        ttk.Button(barre, text="Supprimer", command=self._supprimer_adherent).pack(side="left", padx=4)

    def _remplir_adherents(self):
        """Vide puis remplit le tableau des adhérents."""
        for ligne in self.tableau_adherents.get_children():
            self.tableau_adherents.delete(ligne)
        for a in models.lister_adherents():
            self.tableau_adherents.insert(
                "", "end", iid=str(a["id_adherent"]),
                values=(a["id_adherent"], a["nom"], a["prenom"], a["type_adherent"], a["statut"], a["max_emprunts"], a["telephone"]),
            )

    def _champs_adherent(self):
        """Renvoie la définition des champs du formulaire d'un adhérent."""
        return [
            {"cle": "nom", "libelle": "Nom", "type": "texte"},
            {"cle": "prenom", "libelle": "Prénom", "type": "texte"},
            {"cle": "cin", "libelle": "CIN", "type": "texte"},
            {"cle": "email", "libelle": "Email", "type": "texte"},
            {"cle": "telephone", "libelle": "Téléphone", "type": "texte"},
            {"cle": "type_adherent", "libelle": "Type", "type": "choix", "options": ["Etudiant", "Enseignant", "Externe"]},
            {"cle": "statut", "libelle": "Statut", "type": "choix", "options": ["Actif", "Suspendu", "Bloque"]},
            {"cle": "max_emprunts", "libelle": "Quota d'emprunts", "type": "nombre"},
        ]

    def _ajouter_adherent(self):
        """Ouvre le formulaire de création d'un adhérent AVEC son compte de connexion."""
        champs = self._champs_adherent() + [
            {"cle": "mot_de_passe", "libelle": "Mot de passe (connexion)", "type": "texte"},
        ]

        def enregistrer(valeurs):
            email = str(valeurs["email"]).strip()
            mdp = str(valeurs["mot_de_passe"]).strip()
            if not email or not mdp:
                messagebox.showerror("Champs requis",
                                     "L'email et le mot de passe sont obligatoires pour créer le compte de connexion.")
                return
            if models.obtenir_utilisateur_par_email(email):
                messagebox.showerror("Email déjà utilisé", "Un compte existe déjà avec cet email.")
                return
            id_utilisateur = models.creer_utilisateur(email, mdp, "Adherent")
            models.creer_adherent(
                id_utilisateur, valeurs["nom"], valeurs["prenom"], valeurs["cin"], email,
                valeurs["telephone"], valeurs["type_adherent"], valeurs["statut"], valeurs["max_emprunts"],
            )
            self._remplir_adherents()
            messagebox.showinfo("Succès",
                                "Adhérent créé avec son compte de connexion.\nEmail : " + email)
        valeurs_init = {"type_adherent": "Etudiant", "statut": "Actif", "max_emprunts": 3}
        self._ouvrir_formulaire("Ajouter un adhérent (avec compte)", champs, valeurs_init, enregistrer)

    def _modifier_adherent(self):
        """Ouvre le formulaire de modification de l'adhérent sélectionné."""
        id_adherent = self._selection_id(self.tableau_adherents)
        if id_adherent is None:
            return
        adherent = models.obtenir_adherent(id_adherent)
        valeurs_init = dict(adherent)

        def enregistrer(valeurs):
            models.modifier_adherent(
                id_adherent, valeurs["nom"], valeurs["prenom"], valeurs["cin"], valeurs["email"],
                valeurs["telephone"], valeurs["type_adherent"], valeurs["statut"], valeurs["max_emprunts"],
            )
            self._remplir_adherents()
            messagebox.showinfo("Succès", "Adhérent modifié.")
        self._ouvrir_formulaire("Modifier l'adhérent", self._champs_adherent(), valeurs_init, enregistrer)

    def _supprimer_adherent(self):
        """Supprime l'adhérent sélectionné après confirmation."""
        id_adherent = self._selection_id(self.tableau_adherents)
        if id_adherent is None:
            return
        if messagebox.askyesno("Confirmation", "Supprimer cet adhérent et son compte de connexion ?"):
            adherent = models.obtenir_adherent(id_adherent)
            models.supprimer_adherent(id_adherent)
            if adherent and adherent["id_utilisateur"]:
                models.supprimer_utilisateur(adherent["id_utilisateur"])
            self._remplir_adherents()


    def ecran_emprunter(self):
        """Affiche le formulaire d'emprunt (choix d'un adhérent et d'un exemplaire disponible)."""
        self._vider(self.cadre_contenu)
        self._titre_section("Enregistrer un emprunt")

        cadre = ttk.Frame(self.cadre_contenu)
        cadre.pack(anchor="w", pady=10)

        ttk.Label(cadre, text="Adhérent :").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.adherents_dispo = models.lister_adherents()
        options_adherents = [
            str(a["id_adherent"]) + " - " + a["nom"] + " " + a["prenom"] + " (" + a["type_adherent"] + ")"
            for a in self.adherents_dispo
        ]
        self.combo_adherent = ttk.Combobox(cadre, values=options_adherents, state="readonly", width=45)
        self.combo_adherent.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(cadre, text="Exemplaire disponible :").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.exemplaires_dispo = models.lister_exemplaires_disponibles()
        options_ex = [
            str(e["id_exemplaire"]) + " - " + e["code_barre"] + " - " + e["titre"]
            for e in self.exemplaires_dispo
        ]
        self.combo_exemplaire = ttk.Combobox(cadre, values=options_ex, state="readonly", width=45)
        self.combo_exemplaire.grid(row=1, column=1, padx=6, pady=6)

        ttk.Button(self.cadre_contenu, text="Emprunter", command=self._valider_emprunt).pack(anchor="w", pady=10)

    def _valider_emprunt(self):
        """Valide l'emprunt en lançant le workflow métier avec les sélections."""
        if not self.combo_adherent.get() or not self.combo_exemplaire.get():
            messagebox.showwarning("Champs requis", "Sélectionnez un adhérent et un exemplaire.")
            return
        id_adherent = int(self.combo_adherent.get().split(" - ")[0])
        id_exemplaire = int(self.combo_exemplaire.get().split(" - ")[0])
        succes, message = logique.emprunter_livre(id_adherent, id_exemplaire)
        if succes:
            messagebox.showinfo("Emprunt", message)
            self.ecran_emprunter()
        else:
            messagebox.showerror("Refus", message)


    def ecran_retours(self):
        """Affiche les emprunts en cours avec les actions de retour et de prolongation."""
        self._vider(self.cadre_contenu)
        self._titre_section("Emprunts en cours (retour / prolongation)")

        colonnes = [
            ("id", "N° emprunt", 80),
            ("adherent", "Adhérent", 160),
            ("titre", "Livre", 200),
            ("code", "Code-barres", 110),
            ("prevu", "Retour prévu", 100),
            ("statut", "Statut", 90),
        ]
        self.tableau_emprunts = self._creer_tableau(self.cadre_contenu, colonnes)
        self._remplir_emprunts_en_cours()

        barre = ttk.Frame(self.cadre_contenu)
        barre.pack(fill="x", pady=8)
        ttk.Button(barre, text="Retourner", command=self._valider_retour).pack(side="left", padx=4)
        ttk.Button(barre, text="Prolonger (+7 j)", command=self._valider_prolongation).pack(side="left", padx=4)

    def _remplir_emprunts_en_cours(self):
        """Vide puis remplit le tableau des emprunts en cours."""
        for ligne in self.tableau_emprunts.get_children():
            self.tableau_emprunts.delete(ligne)
        self.emprunts_courants = {}
        for em in models.lister_emprunts_en_cours():
            self.emprunts_courants[em["id_emprunt"]] = em
            self.tableau_emprunts.insert(
                "", "end", iid=str(em["id_emprunt"]),
                values=(
                    em["id_emprunt"], em["nom"] + " " + em["prenom"], em["titre"],
                    em["code_barre"], em["date_retour_prevue"], em["statut"],
                ),
            )

    def _valider_retour(self):
        """Enregistre le retour de l'emprunt sélectionné (workflow de retour)."""
        id_emprunt = self._selection_id(self.tableau_emprunts)
        if id_emprunt is None:
            return
        emprunt = self.emprunts_courants[id_emprunt]
        succes, message = logique.retourner_livre(emprunt["id_exemplaire"])
        if succes:
            messagebox.showinfo("Retour", message)
        else:
            messagebox.showerror("Erreur", message)
        self._remplir_emprunts_en_cours()

    def _valider_prolongation(self):
        """Prolonge l'emprunt sélectionné (workflow de prolongation)."""
        id_emprunt = self._selection_id(self.tableau_emprunts)
        if id_emprunt is None:
            return
        succes, message = logique.prolonger_emprunt(id_emprunt)
        if succes:
            messagebox.showinfo("Prolongation", message)
        else:
            messagebox.showerror("Refus", message)
        self._remplir_emprunts_en_cours()


    def ecran_vol_perte(self):
        """Affiche les emprunts en cours pour déclarer une perte ou un vol."""
        self._vider(self.cadre_contenu)
        self._titre_section("Déclarer un vol ou une perte")

        colonnes = [
            ("id", "N° emprunt", 80),
            ("adherent", "Adhérent", 160),
            ("titre", "Livre", 220),
            ("code", "Code-barres", 110),
            ("statut", "Statut", 90),
        ]
        self.tableau_emprunts = self._creer_tableau(self.cadre_contenu, colonnes)
        self._remplir_emprunts_en_cours_simple()

        barre = ttk.Frame(self.cadre_contenu)
        barre.pack(fill="x", pady=8)
        ttk.Button(barre, text="Déclarer Perte", command=lambda: self._declarer("Perte")).pack(side="left", padx=4)
        ttk.Button(barre, text="Déclarer Vol", command=lambda: self._declarer("Vol")).pack(side="left", padx=4)

    def _remplir_emprunts_en_cours_simple(self):
        """Remplit le tableau des emprunts en cours pour l'écran vol/perte."""
        for ligne in self.tableau_emprunts.get_children():
            self.tableau_emprunts.delete(ligne)
        self.emprunts_courants = {}
        for em in models.lister_emprunts_en_cours():
            self.emprunts_courants[em["id_emprunt"]] = em
            self.tableau_emprunts.insert(
                "", "end", iid=str(em["id_emprunt"]),
                values=(em["id_emprunt"], em["nom"] + " " + em["prenom"], em["titre"], em["code_barre"], em["statut"]),
            )

    def _declarer(self, type_penalite):
        """Déclare une perte ou un vol sur l'emprunt sélectionné (workflow vol/perte)."""
        id_emprunt = self._selection_id(self.tableau_emprunts)
        if id_emprunt is None:
            return
        if not messagebox.askyesno("Confirmation", "Déclarer une " + type_penalite + " pour cet emprunt ?"):
            return
        succes, message = logique.declarer_perte_ou_vol(id_emprunt, type_penalite)
        if succes:
            messagebox.showinfo("Déclaration", message)
        else:
            messagebox.showerror("Erreur", message)
        self._remplir_emprunts_en_cours_simple()


    def ecran_penalites(self):
        """Affiche les pénalités et permet de les payer ou de les exonérer."""
        self._vider(self.cadre_contenu)
        self._titre_section("Gestion des pénalités")

        colonnes = [
            ("id", "ID", 40),
            ("adherent", "Adhérent", 150),
            ("titre", "Livre", 180),
            ("type", "Type", 80),
            ("montant", "Montant (DH)", 90),
            ("paiement", "Paiement", 90),
            ("date", "Date", 100),
        ]
        self.tableau_penalites = self._creer_tableau(self.cadre_contenu, colonnes)
        self._remplir_penalites()

        barre = ttk.Frame(self.cadre_contenu)
        barre.pack(fill="x", pady=8)
        ttk.Button(barre, text="Payer", command=self._payer_penalite).pack(side="left", padx=4)
        ttk.Button(barre, text="Exonérer", command=self._exonerer_penalite).pack(side="left", padx=4)

    def _remplir_penalites(self):
        """Vide puis remplit le tableau des pénalités."""
        for ligne in self.tableau_penalites.get_children():
            self.tableau_penalites.delete(ligne)
        for p in models.lister_toutes_penalites():
            self.tableau_penalites.insert(
                "", "end", iid=str(p["id_penalite"]),
                values=(
                    p["id_penalite"], p["nom"] + " " + p["prenom"], p["titre"],
                    p["type_penalite"], p["montant"], p["statut_paiement"], p["date_creation"],
                ),
            )

    def _payer_penalite(self):
        """Marque la pénalité sélectionnée comme payée (workflow paiement)."""
        id_penalite = self._selection_id(self.tableau_penalites)
        if id_penalite is None:
            return
        succes, message = logique.payer_penalite(id_penalite)
        if succes:
            messagebox.showinfo("Paiement", message)
        else:
            messagebox.showerror("Erreur", message)
        self._remplir_penalites()

    def _exonerer_penalite(self):
        """Exonère la pénalité sélectionnée (workflow exonération)."""
        id_penalite = self._selection_id(self.tableau_penalites)
        if id_penalite is None:
            return
        succes, message = logique.exonerer_penalite(id_penalite)
        if succes:
            messagebox.showinfo("Exonération", message)
        else:
            messagebox.showerror("Erreur", message)
        self._remplir_penalites()


    def ecran_roles(self):
        """Affiche les comptes utilisateurs et permet de changer leur rôle."""
        self._vider(self.cadre_contenu)
        self._titre_section("Gestion des rôles utilisateurs")

        colonnes = [
            ("id", "ID", 50),
            ("email", "Email", 260),
            ("role", "Rôle", 150),
        ]
        self.tableau_utilisateurs = self._creer_tableau(self.cadre_contenu, colonnes)
        self._remplir_utilisateurs()

        barre = ttk.Frame(self.cadre_contenu)
        barre.pack(fill="x", pady=8)
        ttk.Button(barre, text="Changer le rôle", command=self._changer_role).pack(side="left", padx=4)

    def _remplir_utilisateurs(self):
        """Vide puis remplit le tableau des utilisateurs."""
        for ligne in self.tableau_utilisateurs.get_children():
            self.tableau_utilisateurs.delete(ligne)
        for u in models.lister_utilisateurs():
            self.tableau_utilisateurs.insert(
                "", "end", iid=str(u["id_utilisateur"]),
                values=(u["id_utilisateur"], u["email"], u["role"]),
            )

    def _changer_role(self):
        """Ouvre un formulaire pour changer le rôle de l'utilisateur sélectionné."""
        id_utilisateur = self._selection_id(self.tableau_utilisateurs)
        if id_utilisateur is None:
            return
        utilisateur = models.obtenir_utilisateur(id_utilisateur)
        champs = [{"cle": "role", "libelle": "Rôle", "type": "choix", "options": ["Admin", "Bibliothecaire", "Adherent"]}]

        def enregistrer(valeurs):
            models.modifier_role_utilisateur(id_utilisateur, valeurs["role"])
            self._remplir_utilisateurs()
            messagebox.showinfo("Succès", "Rôle mis à jour.")
        self._ouvrir_formulaire("Changer le rôle", champs, {"role": utilisateur["role"]}, enregistrer)


    def ecran_configuration(self):
        """Affiche les quotas des adhérents (configurables) et les paramètres de gestion."""
        self._vider(self.cadre_contenu)
        self._titre_section("Configuration")

        cadre_quota = ttk.LabelFrame(self.cadre_contenu, text="Quotas d'emprunts par adhérent (RG01)", padding=8)
        cadre_quota.pack(fill="both", expand=True, pady=(0, 10))

        colonnes = [
            ("id", "ID", 50),
            ("nom", "Adhérent", 200),
            ("type", "Type", 120),
            ("quota", "Quota", 80),
        ]
        self.tableau_quota = self._creer_tableau(cadre_quota, colonnes, hauteur=6)
        self._remplir_quota()
        ttk.Button(cadre_quota, text="Modifier le quota", command=self._modifier_quota).pack(anchor="w", pady=6)

        cadre_param = ttk.LabelFrame(self.cadre_contenu, text="Paramètres de gestion (fixes)", padding=8)
        cadre_param.pack(fill="x")
        parametres = (
            "Durée d'un emprunt : " + str(logique.DUREE_EMPRUNT_JOURS) + " jours (RG02)\n"
            "Prolongation : +" + str(logique.DUREE_PROLONGATION_JOURS) + " jours, une seule fois (RG02)\n"
            "Pénalité de retard : " + str(logique.TARIF_RETARD_PAR_JOUR) + " DH / jour (RG03)\n"
            "Présomption de perte : au-delà de " + str(logique.SEUIL_PERTE_JOURS) + " jours de retard (RG03)\n"
            "Frais administratifs (perte/vol) : " + str(logique.FRAIS_ADMINISTRATIFS) + " DH"
        )
        ttk.Label(cadre_param, text=parametres, justify="left").pack(anchor="w")

    def _remplir_quota(self):
        """Vide puis remplit le tableau des quotas des adhérents."""
        for ligne in self.tableau_quota.get_children():
            self.tableau_quota.delete(ligne)
        for a in models.lister_adherents():
            self.tableau_quota.insert(
                "", "end", iid=str(a["id_adherent"]),
                values=(a["id_adherent"], a["nom"] + " " + a["prenom"], a["type_adherent"], a["max_emprunts"]),
            )

    def _modifier_quota(self):
        """Ouvre un formulaire pour modifier le quota de l'adhérent sélectionné."""
        id_adherent = self._selection_id(self.tableau_quota)
        if id_adherent is None:
            return
        adherent = models.obtenir_adherent(id_adherent)
        champs = [{"cle": "max_emprunts", "libelle": "Quota d'emprunts", "type": "nombre"}]

        def enregistrer(valeurs):
            models.modifier_quota_adherent(id_adherent, valeurs["max_emprunts"])
            self._remplir_quota()
            messagebox.showinfo("Succès", "Quota mis à jour.")
        self._ouvrir_formulaire("Modifier le quota", champs, {"max_emprunts": adherent["max_emprunts"]}, enregistrer)


    def ecran_emplacements(self):
        """Affiche la liste des emplacements et les actions de gestion."""
        self._vider(self.cadre_contenu)
        self._titre_section("Gestion des emplacements")

        colonnes = [
            ("id", "ID", 50),
            ("salle", "Salle", 100),
            ("etagere", "Étagère", 90),
            ("rangee", "Rangée", 90),
            ("position", "Position", 90),
            ("code", "Code", 160),
        ]
        self.tableau_emplacements = self._creer_tableau(self.cadre_contenu, colonnes)
        self._remplir_emplacements()

        barre = ttk.Frame(self.cadre_contenu)
        barre.pack(fill="x", pady=8)
        ttk.Button(barre, text="Ajouter", command=self._ajouter_emplacement).pack(side="left", padx=4)
        ttk.Button(barre, text="Modifier", command=self._modifier_emplacement).pack(side="left", padx=4)
        ttk.Button(barre, text="Supprimer", command=self._supprimer_emplacement).pack(side="left", padx=4)

    def _remplir_emplacements(self):
        """Vide puis remplit le tableau des emplacements."""
        for ligne in self.tableau_emplacements.get_children():
            self.tableau_emplacements.delete(ligne)
        for e in models.lister_emplacements():
            self.tableau_emplacements.insert(
                "", "end", iid=str(e["id_emplacement"]),
                values=(e["id_emplacement"], e["salle"], e["etagere"], e["rangee"], e["position"], e["code_emplacement"]),
            )

    def _champs_emplacement(self):
        """Renvoie la définition des champs du formulaire d'un emplacement."""
        return [
            {"cle": "salle", "libelle": "Salle", "type": "texte"},
            {"cle": "etagere", "libelle": "Étagère", "type": "texte"},
            {"cle": "rangee", "libelle": "Rangée", "type": "texte"},
            {"cle": "position", "libelle": "Position", "type": "texte"},
            {"cle": "code_emplacement", "libelle": "Code", "type": "texte"},
        ]

    def _ajouter_emplacement(self):
        """Ouvre le formulaire de création d'un emplacement."""
        def enregistrer(valeurs):
            models.creer_emplacement(
                valeurs["salle"], valeurs["etagere"], valeurs["rangee"], valeurs["position"], valeurs["code_emplacement"],
            )
            self._remplir_emplacements()
            messagebox.showinfo("Succès", "Emplacement ajouté.")
        self._ouvrir_formulaire("Ajouter un emplacement", self._champs_emplacement(), {}, enregistrer)

    def _modifier_emplacement(self):
        """Ouvre le formulaire de modification de l'emplacement sélectionné."""
        id_emplacement = self._selection_id(self.tableau_emplacements)
        if id_emplacement is None:
            return
        emplacement = models.obtenir_emplacement(id_emplacement)

        def enregistrer(valeurs):
            models.modifier_emplacement(
                id_emplacement, valeurs["salle"], valeurs["etagere"], valeurs["rangee"],
                valeurs["position"], valeurs["code_emplacement"],
            )
            self._remplir_emplacements()
            messagebox.showinfo("Succès", "Emplacement modifié.")
        self._ouvrir_formulaire("Modifier l'emplacement", self._champs_emplacement(), dict(emplacement), enregistrer)

    def _supprimer_emplacement(self):
        """Supprime l'emplacement sélectionné après confirmation."""
        id_emplacement = self._selection_id(self.tableau_emplacements)
        if id_emplacement is None:
            return
        if messagebox.askyesno("Confirmation", "Supprimer cet emplacement ?"):
            models.supprimer_emplacement(id_emplacement)
            self._remplir_emplacements()


    def ecran_tableau_bord(self):
        """Affiche les indicateurs : livres populaires, emprunts en retard, pertes/vols."""
        self._vider(self.cadre_contenu)
        self._titre_section("Tableau de bord")
        donnees = logique.donnees_tableau_de_bord()

        cadre_pop = ttk.LabelFrame(self.cadre_contenu, text="Livres les plus empruntés", padding=8)
        cadre_pop.pack(fill="x", pady=(0, 10))
        tableau_pop = self._creer_tableau(cadre_pop, [("titre", "Titre", 300), ("nb", "Nombre d'emprunts", 150)], hauteur=5)
        for livre in donnees["populaires"]:
            tableau_pop.insert("", "end", values=(livre["titre"], livre["nb_emprunts"]))

        cadre_retard = ttk.LabelFrame(self.cadre_contenu, text="Emprunts en retard", padding=8)
        cadre_retard.pack(fill="x", pady=(0, 10))
        colonnes_retard = [
            ("id", "N°", 50),
            ("adherent", "Adhérent", 180),
            ("titre", "Livre", 220),
            ("prevu", "Retour prévu", 110),
        ]
        tableau_retard = self._creer_tableau(cadre_retard, colonnes_retard, hauteur=5)
        for em in donnees["retards"]:
            tableau_retard.insert(
                "", "end",
                values=(em["id_emprunt"], em["nom"] + " " + em["prenom"], em["titre"], em["date_retour_prevue"]),
            )

        cadre_pv = ttk.LabelFrame(self.cadre_contenu, text="Pertes et vols", padding=8)
        cadre_pv.pack(fill="x")
        ttk.Label(
            cadre_pv, text="Nombre total de livres perdus ou volés : " + str(donnees["pertes_vols"])
        ).pack(anchor="w")


    def ecran_historique(self):
        """Affiche l'historique des emprunts et des pénalités de l'adhérent connecté."""
        self._vider(self.cadre_contenu)
        self._titre_section("Mon historique")

        cadre_emp = ttk.LabelFrame(self.cadre_contenu, text="Mes emprunts", padding=8)
        cadre_emp.pack(fill="x", pady=(0, 10))
        colonnes_emp = [
            ("id", "N°", 50),
            ("titre", "Livre", 220),
            ("emprunt", "Emprunté le", 100),
            ("prevu", "Retour prévu", 100),
            ("effectif", "Retourné le", 100),
            ("statut", "Statut", 90),
        ]
        tableau_emp = self._creer_tableau(cadre_emp, colonnes_emp, hauteur=6)
        for em in models.lister_emprunts_par_adherent(self.adherent["id_adherent"]):
            tableau_emp.insert(
                "", "end",
                values=(
                    em["id_emprunt"], em["titre"], em["date_emprunt"],
                    em["date_retour_prevue"], em["date_retour_effective"] or "-", em["statut"],
                ),
            )

        cadre_pen = ttk.LabelFrame(self.cadre_contenu, text="Mes pénalités", padding=8)
        cadre_pen.pack(fill="x")
        colonnes_pen = [
            ("id", "ID", 50),
            ("titre", "Livre", 220),
            ("type", "Type", 90),
            ("montant", "Montant (DH)", 100),
            ("paiement", "Paiement", 100),
        ]
        tableau_pen = self._creer_tableau(cadre_pen, colonnes_pen, hauteur=5)
        for p in models.lister_penalites_par_adherent(self.adherent["id_adherent"]):
            tableau_pen.insert(
                "", "end",
                values=(p["id_penalite"], p["titre"], p["type_penalite"], p["montant"], p["statut_paiement"]),
            )


    def ecran_notifications(self):
        """Affiche les notifications de disponibilité (réservations devenues Disponible)."""
        self._vider(self.cadre_contenu)
        self._titre_section("Mes notifications")

        colonnes = [
            ("id", "ID", 50),
            ("titre", "Livre", 250),
            ("date", "Réservé le", 120),
            ("statut", "Statut", 120),
        ]
        tableau = self._creer_tableau(self.cadre_contenu, colonnes)

        notifications = models.lister_notifications_adherent(self.adherent["id_adherent"])
        for r in notifications:
            tableau.insert(
                "", "end", iid=str(r["id_reservation"]),
                values=(r["id_reservation"], r["titre"], r["date_reservation"], r["statut"]),
            )

        if not notifications:
            ttk.Label(self.cadre_contenu, text="Aucune notification pour le moment.", foreground="#555555").pack(
                anchor="w", pady=8
            )
        else:
            ttk.Label(
                self.cadre_contenu,
                text="Les livres ci-dessus sont disponibles : présentez-vous pour les emprunter.",
                foreground="#555555",
            ).pack(anchor="w", pady=8)

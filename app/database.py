import sqlite3
import os

CHEMIN_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bibliotheque.db")


def obtenir_connexion():
    """Ouvre et renvoie une nouvelle connexion SQLite configurée."""
    connexion = sqlite3.connect(CHEMIN_BASE)
    connexion.row_factory = sqlite3.Row
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion


def creer_tables(connexion):
    """Crée toutes les tables de la base si elles n'existent pas encore."""
    curseur = connexion.cursor()

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS utilisateur (
            id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            mot_de_passe TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS adherent (
            id_adherent INTEGER PRIMARY KEY AUTOINCREMENT,
            id_utilisateur INTEGER,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            cin TEXT,
            email TEXT,
            telephone TEXT,
            type_adherent TEXT NOT NULL,
            statut TEXT NOT NULL,
            max_emprunts INTEGER NOT NULL,
            FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur)
        )
        """
    )

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS livre (
            id_livre INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            auteur TEXT,
            editeur TEXT,
            categorie TEXT,
            prix REAL,
            nb_exemplaires INTEGER DEFAULT 0,
            isbn TEXT
        )
        """
    )

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS emplacement (
            id_emplacement INTEGER PRIMARY KEY AUTOINCREMENT,
            salle TEXT,
            etagere TEXT,
            rangee TEXT,
            position TEXT,
            code_emplacement TEXT UNIQUE
        )
        """
    )

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS exemplaire (
            id_exemplaire INTEGER PRIMARY KEY AUTOINCREMENT,
            id_livre INTEGER NOT NULL,
            id_emplacement INTEGER,
            code_barre TEXT UNIQUE,
            etat TEXT NOT NULL,
            disponible INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_livre) REFERENCES livre(id_livre),
            FOREIGN KEY (id_emplacement) REFERENCES emplacement(id_emplacement)
        )
        """
    )

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS emprunt (
            id_emprunt INTEGER PRIMARY KEY AUTOINCREMENT,
            id_adherent INTEGER NOT NULL,
            id_exemplaire INTEGER NOT NULL,
            date_emprunt TEXT NOT NULL,
            date_retour_prevue TEXT NOT NULL,
            date_retour_effective TEXT,
            prolonge INTEGER NOT NULL DEFAULT 0,
            statut TEXT NOT NULL,
            FOREIGN KEY (id_adherent) REFERENCES adherent(id_adherent),
            FOREIGN KEY (id_exemplaire) REFERENCES exemplaire(id_exemplaire)
        )
        """
    )

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS reservation (
            id_reservation INTEGER PRIMARY KEY AUTOINCREMENT,
            id_adherent INTEGER NOT NULL,
            id_livre INTEGER NOT NULL,
            date_reservation TEXT NOT NULL,
            statut TEXT NOT NULL,
            priorite INTEGER NOT NULL,
            FOREIGN KEY (id_adherent) REFERENCES adherent(id_adherent),
            FOREIGN KEY (id_livre) REFERENCES livre(id_livre)
        )
        """
    )

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS penalite (
            id_penalite INTEGER PRIMARY KEY AUTOINCREMENT,
            id_emprunt INTEGER NOT NULL,
            type_penalite TEXT NOT NULL,
            montant REAL NOT NULL,
            statut_paiement TEXT NOT NULL,
            date_creation TEXT NOT NULL,
            FOREIGN KEY (id_emprunt) REFERENCES emprunt(id_emprunt)
        )
        """
    )

    connexion.commit()


def inserer_donnees_test(connexion):
    """Insère un petit jeu de données de test si la base est vide."""
    curseur = connexion.cursor()

    curseur.execute("SELECT COUNT(*) FROM utilisateur")
    if curseur.fetchone()[0] > 0:
        return

    curseur.execute(
        "INSERT INTO utilisateur (email, mot_de_passe, role) VALUES (?, ?, ?)",
        ("admin@biblio.ma", "admin123", "Admin"),
    )
    curseur.execute(
        "INSERT INTO utilisateur (email, mot_de_passe, role) VALUES (?, ?, ?)",
        ("biblio@biblio.ma", "biblio123", "Bibliothecaire"),
    )
    curseur.execute(
        "INSERT INTO utilisateur (email, mot_de_passe, role) VALUES (?, ?, ?)",
        ("sara@biblio.ma", "sara123", "Adherent"),
    )
    id_user_sara = curseur.lastrowid
    curseur.execute(
        "INSERT INTO utilisateur (email, mot_de_passe, role) VALUES (?, ?, ?)",
        ("karim@biblio.ma", "karim123", "Adherent"),
    )
    id_user_karim = curseur.lastrowid

    curseur.execute(
        """INSERT INTO adherent
           (id_utilisateur, nom, prenom, cin, email, telephone, type_adherent, statut, max_emprunts)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (id_user_sara, "Alaoui", "Sara", "AB12345", "sara@biblio.ma", "0600000001", "Etudiant", "Actif", 3),
    )
    curseur.execute(
        """INSERT INTO adherent
           (id_utilisateur, nom, prenom, cin, email, telephone, type_adherent, statut, max_emprunts)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (id_user_karim, "Bennani", "Karim", "CD67890", "karim@biblio.ma", "0600000002", "Enseignant", "Actif", 5),
    )
    id_adherent_sara = 1
    id_adherent_karim = 2

    livres = [
        ("Le Petit Prince", "Antoine de Saint-Exupéry", "Gallimard", "Jeunesse", 45.0, 2, "9782070612758"),
        ("1984", "George Orwell", "Secker & Warburg", "Roman", 60.0, 2, "9780451524935"),
        ("Clean Code", "Robert C. Martin", "Prentice Hall", "Informatique", 350.0, 1, "9780132350884"),
    ]
    for livre in livres:
        curseur.execute(
            """INSERT INTO livre (titre, auteur, editeur, categorie, prix, nb_exemplaires, isbn)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            livre,
        )

    emplacements = [
        ("Salle A", "E01", "R01", "P01", "SA-E01-R01-P01"),
        ("Salle A", "E01", "R01", "P02", "SA-E01-R01-P02"),
        ("Salle A", "E02", "R01", "P01", "SA-E02-R01-P01"),
        ("Salle A", "E02", "R01", "P02", "SA-E02-R01-P02"),
        ("Salle B", "E03", "R02", "P15", "SB-E03-R02-P15"),
    ]
    for emp in emplacements:
        curseur.execute(
            """INSERT INTO emplacement (salle, etagere, rangee, position, code_emplacement)
               VALUES (?, ?, ?, ?, ?)""",
            emp,
        )

    exemplaires = [
        (1, 1, "EX-0001", "Bon", 1),
        (1, 2, "EX-0002", "Bon", 1),
        (2, 3, "EX-0003", "Bon", 1),
        (2, 4, "EX-0004", "Use", 1),
        (3, 5, "EX-0005", "Bon", 1),
    ]
    for ex in exemplaires:
        curseur.execute(
            """INSERT INTO exemplaire (id_livre, id_emplacement, code_barre, etat, disponible)
               VALUES (?, ?, ?, ?, ?)""",
            ex,
        )

    from datetime import date, timedelta
    aujourdhui = date.today()

    date_emp1 = (aujourdhui - timedelta(days=20)).isoformat()
    date_prev1 = (aujourdhui - timedelta(days=6)).isoformat()
    curseur.execute(
        """INSERT INTO emprunt
           (id_adherent, id_exemplaire, date_emprunt, date_retour_prevue, date_retour_effective, prolonge, statut)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (id_adherent_sara, 1, date_emp1, date_prev1, None, 0, "EnCours"),
    )
    curseur.execute("UPDATE exemplaire SET disponible = 0 WHERE id_exemplaire = 1")

    date_emp2 = (aujourdhui - timedelta(days=5)).isoformat()
    date_prev2 = (aujourdhui + timedelta(days=9)).isoformat()
    curseur.execute(
        """INSERT INTO emprunt
           (id_adherent, id_exemplaire, date_emprunt, date_retour_prevue, date_retour_effective, prolonge, statut)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (id_adherent_karim, 3, date_emp2, date_prev2, None, 0, "EnCours"),
    )
    curseur.execute("UPDATE exemplaire SET disponible = 0 WHERE id_exemplaire = 3")

    connexion.commit()


def initialiser_base():
    """Point d'entrée d'initialisation : crée les tables et insère les données de test."""
    connexion = obtenir_connexion()
    creer_tables(connexion)
    inserer_donnees_test(connexion)
    connexion.close()

# Système de Gestion des Emprunts de Livres d'une Bibliothèque

Application **de bureau** écrite en **Python pur** (bibliothèque standard uniquement :
`sqlite3` pour la base de données et `tkinter`/`ttk` pour l'interface graphique).
**Aucune installation externe n'est nécessaire.**

## Lancer l'application

Depuis le dossier `bibliotheque` :

```bash
python main.py
```

Au premier lancement, le fichier de base de données `bibliotheque.db` est créé
automatiquement, les tables sont générées et un jeu de **données de test** est inséré.

> Pour repartir de zéro, supprimez simplement le fichier `bibliotheque.db` :
> il sera recréé au prochain lancement.

## Comptes de test

| Rôle           | Email               | Mot de passe |
|----------------|---------------------|--------------|
| Administrateur | `admin@biblio.ma`   | `admin123`   |
| Bibliothécaire | `biblio@biblio.ma`  | `biblio123`  |
| Adhérent (étudiant)   | `sara@biblio.ma`  | `sara123`  |
| Adhérent (enseignant) | `karim@biblio.ma` | `karim123` |

## Structure du projet

| Fichier        | Rôle                                                                 |
|----------------|----------------------------------------------------------------------|
| `database.py`  | Connexion SQLite, création des tables, données de test.              |
| `models.py`    | Fonctions CRUD (accès aux données) pour chaque entité.               |
| `logique.py`   | Règles de gestion (RG01–RG06) et workflows métier.                   |
| `interface.py` | Interface graphique Tkinter (connexion, menus par rôle, tableaux).   |
| `main.py`      | Point d'entrée : initialise la base puis lance l'application.        |

## Fonctions par rôle

- **Administrateur** : gérer les rôles des utilisateurs, configuration (quotas
  d'emprunt + paramètres de gestion), gestion des emplacements, tableau de bord.
- **Bibliothécaire** : catalogue (CRUD livres + exemplaires), adhérents (CRUD),
  emprunter, retourner / prolonger, déclarer vol/perte, gérer et payer les pénalités.
- **Adhérent** : consulter le catalogue et réserver un livre, consulter son
  historique (emprunts + pénalités), consulter ses notifications de disponibilité.

## Règles de gestion implémentées

- **RG01** — Quota d'emprunts simultanés (lu depuis `adherent.max_emprunts`,
  configurable) : Étudiant 3, Enseignant 5.
- **RG02** — Durée d'emprunt de 14 jours, prolongeable **une seule fois** de +7 jours.
- **RG03** — Retard facturé 2 DH / jour ; au-delà de 30 jours de retard, l'emprunt
  passe au statut **Perdu** (présumé).
- **RG04** — Emprunt impossible si le compte est **Suspendu/Bloqué** ou s'il existe
  une **pénalité impayée**.
- **RG05** — Chaque exemplaire est rangé à un emplacement unique (code emplacement).
- **RG06** — Un livre n'est empruntable que s'il reste un exemplaire disponible.
- **Perte / Vol** — Pénalité = prix du livre + frais administratifs ; le compte
  est bloqué tant que la pénalité n'est pas réglée.

## Workflows reproduits (diagrammes de séquence)

1. **Emprunter** : vérifier le compte (RG04) → vérifier le quota (RG01) →
   vérifier la disponibilité (RG06) → créer l'emprunt (retour à +14 j) →
   marquer l'exemplaire indisponible.
2. **Retourner** : récupérer l'emprunt en cours → enregistrer la date de retour →
   calculer le retard → créer une pénalité si retard → remettre l'exemplaire
   disponible et à son emplacement → notifier le prochain réservataire.
3. **Réserver** : si un exemplaire est disponible → « emprunt direct possible » ;
   sinon créer une réservation *EnAttente* avec une priorité (position dans la file).
4. **Prolonger** : autorisé une seule fois (+7 jours).
5. **Payer une pénalité** : statut *Payé* puis déblocage du compte si plus rien n'est dû.

## Remarques

- Les mots de passe sont stockés en clair : ce projet est **pédagogique**, pas destiné
  à la production.
- Les données de test contiennent volontairement un emprunt **en retard** afin
  d'illustrer le calcul de pénalité et le tableau de bord.

import tkinter as tk

import database
import logique
from interface import ApplicationBibliotheque


def main():
    """Initialise la base, recalcule les retards, puis démarre l'interface graphique."""
    database.initialiser_base()
    logique.mettre_a_jour_statuts_retard()

    racine = tk.Tk()
    ApplicationBibliotheque(racine)
    racine.mainloop()


if __name__ == "__main__":
    main()

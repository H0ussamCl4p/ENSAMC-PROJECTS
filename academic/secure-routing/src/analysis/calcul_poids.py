# Fichier : calcul_poids.py
# Rôle : Calculer les poids des liaisons du réseau
# Modèle : w = alpha * Latence + beta * Risque
# Définition des liaisons du réseau :
# (noeud_source, noeud_destination, latence_en_ms, niveau_de_risque)


def main():
    edges = [
        ("Source", "A", 10, 2),
        ("Source", "B", 50, 1),
        ("Source", "C", 20, 5),
        ("A", "D", 10, 2),
        ("A", "E", 30, 8),
        ("B", "D", 20, 1),
        ("B", "F", 100, 1),
        ("C", "E", 10, 5),
        ("D", "Dest", 40, 2),
        ("D", "E", 10, 3),
        ("E", "Dest", 10, 9),
        ("F", "Dest", 10, 1),
    ]
    alpha = 1
    beta = 10
    print("Calcul des poids des liaisons du réseau :\n")
    for u, v, latence, risque in edges:
        poids = alpha * latence + beta * risque
        print(
            f"{u} -> {v} : "
            f"Latence = {latence} ms, "
            f"Risque = {risque}, "
            f"Poids = {poids}"
        )

if __name__ == "__main__":
    main()

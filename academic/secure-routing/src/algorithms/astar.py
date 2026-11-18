
import heapq
import math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# 1. DONNÉES DU RÉSEAU
# Format : (voisin, latence, risque)
donnees_originales = {
    "Source": [("A", 10, 2), ("B", 50, 1), ("C", 20, 5)],
    "A": [("D", 10, 2), ("E", 30, 8)],
    "B": [("D", 20, 1), ("F", 100, 1)],
    "C": [("E", 10, 5)],
    "D": [("Dest", 40, 2), ("E", 10, 3)],
    "E": [("Dest", 10, 9)],
    "F": [("Dest", 10, 1)],
    "Dest": []
}

# 2. POSITIONS DES NŒUDS (POUR LA FIGURE)
positions = {
    "Source": (0, 1),
    "A": (1, 2),
    "B": (1, 1),
    "C": (1, 0),
    "D": (2, 2),
    "E": (2, 0),
    "F": (2, -1),
    "Dest": (3, 1)
}

# 3. HEURISTIQUES
def heuristique_securisee(n1, n2, pos):
    """Heuristique géométrique admissible (cas sécurisé)."""
    x1, y1 = pos[n1]
    x2, y2 = pos[n2]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def heuristique_performance(n1, n2, pos):
    """Heuristique nulle pour garantir A* = Dijkstra."""
    return 0

# 4. CRÉATION DU GRAPHE PONDÉRÉ
def creer_graphe_pondere(donnees, avec_risque=True, beta=10):
    graphe = {}
    for u in donnees:
        graphe[u] = []
        for v, lat, risk in donnees[u]:
            poids = lat + beta * risk if avec_risque else lat
            graphe[u].append((v, poids))
    return graphe

# 5. ALGORITHME A*
def astar(graphe, pos, source, destination, heuristique):
    open_set = [(0, source)]
    g = {s: float("inf") for s in graphe}
    f = {s: float("inf") for s in graphe}
    parent = {s: None for s in graphe}

    g[source] = 0
    f[source] = heuristique(source, destination, pos)
    parent[source] = source

    while open_set:
        _, u = heapq.heappop(open_set)

        if u == destination:
            break

        for v, poids in graphe[u]:
            tentative_g = g[u] + poids
            if tentative_g < g[v]:
                parent[v] = u
                g[v] = tentative_g
                f[v] = tentative_g + heuristique(v, destination, pos)
                heapq.heappush(open_set, (f[v], v))

    return g, parent

# 6. RECONSTRUCTION DU CHEMIN
def reconstruire_chemin(parent, source, destination):
    chemin = []
    x = destination
    while x != source:
        chemin.append(x)
        x = parent[x]
    chemin.append(source)
    chemin.reverse()
    return chemin

# 7. CALCUL DES MÉTRIQUES
def calculer_metriques(chemin, donnees):
    latence, risque = 0, 0
    arcs = {u: {v: (l, r) for v, l, r in donnees[u]} for u in donnees}
    for i in range(len(chemin) - 1):
        u, v = chemin[i], chemin[i + 1]
        l, r = arcs[u][v]
        latence += l
        risque += r
    return latence, risque

# 8. PROGRAMME PRINCIPAL
def main():
    source, destination = "Source", "Dest"
    beta = 10

    # CAS SÉCURISÉ
    graphe_sec = creer_graphe_pondere(donnees_originales, True, beta)
    g_sec, P_sec = astar(
        graphe_sec, positions, source, destination, heuristique_securisee
    )
    chemin_sec = reconstruire_chemin(P_sec, source, destination)
    lat_sec, risk_sec = calculer_metriques(chemin_sec, donnees_originales)

    # CAS PERFORMANCE
    graphe_perf = creer_graphe_pondere(donnees_originales, False)
    g_perf, P_perf = astar(
        graphe_perf, positions, source, destination, heuristique_performance
    )
    chemin_perf = reconstruire_chemin(P_perf, source, destination)
    lat_perf, risk_perf = calculer_metriques(chemin_perf, donnees_originales)

    # AFFICHAGE
    print("\n=== RÉSULTATS A* ===")

    print("\n--- Routage sécurisé ---")
    print("Chemin :", " -> ".join(chemin_sec))
    print(f"Latence = {lat_sec} ms | Risque = {risk_sec} | Coût = {g_sec[destination]}")

    print("\n--- Routage performance ---")
    print("Chemin :", " -> ".join(chemin_perf))
    print(f"Latence = {lat_perf} ms | Risque = {risk_perf} | Coût = {g_perf[destination]}")

    diff_lat = ((lat_sec - lat_perf) / lat_perf) * 100
    diff_risk = ((risk_perf - risk_sec) / risk_perf) * 100
    print(f"\nComparaison : +{diff_lat:.1f}% latence, -{diff_risk:.1f}% risque")

    # 9. VISUALISATION
    G = nx.DiGraph()
    for u in donnees_originales:
        for v, _, _ in donnees_originales[u]:
            G.add_edge(u, v)

    plt.figure(figsize=(14, 8))
    nx.draw_networkx_nodes(G, positions, node_color="lightblue", node_size=1500)
    nx.draw_networkx_labels(G, positions, font_weight="bold")
    nx.draw_networkx_edges(G, positions, edge_color="gray", arrows=True)

    edges_sec = [(chemin_sec[i], chemin_sec[i + 1]) for i in range(len(chemin_sec) - 1)]
    edges_perf = [(chemin_perf[i], chemin_perf[i + 1]) for i in range(len(chemin_perf) - 1)]

    nx.draw_networkx_edges(G, positions, edgelist=edges_sec,
                           edge_color="green", width=3)
    nx.draw_networkx_edges(G, positions, edgelist=edges_perf,
                           edge_color="red", style="dashed", width=3)

    legend = [
        Patch(facecolor="green", edgecolor="green", label="Chemin A* sécurisé"),
        Patch(facecolor="red", edgecolor="red", label="Chemin A* performance")
    ]
    plt.legend(handles=legend, loc="upper left")
    plt.title("Réseau avec chemins optimaux (A*)", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

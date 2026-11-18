
import heapq
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

# 1. DONNÉES DU RÉSEAU
# Format : (voisin, latence(ms), risque)
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

# 2. CRÉATION DU GRAPHE PONDÉRÉ
def creer_graphe_pondere(donnees, avec_risque=True, beta=10):
    graphe = {}
    for u in donnees:
        graphe[u] = []
        for v, lat, risk in donnees[u]:
            poids = lat + beta * risk if avec_risque else lat
            graphe[u].append((v, poids))
    return graphe

# 3. ALGORITHME DE DIJKSTRA
def dijkstra(graphe, source):
    L = {s: float("inf") for s in graphe}
    P = {s: None for s in graphe}
    L[source] = 0
    P[source] = source
    file = [(0, source)]

    while file:
        dist, u = heapq.heappop(file)
        if dist > L[u]:
            continue
        for v, poids in graphe[u]:
            if L[u] + poids < L[v]:
                L[v] = L[u] + poids
                P[v] = u
                heapq.heappush(file, (L[v], v))
    return L, P

# 4. RECONSTRUCTION DU CHEMIN
def reconstruire_chemin(P, source, dest):
    if P[dest] is None:
        return None
    chemin = []
    x = dest
    while x != source:
        if x is None:
            return None
        chemin.append(x)
        x = P[x]
    chemin.append(source)
    chemin.reverse()
    return chemin

# 5. CALCUL DES MÉTRIQUES
def calculer_metriques(chemin, donnees):
    latence, risque = 0, 0
    arcs = {u: {v: (l, r) for v, l, r in donnees[u]} for u in donnees}
    for i in range(len(chemin) - 1):
        u, v = chemin[i], chemin[i + 1]
        l, r = arcs[u][v]
        latence += l
        risque += r
    return latence, risque

# 6. PROGRAMME PRINCIPAL
def main():
    source, destination = "Source", "Dest"
    beta = 10

    # --- Cas sécurisé ---
    graphe_sec = creer_graphe_pondere(donnees_originales, True, beta)
    L_sec, P_sec = dijkstra(graphe_sec, source)
    chemin_sec = reconstruire_chemin(P_sec, source, destination)
    lat_sec, risk_sec = calculer_metriques(chemin_sec, donnees_originales)

    # --- Cas performance ---
    graphe_perf = creer_graphe_pondere(donnees_originales, False)
    L_perf, P_perf = dijkstra(graphe_perf, source)
    chemin_perf = reconstruire_chemin(P_perf, source, destination)
    lat_perf, risk_perf = calculer_metriques(chemin_perf, donnees_originales)

    # --- Résultats ---
    print("\n=== RÉSULTATS ===")
    print(f"Chemin sécurisé     : {' -> '.join(chemin_sec)}")
    print(f"Latence = {lat_sec} ms | Risque = {risk_sec} | Coût = {L_sec[destination]}")

    print(f"\nChemin performance  : {' -> '.join(chemin_perf)}")
    print(f"Latence = {lat_perf} ms | Risque = {risk_perf} | Coût = {L_perf[destination]}")

    if lat_perf > 0 and risk_perf > 0:
        diff_lat = ((lat_sec - lat_perf) / lat_perf) * 100
        diff_risk = ((risk_perf - risk_sec) / risk_perf) * 100
        print(f"\nComparaison : +{diff_lat:.1f}% latence, -{diff_risk:.1f}% risque")

    # 7. VISUALISATION DU RÉSEAU
    G = nx.DiGraph()
    for u in donnees_originales:
        for v, lat, risk in donnees_originales[u]:
            G.add_edge(u, v)

    pos = {
        "Source": (0, 1), "A": (1, 2), "B": (1, 1), "C": (1, 0),
        "D": (2, 2), "E": (2, 0), "F": (2, -1), "Dest": (3, 1)
    }

    plt.figure(figsize=(14, 8))
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=1500)
    nx.draw_networkx_labels(G, pos, font_weight="bold")
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True)

    edges_sec = [(chemin_sec[i], chemin_sec[i+1]) for i in range(len(chemin_sec)-1)]
    edges_perf = [(chemin_perf[i], chemin_perf[i+1]) for i in range(len(chemin_perf)-1)]

    nx.draw_networkx_edges(G, pos, edgelist=edges_sec, edge_color="green", width=3)
    nx.draw_networkx_edges(G, pos, edgelist=edges_perf, edge_color="red", style="dashed", width=3)

    legend = [
        Patch(facecolor="green", edgecolor="green", label="Chemin sécurisé"),
        Patch(facecolor="red", edgecolor="red", label="Chemin performance")
    ]
    plt.legend(handles=legend, loc="upper left")
    plt.title("Réseau avec chemins optimaux", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

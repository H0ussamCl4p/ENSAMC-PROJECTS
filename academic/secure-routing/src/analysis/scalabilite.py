
import time
import random
import heapq
import math
import matplotlib.pyplot as plt

# GÉNÉRATION DE GRAPHE ALÉATOIRE
def generer_graphe(n):
    graphe = {i: [] for i in range(n)}
    for u in range(n):
        voisins = random.sample(range(n), min(3, n-1))
        for v in voisins:
            if u != v:
                poids = random.randint(1, 20)
                graphe[u].append((v, poids))
    return graphe

# DIJKSTRA
def dijkstra(graphe, source):
    dist = {v: float("inf") for v in graphe}
    dist[source] = 0
    Q = [(0, source)]
    while Q:
        d, u = heapq.heappop(Q)
        if d > dist[u]:
            continue
        for v, w in graphe[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(Q, (dist[v], v))
    return dist

# A* (heuristique nulle pour équité)
def astar(graphe, source, dest):
    g = {v: float("inf") for v in graphe}
    g[source] = 0
    Q = [(0, source)]
    while Q:
        _, u = heapq.heappop(Q)
        if u == dest:
            break
        for v, w in graphe[u]:
            if g[u] + w < g[v]:
                g[v] = g[u] + w
                heapq.heappush(Q, (g[v], v))
    return g

# BENCHMARK
def mesurer_temps(func):
    start = time.perf_counter()
    func()
    return time.perf_counter() - start

# ÉTUDE DE SCALABILITÉ
def main():
    tailles = [10, 20, 40, 80, 160, 320]
    temps_dijkstra = []
    temps_astar = []

    for n in tailles:
        graphe = generer_graphe(n)
        source = 0
        dest = n - 1

        t_dij = mesurer_temps(lambda: dijkstra(graphe, source))
        t_astar = mesurer_temps(lambda: astar(graphe, source, dest))

        temps_dijkstra.append(t_dij)
        temps_astar.append(t_astar)

        print(f"n={n:3d} | Dijkstra={t_dij*1e3:.3f} ms | A*={t_astar*1e3:.3f} ms")

    # COURBES
    plt.figure(figsize=(8, 5))
    plt.plot(tailles, temps_dijkstra, marker='o', label="Dijkstra")
    plt.plot(tailles, temps_astar, marker='s', label="A*")
    plt.xlabel("Nombre de nœuds")
    plt.ylabel("Temps d'exécution (s)")
    plt.title("Étude de scalabilité : Temps vs Taille du graphe")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

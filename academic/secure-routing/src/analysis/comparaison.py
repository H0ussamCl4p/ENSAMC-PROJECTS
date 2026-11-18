
import time
import tracemalloc
import matplotlib.pyplot as plt
from algorithms.dijkstra import dijkstra, reconstruire_chemin
from algorithms.astar import astar, heuristique_securisee, creer_graphe_pondere, donnees_originales, positions

# PARAMÈTRES
source = "Source"
destination = "Dest"
beta = 10
NB_RUNS = 1000  # pour lisser le temps

# OUTILS DE MESURE
def mesurer_performance(func):
    tracemalloc.start()
    start_time = time.perf_counter()

    result = func()

    exec_time = time.perf_counter() - start_time
    current, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return exec_time, peak_memory, result

# DIJKSTRA
def run_dijkstra():
    graphe = creer_graphe_pondere(donnees_originales, True, beta)
    L, P = dijkstra(graphe, source)
    chemin = reconstruire_chemin(P, source, destination)
    return chemin, L[destination], len(L)

# A*
def run_astar():
    graphe = creer_graphe_pondere(donnees_originales, True, beta)
    g, P = astar(graphe, positions, source, destination, heuristique_securisee)
    chemin = reconstruire_chemin(P, source, destination)
    return chemin, g[destination], len(g)

# EXÉCUTION MULTIPLE
def benchmark(func):
    total_time = 0
    peak_mem = 0
    for _ in range(NB_RUNS):
        t, m, _ = mesurer_performance(func)
        total_time += t
        peak_mem = max(peak_mem, m)
    return total_time / NB_RUNS, peak_mem

def main():
    time_dij, mem_dij = benchmark(run_dijkstra)
    time_astar, mem_astar = benchmark(run_astar)

    # AFFICHAGE RÉSULTATS
    print("\n=== COMPARAISON DE PERFORMANCE ===\n")
    print(f"Dijkstra : Temps = {time_dij*1e6:.2f} µs | Mémoire = {mem_dij/1024:.2f} KB")
    print(f"A*       : Temps = {time_astar*1e6:.2f} µs | Mémoire = {mem_astar/1024:.2f} KB")

    # GRAPHIQUES
    algos = ["Dijkstra", "A*"]
    times = [time_dij*1e6, time_astar*1e6]
    memories = [mem_dij/1024, mem_astar/1024]

    plt.figure()
    plt.bar(algos, times)
    plt.ylabel("Temps d'exécution moyen (µs)")
    plt.title("Comparaison du temps d'exécution")
    plt.show()

    plt.figure()
    plt.bar(algos, memories)
    plt.ylabel("Mémoire utilisée (KB)")
    plt.title("Comparaison de la consommation mémoire")
    plt.show()

if __name__ == "__main__":
    main()

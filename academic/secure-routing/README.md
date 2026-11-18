# Secure routing with graph algorithms

Mini-projet de Recherche Opérationnelle à l’ENSAM Casablanca.

Le réseau est un graphe orienté pondéré. Chaque lien a une latence et un niveau de risque, et le poids combine les deux. On cherche le chemin le plus sûr et le plus rapide, puis on compare les algorithmes.

- **Dijkstra** : plus court chemin avec des poids positifs.
- **A\*** : deux versions, l’initiale et une version corrigée avec une heuristique cohérente.
- **Comparaison** : temps d’exécution et mémoire de Dijkstra et A\*.
- **Scalabilité** : évolution des performances quand le réseau grandit.

Une interface CustomTkinter lance chaque étape. Les résultats s’affichent dans le terminal et en graphiques (voir `src/figures`).

## Lancer le projet

```bash
pip install -r requirements.txt
cd src
python main.py
```

Python 3.8 ou plus, avec customtkinter, matplotlib et networkx.

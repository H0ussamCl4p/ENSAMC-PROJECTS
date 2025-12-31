<div align="center">

# Secure Routing with Graph Algorithms

### *Mini-projet de Recherche Opérationnelle*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Algorithms-Dijkstra%20%7C%20A*-FF6B6B?style=for-the-badge&logo=algorithm&logoColor=white" alt="Algorithms"/>
  <img src="https://img.shields.io/badge/Graphs-NetworkX-4ECDC4?style=for-the-badge&logo=graphql&logoColor=white" alt="NetworkX"/>
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-9B59B6?style=for-the-badge&logo=tkinter&logoColor=white" alt="CustomTkinter"/>
  <img src="https://img.shields.io/badge/Status-Academic%20Project-success?style=for-the-badge&logo=academia&logoColor=white" alt="Status"/>
</p>

<p align="center">
  <em>Optimizing secure data routing through advanced graph algorithms and operations research</em>
</p>

<p align="center">
  <a href="#-version-française">🇫🇷 Français</a> •
  <a href="#-english-version">🇬🇧 English</a> •
  <a href="#️-how-to-run-the-project">🚀 Quick Start</a> •
  <a href="#-structure-du-projet">📂 Structure</a>
</p>

---

</div>

---

## 🇫🇷 Version Française

### 📌 Objectif du Projet
Ce mini-projet a pour objectif de modéliser et d'optimiser le routage de données sensibles au 
sein d'un réseau de communication à l'aide des méthodes de la Recherche Opérationnelle.  
Le réseau est représenté sous forme de **graphe orienté pondéré**, intégrant à la fois des 
critères de **performance (latence)** et de **sécurité (niveau de risque)**.

L'objectif principal est de comparer différentes stratégies de routage et d'analyser les 
compromis entre rapidité de transmission et protection des informations.

---

### ⚙️ Algorithmes Utilisés
- **Algorithme de Dijkstra**  
  Détermination du plus court chemin dans un graphe pondéré à poids positifs.

- **Algorithme A\***  
  Recherche heuristique du plus court chemin :
  - version initiale (avant correction)
  - version corrigée (heuristique cohérente)

- **Module de comparaison**  
  Comparaison expérimentale entre Dijkstra et A* (temps d'exécution, mémoire, résultats).

- **Analyse de scalabilité**  
  Étude de l'évolution des performances lorsque la taille du réseau augmente.

---

### 🖥️ Lancement du Projet

#### 1️⃣ Création d'un environnement virtuel (recommandé)
```bash
python -m venv venv
```

**Activation :**

- **Windows**
```bash
  venv\Scripts\activate
```

- **Linux / macOS**
```bash
  source venv/bin/activate
```

#### 2️⃣ Installation des dépendances
```bash
pip install -r requirements.txt
```

#### 3️⃣ Exécution de l'application principale
```bash
python main.py
```

Une interface graphique (CustomTkinter) permet de lancer :
- Dijkstra
- A* (initial et corrigé)
- la comparaison des algorithmes
- l'analyse de scalabilité

---

### 📁 Structure du Projet
```
RO-project/
│
├── README.md               # Documentation du projet
├── requirements.txt        # Dépendances Python
│
├── src/
│   ├── main.py # Application principale (GUI)
│   ├── algorithms/
│   │   ├── dijkstra.py
│   │   ├── astar.py
│   │   └── astar_initial.py
│   │
│   ├── analysis/
│   │   ├── comparaison.py
│   │   ├── scalabilite.py
│   │   └── calcul_poids.py
│   │
│   └── figures/
│       ├── comparaison-temps.png
│       ├── comparaison-memoire.png
│       ├── scalabilite.png
│       ├── astar.png
│       ├── astar_initial.png
│       └── dijkstra.png

```

---

### 📝 Remarques
- Tous les scripts exposent une fonction `main()` pour être appelés depuis l'interface.
- Les résultats sont affichés dans le terminal et sous forme de graphiques.
- Le projet est structuré pour une présentation académique claire et professionnelle.

---

## 🇬🇧 English Version

### 📌 Project Objective
This mini-project aims to model and optimize secure data routing in a communication network 
using Operations Research techniques.  
The network is represented as a **weighted directed graph**, integrating both 
**performance (latency)** and **security (risk level)** criteria.

The main goal is to compare routing strategies and analyze the trade-offs between 
transmission speed and data protection.

---

### ⚙️ Algorithms Used
- **Dijkstra's Algorithm**  
  Shortest path computation in weighted graphs with positive weights.

- **A\* Algorithm**  
  Heuristic-based shortest path search:
  - initial (uncorrected) version
  - corrected version with consistent heuristic

- **Comparison Module**  
  Experimental comparison between Dijkstra and A* (execution time, memory usage, results).

- **Scalability Analysis**  
  Performance evaluation as the network size increases.

---

### 🖥️ How to Run the Project

#### 1️⃣ Create a virtual environment (recommended)
```bash
python -m venv venv
```

**Activate:**

- **Windows**
```bash
  venv\Scripts\activate
```

- **Linux / macOS**
```bash
  source venv/bin/activate
```

#### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

#### 3️⃣ Run the main application
```bash
python main.py
```

A graphical interface (CustomTkinter) allows running:
- Dijkstra
- A* (initial and corrected)
- algorithm comparison
- scalability analysis

---

### 📝 Notes
- All algorithm scripts expose a `main()` function.
- The GUI centralizes execution and visualization.
- The project is structured for clarity, maintainability, and academic use.

---

## Final Note
This project illustrates how graph algorithms and Operations Research methods can be applied to real-world problems involving security, performance, and decision-making in networked systems.


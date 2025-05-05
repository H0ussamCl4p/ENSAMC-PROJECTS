# SIRD App - Tableau de Bord d’Analyse Numérique

Bienvenue dans l’application **SIRD App**, un outil interactif développé par CHOUBIK Houssaù dans le cadre du mini-projet d’Analyse Numérique 2024-2025 à l’ENSAM Casablanca.

## Présentation

Cette application permet d’explorer, de modéliser et d’analyser la propagation du virus Covid-19 en Indonésie à travers le modèle SIRD (Susceptibles, Infectés, Rétablis, Décédés). 

Elle propose des outils d’analyse numérique tels que l’interpolation, la résolution d’équations non linéaires, la dérivation numérique, l’intégration et la résolution d’équations différentielles.

## Fonctionnalités

- **Interpolation** : Lagrange, Newton, Neville, Splines cubiques, Comparaison des méthodes.
- **Équations non linéaires** : Pic épidémique, seuil d’immunité, temps critique d’intervention.
- **Dérivation numérique** : Taux de transmission, croissance initiale, moment de décroissance, vitesse de propagation, taux de variation.
- **Intégration numérique** : Méthodes de Simpson et des trapèzes, calculs de durée, impact des mesures sanitaires.
- **Équations différentielles** : Résolution des EDO du modèle SIRD.
- **Visualisation interactive** : Graphiques, résultats détaillés, navigation intuitive.

## Installation

1. **Cloner le dépôt ou télécharger les fichiers.**
2. **Installer les dépendances** (Python ≥ 3.8 recommandé) :
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancer l’application** :
   ```bash
   python SIRD-main.py
   ```

## Structure du projet

- `SIRD-main.py` : Lancement de l’interface principale.
- `Interpolation/` : Scripts d’interpolation.
- `Equations-non-lineaires/` : Scripts pour les équations non linéaires.
- `Derivation/` : Scripts de dérivation numérique.
- `Integration/` : Scripts d’intégration numérique.
- `EDO/` : Résolution des équations différentielles.
- `BaseDedonnées/BD-Indonesie.xlsx` : Base de données utilisée.

## Membres du groupe

- **CHOUBIK Houssam** (Chef de projet)
- KAZOURY Chaimae (Vice chef de projet)
- MOUZAKKI Othmane
- ELHAMOUDI Wiam
- EL MAAROUFI Soukaina
- EL MAATAOUI Ihssane
- LABBAD Mariam

## Encadrant

**Pr. Abdessamad KAMOUSS**  
Département d’informatique  
École Nationale Supérieure d’Arts et Métiers de Casablanca  
Université Hassan II Casablanca

## Remerciements

Tout nos remerciements à notre Professeur pour son encadrement et ses précieux conseils tout au long de ce projet.

---

© 2025 CHOUBIK Houssam. Tous droits réservés.
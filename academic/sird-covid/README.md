# SIRD App

Mini-projet d’Analyse Numérique 2024-2025 à l’ENSAM Casablanca.

## Présentation

Application qui modélise la propagation du virus Covid-19 en Indonésie à travers le modèle SIRD (Susceptibles, Infectés, Rétablis, Décédés). 

Elle applique l’interpolation, la résolution d’équations non linéaires, la dérivation numérique, l’intégration et la résolution d’équations différentielles.

## Fonctionnalités

- **Interpolation** : Lagrange, Newton, Neville, Splines cubiques, Comparaison des méthodes.
- **Équations non linéaires** : Pic épidémique, seuil d’immunité, temps critique d’intervention.
- **Dérivation numérique** : Taux de transmission, croissance initiale, moment de décroissance, vitesse de propagation, taux de variation.
- **Intégration numérique** : Méthodes de Simpson et des trapèzes, calculs de durée, impact des mesures sanitaires.
- **Équations différentielles** : Résolution des EDO du modèle SIRD.
- **Visualisation** : graphiques et résultats pour chaque méthode.

## Installation

1. Installer les dépendances (Python 3.8 ou plus) :
   ```bash
   pip install -r requirements.txt
   ```
2. Lancer l’application :
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
- `data/BD-Indonesie.xlsx` : données Covid-19 de l’Indonésie.

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

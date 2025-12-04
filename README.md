# Simulateur de Circulation avec Intelligence Artificielle

## Description du Projet

Ce projet est un simulateur de circulation urbaine qui utilise l'intelligence artificielle via **Reinforcement Learning** pour optimiser la gestion des feux de circulation. L'objectif principal est de réduire les temps d'attente des véhicules aux intersections en apprenant des stratégies optimales de changement de phase des feux.

## Fonctionnement Général

Le simulateur modélise une ville avec :
- **Des routes** organisées en grille
- **Des intersections** contrôlées par des feux de circulation
- **Des véhicules** qui se déplacent selon des règles réalistes
- **Un système de feux** qui peut être contrôlé manuellement ou par IA

## Architecture du Projet

### Dossier `traffic_sim/`
Contient le cœur de la simulation :

- **`simulation.py`** : Classe principale qui gère l'état global de la simulation, le spawn des voitures, et les statistiques
- **`car.py`** : Modèle des véhicules avec logique de mouvement, gestion des files d'attente et effet accordéon
- **`traffic_light.py`** : Gestion des feux de circulation avec états (rouge/vert) et modes manuel/automatique
- **`map.py`** : Définition de la carte urbaine avec routes, intersections et bâtiments
- **`renderer.py`** : Affichage graphique de la simulation
- **`constants.py`** : Paramètres configurables (vitesse de spawn, délais, dimensions, etc.)

### Dossier `ai_controller/`
Contient l'intelligence artificielle :

- **`q_agent.py`** : Agent Q-learning qui apprend à optimiser les feux de circulation
- **`traffic_env.py`** : Environnement de reinforcement learning pour l'IA
- **`train.py`** : Script d'entraînement de l'agent IA
- **`run_ai.py`** : Exécution de la simulation avec l'IA en contrôle

### Fichiers Racine

- **`main.py`** : Point d'entrée principal pour lancer la simulation avec interface graphique
- **`test_headless.py`** : Version de test sans affichage pour les benchmarks

## Fonctionnalités Principales

### Simulation Réaliste
- **Spawn dynamique** : Les voitures apparaissent aléatoirement aux points de spawn
- **Gestion des intersections** : Logique de priorité et prévention des collisions
- **Effet accordéon** : Délai de redémarrage réaliste pour les voitures à l'arrêt
- **Statistiques** : Suivi des temps d'attente, longueurs de files, débit de circulation

### Intelligence Artificielle
- **Q-Learning** : Algorithme d'apprentissage par renforcement
- **États** : Représentation de l'état des intersections (files d'attente par direction)
- **Actions** : Changement de phase des feux (vertical/horizontal)
- **Récompenses** : Basées sur la réduction des temps d'attente

### Visualisation
- **Interface graphique** : Affichage en temps réel de la simulation
- **Mode headless** : Exécution sans affichage pour l'entraînement et les tests

## Installation et Utilisation

### Prérequis
- Python 3.8+
- Bibliothèques : numpy, pygame (pour l'affichage)

### Installation
```bash
# Cloner le repository
git clone https://github.com/SkayKer/projet-ia-circulation.git
cd projet-ia-circulation

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances
pip install numpy pygame
```

### Utilisation

#### Simulation avec interface graphique
```bash
python main.py
```

#### Entraînement de l'IA
```bash
python ai_controller/train.py
```

#### Test de l'IA entraînée
```bash
python ai_controller/run_ai.py
```

#### Tests sans affichage
```bash
python test_headless.py
```

## Configuration

Les paramètres principaux peuvent être modifiés dans `traffic_sim/constants.py` :

- `SPAWN_RATE` : Fréquence d'apparition des voitures
- `CARS_PER_SPAWN` : Nombre de voitures par spawn
- `RESTART_DELAY` : Délai de redémarrage (effet accordéon)
- `MAX_CARS` : Nombre maximum de voitures simultanées
- `FPS` : Vitesse de simulation

## Métriques et Statistiques

La simulation suit plusieurs indicateurs de performance :

- **Temps d'attente moyen** : Par véhicule et global
- **Longueur des files** : Maximum et moyenne par intersection
- **Débit** : Nombre de véhicules traversant par minute
- **Temps d'attente sur 10 secondes** : Moyenne glissante

## Algorithme d'Apprentissage

L'agent IA utilise Q-Learning avec :

- **État** : Vecteur des longueurs de files pour chaque direction des intersections
- **Actions** : Changement de phase des feux (2 phases possibles)
- **Récompense** : Négative proportionnelle aux temps d'attente cumulés
- **Exploration** : ε-greedy avec décroissance exponentielle

## Améliorations Futures

- Support multi-intersections
- Algorithmes d'IA plus avancés (Deep Q-Learning)
- Interface utilisateur pour configuration
- Statistiques détaillées et graphiques
- Modes de simulation variés (heure de pointe, accident, etc.)

## Contributeurs

- Evan Bodineau
- Antonin Urbain

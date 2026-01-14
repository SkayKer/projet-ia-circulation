# Simulateur de Circulation avec Intelligence Artificielle

## Description du Projet

Ce projet est un simulateur de circulation urbaine qui utilise l'intelligence artificielle via **Reinforcement Learning** pour optimiser la gestion des feux de circulation. L'objectif principal est de réduire les temps d'attente des véhicules aux intersections en apprenant des stratégies optimales de changement de phase des feux.

## Fonctionnement Général

Le simulateur modélise une ville avec :

- **Des routes** organisées en grille
- **Des intersections** contrôlées par des feux de circulation
- **Des véhicules** qui se déplacent selon des règles réalistes
- **Un système de feux** qui peut être contrôlé manuellement ou par IA

## 🚀 Installation et Utilisation

### Prérequis

- Python 3.8+
- Bibliothèques : numpy, pygame

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

---

## 🎮 Les 3 Méthodes de Contrôle des Feux

### 1. 🔄 Fixed Switch (Feux Temporisés)

Les feux changent automatiquement selon un timer fixe. C'est la méthode de référence sans IA.

```bash
python main.py
```

> Utilisez le slider dans l'interface pour ajuster le taux de spawn des voitures.

---

### 2. 🤖 Q-Learning

Agent IA qui apprend à optimiser les feux sans contexte de trafic global.

**Entraînement :**

```bash
python ai_controller/train.py --episodes 1000
```

> Crée le fichier `q_agent.pkl` avec le modèle entraîné.

**Exécution :**

```bash
python ai_controller/run_ai.py
```

---

### 3. 🧠 Contextual Q-Learning

Agent IA avancé qui prend en compte le niveau de trafic (faible/moyen/élevé) dans son état.

**Entraînement :**

```bash
python ai_controller/contextual_train.py --episodes 500
```

> Crée le fichier `q_agent_contextual.pkl` avec le modèle contextuel.

**Exécution :**

```bash
python ai_controller/run_ai.py --contextual
```

**Avec un spawn rate personnalisé :**

```bash
python ai_controller/run_ai.py --contextual --spawn-rate 3
```

---

## 📊 Benchmark des Méthodes

Le script `benchmark.py` compare les 3 méthodes avec analyse statistique.

### Benchmark Rapide (5 simulations par méthode)

```bash
python benchmark.py --test
```

### Benchmark Complet (50 simulations par méthode)

```bash
python benchmark.py
```

### Options Avancées

```bash
# Nombre personnalisé de simulations
python benchmark.py --runs 100

# Durée personnalisée (en ticks, 1 tick = 0.1s)
python benchmark.py --duration 3000

# Export CSV
python benchmark.py --csv resultats.csv

# Mode silencieux
python benchmark.py --quiet --csv resultats.csv
```

### Scénarios Testés

| Scénario     | Spawn Rate | Description                    |
| ------------ | ---------- | ------------------------------ |
| High Traffic | 1          | 2 voitures/tick (trafic dense) |
| Medium-High  | 2          | Trafic soutenu                 |
| Medium       | 5          | Trafic modéré                  |
| Low Traffic  | 10         | Trafic léger                   |
| Fluctuating  | Variable   | Simule les heures de pointe    |

### Métriques Collectées

- **Temps d'attente moyen** (moyenne ± écart-type)
- **Temps d'attente maximum**
- **Longueur moyenne des files**
- **Longueur maximum des files**

---

## 📁 Architecture du Projet

### Dossier `traffic_sim/`

- **`simulation.py`** : Classe principale de simulation
- **`car.py`** : Modèle des véhicules
- **`traffic_light.py`** : Gestion des feux de circulation
- **`map.py`** : Définition de la carte urbaine
- **`renderer.py`** : Affichage graphique
- **`constants.py`** : Paramètres configurables

### Dossier `ai_controller/`

- **`q_agent.py`** : Agent Q-learning
- **`traffic_env.py`** : Environnement RL
- **`train.py`** : Entraînement Q-Learning
- **`contextual_train.py`** : Entraînement Contextual Q-Learning
- **`run_ai.py`** : Exécution avec IA

### Fichiers Racine

- **`main.py`** : Simulation avec feux temporisés
- **`benchmark.py`** : Comparaison des 3 méthodes
- **`q_agent.pkl`** : Modèle Q-Learning entraîné
- **`q_agent_contextual.pkl`** : Modèle Contextual Q-Learning entraîné

---

## ⚙️ Configuration

Paramètres dans `traffic_sim/constants.py` :

| Paramètre        | Valeur par défaut | Description                            |
| ---------------- | ----------------- | -------------------------------------- |
| `SPAWN_RATE`     | 2                 | Voitures spawn tous les N ticks        |
| `CARS_PER_SPAWN` | 2                 | Nombre de voitures par spawn           |
| `MAX_CARS`       | 100               | Maximum de voitures simultanées        |
| `FPS`            | 10                | Vitesse de simulation                  |
| `RESTART_DELAY`  | 2                 | Délai de redémarrage (effet accordéon) |

---

## 📈 Algorithme d'Apprentissage

L'agent IA utilise Q-Learning avec :

- **État** : Vecteur des files d'attente discrétisées + phase actuelle (+niveau de trafic pour contextuel)
- **Actions** : 2 phases (vertical vert / horizontal vert)
- **Récompense** : -1 × (temps d'attente + longueur files)
- **Exploration** : ε-greedy avec décroissance

---

## 🔮 Améliorations Futures

- **Deep Q-Networks (DQN)** : Utilisation de réseaux de neurones pour une meilleure généralisation
- Interface utilisateur pour configuration
- Statistiques détaillées et graphiques
- Modes de simulation variés (accident, travaux, etc.)

---

## 👥 Contributeurs

- Evan Bodineau
- Antonin Urbain

# Constants for the Traffic Simulator

# Grid Dimensions
GRID_SIZE = 20
CELL_SIZE = 30  # Pixels per cell for visualization
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE

# Cell Types
EMPTY = 0
ROAD = 1
INTERSECTION = 2
BUILDING = 3
GRASS = 4

# Directions (dx, dy)
NORTH = (0, -1)
SOUTH = (0, 1)
EAST = (1, 0)
WEST = (-1, 0)

DIRECTIONS = [NORTH, SOUTH, EAST, WEST]

# Traffic Light States
RED = 0
GREEN = 1
YELLOW = 2  # Optional, can be added later

# Simulation Settings
FPS = 10  # Frames per second (simulation speed)
SPAWN_RATE = 20  # Spawn a car every N ticks (approx)
MAX_CARS = 20

import random
from .constants import GRID_SIZE, ROAD, INTERSECTION, GRASS, BUILDING, NORTH, SOUTH, EAST, WEST

class Map:
    def __init__(self):
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.grid = [[GRASS for _ in range(self.width)] for _ in range(self.height)]
        self.intersections = []
        self.spawn_points = []
        self._generate_map()

    def _generate_map(self):
        """
        Generates a fixed map with 2-lane roads and intersections.
        Right-Hand Traffic (RHT).
        
        Vertical Roads:
        - Road 1: x=10 (Southbound), x=11 (Northbound)
        - Road 2: x=5 (Southbound), x=6 (Northbound)
        
        Horizontal Road:
        - y=10 (Westbound), y=11 (Eastbound)
        
        Intersections (2x2):
        - (5, 10), (6, 10), (5, 11), (6, 11)
        - (10, 10), (11, 10), (10, 11), (11, 11)
        """
        # Fill background with some buildings randomly
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.1:
                    self.grid[y][x] = BUILDING

        # Define roads
        # Horizontal road (y=10 Westbound, y=11 Eastbound)
        for x in range(self.width):
            self.grid[10][x] = ROAD
            self.grid[11][x] = ROAD
        
        # Vertical road 1 (x=10 Southbound, x=11 Northbound)
        for y in range(self.height):
            self.grid[y][10] = ROAD
            self.grid[y][11] = ROAD

        # Vertical road 2 (x=5 Southbound, x=6 Northbound)
        for y in range(self.height):
            self.grid[y][5] = ROAD
            self.grid[y][6] = ROAD

        # Define Intersections (2x2 areas)
        # Intersection 1
        for y in [10, 11]:
            for x in [5, 6]:
                self.grid[y][x] = INTERSECTION
                self.intersections.append((x, y))
        
        # Intersection 2
        for y in [10, 11]:
            for x in [10, 11]:
                self.grid[y][x] = INTERSECTION
                self.intersections.append((x, y))

        # Define Spawn Points (start of roads)
        # (x, y, direction)
        self.spawn_points = [
            (0, 11, EAST),     # Horizontal Eastbound start
            (self.width-1, 10, WEST), # Horizontal Westbound start
            (10, 0, SOUTH),    # Vertical 1 Southbound start
            (11, self.height-1, NORTH), # Vertical 1 Northbound start
            (5, 0, SOUTH),     # Vertical 2 Southbound start
            (6, self.height-1, NORTH)   # Vertical 2 Northbound start
        ]

    def get_cell(self, x, y):
        """Returns the type of the cell at (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def is_road(self, x, y):
        cell = self.get_cell(x, y)
        return cell == ROAD or cell == INTERSECTION

    def is_intersection(self, x, y):
        return self.get_cell(x, y) == INTERSECTION

    def get_allowed_directions(self, x, y):
        """
        Returns a list of allowed directions for a given cell.
        Based on RHT logic.
        """
        # Horizontal Road
        if y == 11: return [EAST]
        if y == 10: return [WEST]
        
        # Vertical Roads
        if x == 10 or x == 5: return [SOUTH]
        if x == 11 or x == 6: return [NORTH]

        # Intersections: Allow straight through (simplified)
        # Ideally, we allow turning, but for now, keep direction.
        # This method is mainly used to correct cars if they get lost, 
        # but cars usually keep their direction.
        return []

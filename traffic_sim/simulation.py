import random
from .map import Map
from .car import Car
from .traffic_light import TrafficLight
from .constants import SPAWN_RATE, MAX_CARS, RED, GREEN

class Simulation:
    def __init__(self):
        self.map = Map()
        self.cars = []
        self.traffic_lights = []
        self.tick_count = 0
        self._init_traffic_lights()

    def _init_traffic_lights(self):
        """Initialize traffic lights at intersections."""
        # We need lights at the ENTRY points of intersections.
        # Intersection 1: x=[5,6], y=[10,11]
        # Entries:
        # - Southbound (x=5) at y=9 (Stop line)
        # - Northbound (x=6) at y=12 (Stop line)
        # - Eastbound (y=11) at x=4 (Stop line)
        # - Westbound (y=10) at x=7 (Stop line)
        
        # Intersection 2: x=[10,11], y=[10,11]
        # Entries:
        # - Southbound (x=10) at y=9
        # - Northbound (x=11) at y=12
        # - Eastbound (y=11) at x=9
        # - Westbound (y=10) at x=12

        # Let's create a helper to add a group of lights for an intersection
        self._add_intersection_lights(5, 6, 10, 11)
        self._add_intersection_lights(10, 11, 10, 11)

    def _add_intersection_lights(self, x_min, x_max, y_min, y_max):
        # Vertical Lights (Control N/S flow)
        # Southbound entry: (x_min, y_min - 1)
        self.traffic_lights.append(TrafficLight(x_min, y_min - 1, axis='VERTICAL', initial_state=GREEN))
        # Northbound entry: (x_max, y_max + 1)
        self.traffic_lights.append(TrafficLight(x_max, y_max + 1, axis='VERTICAL', initial_state=GREEN))

        # Horizontal Lights (Control E/W flow)
        # Eastbound entry: (x_min - 1, y_max)
        self.traffic_lights.append(TrafficLight(x_min - 1, y_max, axis='HORIZONTAL', initial_state=RED))
        # Westbound entry: (x_max + 1, y_min)
        self.traffic_lights.append(TrafficLight(x_max + 1, y_min, axis='HORIZONTAL', initial_state=RED))

    def spawn_car(self):
        """Attempts to spawn a new car at a random spawn point."""
        if len(self.cars) >= MAX_CARS:
            return

        spawn_point = random.choice(self.map.spawn_points)
        x, y, direction = spawn_point

        # Check if spawn point is occupied
        occupied = False
        for car in self.cars:
            if car.x == x and car.y == y:
                occupied = True
                break
        
        if not occupied:
            self.cars.append(Car(x, y, direction))

    def step(self):
        """Advances the simulation by one tick."""
        self.tick_count += 1

        # 1. Update Traffic Lights
        # We need to synchronize them. 
        # For this simple version, each light updates itself.
        # BUT we initialized them with opposite states (V=GREEN, H=RED).
        # As long as they have the same cycle time, they will swap in sync.
        for tl in self.traffic_lights:
            tl.update()

        # 2. Spawn Cars
        if self.tick_count % SPAWN_RATE == 0:
            self.spawn_car()

        # 3. Move Cars
        # We iterate backwards or create a copy to safely remove cars if needed
        # But for movement, we should be careful about order. 
        # Ideally, cars at the front move first.
        # For simplicity, we just iterate. Collision logic handles "waiting".
        
        cars_to_remove = []
        for car in self.cars:
            # Pass other cars to check collisions
            moved = car.move(self.map, self.traffic_lights, self.cars)
            
            # Check if car has left the map (simple check: if it didn't move and wasn't blocked, maybe it's at edge?)
            # Actually, move() returns False if blocked OR if end of road.
            # Let's check bounds explicitly to remove cars.
            if not (0 <= car.x < self.map.width and 0 <= car.y < self.map.height):
                cars_to_remove.append(car)

        for car in cars_to_remove:
            self.cars.remove(car)

    def get_state(self):
        """Returns the current state of the simulation (for RL or visualization)."""
        return {
            "tick": self.tick_count,
            "cars": [car.get_state() for car in self.cars],
            "lights": [(tl.x, tl.y, tl.state) for tl in self.traffic_lights],
            "map": self.map # Reference to map (static)
        }

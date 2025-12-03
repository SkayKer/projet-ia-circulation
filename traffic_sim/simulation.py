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
        # But now placed to the RIGHT of the road.
        
        # Intersection 1: x=[5,6], y=[10,11]
        self._add_intersection_lights(5, 6, 10, 11)
        
        # Intersection 2: x=[10,11], y=[10,11]
        self._add_intersection_lights(10, 11, 10, 11)

    def _add_intersection_lights(self, x_min, x_max, y_min, y_max):
        # Vertical Lights (Control N/S flow)
        # Southbound entry: Road is x=x_min, Stop line y=y_min-1. Light to right -> (x_min-1, y_min-1)
        self.traffic_lights.append(TrafficLight(x_min - 1, y_min - 1, axis='VERTICAL', initial_state=GREEN))
        
        # Northbound entry: Road is x=x_max, Stop line y=y_max+1. Light to right -> (x_max+1, y_max+1)
        self.traffic_lights.append(TrafficLight(x_max + 1, y_max + 1, axis='VERTICAL', initial_state=GREEN))

        # Horizontal Lights (Control E/W flow)
        # Eastbound entry: Road is y=y_max, Stop line x=x_min-1. Light to right -> (x_min-1, y_max+1)
        self.traffic_lights.append(TrafficLight(x_min - 1, y_max + 1, axis='HORIZONTAL', initial_state=RED))
        
        # Westbound entry: Road is y=y_min, Stop line x=x_max+1. Light to right -> (x_max+1, y_min-1)
        self.traffic_lights.append(TrafficLight(x_max + 1, y_min - 1, axis='HORIZONTAL', initial_state=RED))

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
        for tl in self.traffic_lights:
            tl.update()

        # 2. Spawn Cars
        if self.tick_count % SPAWN_RATE == 0:
            self.spawn_car()

        # 3. Move Cars
        cars_to_remove = []
        for car in self.cars:
            # Pass other cars to check collisions
            moved = car.move(self.map, self.traffic_lights, self.cars)
            
            # Check if car has left the map
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

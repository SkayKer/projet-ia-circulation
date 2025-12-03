import random
from collections import deque
from .map import Map
from .car import Car
from .traffic_light import TrafficLight
from .constants import SPAWN_RATE, MAX_CARS, RED, GREEN, FPS

class Simulation:
    def __init__(self):
        self.map = Map()
        self.cars = []
        self.traffic_lights = []
        self.tick_count = 0
        self.total_wait_time_all_cars = 0  # Cumulative wait time of all cars (including removed)
        self.total_cars_spawned = 0  # Total number of cars spawned
        self.spawn_rate = SPAWN_RATE  # Configurable spawn rate
        # History of wait times for last 10 seconds (10 * FPS ticks)
        self.wait_time_history = deque(maxlen=10 * FPS)
        # History of queue lengths for average calculation
        self.queue_length_history = deque(maxlen=10 * FPS)
        self.max_queue_length = 0  # Maximum queue length observed
        self._init_traffic_lights()

    def _init_traffic_lights(self):
        """Initialize traffic lights at intersections."""
        # We need lights at the ENTRY points of intersections.
        # But now placed to the RIGHT of the road.
        
        # Intersection 1: x=[5,6], y=[10,11]
        self._add_intersection_lights(5, 6, 10, 11)
        
        # Intersection 2: x=[20,21], y=[10,11]
        self._add_intersection_lights(20, 21, 10, 11)

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
            self.total_cars_spawned += 1

    def step(self):
        """Advances the simulation by one tick."""
        self.tick_count += 1

        # 1. Update Traffic Lights
        for tl in self.traffic_lights:
            tl.update()

        # 2. Spawn Cars
        if self.tick_count % self.spawn_rate == 0:
            self.spawn_car()

        # 3. Move Cars
        cars_to_remove = []
        for car in self.cars:
            # Pass other cars to check collisions
            moved = car.move(self.map, self.traffic_lights, self.cars)
            
            # Update wait time tracking
            car.increment_wait_time()
            
            # Check if car has left the map
            if not (0 <= car.x < self.map.width and 0 <= car.y < self.map.height):
                cars_to_remove.append(car)

        for car in cars_to_remove:
            # Add the car's wait time to the global total before removing
            self.total_wait_time_all_cars += car.total_wait_time
            self.cars.remove(car)
        
        # Record average wait time for waiting cars only (for 10-second rolling average)
        waiting_cars = [car for car in self.cars if car.waiting]
        if len(waiting_cars) > 0:
            avg_wait_this_tick = sum(car.current_wait_time for car in waiting_cars) / len(waiting_cars)
        else:
            avg_wait_this_tick = 0.0
        self.wait_time_history.append(avg_wait_this_tick)
        
        # Calculate queue lengths and update stats
        queue_lengths = self._calculate_queue_lengths()
        if queue_lengths:
            current_max = max(queue_lengths)
            self.max_queue_length = max(self.max_queue_length, current_max)
            self.queue_length_history.append(sum(queue_lengths) / len(queue_lengths))
        else:
            self.queue_length_history.append(0)

    def _calculate_queue_lengths(self):
        """Calculate the length of each queue (consecutive waiting cars)."""
        if not self.cars:
            return []
        
        # Group waiting cars by their position and direction to find queues
        queues = []
        visited = set()
        
        for car in self.cars:
            if not car.waiting or car.id in visited:
                continue
            
            # Start a new queue from this car
            queue_length = 1
            visited.add(car.id)
            
            # Look for cars behind this one (opposite of their direction)
            dx, dy = -car.direction[0], -car.direction[1]
            check_x, check_y = car.x + dx, car.y + dy
            
            # Count consecutive waiting cars behind
            while True:
                found = False
                for other_car in self.cars:
                    if (other_car.id not in visited and 
                        other_car.waiting and
                        other_car.x == check_x and 
                        other_car.y == check_y and
                        other_car.direction == car.direction):
                        queue_length += 1
                        visited.add(other_car.id)
                        check_x += dx
                        check_y += dy
                        found = True
                        break
                if not found:
                    break
            
            if queue_length > 0:
                queues.append(queue_length)
        
        return queues
    
    def get_max_queue_length(self):
        """Returns the maximum queue length observed."""
        return self.max_queue_length
    
    def get_average_queue_length(self):
        """Returns the average queue length over the last 10 seconds."""
        if len(self.queue_length_history) == 0:
            return 0.0
        return sum(self.queue_length_history) / len(self.queue_length_history)
    
    def get_current_queue_lengths(self):
        """Returns the current queue lengths."""
        return self._calculate_queue_lengths()

    def get_total_wait_time(self):
        """Returns the total wait time of all cars (current + removed) in ticks."""
        current_cars_wait = sum(car.total_wait_time for car in self.cars)
        return self.total_wait_time_all_cars + current_cars_wait
    
    def get_total_wait_time_seconds(self):
        """Returns the total wait time in seconds."""
        return self.get_total_wait_time() / FPS
    
    def get_average_wait_time(self):
        """Returns the average wait time per car in ticks."""
        if self.total_cars_spawned == 0:
            return 0.0
        return self.get_total_wait_time() / self.total_cars_spawned
    
    def get_average_wait_time_seconds(self):
        """Returns the average wait time per car in seconds."""
        return self.get_average_wait_time() / FPS
    
    def get_average_wait_time_last_10s(self):
        """Returns the average wait time per car over the last 10 seconds in seconds."""
        if len(self.wait_time_history) == 0:
            return 0.0
        # Average of average wait times over the window, converted to seconds
        avg_wait_ticks = sum(self.wait_time_history) / len(self.wait_time_history)
        return avg_wait_ticks / FPS
    
    def get_current_cars_waiting(self):
        """Returns the number of cars currently waiting."""
        return sum(1 for car in self.cars if car.waiting)

    def get_state(self):
        """Returns the current state of the simulation (for RL or visualization)."""
        return {
            "tick": self.tick_count,
            "cars": [car.get_state() for car in self.cars],
            "lights": [(tl.x, tl.y, tl.state) for tl in self.traffic_lights],
            "map": self.map,
            "total_wait_time": self.get_total_wait_time(),
            "total_wait_time_seconds": self.get_total_wait_time_seconds(),
            "average_wait_time": self.get_average_wait_time(),
            "average_wait_time_seconds": self.get_average_wait_time_seconds(),
            "average_wait_time_last_10s": self.get_average_wait_time_last_10s(),
            "cars_waiting": self.get_current_cars_waiting(),
            "total_cars_spawned": self.total_cars_spawned
        }

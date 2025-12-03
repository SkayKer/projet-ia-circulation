import uuid
from .constants import NORTH, SOUTH, EAST, WEST

class Car:
    def __init__(self, x, y, direction):
        self.id = str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 1  # Cells per tick
        self.waiting = False

    def move(self, game_map, traffic_lights, other_cars):
        """
        Attempts to move the car one step in its current direction.
        Checks for:
        1. Map boundaries and road validity.
        2. Traffic lights at intersections.
        3. Collision with other cars.
        """
        dx, dy = self.direction
        next_x = self.x + dx
        next_y = self.y + dy

        # 1. Check Map Boundaries and Road Validity
        # Check if we are leaving the map
        if not (0 <= next_x < game_map.width and 0 <= next_y < game_map.height):
            # Allow moving off-map so simulation can remove the car
            self.x = next_x
            self.y = next_y
            return True

        if not game_map.is_road(next_x, next_y):
            # End of road (but inside map), remove car or stop?
            # For now, stop.
            return False  # Cannot move

        # 2. Check Traffic Lights
        # Check if the NEXT cell is a traffic light location
        # In our new logic, lights are placed at the cell BEFORE the intersection.
        # So if we are AT a light's location, we check it before moving into the intersection.
        
        # Wait, if the light is at (x, y) (current pos), we check it before moving to next.
        # OR if the light is at next_x, next_y.
        # Our placement: Light is at the "Stop line".
        # If I am at the stop line, I check the light.
        
        light = None
        for tl in traffic_lights:
            if tl.x == self.x and tl.y == self.y: # Light is at my current position
                light = tl
                break
        
        # If there is a light where I am, and I want to move forward (into intersection), check it.
        # Actually, usually you stop BEFORE the line.
        # Let's say the light is at `next_x, next_y`.
        # If `next_x, next_y` is the light position, I can't enter it if red?
        # No, the light object is just a logical marker.
        # Let's stick to: If `next_x, next_y` is an INTERSECTION, check if there is a light controlling my entry.
        
        # Simpler approach matching `_init_traffic_lights`:
        # Lights are placed at specific coordinates (the cell BEFORE the intersection).
        # If I am AT that coordinate, I must check the light before moving.
        
        if light and light.is_red():
             # I am at a light, and it is red. I cannot move.
             self.waiting = True
             return False

        # 3. Check Collision with Other Cars

        # 3. Check Collision with Other Cars
        for car in other_cars:
            if car.id != self.id and car.x == next_x and car.y == next_y:
                self.waiting = True
                return False # Stop behind car

        # If all clear, move
        self.x = next_x
        self.y = next_y
        self.waiting = False
        
        # Update direction if needed (simple logic for now: keep going or turn at intersection if forced)
        # For this simple version, cars just go straight unless the map forces a turn (not implemented yet)
        # But we should check if the new cell allows the current direction, if not, pick a valid one.
        allowed_dirs = game_map.get_allowed_directions(self.x, self.y)
        if self.direction not in allowed_dirs and allowed_dirs:
             self.direction = allowed_dirs[0] # Force turn if necessary

        return True

    def get_state(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "waiting": self.waiting
        }

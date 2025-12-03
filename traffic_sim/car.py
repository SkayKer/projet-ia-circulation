import uuid
import random
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
        """
        dx, dy = self.direction
        next_x = self.x + dx
        next_y = self.y + dy

        # 1. Check Map Boundaries and Road Validity
        if not (0 <= next_x < game_map.width and 0 <= next_y < game_map.height):
            # Allow moving off-map so simulation can remove the car
            self.x = next_x
            self.y = next_y
            return True

        if not game_map.is_road(next_x, next_y):
            return False  # Cannot move

        # 2. Check Traffic Lights
        # We need to check if there is a light controlling the entry to the NEXT cell (intersection).
        # Logic: If I am at the stop line (cell before intersection), check the light to my RIGHT.
        
        # Determine where "Right" is based on direction
        check_x, check_y = -1, -1
        if self.direction == SOUTH:
            # I am at (x, y). Light should be at (x-1, y)
            check_x, check_y = self.x - 1, self.y
        elif self.direction == NORTH:
            # Light at (x+1, y)
            check_x, check_y = self.x + 1, self.y
        elif self.direction == EAST:
            # Light at (x, y+1)
            check_x, check_y = self.x, self.y + 1
        elif self.direction == WEST:
            # Light at (x, y-1)
            check_x, check_y = self.x, self.y - 1
            
        # Check if there is a light at (check_x, check_y)
        # AND if the next cell is actually an intersection (to avoid checking lights when just driving)
        if game_map.is_intersection(next_x, next_y):
            light = None
            for tl in traffic_lights:
                if tl.x == check_x and tl.y == check_y:
                    light = tl
                    break
            
            if light and light.is_red():
                self.waiting = True
                return False # Stop at red light

        # 3. Check Collision with Other Cars
        for car in other_cars:
            if car.id != self.id and car.x == next_x and car.y == next_y:
                self.waiting = True
                return False # Stop behind car

        # If all clear, move
        self.x = next_x
        self.y = next_y
        self.waiting = False
        
        # Update direction with probabilistic logic
        allowed_dirs = game_map.get_allowed_directions(self.x, self.y)
        
        if allowed_dirs:
            # Filter to ensure we don't do immediate 180 unless necessary (not an issue with current map flow)
            valid_dirs = allowed_dirs
            
            if len(valid_dirs) > 1:
                # Identify turn types
                options = {}
                for d in valid_dirs:
                    if d == self.direction:
                        options["STRAIGHT"] = d
                    else:
                        # Determine Left vs Right
                        is_right = False
                        if self.direction == NORTH and d == EAST: is_right = True
                        elif self.direction == EAST and d == SOUTH: is_right = True
                        elif self.direction == SOUTH and d == WEST: is_right = True
                        elif self.direction == WEST and d == NORTH: is_right = True
                        
                        if is_right:
                            options["RIGHT"] = d
                        else:
                            options["LEFT"] = d
                
                # Apply Probabilities
                # 1. Entry Case (Straight + Right): 1/3 Right, 2/3 Straight
                if "STRAIGHT" in options and "RIGHT" in options and "LEFT" not in options:
                    if random.random() < 0.333:
                        self.direction = options["RIGHT"]
                    else:
                        self.direction = options["STRAIGHT"]
                
                # 2. Exit Case (Straight + Left): 1/2 Left, 1/2 Straight (conditional probability)
                elif "STRAIGHT" in options and "LEFT" in options and "RIGHT" not in options:
                    if random.random() < 0.5:
                        self.direction = options["LEFT"]
                    else:
                        self.direction = options["STRAIGHT"]
                        
                # 3. All 3 available (Generic intersection): 1/3 each
                elif "STRAIGHT" in options and "LEFT" in options and "RIGHT" in options:
                    r = random.random()
                    if r < 0.333: self.direction = options["RIGHT"]
                    elif r < 0.666: self.direction = options["LEFT"]
                    else: self.direction = options["STRAIGHT"]
                    
                # 4. Forced Turn (no straight)
                elif "STRAIGHT" not in options:
                    self.direction = random.choice(list(options.values()))
                    
            elif len(valid_dirs) == 1:
                self.direction = valid_dirs[0]

        return True

    def get_state(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "waiting": self.waiting
        }

import uuid
import random
from .constants import NORTH, SOUTH, EAST, WEST, RESTART_DELAY

class Car:
    def __init__(self, x, y, direction):
        self.id = str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 1  # Cells per tick
        self.waiting = False
        self.entry_direction = None
        self.ticks_in_intersection = 0  # Track time spent in intersection
        self.total_wait_time = 0  # Total ticks spent waiting at red lights
        self.current_wait_time = 0  # Current consecutive wait time
        self.restart_delay_counter = 0  # Ticks remaining before car can restart (accordion effect)
        self.was_waiting = False  # Track if car was waiting in previous tick

    def move(self, game_map, traffic_lights, other_cars):
        """
        Attempts to move the car one step in its current direction.
        """
        dx, dy = self.direction
        next_x = self.x + dx
        next_y = self.y + dy
        
        # Accordion effect: if car was waiting and now wants to move, apply restart delay
        if self.restart_delay_counter > 0:
            self.restart_delay_counter -= 1
            self.waiting = True
            return False  # Still restarting, cannot move yet
        
        # Track if currently in intersection
        currently_in_intersection = game_map.is_intersection(self.x, self.y)
        if currently_in_intersection:
            self.ticks_in_intersection += 1
        else:
            self.ticks_in_intersection = 0

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
        next_is_intersection = game_map.is_intersection(next_x, next_y)
        
        if next_is_intersection:
            light = None
            for tl in traffic_lights:
                if tl.x == check_x and tl.y == check_y:
                    light = tl
                    break
            
            if light and light.is_red():
                self.waiting = True
                self.was_waiting = True
                return False # Stop at red light
            
            # 2b. Check if intersection is safe to enter
            # Don't enter if there's a car in the intersection going in a conflicting direction
            if not currently_in_intersection:
                for car in other_cars:
                    if car.id != self.id and game_map.is_intersection(car.x, car.y):
                        # Check if the other car is going in a perpendicular direction (conflict)
                        if self._is_conflicting_direction(car.direction):
                            self.waiting = True
                            return False  # Wait for intersection to clear

        # 3. Check Collision with Other Cars
        for car in other_cars:
            if car.id != self.id and car.x == next_x and car.y == next_y:
                # If we're stuck in intersection for too long, give priority to exit
                if currently_in_intersection and self.ticks_in_intersection > 3:
                    # Check if the blocking car is NOT in intersection - we have priority
                    if not game_map.is_intersection(car.x, car.y):
                        continue  # Ignore this car, force our way out
                self.waiting = True
                self.was_waiting = True
                return False  # Stop behind car
        
        # 4. Deadlock prevention: If stuck in intersection too long, try alternative direction
        if currently_in_intersection and self.ticks_in_intersection > 5:
            allowed_dirs = game_map.get_allowed_directions(self.x, self.y)
            for alt_dir in allowed_dirs:
                if alt_dir == self.direction:
                    continue
                # Check if this direction is clear
                alt_next_x = self.x + alt_dir[0]
                alt_next_y = self.y + alt_dir[1]
                is_clear = True
                for car in other_cars:
                    if car.id != self.id and car.x == alt_next_x and car.y == alt_next_y:
                        is_clear = False
                        break
                if is_clear and game_map.is_road(alt_next_x, alt_next_y):
                    # Take this alternative route to escape deadlock
                    self.direction = alt_dir
                    self.x = alt_next_x
                    self.y = alt_next_y
                    self.waiting = False
                    self.ticks_in_intersection = 0
                    return True

        # 5. If all clear, move
        # Apply accordion effect: if car was waiting, it needs time to restart
        if self.was_waiting:
            self.restart_delay_counter = RESTART_DELAY
            self.was_waiting = False
            self.waiting = True
            return False  # Start restart delay, will move next tick after delay
        
        self.x = next_x
        self.y = next_y
        self.waiting = False
        
        # 6. Update direction at intersection
        self._update_direction_at_intersection(game_map, other_cars)
        
        return True

    def _is_conflicting_direction(self, other_direction):
        """Check if another car's direction conflicts with ours (perpendicular)."""
        # Same or opposite direction = no conflict (parallel traffic)
        if self.direction == other_direction:
            return False
        if self.direction[0] == -other_direction[0] and self.direction[1] == -other_direction[1]:
            return False
        # Perpendicular directions = conflict
        return True

    def _update_direction_at_intersection(self, game_map, other_cars):
        """Update direction with probabilistic logic at intersections."""
        allowed_dirs = game_map.get_allowed_directions(self.x, self.y)
        
        # Track Intersection Entry/Exit
        is_in_intersection = game_map.is_intersection(self.x, self.y)
        
        if is_in_intersection:
            if self.entry_direction is None:
                self.entry_direction = self.direction
        else:
            self.entry_direction = None

        if not allowed_dirs:
            return

        # Filter based on Entry Direction
        if self.entry_direction:
            filtered_dirs = []
            for d in allowed_dirs:
                # Prevent U-turn relative to ENTRY direction
                if d[0] == -self.entry_direction[0] and d[1] == -self.entry_direction[1]:
                    continue
                filtered_dirs.append(d)
            
            if filtered_dirs:
                allowed_dirs = filtered_dirs
        
        # Also filter immediate U-turns (just in case)
        if len(allowed_dirs) > 1:
            filtered_dirs = []
            for d in allowed_dirs:
                if d[0] == -self.direction[0] and d[1] == -self.direction[1]:
                    continue
                filtered_dirs.append(d)
            if filtered_dirs:
                allowed_dirs = filtered_dirs

        # NEW: Filter out directions where the target cell is occupied
        # Only apply this if we have multiple choices (if only 1, we must take it)
        if len(allowed_dirs) > 1:
            non_blocked_dirs = []
            for d in allowed_dirs:
                target_x = self.x + d[0]
                target_y = self.y + d[1]
                is_blocked = False
                for car in other_cars:
                    if car.id != self.id and car.x == target_x and car.y == target_y:
                        is_blocked = True
                        break
                if not is_blocked:
                    non_blocked_dirs.append(d)
            
            # If we have at least one non-blocked direction, restrict to those
            if non_blocked_dirs:
                allowed_dirs = non_blocked_dirs

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
                    if self.direction == NORTH and d == EAST:
                        is_right = True
                    elif self.direction == EAST and d == SOUTH:
                        is_right = True
                    elif self.direction == SOUTH and d == WEST:
                        is_right = True
                    elif self.direction == WEST and d == NORTH:
                        is_right = True
                    
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
            
            # 2. Exit Case (Straight + Left): 1/2 Left, 1/2 Straight
            elif "STRAIGHT" in options and "LEFT" in options and "RIGHT" not in options:
                if random.random() < 0.5:
                    self.direction = options["LEFT"]
                else:
                    self.direction = options["STRAIGHT"]
                    
            # 3. All 3 available (Generic intersection): 1/3 each
            elif "STRAIGHT" in options and "LEFT" in options and "RIGHT" in options:
                r = random.random()
                if r < 0.333:
                    self.direction = options["RIGHT"]
                elif r < 0.666:
                    self.direction = options["LEFT"]
                else:
                    self.direction = options["STRAIGHT"]
                
            # 4. Forced Turn (no straight)
            elif "STRAIGHT" not in options:
                self.direction = random.choice(list(options.values()))
                
        elif len(valid_dirs) == 1:
            self.direction = valid_dirs[0]

    def increment_wait_time(self):
        """Called each tick when the car is waiting."""
        if self.waiting:
            self.total_wait_time += 1
            self.current_wait_time += 1
        else:
            self.current_wait_time = 0

    def get_state(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "waiting": self.waiting,
            "total_wait_time": self.total_wait_time,
            "current_wait_time": self.current_wait_time
        }

from .constants import RED, GREEN

class TrafficLight:
    def __init__(self, x, y, axis, initial_state=RED, cycle_time=30):
        """
        Initialize a traffic light at a specific position.
        
        Args:
            x (int): X coordinate on the grid.
            y (int): Y coordinate on the grid.
            axis (str): 'VERTICAL' or 'HORIZONTAL' - the flow this light controls.
            initial_state (int): Initial state (RED or GREEN).
            cycle_time (int): Number of ticks before toggling state automatically.
        """
        self.x = x
        self.y = y
        self.axis = axis
        self.state = initial_state
        self.timer = 0
        self.cycle_time = cycle_time

    def toggle(self):
        """Switch the traffic light state."""
        if self.state == RED:
            self.state = GREEN
        else:
            self.state = RED

    def update(self):
        """Update the traffic light timer and toggle if necessary."""
        self.timer += 1
        if self.timer >= self.cycle_time:
            self.toggle()
            self.timer = 0

    def is_green(self):
        return self.state == GREEN

    def is_red(self):
        return self.state == RED

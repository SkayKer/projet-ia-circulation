import pygame
from .constants import *

class Renderer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Traffic Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 12)

    def render(self, simulation):
        """Draws the current state of the simulation."""
        self.screen.fill((50, 150, 50))  # Grass background

        # Draw Map
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = simulation.map.get_cell(x, y)
                rect = (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if cell == ROAD or cell == INTERSECTION:
                    pygame.draw.rect(self.screen, (50, 50, 50), rect) # Dark Gray Road
                    # Draw lane markings (simplified)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)
                elif cell == BUILDING:
                    pygame.draw.rect(self.screen, (100, 100, 100), rect) # Gray Building
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        # Draw Traffic Lights
        for tl in simulation.traffic_lights:
            cx = tl.x * CELL_SIZE + CELL_SIZE // 2
            cy = tl.y * CELL_SIZE + CELL_SIZE // 2
            color = (255, 0, 0) if tl.is_red() else (0, 255, 0)
            
            # Draw a small box for the light housing
            light_rect = (tl.x * CELL_SIZE + 5, tl.y * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
            pygame.draw.rect(self.screen, (0, 0, 0), light_rect)
            pygame.draw.circle(self.screen, color, (cx, cy), CELL_SIZE // 3 - 2)

        # Draw Cars
        for car in simulation.cars:
            cx = car.x * CELL_SIZE + CELL_SIZE // 2
            cy = car.y * CELL_SIZE + CELL_SIZE // 2
            
            # Draw car body
            pygame.draw.circle(self.screen, (0, 0, 255), (cx, cy), CELL_SIZE // 2 - 2)
            
            # Draw direction indicator (small line)
            dx, dy = car.direction
            end_x = cx + dx * (CELL_SIZE // 2)
            end_y = cy + dy * (CELL_SIZE // 2)
            pygame.draw.line(self.screen, (255, 255, 0), (cx, cy), (end_x, end_y), 2)

        pygame.display.flip()

    def handle_events(self):
        """Handles Pygame events (quit, etc.). Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def tick(self):
        """Controls the frame rate."""
        self.clock.tick(FPS)

    def quit(self):
        pygame.quit()

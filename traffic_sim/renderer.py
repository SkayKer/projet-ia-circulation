import pygame
from .constants import *

class Renderer:
    def __init__(self):
        pygame.init()
        
        # Get screen info for adaptive sizing
        screen_info = pygame.display.Info()
        max_screen_width = screen_info.current_w
        max_screen_height = screen_info.current_h
        
        # Calculate the ideal cell size to fit the grid on screen (with some margin)
        margin = 100  # Leave some space for window decorations
        ideal_cell_width = (max_screen_width - margin) // GRID_SIZE
        ideal_cell_height = (max_screen_height - margin) // GRID_SIZE
        self.cell_size = min(ideal_cell_width, ideal_cell_height, CELL_SIZE)
        
        # Calculate window dimensions based on cell size
        self.width = GRID_SIZE * self.cell_size
        self.height = GRID_SIZE * self.cell_size
        
        # Create window (fixed size, adapted to screen)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Traffic Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 12)
        
        # Slider settings (will be updated on resize)
        self._update_slider_position()
        self.slider_width = 200
        self.slider_height = 10
        self.slider_dragging = False
    
    def _update_slider_position(self):
        """Update slider position based on current window size."""
        self.slider_x = self.width - 220
        self.slider_y = self.height - 50

    def render(self, simulation):
        """Draws the current state of the simulation."""
        self.screen.fill((50, 150, 50))  # Grass background

        # Draw Map
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = simulation.map.get_cell(x, y)
                rect = (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                
                if cell == ROAD or cell == INTERSECTION:
                    pygame.draw.rect(self.screen, (50, 50, 50), rect) # Dark Gray Road
                    # Draw lane markings (simplified)
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)
                elif cell == BUILDING:
                    pygame.draw.rect(self.screen, (100, 100, 100), rect) # Gray Building
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        # Draw Traffic Lights
        for tl in simulation.traffic_lights:
            cx = tl.x * self.cell_size + self.cell_size // 2
            cy = tl.y * self.cell_size + self.cell_size // 2
            color = (255, 0, 0) if tl.is_red() else (0, 255, 0)
            
            # Draw a small box for the light housing
            padding = max(2, self.cell_size // 6)
            light_rect = (tl.x * self.cell_size + padding, tl.y * self.cell_size + padding, self.cell_size - padding * 2, self.cell_size - padding * 2)
            pygame.draw.rect(self.screen, (0, 0, 0), light_rect)
            pygame.draw.circle(self.screen, color, (cx, cy), self.cell_size // 3 - 2)

        # Draw Cars
        for car in simulation.cars:
            cx = car.x * self.cell_size + self.cell_size // 2
            cy = car.y * self.cell_size + self.cell_size // 2
            
            # Draw car body
            pygame.draw.circle(self.screen, (0, 0, 255), (cx, cy), self.cell_size // 2 - 2)
            
            # Draw direction indicator (small line)
            dx, dy = car.direction
            end_x = cx + dx * (self.cell_size // 2)
            end_y = cy + dy * (self.cell_size // 2)
            pygame.draw.line(self.screen, (255, 255, 0), (cx, cy), (end_x, end_y), 2)

        # Draw Statistics Panel
        self._draw_stats(simulation)
        
        # Draw Spawn Rate Slider
        self._draw_slider(simulation)

        pygame.display.flip()

    def _draw_stats(self, simulation):
        """Draw statistics panel in the top-left corner."""
        # Semi-transparent background for stats
        stats_surface = pygame.Surface((270, 140))
        stats_surface.set_alpha(200)
        stats_surface.fill((0, 0, 0))
        self.screen.blit(stats_surface, (5, 5))
        
        # Get statistics
        time_sec = simulation.tick_count / FPS
        cars_waiting = simulation.get_current_cars_waiting()
        total_cars = len(simulation.cars)
        avg_wait_10s = simulation.get_average_wait_time_last_10s()
        max_queue = simulation.get_max_queue_length()
        avg_queue = simulation.get_average_queue_length()
        current_queues = simulation.get_current_queue_lengths()
        current_max_queue = max(current_queues) if current_queues else 0
        
        # Render text in French
        stats = [
            f"Temps: {time_sec:.1f}s",
            f"Voitures: {total_cars} (en attente: {cars_waiting})",
            f"Attente moy. (10 dern. sec): {avg_wait_10s:.2f}s",
            f"File d'attente actuelle max: {current_max_queue}",
            f"File d'attente max (record): {max_queue}",
            f"File d'attente moy. (10s): {avg_queue:.1f}",
        ]
        
        y_offset = 10
        for stat in stats:
            text = self.font.render(stat, True, (255, 255, 255))
            self.screen.blit(text, (10, y_offset))
            y_offset += 20

    def _draw_slider(self, simulation):
        """Draw spawn rate slider in the bottom-right corner."""
        # Semi-transparent background
        bg_surface = pygame.Surface((250, 60))
        bg_surface.set_alpha(200)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, (self.slider_x - 15, self.slider_y - 30))
        
        # Draw label in French
        spawn_interval_sec = simulation.spawn_rate / FPS
        label = f"Apparition toutes les {spawn_interval_sec:.2f}s ({simulation.spawn_rate} ticks)"
        text = self.font.render(label, True, (255, 255, 255))
        self.screen.blit(text, (self.slider_x - 10, self.slider_y - 20))
        
        # Draw slider track
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (self.slider_x, self.slider_y, self.slider_width, self.slider_height))
        
        # Calculate knob position (spawn_rate: 1-10 -> position on slider)
        knob_pos = self.slider_x + ((simulation.spawn_rate - 1) / 9) * self.slider_width
        
        # Draw slider knob
        pygame.draw.circle(self.screen, (255, 255, 255), (int(knob_pos), self.slider_y + 5), 8)
        pygame.draw.circle(self.screen, (0, 150, 255), (int(knob_pos), self.slider_y + 5), 6)
        
        # Draw min/max labels
        min_text = self.font.render("1", True, (255, 255, 255))
        max_text = self.font.render("10", True, (255, 255, 255))
        self.screen.blit(min_text, (self.slider_x - 10, self.slider_y - 2))
        self.screen.blit(max_text, (self.slider_x + self.slider_width + 5, self.slider_y - 2))

    def handle_events(self, simulation=None):
        """Handles Pygame events (quit, slider, resize, etc.). Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle slider interaction
            if simulation is not None:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_x, mouse_y = event.pos
                        # Check if click is on slider area
                        if (self.slider_x <= mouse_x <= self.slider_x + self.slider_width and
                            self.slider_y - 10 <= mouse_y <= self.slider_y + 20):
                            self.slider_dragging = True
                            self._update_spawn_rate(mouse_x, simulation)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.slider_dragging = False
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.slider_dragging:
                        mouse_x, _ = event.pos
                        self._update_spawn_rate(mouse_x, simulation)
        
        return True
    
    def _update_spawn_rate(self, mouse_x, simulation):
        """Update spawn rate based on mouse position."""
        # Clamp mouse_x to slider bounds
        rel_x = max(0, min(mouse_x - self.slider_x, self.slider_width))
        # Convert to spawn rate (1-10)
        spawn_rate = int(1 + (rel_x / self.slider_width) * 9)
        spawn_rate = max(1, min(10, spawn_rate))
        simulation.spawn_rate = spawn_rate

    def tick(self):
        """Controls the frame rate."""
        self.clock.tick(FPS)

    def quit(self):
        pygame.quit()

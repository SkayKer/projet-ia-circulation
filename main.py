import sys
import os

# Ensure we can import modules from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from traffic_sim.simulation import Simulation
from traffic_sim.renderer import Renderer

def main():
    print("Starting Traffic Simulator...")
    print("Press Ctrl+C to stop if running in terminal without GUI support.")
    
    sim = Simulation()
    
    try:
        renderer = Renderer()
        running = True
        
        while running:
            # 1. Handle Input (pass simulation for slider control)
            running = renderer.handle_events(sim)
            
            # 2. Update Simulation
            sim.step()
            
            # 3. Render
            renderer.render(sim)
            
            # 4. Wait
            renderer.tick()
            
    except ImportError:
        print("Pygame not found. Please install it using 'pip install pygame'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'renderer' in locals():
            renderer.quit()
        print("Simulation ended.")

if __name__ == "__main__":
    main()

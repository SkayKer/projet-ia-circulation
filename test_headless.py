import sys
import os

# Ensure we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from traffic_sim.simulation import Simulation

def test_simulation():
    print("Initializing Simulation...")
    sim = Simulation()
    
    print("Running 100 steps...")
    for i in range(100):
        sim.step()
        state = sim.get_state()
        
        # Basic checks
        if i % 20 == 0:
            print(f"Step {i}: {len(state['cars'])} cars, Lights: {[l[2] for l in state['lights']]}")
            
    print("Simulation ran successfully for 100 steps.")

if __name__ == "__main__":
    test_simulation()

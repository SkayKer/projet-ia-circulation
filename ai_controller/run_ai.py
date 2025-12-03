import sys
import os
import pygame

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traffic_sim.renderer import Renderer
from ai_controller.traffic_env import TrafficEnv
from ai_controller.q_agent import QLearningAgent

def run_ai():
    print("Starting AI Controlled Traffic Simulator...")
    
    env = TrafficEnv()
    agent = QLearningAgent()
    agent.load("q_agent.pkl")
    agent.epsilon = 0.0 # No exploration during test
    
    try:
        renderer = Renderer()
        running = True
        states = env.reset() # Reset env but we need to sync with renderer's sim? 
        # Actually TrafficEnv creates its own Simulation. 
        # We need to use the env's simulation for rendering.
        
        while running:
            # 1. Handle Input
            running = renderer.handle_events()
            
            # 2. AI Action
            actions = {}
            for i_id, state in states.items():
                action = agent.choose_action(state)
                actions[i_id] = action
            
            # 3. Step Environment
            next_states, reward, done = env.step(actions)
            states = next_states
            
            # 4. Render
            renderer.render(env.sim)
            
            # 5. Wait
            renderer.tick()
            
            if done:
                print("Episode finished. Resetting...")
                states = env.reset()
            
    except ImportError:
        print("Pygame not found. Please install it using 'pip install pygame'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'renderer' in locals():
            renderer.quit()
        print("Simulation ended.")

if __name__ == "__main__":
    run_ai()

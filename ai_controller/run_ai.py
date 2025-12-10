import sys
import os
import argparse
import pygame

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traffic_sim.renderer import Renderer
from ai_controller.traffic_env import TrafficEnv
from ai_controller.q_agent import QLearningAgent

def run_ai(spawn_rate=None, contextual=False):
    """
    Run the AI-controlled traffic simulator.
    
    Args:
        spawn_rate: Optional spawn rate to use. If None, uses default.
        contextual: If True, uses contextual model with traffic level in state.
    """
    print("=== AI Controlled Traffic Simulator ===")
    
    # Determine which model to load
    if contextual:
        model_file = "q_agent_contextual.pkl"
        print(f"Mode: Contextual Q-Learning")
    else:
        model_file = "q_agent.pkl"
        print(f"Mode: Standard Q-Learning")
    
    if spawn_rate is not None:
        print(f"Spawn Rate: {spawn_rate} (cars spawn every {spawn_rate} ticks)")
    else:
        print(f"Spawn Rate: Default (from constants)")
    
    # Initialize environment
    env = TrafficEnv(spawn_rate=spawn_rate, contextual=contextual)
    
    if contextual:
        print(f"Traffic Level: {env.get_traffic_level_name()}")
    
    # Load agent
    agent = QLearningAgent()
    if not os.path.exists(model_file):
        print(f"Warning: Model file '{model_file}' not found. Using untrained agent.")
    else:
        agent.load(model_file)
        print(f"Loaded model: {model_file} ({len(agent.q_table)} states)")
    
    agent.epsilon = 0.0  # No exploration during test
    print()
    
    try:
        renderer = Renderer()
        running = True
        states = env.reset()
        
        # Track last spawn_rate to detect slider changes
        last_spawn_rate = env.sim.spawn_rate
        
        while running:
            # 1. Handle Input (pass simulation for slider control)
            running = renderer.handle_events(env.sim)
            
            # Check if spawn rate changed via slider
            if env.sim.spawn_rate != last_spawn_rate:
                last_spawn_rate = env.sim.spawn_rate
                # Sync environment with new spawn rate (for contextual learning)
                env.set_spawn_rate(env.sim.spawn_rate)
                if contextual:
                    print(f"Spawn Rate changed to {env.sim.spawn_rate} - Traffic Level: {env.get_traffic_level_name()}")
            
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

def main():
    parser = argparse.ArgumentParser(description="Run AI-controlled traffic simulator")
    parser.add_argument("--spawn-rate", type=int, default=None,
                        help="Spawn rate (cars spawn every N ticks). Lower = more traffic.")
    parser.add_argument("--contextual", action="store_true",
                        help="Use contextual Q-learning model (includes traffic level in state)")
    args = parser.parse_args()
    
    run_ai(spawn_rate=args.spawn_rate, contextual=args.contextual)

if __name__ == "__main__":
    main()


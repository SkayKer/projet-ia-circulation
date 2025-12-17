import sys
import os
import time

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_controller.traffic_env import TrafficEnv
from ai_controller.q_agent import QLearningAgent

def train(episodes=100):
    env = TrafficEnv()
    # One agent per intersection, or one shared agent?
    # Let's use one shared agent for simplicity as intersections are identical.
    agent = QLearningAgent()
    
    print(f"Starting training for {episodes} episodes...")
    
    for e in range(episodes):
        states = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            actions = {}
            for i_id, state in states.items():
                action = agent.choose_action(state)
                actions[i_id] = action
            
            next_states, reward, done = env.step(actions)
            
            for i_id, state in states.items():
                action = actions[i_id]
                next_state = next_states[i_id]
                agent.learn(state, action, reward, next_state)
            
            states = next_states
            total_reward += reward
            
        # Decay epsilon
        agent.epsilon = max(0.01, agent.epsilon * 0.995)
        
        if (e + 1) % 10 == 0:
            print(f"Episode {e+1}/{episodes} - Total Reward: {total_reward:.2f} - Epsilon: {agent.epsilon:.2f}")
            
    agent.save("q_agent.pkl")
    print("Training finished. Agent saved to q_agent.pkl")

if __name__ == "__main__":
    train(episodes=10000)

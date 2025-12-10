"""
Contextual Q-Learning Training Script

This script trains a Q-learning agent with traffic level context.
The agent learns to optimize traffic light control across different
traffic intensities (spawn rates).
"""

import sys
import os
import argparse
import random

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_controller.traffic_env import TrafficEnv, get_traffic_level
from ai_controller.q_agent import QLearningAgent

# Define spawn rates to train on
SPAWN_RATES = [1, 2, 3, 5, 10]

def train_contextual(episodes=500, test_mode=False):
    """
    Train a contextual Q-learning agent across different traffic levels.
    
    Args:
        episodes: Total number of episodes to train
        test_mode: If True, runs fewer episodes for quick testing
    """
    if test_mode:
        episodes = len(SPAWN_RATES) * 5  # 5 episodes per spawn rate
        
    # Create environment in contextual mode
    env = TrafficEnv(contextual=True)
    agent = QLearningAgent()
    
    print(f"=== Contextual Q-Learning Training ===")
    print(f"Training for {episodes} episodes across spawn rates: {SPAWN_RATES}")
    print(f"Traffic levels: LOW (spawn>=5), MEDIUM (spawn=2-4), HIGH (spawn<=1)")
    print()
    
    # Track performance per traffic level
    rewards_by_level = {"LOW": [], "MEDIUM": [], "HIGH": []}
    
    for e in range(episodes):
        # Select spawn rate for this episode (cycle through options)
        spawn_rate = SPAWN_RATES[e % len(SPAWN_RATES)]
        env.set_spawn_rate(spawn_rate)
        
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
        
        # Track reward by traffic level
        level_name = env.get_traffic_level_name()
        rewards_by_level[level_name].append(total_reward)
        
        # Decay epsilon
        agent.epsilon = max(0.01, agent.epsilon * 0.995)
        
        # Progress logging
        if (e + 1) % 10 == 0:
            print(f"Episode {e+1}/{episodes} - Spawn Rate: {spawn_rate} ({level_name}) - "
                  f"Reward: {total_reward:.2f} - Epsilon: {agent.epsilon:.3f}")
    
    # Save the contextual agent
    output_file = "q_agent_contextual.pkl"
    agent.save(output_file)
    
    # Print summary
    print()
    print("=== Training Complete ===")
    print(f"Agent saved to: {output_file}")
    print(f"Q-table size: {len(agent.q_table)} states")
    print()
    print("Average rewards by traffic level:")
    for level, rewards in rewards_by_level.items():
        if rewards:
            avg_reward = sum(rewards) / len(rewards)
            print(f"  {level}: {avg_reward:.2f} (over {len(rewards)} episodes)")
    
    return agent

def main():
    parser = argparse.ArgumentParser(description="Train contextual Q-learning agent")
    parser.add_argument("--episodes", type=int, default=500, 
                        help="Number of training episodes (default: 500)")
    parser.add_argument("--test", action="store_true",
                        help="Quick test mode (5 episodes per spawn rate)")
    args = parser.parse_args()
    
    train_contextual(episodes=args.episodes, test_mode=args.test)

if __name__ == "__main__":
    main()

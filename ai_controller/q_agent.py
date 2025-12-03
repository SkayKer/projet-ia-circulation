import random
import pickle
import os

class QLearningAgent:
    def __init__(self, action_size=2, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = {} # State -> [Q(s, a0), Q(s, a1)]
        self.action_size = action_size
        self.alpha = alpha # Learning rate
        self.gamma = gamma # Discount factor
        self.epsilon = epsilon # Exploration rate

    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * self.action_size
        return self.q_table[state]

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        
        q_values = self.get_q_values(state)
        # Break ties randomly
        max_q = max(q_values)
        actions_with_max_q = [i for i, q in enumerate(q_values) if q == max_q]
        return random.choice(actions_with_max_q)

    def learn(self, state, action, reward, next_state):
        q_values = self.get_q_values(state)
        next_q_values = self.get_q_values(next_state)
        
        # Q(s, a) = Q(s, a) + alpha * (r + gamma * max(Q(s', a')) - Q(s, a))
        target = reward + self.gamma * max(next_q_values)
        q_values[action] += self.alpha * (target - q_values[action])

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.q_table, f)
            
    def load(self, filename):
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                self.q_table = pickle.load(f)

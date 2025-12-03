import sys
import os
import numpy as np

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traffic_sim.simulation import Simulation

class TrafficEnv:
    def __init__(self):
        self.sim = Simulation()
        self.intersections = [0, 1] # IDs of intersections to control
        self.action_space_size = 2 # 0: Vertical Green, 1: Horizontal Green
        self.state_space_size = (3, 3, 3, 3, 2) # (NB, SB, EB, WB, Phase) - Discretized queues + Phase
        
        # Current phase for each intersection
        self.current_phases = {0: 0, 1: 0} 
        self.min_phase_time = 30 # Minimum ticks before switching
        self.time_since_last_switch = {0: 0, 1: 0}

    def reset(self):
        self.sim = Simulation()
        self.current_phases = {0: 0, 1: 0}
        self.time_since_last_switch = {0: 0, 1: 0}
        return self._get_state()

    def step(self, actions):
        """
        actions: dict {intersection_id: action}
        action: 0 (Vertical Green), 1 (Horizontal Green)
        """
        # Apply actions
        for i_id, action in actions.items():
            if action != self.current_phases[i_id]:
                if self.time_since_last_switch[i_id] >= self.min_phase_time:
                    self.current_phases[i_id] = action
                    self.time_since_last_switch[i_id] = 0
            
            self.sim.set_intersection_light_phase(i_id, self.current_phases[i_id])
            self.time_since_last_switch[i_id] += 1

        # Step simulation
        self.sim.step()

        # Calculate reward
        # User request: "reward must be calculated with average wait time, max queue length, 
        # and average queue length. More importance on time saved than on average queue length."
        
        avg_wait_10s = self.sim.get_average_wait_time_last_10s()
        max_queue = self.sim.get_max_queue_length()
        avg_queue = self.sim.get_average_queue_length()
        
        # Weights
        w_wait = 2.0
        w_max_q = 0.5
        w_avg_q = 0.1
        
        # Negative reward (penalty)
        reward = - (w_wait * avg_wait_10s + w_max_q * max_queue + w_avg_q * avg_queue)
        
        done = False # Continuous task
        if self.sim.tick_count >= 2000: # Max episode length
            done = True
            
        return self._get_state(), reward, done

    def _get_state(self):
        """
        Returns state for each intersection.
        State: (NB_queue, SB_queue, EB_queue, WB_queue, current_phase)
        Queues are discretized: 0 (0), 1 (1-3), 2 (>3)
        """
        states = {}
        for i_id in self.intersections:
            queues = self.sim.get_intersection_queues(i_id)
            discretized_queues = [self._discretize(q) for q in queues]
            state = tuple(discretized_queues + [self.current_phases[i_id]])
            states[i_id] = state
        return states

    def _discretize(self, val):
        if val == 0: return 0
        if val <= 3: return 1
        return 2

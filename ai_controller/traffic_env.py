import sys
import os
import numpy as np

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traffic_sim.simulation import Simulation

# Traffic level constants based on spawn_rate
# spawn_rate >= 5: Low traffic (0)
# spawn_rate 2-4: Medium traffic (1)
# spawn_rate <= 1: High traffic (2)
TRAFFIC_LEVELS = {
    "LOW": 0,      # spawn_rate >= 5
    "MEDIUM": 1,   # spawn_rate 2-4
    "HIGH": 2      # spawn_rate <= 1
}

def get_traffic_level(spawn_rate):
    """Convert spawn_rate to discretized traffic level."""
    if spawn_rate >= 5:
        return TRAFFIC_LEVELS["LOW"]
    elif spawn_rate >= 2:
        return TRAFFIC_LEVELS["MEDIUM"]
    else:
        return TRAFFIC_LEVELS["HIGH"]

class TrafficEnv:
    def __init__(self, spawn_rate=None, contextual=False):
        """
        Initialize the traffic environment.
        
        Args:
            spawn_rate: Cars spawn every N ticks. Lower = more traffic.
                       If None, uses default from constants.
            contextual: If True, includes traffic level in state for contextual Q-learning.
        """
        self.spawn_rate = spawn_rate
        self.contextual = contextual
        self.sim = Simulation()
        
        # Set spawn rate if provided
        if spawn_rate is not None:
            self.sim.spawn_rate = spawn_rate
        
        self.intersections = [0, 1] # IDs of intersections to control
        self.action_space_size = 2 # 0: Vertical Green, 1: Horizontal Green
        
        # State space size depends on contextual mode
        if contextual:
            # (NB, SB, EB, WB, Phase, TrafficLevel) - Discretized queues + Phase + Traffic context
            self.state_space_size = (3, 3, 3, 3, 2, 3)
        else:
            # Original: (NB, SB, EB, WB, Phase) - Discretized queues + Phase
            self.state_space_size = (3, 3, 3, 3, 2)
        
        # Current phase for each intersection
        self.current_phases = {0: 0, 1: 0} 
        self.min_phase_time = 30 # Minimum ticks before switching
        self.time_since_last_switch = {0: 0, 1: 0}
        
        # Traffic level (for contextual learning)
        self.traffic_level = get_traffic_level(self.sim.spawn_rate)

    def reset(self):
        """Reset the environment for a new episode."""
        self.sim = Simulation()
        
        # Set spawn rate if configured
        if self.spawn_rate is not None:
            self.sim.spawn_rate = self.spawn_rate
            
        self.current_phases = {0: 0, 1: 0}
        self.time_since_last_switch = {0: 0, 1: 0}
        self.traffic_level = get_traffic_level(self.sim.spawn_rate)
        return self._get_state()
    
    def set_spawn_rate(self, spawn_rate):
        """Dynamically change the spawn rate (useful for contextual training)."""
        self.spawn_rate = spawn_rate
        self.sim.spawn_rate = spawn_rate
        self.traffic_level = get_traffic_level(spawn_rate)

    def step(self, actions):
        """
        Execute one step in the environment.
        
        Args:
            actions: dict {intersection_id: action}
                     action: 0 (Vertical Green), 1 (Horizontal Green)
        
        Returns:
            tuple: (next_state, reward, done)
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
        
        Non-contextual State: (NB_queue, SB_queue, EB_queue, WB_queue, current_phase)
        Contextual State: (NB_queue, SB_queue, EB_queue, WB_queue, current_phase, traffic_level)
        
        Queues are discretized: 0 (0), 1 (1-3), 2 (>3)
        Traffic level: 0 (low), 1 (medium), 2 (high)
        """
        states = {}
        for i_id in self.intersections:
            queues = self.sim.get_intersection_queues(i_id)
            discretized_queues = [self._discretize(q) for q in queues]
            
            if self.contextual:
                # Include traffic level in state
                state = tuple(discretized_queues + [self.current_phases[i_id], self.traffic_level])
            else:
                # Original state without traffic context
                state = tuple(discretized_queues + [self.current_phases[i_id]])
                
            states[i_id] = state
        return states

    def _discretize(self, val):
        """Discretize queue length into buckets."""
        if val == 0: return 0
        if val <= 3: return 1
        return 2
    
    def get_traffic_level_name(self):
        """Get human-readable traffic level name."""
        for name, level in TRAFFIC_LEVELS.items():
            if level == self.traffic_level:
                return name
        return "UNKNOWN"

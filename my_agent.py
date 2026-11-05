import random
import hashlib
import time
import numpy as np
from collections import deque
from typing import Any
from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent

class MyAgent(Agent):
    MAX_ACTIONS = float('inf')

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        seed = int(time.time() * 1000000) + hash(self.game_id) % 1000000
        random.seed(seed)
        np.random.seed(seed % (2**32 - 1))
        
        self.transitions = {}       # Maps state -> {action: next_state}
        self.known_states = set()   # Set of all discovered states
        self.useless_actions = {}   # Maps state -> set of actions that do nothing
        
        self.prev_state_key = None
        self.prev_action_id = None
        
        # Sprint Memory
        self.current_path = [] 
        self.winning_path = [] 
        self.current_level = 0
        self.is_replaying = False
        self.replay_index = 0

    def _hash_state(self, frame):
        if frame is not None and hasattr(frame, 'frame') and frame.frame is not None:
            return hashlib.md5(str(frame.frame).encode()).hexdigest()
        return str(frame.state)

    def _get_smart_click(self, frame_data):
        """Centroid Sniper: Finds the bounding box of the smallest object and clicks its center."""
        try:
            grid = np.array(frame_data.frame)
            if len(grid.shape) == 3:
                grid = grid[-1]
            
            unique, counts = np.unique(grid, return_counts=True)
            # Filter out background (usually the most common color)
            if len(unique) <= 1:
                return random.randint(0, 63), random.randint(0, 63)
            
            # Find the 2nd least common color (more likely to be a target than a single pixel)
            sorted_indices = np.argsort(counts)
            target_color = unique[sorted_indices[1]] if len(unique) > 2 else unique[sorted_indices[0]]
            
            coords = np.argwhere(grid == target_color)
            if len(coords) > 0:
                # Calculate centroid
                y_center = int(np.mean(coords[:, 0]))
                x_center = int(np.mean(coords[:, 1]))
                return x_center, y_center
        except Exception:
            pass
        return random.randint(0, 63), random.randint(0, 63)

    def _bfs_to_unexplored(self, start_state, valid_actions):
        """Calculates the shortest path to any state that hasn't had all its actions tried."""
        queue = deque([(start_state, [])])
        visited = set([start_state])
        
        while queue:
            current, path = queue.popleft()
            
            # Check if this state has untried actions
            if current in self.transitions:
                tried = set(self.transitions[current].keys())
                untried = [str(a) for a in valid_actions if str(a) not in tried and a not in self.useless_actions.get(current, set())]
                if untried:
                    return path # Found a path to an unexplored node
            
            # Expand search
            if current in self.transitions:
                for action_str, next_state in self.transitions[current].items():
                    if next_state not in visited:
                        visited.add(next_state)
                        queue.append((next_state, path + [int(action_str)]))
        return [] # No path found

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        current_state_key = self._hash_state(latest_frame)
        current_lvl = getattr(latest_frame, 'levels_completed', 0)
        
        # 1. Sprint Memory
        if current_lvl > self.current_level:
            self.winning_path = list(self.current_path)
            self.current_level = current_lvl
            self.current_path = []
            self.is_replaying = False 
            print(f"[Grandmaster] Level {current_lvl} cleared! Saved path: {len(self.winning_path)} steps.")

        # 2. Reset
        if latest_frame.state in [GameState.NOT_PLAYED, GameState.GAME_OVER]:
            self.prev_state_key = None
            self.prev_action_id = None
            self.current_path = []
            self.is_replaying = False
            return GameAction.RESET

        if latest_frame.state is GameState.WIN:
            return GameAction.RESET

        # 3. Replay Sprint
        if self.winning_path and self.replay_index < len(self.winning_path):
            expected_state, action_id, action_data = self.winning_path[self.replay_index]
            if current_state_key == expected_state:
                self.replay_index += 1
                action = GameAction.from_id(action_id)
                if action.is_complex() and action_data:
                    action.set_data(action_data) 
                return action
            else:
                self.replay_index = 0
                self.winning_path = []

        # 4. Log Transition & Dead-End Detection
        if current_state_key not in self.transitions:
            self.transitions[current_state_key] = {}
            self.known_states.add(current_state_key)
            self.useless_actions[current_state_key] = set()

        if self.prev_state_key is not None and self.prev_action_id is not None:
            # DEAD-END DETECTION: Did the action do absolutely nothing?
            if self.prev_state_key == current_state_key:
                self.useless_actions[self.prev_state_key].add(self.prev_action_id)
            else:
                self.transitions[self.prev_state_key][str(self.prev_action_id)] = current_state_key

        # 5. Action Selection
        valid_action_ids = [a.value if hasattr(a, 'value') else int(a) for a in latest_frame.available_actions]
        if not valid_action_ids:
            return GameAction.RESET

        # Priority A: Untried actions in the current state
        tried_here = set(self.transitions[current_state_key].keys())
        useless_here = self.useless_actions.get(current_state_key, set())
        untried_here = [a for a in valid_action_ids if str(a) not in tried_here and a not in useless_here]

        chosen_id = None
        if untried_here:
            chosen_id = random.choice(untried_here)
        else:
            # Priority B: BFS to the nearest node with untried actions
            path = self._bfs_to_unexplored(current_state_key, valid_action_ids)
            if path:
                chosen_id = path[0]
            else:
                # Priority C: Least-visited neighbor
                best_action = None
                best_score = float('inf')
                for a_id in valid_action_ids:
                    if str(a_id) in self.transitions[current_state_key]:
                        next_key = self.transitions[current_state_key][str(a_id)]
                        visits = 0 
                        if visits < best_score:
                            best_score = visits
                            best_action = a_id
                chosen_id = best_action if best_action is not None else random.choice(valid_action_ids)

        action = GameAction.from_id(chosen_id)
        action_data = None
        if action.is_complex():
            x, y = self._get_smart_click(latest_frame)
            action_data = {"x": x, "y": y}
            action.set_data(action_data)

        self.prev_state_key = current_state_key
        self.prev_action_id = chosen_id
        self.current_path.append((current_state_key, chosen_id, action_data))
        return action
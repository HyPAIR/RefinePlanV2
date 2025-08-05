import json
import os
from datetime import datetime
from uuid import uuid4

class TransitionLogger:
    def __init__(self, save_dir="rl/dateset"):
        self.episode =[]
        self.episode_count = 0
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.last_action = None

    def log_transition(self, state, action, reward, next_state, done):
        transition = {
            "state": state,
            "action": repr(action),
            "reward": reward,
            "next_state": next_state,
            "done": done
        }
        self.episode.append(transition)
        if done:
            self.save_episode()
            self.reset()
    
    def save_episode(self):
        filename = f"episode_{self.episode_count:05d}.json"
        filepath = os.path.join(self.save_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.episode, f, indent=2)
        print(f"[LOG] Episode saved: {filepath}")
        self.episode_count += 1

    def reset(self):
        self.episode = []
        self.last_action = None
        print("[LOG] Episode reset")
    
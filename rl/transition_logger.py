import json
import yaml
import os
from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient
class TransitionLogger:
    def __init__(self, save_dir="rl/dataset"):
        self.episode_count = 0
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.last_action = None
        self.unique_id = str(uuid4())
        print(f"[LOG] TransitionLogger initialized with ID: {self.unique_id}")
        self.episode = [{"id": "start", "timestamp": datetime.now().isoformat(), "unique_id": self.unique_id}]
        self._db_setup()
    def log_transition(self, state, action, reward, next_state, done, execution_time=None):
        transition = {
            "state": state,
            "action": repr(action),
            "reward": reward,
            "next_state": next_state,
            "done": done,
            "execution_time": execution_time
        }
        self.episode.append(transition)
        #Log to MongoDB
        self.log_to_db(state, action, reward, next_state, done, execution_time)
        if done:
            self.save_episode()
            self.reset()
    
    def save_episode(self):
        # filename = f"episode_{self.episode_count:05d}_{self.unique_id}.json"
        filename = f"episode_{self.episode_count:05d}_{self.unique_id}.yaml"
        print(f"[LOG] Saving episode {self.episode_count} to {filename}")
        filepath = os.path.join(self.save_dir, filename)
        with open(filepath, 'w') as f:
            # json.dump(self.episode, f, indent=2)
            yaml.dump(self.episode, f, default_flow_style=False)
        # Save to MongoDB
        print(f"[LOG] Episode saved: {filepath}")
        self.episode_count += 1

    def reset(self):
        self.episode = []
        self.last_action = None
        print("[LOG] Episode reset")
    
    def _db_setup(self):
        """
        Setup a MongoDB database connection for logging.
        """
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['robotics']
        self.collection = self.db['transitions']
        print("[LOG] MongoDB connection established")
    def log_to_db(self, state, action, reward, next_state, done, execution_time=None):
        """
        Log a transition to the MongoDB database.
        """
        # transition = {
        #     "episode_id": self.episode_count,
        #     "unique_id": self.unique_id,
        #     "state": state,
        #     "action": repr(action),
        #     "reward": reward,
        #     "next_state": next_state,
        #     "done": done,
        #     "timestamp": datetime.now().isoformat(),
        #     "execution_time": execution_time
        # }
        transition = {
            "episode_id": self.episode_count,
            "unique_id": self.unique_id,
            "sf_0_name": state,
            "action": repr(action),
            "reward": reward,
            "sf_t_name": next_state,
            "done": done,
            "timestamp": datetime.now().isoformat(),
            "duration": execution_time
        }
     
        self.collection.insert_one(transition)
        print(f"[LOG] Transition logged to MongoDB: {transition}")

    #get a log from the database by unique_id
    def get_log_by_id(self, unique_id):
        """
        Retrieve a log entry from the MongoDB database by unique_id.
        """
        log = self.collection.find_one({"unique_id": unique_id})
        if log:
            print(f"[LOG] Retrieved log for unique_id {unique_id}")
            return log
        else:
            print(f"[LOG] No log found for unique_id {unique_id}")
            return None
    def get_all_logs(self):
        """
        Retrieve all logs from the MongoDB database.
        """
        logs = list(self.collection.find())
        print(f"[LOG] Retrieved {len(logs)} logs from MongoDB")
        return logs
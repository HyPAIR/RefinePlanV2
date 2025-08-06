"""
Class to excecute refined policies in the robotic arm environment

Author: Mohammed Saleeq Kolleth
Owner: Mohammed Saleeq Kolleth

"""
import yaml
class PolicyExcecutor:
    def __init__(self,policy_filename):
        self.policy_filename = policy_filename
        self.loaded_policy = None
        self._load_policy()

    def _load_policy(self):
        with open(self.policy_filename,"r") as f:
            self.loaded_policy = yaml.safe_load(f)
    
    def policy_action(self,state):
        return self.loaded_policy['state_action_map'][state]


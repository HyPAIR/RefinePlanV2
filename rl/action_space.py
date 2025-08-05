from enum import Enum

class ActionType(Enum):
    PICK= "pick"
    PLACE = "place"

class Action:
    def __init__(self,action_type:ActionType,obj=None, target_slot=None, target_pos=None):
        self.action_type = action_type
        self.obj = obj
        self.target_slot = target_slot
        self.target_pos = target_pos

    def __repr__(self):
        return f"Action({self.action_type}, obj={self.obj}, slot={self.target_slot})"
    
    def to_dict(self):
        return {
            "type": self.action_type.value,
            "obj": self.obj,
            "target_slot":self.target_slot,
            "target_pos": self.target_pos
        }
    
    @staticmethod
    def from_dict(d:dict):
        return Action(
            action_type=ActionType(d["type"]),
            obj=d.get("obj"),
            target_slot=d.get("obj"),
            target_pos = list(d["target_pos"]) if d.get("target_pose") else None
        )

class ActionSet:
    """
    Central descrete Action set for RL and BT
    """
    def __init__(self,goal_objects,obstacle_objects,shop_slots:dict,goal_slots:dict):
        self.goal_objects = goal_objects
        self.obstacle_objects = obstacle_objects
        self.all_objects = goal_objects + obstacle_objects
        self.shop_slots = shop_slots
        self.goal_slots = goal_slots

        self.actions = self._generate_actions()

    def _generate_actions(self):
        actions=[]

        #Pick: pick any movable object
        for obj in self.all_objects:
            actions.append(Action(ActionType.PICK,obj=obj))
        
        #Place: place goal_objects or obstacles on goal or shop
        for obj in self.all_objects:
            for slot_id,pos in self.shop_slots.items():
                actions.append(Action(ActionType.PLACE,obj=obj,target_slot=slot_id,target_pos=pos))
            for slot_id,pos in self.goal_slots.items():
                actions.append(Action(ActionType.PLACE,obj=obj,target_slot=slot_id,target_pos=pos))

        return actions
    
    def get_action(self,index):
        return self.actions[index]
    
    def get_index(self,action):
        return self.actions.index(action)
    
    def num_actions(self):
        return len(self.actions)
    
    def get_all_actions(self):
        return self.actions
    
    def valid_actions(self,state):
        """
        Returns a list of valid actions for given state
        """
        valid_indices =[]
        valid_actions = []
        for idx,action in enumerate(self.actions):
            place_slot = action.target_slot

            #Rule 1: place actions are only valid if holding if holding:obj
            if action.action_type == ActionType.PLACE and state['gripper_status']['holding'] is not action.obj:
                continue

            #Rule 2: pick actions can only be valid if holding:None
            if action.action_type == ActionType.PICK and state['gripper_status']['holding'] is not None:
                continue
            #Rule 3: place slot has to be empty (if there is obstacle pick action for obstalce will later make it empty)
            if action.action_type == ActionType.PLACE and action.target_slot in state['object_slots'].values():
                continue
            #Rule 3: (optional) Can prevent no-op 

            valid_actions.append(action)
            valid_indices.append(idx)
        return valid_actions, valid_indices

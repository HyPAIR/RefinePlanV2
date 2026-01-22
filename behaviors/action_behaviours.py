import py_trees
from rl.action_space import Action,ActionType
from state.slot_config import GOAL_SLOTS

class Pick(py_trees.behaviour.Behaviour):
    def __init__(self,name,obj_name,blackboard):
        super().__init__(name)
        self.obj_name = obj_name
        self.blackboard = blackboard
        self.started = False

    def update(self):
        print(f"[BT] Trying to pick {self.obj_name}")
        action = Action(
            action_type=ActionType.PICK,
            obj=self.obj_name
        )

        if not self.started:
            self.blackboard.current_action =action
            self.started = True
            return py_trees.common.Status.RUNNING
        else:
            if self.blackboard.current_action is None:
                return py_trees.common.Status.SUCCESS
            else:
                return py_trees.common.Status.RUNNING




class Place(py_trees.behaviour.Behaviour):
    """
    Behaviour node for place designed as a simple FSM(finite-state machine)
    with started and not-started sates based on current action as input
    """
    def __init__(self,name, obj_name, target_slot, blackboard):
        super().__init__(name)
        self.obj_name = obj_name
        self.target_slot = target_slot
        self.blackboard = blackboard
        self.started = False
    
    def update(self):
        print(f"[BT] Trying to place {self.obj_name} at {self.target_slot}")
        action = Action(
            action_type=ActionType.PLACE,
            obj=self.obj_name,
            target_slot=self.target_slot,  
            target_pos=GOAL_SLOTS[self.target_slot]
        )

 
        if not self.started:
            self.blackboard.current_action = action
            self.started = True
            return py_trees.common.Status.RUNNING
        else:
            if self.blackboard.current_action is None:
                return py_trees.common.Status.SUCCESS
            else:
                return py_trees.common.Status.RUNNING
            

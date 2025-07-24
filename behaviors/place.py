import py_trees
from rl.action_space import Action,ActionType

class Place(py_trees.behaviour.Behaviour):
    def __init__(self,name, obj_name, target_slot, blackboard):
        super().__init__(name)
        self.obj_name = obj_name
        self.target_slot = target_slot
        self.blackboard = blackboard
    
    def update(self):
        print(f"[BT] Trying to place {self.obj_name} at {self.target_slot}")
        action = Action(
            action_type=ActionType.PLACE,
            obj=self.obj_name,
            target_slot=self.target_slot
        )
        self.blackboard.current_action = action
        return py_trees.common.Status.SUCCESS
import py_trees
from rl.action_space import Action,ActionType

class Pick(py_trees.behaviour.Behaviour):
    def __init__(self,name,obj_name,blackboard):
        super().__init__(name)
        self.obj_name = obj_name
        self.blackboard = blackboard

    def update(self):
        print(f"[BT] Trying to pick {self.obj_name}")
        action = Action(
            action_type=ActionType.PICK,
            obj=self.obj_name
        )
        self.blackboard.current_action = action
        return py_trees.common.Status.SUCCESS
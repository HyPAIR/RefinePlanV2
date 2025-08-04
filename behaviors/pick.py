import py_trees
from rl.action_space import Action,ActionType

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

    
import py_trees
from state.scene_state import SceneState

class IsGoalAchieved(py_trees.behaviour.Behaviour):
    def __init__(self, name,scene_state:SceneState):
        super().__init__(name)
        self.scene_state = scene_state

    def update(self):
        self.scene_state.update()
        if self.scene_state.is_goal_achieved():
            print(f"[BT] Goal Acieved!")
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE
import py_trees
from state.scene_state import SceneState

class IsObstacleOnGoal(py_trees.behaviour.Behaviour):
    '''
    Succeeds if no obstacle on goal
    '''
    def __init__(self,name, scene_state:SceneState, obstacle_name):
        super().__init__(name)
        self.scene_state = scene_state
        self.obstacle_name = obstacle_name

    def update(self):
        self.scene_state.update()
        goal_region = self.scene_state.goal_region_occuppancy
        if self.obstacle_name in goal_region.values():
            print(f"[BT] Obstacle {self.obstacle_name} is on a goal")
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE
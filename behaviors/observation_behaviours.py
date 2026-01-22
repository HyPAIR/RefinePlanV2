import py_trees
from state.scene_state import SceneState

class IsObjectOnGoal(py_trees.behaviour.Behaviour):
    '''
    Succeeds if object on goal
    '''
    def __init__(self,name, scene_state:SceneState, object_name):
        super().__init__(name)
        self.scene_state = scene_state
        self.object_name = object_name

    def update(self):
        self.scene_state.update()
        goal_region = self.scene_state.goal_region_occupancy
        if self.object_name in goal_region.values():
            print(f"[BT] object {self.object_name} is on a goal")
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

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
        
class IsObjectHeld(py_trees.behaviour.Behaviour):
    '''
    Succeeds if object is held by gripper
    '''
    def __init__(self,name, scene_state:SceneState, object_name):
        super().__init__(name)
        self.scene_state = scene_state
        self.object_name = object_name

    def update(self):
        self.scene_state.update()
        holding_obj = self.scene_state.gripper_status["holding"]
        if holding_obj == self.object_name:
            print(f"[BT] object {self.object_name} is held by gripper")
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE
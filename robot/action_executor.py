from rl.action_space import ActionType, Action
from robot.robot_interface import RoboticsEnvironment
class ActionExecutor:
    def __init__(self,robot_interface:RoboticsEnvironment):
        self.robot = robot_interface
        self.last_result = None
    
    def execute(self,action:Action):
        """
        Executes the given action on the robot interface. Return true if the action was successful, false otherwise.
        """
        if action.action_type == ActionType.PICK:
            success = self._pick(action.obj)
        elif action.action_type == ActionType.PLACE:
            success = self._place(action.obj,action.target_pos)
        else:
            print(f"[WARN] Unknown action type: {action.action_type}")
            success = False

        self.last_result = success
        return success
    
    def _pick(self,obj):
        print(f"[EXEC] Picking {obj}")
        return self.robot.pick(obj)
    
    def _place(self,obj,pos):
        print(f"[EXEC] Placing {obj} at {pos}")
        return self.robot.place(obj, pos)
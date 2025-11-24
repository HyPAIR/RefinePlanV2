from rl.action_space import ActionType, Action,GraspType
from robot.robot_interface import RoboticsEnvironment
from state.slot_config import GOAL_SLOTS,SHOP_SLOTS
import time
import numpy as np

ALL_SLOTS={**GOAL_SLOTS,**SHOP_SLOTS}
class ActionExecutor:
    def __init__(self,robot_interface:RoboticsEnvironment):
        self.robot = robot_interface
        self.last_result = None
    
    def _pick(self, obj, grasp: GraspType = None):
        # Default to top grasp if None
        grasp_value = grasp.value if isinstance(grasp, GraspType) else "top_0"
        print(f"[EXEC] Picking {obj} with {grasp_value}")
        return self.robot.pick(obj, grasp_value)


    def _place(self, obj, pos,grasp):
        grasp_value = grasp.value if isinstance(grasp,GraspType) else "top_0"
        print(f"[EXEC] Placing {obj} at {pos} with grasp {grasp_value}")
        return self.robot.place(obj, pos,grasp_value)
    
    def execute(self,action:Action):
        """
        Executes the given action on the robot interface. Return true if the action was successful, false otherwise.
        """
        start_time = time.time()
        if action.action_type == ActionType.PICK:
            success,duration = self._pick(action.obj, action.grasp)
        elif action.action_type == ActionType.PLACE:
            if action.obj == None or action.target_pos is None:
                print(f"[ERROR] PLACE action requires obj and target_pos to be specified.")
                return 0, 0.0
            success,duration = self._place(action.obj, action.target_pos,action.grasp)
        else:
            print(f"[WARN] Unknown action type: {action.action_type}")
            success = False
            duration = np.inf

        self.last_result = success
        end_time = time.time()
        execution_time = duration
        print(f"[EXEC] Action {action.action_type} executed in {end_time - start_time:.2f} seconds")
        if not success:
            print(f"[ERROR] Action {action.action_type} failed for object {action.obj}")
        else:
            print(f"[SUCCESS] Action {action.action_type} succeeded for object {action.obj}")
        # Return success status
        return success, execution_time

    def create_action_from_option(self,option_name:str,motion_param:str)->Action:
        """
        Create an Action object from an option name and motion parameter.
        Example option names:
            pick_column0
            place_column0_region_1
        """ 
        parts = option_name.split("_")
        if parts[0] == "pick":
            obj = "_".join(parts[1:])
            return Action(
                action_type=ActionType.PICK,
                obj=obj,
                target_slot=None,
                target_pos=None,
                grasp=GraspType(motion_param)
            )
        elif parts[0] == "place":
            obj = parts[1]
            target_slot = "_".join(parts[2:])
            # For simplicity, we will set target_pos to None here. In a real scenario, you would look up the position.
            return Action(
                action_type=ActionType.PLACE,
                obj=obj,
                target_slot=target_slot,
                target_pos=None,  # This should be replaced with actual position lookup
                grasp=GraspType(motion_param)
            )
        else:
            raise ValueError(f"Unknown option name: {option_name}")
    
    def policy_action_to_executor_action(self,policy_action:str,state)->Action:
        """
        Convert a policy action to an executor action. This is a placeholder for any necessary conversion.
        In this case, we assume they are the same.
        """
        policy_action_type,policy_action_target,policy_action_grasp = policy_action.split('.')
        if policy_action_type =='pick':
            executor_action = Action(
                action_type= ActionType.PICK,
                obj='/'+policy_action_target,
                target_slot=None,
                target_pos=None,
                grasp=GraspType(policy_action_grasp)
            )
        else:
            executor_action = Action(
                action_type= ActionType.PLACE,
                obj=state['holding'],
                target_slot=policy_action_target,
                target_pos=ALL_SLOTS['/'+policy_action_target],
                grasp=GraspType(policy_action_grasp)
            )
        return executor_action
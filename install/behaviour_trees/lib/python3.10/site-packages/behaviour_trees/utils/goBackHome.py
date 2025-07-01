import py_trees_ros
from simulation.config_planning import RoboticsEnvironment
from action_interfaces.action import GoBackHome as GH

class GoBackHome(py_trees_ros.actions.ActionClient):
    def __init__(self,name="Homing action"):
        goal = GH.Goal()
        goal.pose = [0,0]
        super().__init__(
            name=name,
            action_type=GH,
            action_name='/goBackHome',
            action_goal=goal
        )

    def result_callback(self, result_msg):
        result = result_msg.result
        status = result_msg.status

        print(f"[Result Status] {status} ({GoalStatus.to_string(status)})")

        # Optional: print result content too
        print(f"[Result Data] {result.sequence}")

        # Important: call the super() to ensure SUCCESS/FAILURE is set
        super().result_callback(result_msg)

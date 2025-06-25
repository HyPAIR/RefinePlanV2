import py_trees
import py_trees_ros.actions
from example_interfaces.action import Fibonacci

from action_msgs.msg import GoalStatus  # Built-in ROS 2 status enum

class SendFibonacciGoal(py_trees_ros.actions.ActionClient):
    def __init__(self, name="Fibonacci Action"):
        # Build a goal message
        goal = Fibonacci.Goal()
        goal.order = 5

        super().__init__(
            name=name,
            action_type=Fibonacci,
            action_name="/fibonacci",
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

import py_trees
import py_trees_ros.actions
from example_interfaces.action import Fibonacci

from action_msgs.msg import GoalStatus  # Built-in ROS 2 status enum

class SendFibonacciGoal(py_trees_ros.actions.ActionClient):
    def __init__(self, name="FibonacciFromBB"):
        self.goal = Fibonacci.Goal()
        self.feedback = None
        super().__init__(
            name=name,
            action_type=Fibonacci,
            action_name="/fibonacci",
            action_goal=self.goal
        )
        self.blackboard = self.attach_blackboard_client(name="BB")
        self.blackboard.register_key(key="fibonacci_order", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="fibonacci_result", access=py_trees.common.Access.WRITE)

    def initialise(self):
        # Read dynamic goal from blackboard
        goal = self.goal
        goal.order = self.blackboard.fibonacci_order
        self.send_goal_request(goal)

    def update(self):
        if self.feedback is not None:
            print(f"[Feedback] Partial Sequence: {self.feedback.partial_sequence}")

        if self.status is py_trees.common.Status.RUNNING:
            return py_trees.common.Status.RUNNING
        elif self.status == py_trees.common.Status.SUCCESS:
            self.blackboard.fibonacci_result = self.result.sequence
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


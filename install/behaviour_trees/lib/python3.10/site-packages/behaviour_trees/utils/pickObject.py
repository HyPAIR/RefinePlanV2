import py_trees
from rclpy.action import ActionClient
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from action_interfaces.action import PickObject
from simulation.config_planning import RoboticsEnvironment


class SetPickTarget(Behaviour):
    def __init__(self,name="SetPickTaraget",blackboard_key="pick_goal"):
        super(SetPickTarget,self).__init__(name=name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.blackboard_key = blackboard_key
    def setup(self, **kwargs):
        return True
    def initialise(self):
        pass
    def update(self):
        
        goal = PickObject.Goal()
        approachIKTr = [ 0,0,-0.10, 0, 0, 0, 1]
        withdrawIKTr= [0,0,0.10, 0, 0, 0, 1]
        #column 0 for dummy pick
        col0Pose = [0.1999999999999999, 0.9750000000000015, 0.55, 4.447461232170236e-18, 8.658293534037561e-18, 0.0, 1.0]
        col0Pose = [0.6250000000000001, 0.7000000000000013, 0.55, 4.447461232170236e-18, 8.658293534037561e-18, 0.0, 1.0]
        col0Pose[2] +=0.125
        goal_pose = col0Pose+approachIKTr+withdrawIKTr
        print(f"Goal Pose: {goal_pose}")
        goal.pose =[float(x) for x in goal_pose]
        self.blackboard.set(self.blackboard_key,goal)
        self.logger.info(f'[setpickTaret] set goal for col0 at: {goal.pose}')
        return Status.SUCCESS

    #get the object pose from object
    #get object type from object 
    #sample grasp for object
    #caluclate approacn and withdraw transform based on object type and grasp
    #create combined pose vector
    #call the ros action client

class PickObjectBehaviour(Behaviour):
    def __init__(self,  node, pose):
        super(PickObjectBehaviour,self).__init__('pickObjectBehaviour')
        self.node = node
        self.pose = pose
        self.client = ActionClient(self.node, PickObject, 'pickObject')
        self.goal_handle = None
        self.result_future = None
        self.result = None

    def setup(self, timeout=5,**kwargs):
        if not self.client.wait_for_server(timeout_sec=timeout):
            self.logger.error("PickObject action server not available")
            return False
        return True

    def initialise(self):
        goal_msg = PickObject.Goal()
        goal_msg.pose = self.pose

        self.logger.info("Sending PickObject goal...")
        send_goal_future = self.client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.logger.error("PickObject goal rejected")
            self.result = False
            return

        self.logger.info("PickObject goal accepted")
        self.result_future = self.goal_handle.get_result_async()
        self.result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        self.result = future.result().result.success
        self.logger.info(f"PickObject result: {self.result}")

    def update(self):
        if self.result is None:
            return Status.RUNNING
        elif self.result:
            return Status.SUCCESS
        else:
            return Status.FAILURE

    def terminate(self, new_status):
        self.logger.debug(f"Terminating with status: {new_status}")
        self.result = None

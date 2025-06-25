from simulation.config_planning import RoboticsEnvironment
import rclpy
from rclpy.action import ActionClient

class GoToPose:
    '''
    Action client to go to a particular pose in env
    '''
    def __init__(self,env:RoboticsEnvironment,pose):
        self.env = env
        self.target_pose = pose
    def execute(self):
        self.env.action_go_to(self.target_pose)
    
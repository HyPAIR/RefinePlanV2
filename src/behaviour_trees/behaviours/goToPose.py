from simulations.sim_interface import RoboticsEnvironment

class GoToPose:
    def __init__(self,env:RoboticsEnvironment,pose):
        self.env = env
        self.target_pose = pose
    def execute(self):
        self.env.action_go_to(self.target_pose)
    
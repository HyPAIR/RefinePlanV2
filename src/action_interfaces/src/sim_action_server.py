import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from simulations.sim_interface import RoboticsEnvironment

from action_interfaces.action import GoBackHome

class SimActionServer(Node):
    '''
    Action server to provide all robot actions from coppeliaSim to ros env
    '''
    def __init__(self):
        super().__init__('sim_action_server')
        #setup connection to sim
        self.env = RoboticsEnvironment()
        self.env.connect()
        self.env.initialize_params()
        self.initConfig = self.env.getConfig()

        #setup action servers for actions
        self._go_back_home_server = ActionServer(
            self,

        )

    async def go_back_home_callback():
        pass
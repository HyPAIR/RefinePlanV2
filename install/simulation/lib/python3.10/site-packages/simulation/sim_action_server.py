import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from simulation.config_planning import RoboticsEnvironment
from action_interfaces.action import GoBackHome,GoToPose,PickObject,PlaceObject

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
            GoBackHome,
            'goBackHome',
            self.go_back_home_callback
        )
        self._go_to_pose_server = ActionServer(
            self,
            GoToPose,
            'goToPose',
            self.go_to_pose_callback
        )
        self._pick_object_server = ActionServer(
            self,
            PickObject,
            'pickObject',
            self.pick_object_callback
        )
        self._place_object_server = ActionServer(
            self,
            PlaceObject,
            'placeObject',
            self.place_object_callback
        )

    #Define callback functions

    async def go_back_home_callback(self,goal_handle):
        self.get_logger().info('Executing homing callback')
        #move to home pose
        pathbackHome =self.env.findPath(self.initConfig)
        self.get_logger().info('going to home config')
        # self.env.followPath(pathbackHome)
        goal_handle.succeed()
        result = GoBackHome.Result()
        result.success = True
        return result
    
    async def go_to_pose_callback(self,goal_handle):
        self.get_logger().info('Executing go to pose callback')
        combinedRequest = list(goal_handle.request.pose)
        pickPose = combinedRequest[:7]
        approachDummy=combinedRequest[7:14]
        withdrawDummy = combinedRequest[14:21]
        feedback = GoToPose.Feedback()
        feedback.currentpose = self.env.getTipPose()
        self.get_logger().info(f'recived target {pickPose}')
        outcome = self.env.ActionPick(
                                    pickPose=pickPose,
                                    approachIKTr=approachDummy,
                                    withdrawIktr=withdrawDummy
                                      )
        goal_handle.publish_feedback(feedback)
        result = GoToPose.Result()
        goal_handle.succeed()
        if outcome:
            result.success=True
        else:
            result.success=False
        return result
    
    async def pick_object_callback(self,goal_handle):
        self.get_logger().info('Executing pick object callback')
        combinedRequest = list(goal_handle.request.pose)
        pickPose = combinedRequest[:7]
        approachDummy=combinedRequest[7:14]
        withdrawDummy = combinedRequest[14:21]
        feedback = PickObject.Feedback()
        feedback.currentpose = self.env.getTipPose()
        self.get_logger().info(f'recived target {pickPose}')
        outcome =self.env.ActionPick(
                                    pickPose=pickPose,
                                    approachIKTr=approachDummy,
                                    withdrawIktr=withdrawDummy
                                    )
        goal_handle.publish_feedback(feedback)
        result = PickObject.Result()
        self.get_logger().info(f'outcome: {outcome}')

        if outcome:
            result.success=True
            goal_handle.succeed()
        else:
            result.success=False
            goal_handle.abort()

        return result
    
    async def place_object_callback(self,goal_handle):
        pass
    
def main(args=None):
    rclpy.init(args=args)
    sim_action_server = SimActionServer()
    rclpy.spin(sim_action_server)

if __name__=='__main__':
    main()
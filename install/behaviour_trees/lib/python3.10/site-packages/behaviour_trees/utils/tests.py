import rclpy
from rclpy.action import ActionClient
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from action_interfaces.action import PickObject

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



# import rclpy
# from rclpy.action import ActionClient
# from rclpy.node import Node
# from action_interfaces.action import PickObject

# class PickActionTestClient(Node):
#     def __init__(self):
#         super().__init__('pick_action_test_client')
#         self._action_client = ActionClient(self,PickObject,'pickObject')

#     def send_goal(self,pose):
#         goal_msg = PickObject.Goal()
#         goal_msg.pose = pose

#         self._action_client.wait_for_server()
#         self._send_goal_future = self._action_client.send_goal_async(goal_msg)
#         self._send_goal_future.add_done_callback(self.goal_response_callback)

#     def goal_response_callback(self,future):
#         goal_handle = future.result()
#         if not goal_handle.accepted:
#             self.get_logger().info('Goal rejected :(')
#             return
#         self.get_logger().info('Goal accepted :)')

#         self._get_result_future = goal_handle.get_result_async()
#         self._get_result_future.add_done_callback(self.get_result_callback)
    
#     def get_result_callback(self,future):
#         result = future.result().result
#         self.get_logger().info('Result: {0}'.format(result.success))
#         rclpy.shutdown()

# def main(args=None):
#     rclpy.init(args=args)

#     action_client = PickActionTestClient()
#     pose=[0.625, 0.699999988079071, 0.6499999761581421, 4.4474610540735425e-18, 8.65829385903649e-18, 0.0, 1.0,0,0,-0.10, 0, 0, 0, 1,0,0,0.10, 0, 0, 0, 1]
#     action_client.send_goal([float(x) for x in pose])
#     rclpy.spin(action_client)

# if __name__=='__main__':
#     main()
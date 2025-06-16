
import py_trees
import py_trees_ros
import rclpy

from rclpy.node  import Node
from std_srvs.srv import Trigger
from std_msgs.msg import String


class MainPlanner(Node):
    '''
    Class defining the main planner, handles action and service requests, creation of behaviour tree
    '''
    def __init__(self):
        super().__init__("")
        

        self.get_logger().info("Starting main planner node")

def generate_tree():
    root = py_trees.composites.Sequence("startSequence",memory=True)
    clearPlacingArea = py_trees.composites.Sequence("clearPlacingArea")
    pickPlaceObject = py_trees.composites.Sequence("pickAndPlace")
    return root

    

def main(args=None):
    rclpy.init(args=args)

    node = MainPlanner()
    global blackboard

    behaviour_tree = py_trees_ros.trees.BehaviourTree(generate_tree())
    behaviour_tree.setup(timeout=60)
    try:
        while rclpy.ok():
            rclpy.spin_once(node,timeout_sec=0.1)
            behaviour_tree.root.tick_once()
            status = behaviour_tree.root.status
            if status == py_trees.common.Status.SUCCESS:
                node.get_logger().info("Behaviour tree compiled successfully")
                py_trees.display.render_dot_tree(behaviour_tree.root)
                break
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()
    

if __name__ == '__main__':
    main()
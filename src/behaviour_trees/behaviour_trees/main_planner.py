
import py_trees
import py_trees_ros
import rclpy
import random
import rclpy.logging
from rclpy.node  import Node
from std_srvs.srv import Trigger
from std_msgs.msg import String
# from simulation.config_planning import RoboticsEnvironment
from behaviour_trees.utils.goBackHome import GoBackHome
from behaviour_trees.utils.fibLeaf import SendFibonacciGoal
from behaviour_trees.utils.pickObject import SetPickTarget, PickObjectBehaviour
from simulation.config_planning import RoboticsEnvironment
# from behaviour_trees.utils.tests import 
class MainPlanner(Node):
    '''
    Class defining the main planner, handles action and service requests, creation of behaviour tree
    '''
    def __init__(self):
        super().__init__("main_planner")
        

        self.get_logger().info("Starting main planner node")

def generate_tree(node:Node):
    root = py_trees.composites.Sequence("startSequence",memory=True)
    clearPlacingArea = py_trees.composites.Sequence("clearPlacingArea",memory=True)
    pickPlaceObject = py_trees.composites.Sequence("pickAndPlace",memory=True)
    parallelSelector = py_trees.composites.Parallel(name='setTargetParallelSelector',policy=py_trees.common.ParallelPolicy.SuccessOnOne,children=[])
    goBackHome = GoBackHome()
    fibLeaf = SendFibonacciGoal()
    setpicktarget = SetPickTarget()
    pose=[0.625, 0.699999988079071, 0.6499999761581421, 4.4474610540735425e-18, 8.65829385903649e-18, 0.0, 1.0,0,0,-0.10, 0, 0, 0, 1,0,0,0.10, 0, 0, 0, 1]
    pose =[float(x) for x in pose]
    pickobject= PickObjectBehaviour(node,pose)
    #add child sequnces to root
    root.add_children([setpicktarget,clearPlacingArea,pickobject,pickPlaceObject])
    return root
class Scene:
    def __init__(self,regions,targets,objects):
        self.env = RoboticsEnvironment()
        self.regions = [self.env.sim.getObject(handle) for handle in region_handles]
        self.targets = [self.env.sim.getObject(handle) for handle in target_handles]
        self.objects = [self.env.sim.getObject(handle) for handle in object_handles]

        self.state_map = dict()
    
'''
PROBLEM SETUP
'''
 #get all regions
region_handles = [f'/region_{i+1}' for i in range(9)]
#get all targets
target_handles = [f'/place_plate{i}' for i in range(6)]
#get all objects
object_handles =[
        '/column0',
        '/column1',
        '/column2',
        '/column3',
        '/Cuboid0',
        '/Cuboid1'   
    ]

def update_blackboard(env:RoboticsEnvironment):
    pass

def main(args=None):
    rclpy.init(args=args)
    env = RoboticsEnvironment()
    env.connect()
    env.GetTargetStats
    regions = [env.sim.getObject(handle) for handle in region_handles]
    targets = [env.sim.getObject(handle) for handle in target_handles]
    objects = [env.sim.getObject(handle) for handle in object_handles]
    node = MainPlanner()
    global blackboard
    blackboard = py_trees.blackboard.Client(name="provided")

    behaviour_tree = py_trees_ros.trees.BehaviourTree(generate_tree(node))
    behaviour_tree.setup(timeout=60)
    epsilon = 0.5
    # valid_actions=[SetPickTarget(),PickObjectBehaviour()]#, placeObjectBehaviour()] 
    try:
        while rclpy.ok():
            rclpy.spin_once(node,timeout_sec=0.1)
            #TODO:Update the state on blackboard
            update_blackboard(env)
            #Roll the dice to make a choice between the BT and random action
            p = 0.4 #random.random()
            if p < epsilon:
                #BT behaviour / Action Execution
                behaviour_tree.root.tick_once()
                status = behaviour_tree.root.status
                print(py_trees.display.unicode_tree(behaviour_tree.root, show_status=True))
                if status == py_trees.common.Status.SUCCESS:
                    node.get_logger().info("Behaviour tree compiled successfully")
                    py_trees.display.render_dot_tree(behaviour_tree.root)
                    break
                elif False and status == py_trees.common.Status.RUNNING:
                    while status==py_trees.common.Status.RUNNING:
                        rclpy.spin_once(node,timeout_sec=0.1)
                        behaviour_tree.root.tick_once()
                        status = behaviour_tree.root.status

            else:
            # Random action execution, based on epsilon greedy 
                # action = random.choice(valid_actions)
                # action.execute()
                print("Taking random action")

    except KeyboardInterrupt:
        pass

    rclpy.shutdown()
    

if __name__ == '__main__':
    main()
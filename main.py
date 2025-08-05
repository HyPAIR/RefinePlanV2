import time
import py_trees
import random
from robot.robot_interface import RoboticsEnvironment
from robot.action_executor import ActionExecutor
from state.scene_state import SceneState
from state.slot_config import GOAL_SLOTS,SHOP_SLOTS
from rl.transition_logger import TransitionLogger
from rl.reward_function import compute_reward
from rl.action_space import ActionSet
from trees.pick_place_tree import create_behaviour_tree


#Configurations
MAX_STEPS = 15#100
#these are objects to be picked up / manipulated
goal_objects = ["/column0","/column1","/column2","/column3"]
obstacle_objects=["/obs0","/obs1"]
shop_slots =[f"/region_{i}" for i in range(9)]
# goal_slots =[f"/goal_{i}" for i in range(5)]
goal_slots=["/goal_1","/goal_2","/goal_4","/goal_5"]
objects = goal_objects + obstacle_objects
initial_locations = [
    [0.5750000000000004, 0.7000000000000004, 0.5499999999999998],
    [0.3500000000000002, 0.7000000000000004, 0.5499999999999998],
    [0.30000000000000016, 0.9750000000000008, 0.5499999999999998],
    [0.5250000000000004, 0.8750000000000003, 0.5499999999999998], 
    [0.9000000000000006, 0.6249999999999993, 0.5499999999999999], 
    [0.8000076260094475, 0.9000043343419417, 0.5499999988422022]
    ]

initial_arm_config = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]

#Initialize modules
robot = RoboticsEnvironment()
robot.connect()
robot.initialize_params()
scene = SceneState(robot)
executor = ActionExecutor(robot)
logger = TransitionLogger()

#Reset the simulation
robot.reset_scene(objects,initial_locations,initial_arm_config)

scene.update()
state = scene.get_state()

###### BEHAVOUR TREE ######

#Init behaviour tree
tree = create_behaviour_tree(scene,goal_objects,obstacle_objects,shop_slots,goal_slots)
bt = py_trees.trees.BehaviourTree(tree)
bt.setup(timeout=3.0)
#Render the behaviout tree
py_trees.display.render_dot_tree(tree,with_blackboard_variables=True)

#setup the blackboard client for bt
blackboard = py_trees.blackboard.Client(name="bt")
blackboard.register_key(key="current_action",access=py_trees.common.Access.READ)
blackboard.register_key(key="current_action",access=py_trees.common.Access.WRITE)


###RANDOM ACION SET FOR RL ####
action_set = ActionSet(goal_objects=goal_objects,obstacle_objects=obstacle_objects,shop_slots=SHOP_SLOTS,goal_slots=GOAL_SLOTS)

#Episode loop
for step in range(MAX_STEPS):
    print(f"\n[INFO] Simulation action step: {step}")

    #Tick the BT
    bt.tick()
    action = blackboard.current_action
    print(py_trees.display.unicode_tree(tree,show_status=True))

    if action is None:
        print("[WARN] No action produced by BT")
        #Select a random action from the action set
        valid_actions,_ = action_set.valid_actions(state)
        if not valid_actions:
            print("[WARN] No valid actions available, skipping step")
            continue
        else:
            action = random.choice(valid_actions)
            print(f"[INFO] Randomly selected action: {action}")
            blackboard.current_action = action
        


    #Excecute action
    print(f"[INFO] Executing {action}")
    success = executor.execute(action)
    if success:
        blackboard.current_action = None
    
    #Observer next state and compute reward
    scene.update()
    next_state = scene.get_state()
    reward = compute_reward(state,action,next_state)
    done = scene.is_goal_achieved()


    #Log transition
    logger.log_transition(state, action, reward, next_state, done)
    print(f"[INFO] Success: {success} | Reward: {reward} | Done: {done}")
    if step == 99:
        print("[DEBUG]step stop")

    if done:
        print(f"\n[INFO] Goal Achieved in {step +1 } steps")
        #logger automatically saves episodes when done and resets
        break
    if step+2 >MAX_STEPS:
        print(f"\n[INFO] Max steps reached episode ended")
        logger.save_episode()
        logger.reset()

    state = next_state
#if loop ends save and reset the logger
if logger.episode:
    logger.save_episode()
    logger.reset()

robot.stop_simulation()
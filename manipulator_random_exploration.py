#!/usr/bin/env/ python3
"""
Refine plan v2 with exploration integrated in manipulator environment

Author: Mohammed Saleeq Kolleth
Owner: Mohammed Saleeq Kolleth
"""

from refine_plan.models.condition import EqCondition, AndCondition, OrCondition,NeqCondition
from refine_plan.algorithms.explore import synthesise_exploration_policy
from refine_plan.models.state_factor import StateFactor
from planned_actions import PLAN_1, PLAN_2, PLAN_3,PLAN_ALL_COMBOS, PLAN_CUSTOM
from robot.robot_interface import RoboticsEnvironment
from state.scene_state import SceneState
from rl.transition_logger import TransitionLogger
from rl.reward_function import compute_reward
from rl.action_space import ActionSet, GraspType,Action,ActionType
from state.slot_config import GOAL_SLOTS, SHOP_SLOTS
from robot.action_executor import ActionExecutor
from refine_plan.models.state import State
import random
import copy
import argparse
import time
# Define constants
collection_name ="random-exploration"
connection_string="mongodb://localhost:27017/"
goal_objects = ["/column0","/column1","/column2"]
shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]
objects_formatted =[obj.replace('/','') for obj in goal_objects] #Boolean conversion issue
EPISODE_LENGTH =30
EPISIDE_COUNT = 20
FAILSAFE_LIMIT = 6

def select_random_action(valid_actions,motion_params,picked_grasp=None):
        action = random.choice(valid_actions)
        #select a random motion param for the action
        if action.action_type.value == "pick":
            selected_motion_param = random.choice(motion_params["{}_{}".format(action.action_type.value,action.obj[1:])])
            picked_grasp = selected_motion_param
        else:
            selected_motion_param = random.choice(motion_params["{}_{}".format(action.action_type.value,action.target_slot[1:])])
            # selected_motion_param = picked_grasp #random.choice(motion_params["place"])
        print(f"Selected action: {action} with motion param: {selected_motion_param}")
        print("here")
        action.grasp = GraspType(selected_motion_param)
        return action ,picked_grasp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run random exploration in manipulator environment')
    parser.add_argument("-p", "--port", type=int, default=23000, 
                        help="The port to connect to (default: 23000)")
    args = parser.parse_args()
    print(f"Connecting to port {args.port}")
    #setup the initial state
    initial_locations =[[0.35, 0.8, 0.5625, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838],#region 0
                        [0.6, 1.075, 0.5625, 3.7923564988209e-08, 6.836504668418399e-08, -0.0009820818013717147, 0.9999995177575484],#region 1
                        [0.6, 0.8000057601488304, 0.5625, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838]#region 2
                        ]

    initial_arm_config = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]

    #Initialize modules
    robot = RoboticsEnvironment(port=args.port)
    robot.connect()
    robot.initialize_params()
    scene = SceneState(robot)
    executor = ActionExecutor(robot)
    random_logger = TransitionLogger(connection_string=connection_string,database_name="refine-plan-v2", collection_name=collection_name)

    #Reset the simulation
    robot.reset_scene(goal_objects,initial_locations,initial_arm_config,domain_randomization=True)

    scene.update()
    state = scene.get_state()

    #compile options
    option_names =[
        "pick_/column0","pick_/column1","pick_/column2",
        "place_/goal_0","place_/goal_1","place_/goal_2",
        "place_/region_0","place_/region_1","place_/region_2",
    ]

    #compile motion parameters
    motion_params={
        "pick_column0": ["top_0","left_0","right_0","front_270"],
        "pick_column1": ["top_0","left_0","right_0","front_270"],
        "pick_column2": ["top_0","left_0","right_0","front_270"],
        "place_goal_0": ["top_0","left_0","right_0","front_270"],#right_0 is physically not possible for goal 0 ? it seems to work
        "place_goal_1": ["top_0","left_0","right_0","front_270"],#left_0 is physically not possible for goal 1
        "place_goal_2": ["top_0","left_0","right_0","front_270"],
        "place_region_0": ["top_0","left_0","right_0","front_270"],#top_0,front_270,left_0 are physically not possible for region 0
        "place_region_1": ["top_0","left_0","right_0","front_270"],#top_0, right_0,front_270 are physically not possible for region 1
        "place_region_2": ["top_0","left_0","right_0","front_270"],#left_0 is physically not possible for region 2
    }
    ###RANDOM ACTION SET FOR EXPLORATION ####
    action_set = ActionSet(goal_objects=goal_objects,obstacle_objects=[],shop_slots=SHOP_SLOTS,goal_slots=GOAL_SLOTS)

    random_collection = True
    picked_grasp = None
    # --- CONFIGURATION FOR RANDOM BASELINE ---
    RANDOM_EPISODE_LENGTH = 100  # Double the length to allow for "stumbling"
    RANDOM_EPISODE_COUNT = 3  # Adjust to keep total steps (~600) consistent with MAX
    start_time = time.time()

    if random_collection:
        for run in range(RANDOM_EPISODE_COUNT):
            robot.reset_scene(goal_objects, initial_locations, initial_arm_config, domain_randomization=True)
            scene.update()
            state = scene.get_state()
            
            # Notice we use the longer length here
            for step in range(RANDOM_EPISODE_LENGTH):
                valid_actions, _ = action_set.valid_actions(state)
                
                # 1. No Failsafe: Let the random agent fail and learn from it
                action, _ = select_random_action(valid_actions, motion_params)
                success, exec_time = executor.execute(action)
                
                scene.update()
                next_state = scene.get_state()
                
                # 2. Log everything to build a complete model of the physics
                reward = compute_reward(state, action, next_state, exec_time)
                done = scene.is_goal_achieved()
                random_logger.log_transition(state, action, reward, next_state, done, exec_time)
                
                state = next_state
                if done:
                    break # Still exit if it accidentally wins!
    
        print(f"Time taken for random data collection: {time.time()-start_time} seconds")



    robot.stop_simulation()

        
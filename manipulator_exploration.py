#!/usr/bin/env/ python3
"""
Refine plan v2 with exploration integrated in manipulator environment

Author: Mohammed Saleeq Kolleth
Owner: Mohammed Saleeq Kolleth
"""

from refine_plan.models.condition import EqCondition, AndCondition, OrCondition,NeqCondition
from refine_plan.algorithms.explore import synthesise_exploration_policy
from refine_plan.models.state_factor import StateFactor
from robot.robot_interface import RoboticsEnvironment
from state.scene_state import SceneState
from rl.transition_logger import TransitionLogger
from rl.reward_function import compute_reward
from rl.action_space import ActionSet
from state.slot_config import GOAL_SLOTS, SHOP_SLOTS
from robot.action_executor import ActionExecutor
from refine_plan.models.state import State
import random

goal_objects = ["/column0","/column1","/column2","/column3"]
obstacle_objects=["/obs0","/obs1"]
shop_slots =[f"/region_{i}" for i in range(9)]
goal_slots=["/goal_1","/goal_2","/goal_4","/goal_5"]
objects = goal_objects + obstacle_objects



def _get_enabled_cond(sf_list, option):
    """Get the enabled condition for an option.

    Args:
        sf_list: The list of state factors
        option: The option we want the condition for

    Returns:
        The enabled condition for the option
    """
    #we need to define the enabled conditions for the options as boolean condition expressions based on state factors
    sf_dict = {sf.get_name(): sf for sf in sf_list}
    enable = OrCondition()
    #Rule 1: place actions are only valid if holding if holding:obj place slot has to be empty
    if option[:5] == "place":
        enable = AndCondition(NeqCondition(sf_dict["holding"], "None"), EqCondition(sf_dict[option[6:]], "None"))

    #Rule 2: pick actions can only be valid if holding:None
    if option[:4] == "pick":
        enable = EqCondition(sf_dict["holding"], "None")

    return enable

def build_exploration_policy(connection_str,initial_state):
    """Run the exploration algorithm to synthesise a policy

    Args:
        connection_str: The MongoDB connection String

    Returns:
        The exploration policy
    """
    #need to create statefactors for PRISM conversion
    """
    combination of state factos is what makes a state in manuplator domain
    state:
        - goal_region_occuppancy
        - gripper_status
        x object_poses (Discarded for policy)
        - object_slots  
        x object_status (Discarded for policy)

    """
    #goal region occupancy
    #goal could be not filled, filled with objects
    goal_region_sfs = [StateFactor(goal_region,objects+["None"]) for goal_region in goal_slots]

    #shop region state factors, filled with objects or None
    shop_region_sfs = [StateFactor(shop_region,objects+["None"]) for shop_region in shop_slots]

    #gripper state factors
    #gripper can hold all objects
    gripper_sfs = [StateFactor("holding",objects+["None"])]

    #object and obstacle state factos # object slots in data
    possible_slots = goal_slots+shop_slots+["held","unknown"]
    object_sfs = [StateFactor(obj,possible_slots) for obj in objects]

    #compile state factor list    
    sf_list = goal_region_sfs + gripper_sfs + object_sfs + shop_region_sfs

    #compile options
    option_names =[
        "pick_/column0","pick_/column1","pick_/column2","pick_/column3",
        "pick_/obs0","pick_/obs1",
        "place_/goal_1","place_/goal_2","place_/goal_4","place_/goal_5",
        "place_/region_0","place_/region_1","place_/region_2","place_/region_3",
        "place_/region_4","place_/region_5","place_/region_6","place_/region_7","place_/region_8"
    ]

    #compile motion parameters
    motion_params={
        "pick":["top_0","top_90","top_180","top_270","front_0","front_180","back_0","back_180","left_0","left_180","right_0","right_180"],
        "place":["top_0","top_90","top_180","top_270","front_0","front_180","back_0","back_180","left_0","left_180","right_0","right_180"]
    }

    enabled_conds = {}
    for option in option_names:
        enabled_conds[option] = _get_enabled_cond(sf_list,option)
    #define_initial state as a state object
    goal_region_sfs_dict = {sf:"None" for sf in goal_region_sfs}
    gripper_sfs_dict = {sf:"None" for sf in gripper_sfs}
    object_sfs_dict = {sf:"unknown" for sf in object_sfs}
    for obj,slot in initial_state["object_slots"].items():
        sf = next((s for s in object_sfs if s.get_name() == obj),None)
        if sf:
            object_sfs_dict[sf]=slot
    initial_state_dict = {**goal_region_sfs_dict, **gripper_sfs_dict, **object_sfs_dict}    
    initial_state = State(initial_state_dict)
    exploration_policy = synthesise_exploration_policy(
        connection_str=connection_str,
        db_name="robotics",
        collection_name="exploration",
        sf_list=sf_list,
        option_names=option_names,
        ensemble_size=10,
        horizon=100,
        enabled_conds=enabled_conds,
        initial_state=initial_state,
        use_storm=False,
        motion_params=motion_params,
        )
    return exploration_policy

if __name__ == "__main__":
    #setup the initial state
    initial_locations = [
                            [0.5750525244646281, 0.7000668518820146, 0.6249999978830472],
                            [0.5253616900698888, 0.8750959753242942, 0.6249999976307693],
                            [0.30003665512633365, 0.9750314041860764, 0.6249999938207642], 
                            [0.7500341522349177, 0.9999783907620676, 0.6249999916882001], 
                            [0.3500353556499841, 0.8507616060759815, 0.7499999224994444], 
                            [0.8000297171903081, 0.8999871961360432, 0.5499999960678859]
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

    #Run 3 pilot runs to have seed data for exploration and save them to the database
    
    #compile options
    option_names =[
        "pick_/column0","pick_/column1","pick_/column2","pick_/column3",
        "pick_/obs0","pick_/obs1",
        "place_/goal_1","place_/goal_2","place_/goal_4","place_/goal_5",
        "place_/region_0","place_/region_1","place_/region_2","place_/region_3",
        "place_/region_4","place_/region_5","place_/region_6","place_/region_7","place_/region_8"
    ]

    #compile motion parameters
    motion_params={
        "pick":["top_0","top_90","top_180","top_270","front_0","front_180","back_0","back_180","left_0","left_180","right_0","right_180"],
        "place":["top_0","top_90","top_180","top_270","front_0","front_180","back_0","back_180","left_0","left_180","right_0","right_180"]
    }
    ###RANDOM ACION SET FOR RL ####
    action_set = ActionSet(goal_objects=goal_objects,obstacle_objects=obstacle_objects,shop_slots=SHOP_SLOTS,goal_slots=GOAL_SLOTS)

    def pick_random_action(option_name,motion_params):

            #for now we will select this completely at random not epsilon greedy with BT
            selected_option = random.choice(option_name)
            #if option starts with pick selecta a random pick motion parameter else select a random place motion parameter
            if selected_option.startswith("pick"):
                selected_motion_param = random.choice(motion_params["pick"])
            else:
                selected_motion_param = random.choice(motion_params["place"])
            print(f"Selected option: {selected_option} with motion param: {selected_motion_param}")
            action = executor.create_action_from_option(selected_option,selected_motion_param)
            return action
    n_runs = 3
    for run in range(n_runs):
        print(f"Pilot run {run}")
        #execute 5 random actions
        for step in range(5):
            print(f"Step {step}")
            action = pick_random_action(option_name=option_names,motion_params=motion_params)
            #check if the picked action is valid if not pick again till it is
            while action not in action_set.valid_actions(state)[0]:
                print(f"Invalid action: {action}, picking again")
                action = pick_random_action(option_name=option_names,motion_params=motion_params)
            success,exec_time = executor.execute(action)
            if not success:
                print("Action failed, stopping")
                break
            #update the scene state
            state = scene.get_state()
            scene.update()
            next_state = scene.get_state()
            reward = compute_reward(state,action,next_state)
            done = scene.is_goal_achieved()
            #log the transition
            logger.log_transition(state,action,reward,next_state,done,exec_time)
        print("Pilot run finished, resetting scene")
        robot.reset_scene(objects,initial_locations,initial_arm_config)
        scene.update()
        state = scene.get_state()


    policy = build_exploration_policy("mongodb://localhost:27017/",state)

    print("Exploration policy built")
    #execute the exploration policy
    for step in range(5):
        print(f"Step {step}")
        action = policy.get_next_action(state)
        print(f"Action: {action}")
        if action is None:
            print("No action found, stopping")
            break
        success = executor.execute(action)
        if not success:
            print("Action failed, stopping")
            break
        #update the scene state
        scene.update()
        state = scene.get_state()
        #log the transition
        logger.log_transition(state, action, success)
    print("Exploration finished")
    robot.stop_simulation()

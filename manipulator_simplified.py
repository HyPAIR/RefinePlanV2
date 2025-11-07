#!/usr/bin/env/ python3
"""
Refine plan v2 with exploration integrated in manipulator environment

Author: Mohammed Saleeq Kolleth
Owner: Mohammed Saleeq Kolleth
"""

from refine_plan.models.condition import EqCondition, AndCondition, OrCondition,NeqCondition
from refine_plan.algorithms.explore import synthesise_exploration_policy
from refine_plan.models.state_factor import StateFactor
from planned_actions import PLAN_1
from robot.robot_interface import RoboticsEnvironment
from state.scene_state import SceneState
from rl.transition_logger import TransitionLogger
from rl.reward_function import compute_reward
from rl.action_space import ActionSet, GraspType
from state.slot_config import GOAL_SLOTS, SHOP_SLOTS
from robot.action_executor import ActionExecutor
from refine_plan.models.state import State
import random
import copy

goal_objects = ["/column0","/column1","/column2","/column3"]
obstacle_objects=["/obs1"]#"/obs0",
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
    #Rule 1: place actions are only valid if holding:obj and place slot has to be empty
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
        "pick_/obs1",#"pick_/obs0",
        "place_/goal_1","place_/goal_2","place_/goal_4","place_/goal_5",
        "place_/region_0","place_/region_2","place_/region_3",#"place_/region_1",
        "place_/region_4","place_/region_5","place_/region_6","place_/region_7","place_/region_8"
    ]

    #compile motion parameters
    motion_params={
        "pick":["top_0","top_90","top_180","top_270","left_0","left_180","right_0","right_180"],
        "place":["top_0","top_90","top_180","top_270","left_0","left_180","right_0","right_180"]
    }

    enabled_conds = {}
    for option in option_names:
        enabled_conds[option] = _get_enabled_cond(sf_list,option)
    #define_initial state as a state object
    goal_region_sfs_dict = {sf:"None" for sf in goal_region_sfs}
    shop_region_sfs_dict = {sf:"None" for sf in shop_region_sfs}    
    gripper_sfs_dict = {sf:"None" for sf in gripper_sfs}
    object_sfs_dict = {sf:"unknown" for sf in object_sfs}
    for obj,slot in initial_state["object_slots"].items():
        sf = next((s for s in object_sfs if s.get_name() == obj),None)
        if sf:
            object_sfs_dict[sf]=slot
    initial_state_dict = {**goal_region_sfs_dict, **gripper_sfs_dict, **object_sfs_dict, **shop_region_sfs_dict}    
    initial_state = State(initial_state_dict)
    exploration_policy = synthesise_exploration_policy(
        connection_str=connection_str,
        db_name="refine-plan-v2",
        collection_name="manipulator-exploration-data",
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

def pick_random_action(option_name,motion_params):

            #for now we will select this completely at random not epsilon greedy with BT
            selected_option = random.choice(option_name)
            #if option starts with pick selecta a random pick motion parameter else select a random place motion parameter
            if selected_option.startswith("pick"):
                selected_motion_param = random.choice(motion_params["pick"])
                picked_grasp = selected_motion_param
            else:
                selected_motion_param =picked_grasp # random.choice(motion_params["place"])
            print(f"Selected option: {selected_option} with motion param: {selected_motion_param}")
            action = executor.create_action_from_option(selected_option,selected_motion_param)
            return action
def select_random_action(valid_actions,motion_params,picked_grasp=None):
        action = random.choice(valid_actions)
        #select a random motion param for the action
        if action.action_type.value == "pick":
            selected_motion_param = random.choice(motion_params["pick"])
            picked_grasp = selected_motion_param
        else:
            selected_motion_param = picked_grasp #random.choice(motion_params["place"])
        print(f"Selected action: {action} with motion param: {selected_motion_param}")
        print("here")
        action.grasp = GraspType(selected_motion_param)
        return action ,picked_grasp

if __name__ == "__main__":
    #setup the initial state
    initial_locations =[[0.34998767538500297, 0.8500032648466329, 0.6249999912820565, 1.4567442500551277e-07, 7.398154799781017e-09, 4.370202318115802e-05, 0.999999999045056],#column0
                        [0.5249742412435867, 0.8751135208928311, 0.6249999984821841, 3.7923564988208997e-08, 6.836504668418398e-08, -0.0009820818013717147, 0.9999995177575485],#column1
                        [0.300003473985302, 0.9750057601488298, 0.6249999972840121, 3.071012527623133e-08, 2.2171811830454323e-08, 1.83856228637147e-05, 0.9999999998309839],#column2
                        #[0.575011431638082, 0.6999800182034377, 0.7499998801076886, -6.055639648183646e-06, 7.510927698140023e-07, -0.0003510037742730261, 0.9999999383795559],#obs0
                        [0.8000096614105919, 0.900009032540021, 0.574999998605769, -6.34110895683591e-09, 2.898768876911345e-09, -2.739143064146132e-05, 0.9999999996248548], #obs1
                        [0.8250000000000004, 1.0250000000000006, 0.6249999962330817, 7.499215073503913e-08, 1.876124864445975e-08, -0.0010048939559080816, 0.9999994950939384],#column3
                        ]

    initial_arm_config = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]

    #Initialize modules
    robot = RoboticsEnvironment()
    robot.connect()
    robot.initialize_params()
    scene = SceneState(robot)
    executor = ActionExecutor(robot)
    logger = TransitionLogger(connection_string="mongodb://localhost:27017/",database_name="refine-plan-v2", collection_name="manipulator-exploration-data")

    #Reset the simulation
    robot.reset_scene(objects,initial_locations,initial_arm_config)

    scene.update()
    state = scene.get_state()

    #compile options
    option_names =[
        "pick_/column0","pick_/column1","pick_/column2","pick_/column3",
        "pick_/obs1",#"pick_/obs0",
        "place_/goal_1","place_/goal_2","place_/goal_4","place_/goal_5",
        "place_/region_0","place_/region_2","place_/region_3",#"place_/region_1",
        "place_/region_4","place_/region_5","place_/region_6","place_/region_7","place_/region_8"
    ]

    #compile motion parameters
    motion_params={
        "pick":["top_0","top_90","top_270","left_0","left_180","right_0","right_180"],
        "place":["top_0","top_90","top_270","left_0","left_180","right_0","right_180"]
    }
    ###RANDOM ACION SET FOR EXPLORATION ####
    action_set = ActionSet(goal_objects=goal_objects,obstacle_objects=obstacle_objects,shop_slots=SHOP_SLOTS,goal_slots=GOAL_SLOTS)

    warmup = False
    picked_grasp = None
    #Run 3 pilot runs to have seed data for exploration and save them to the database
    if warmup:
        n_runs = 3
        action = None
        for run in range(n_runs):
            print(f"Pilot run {run}")
            #execute 10 random actions
            for step in range(10):
                print(f"Step {step}")
                #We should pick a random action from valid actions
                valid_actions,_ = action_set.valid_actions(state)
                if not valid_actions:
                    print("[Error] No valid actions found, object lost in scene")
                    robot.leave_object(action=action)
                else:
                    action, picked_grasp = select_random_action(valid_actions,motion_params,picked_grasp=picked_grasp)
                    print(f"Action: {action}")
                    success,exec_time = executor.execute(action)
                    if not success:
                        print(f"Action failed ! time elapsed: {exec_time}")
                        robot.leave_object(action=action)
                    # break
                #update the scene state
                scene.update()
                next_state = scene.get_state()
                reward = compute_reward(state,action,next_state)
                done = scene.is_goal_achieved()
                #log the transition
                logger.log_transition(state,action,reward,next_state,done,exec_time)
                #update state
                state = next_state
            print("Pilot run finished, resetting scene")
            robot.reset_scene(objects,initial_locations,initial_arm_config)
            robot.sim.step()
            robot.sim.wait(0.5)
            scene.update()
            state = scene.get_state()
            #in case the gripper is holding an object release it
            try:
                robot.leave_object(action=action)
            except:
                pass
    else:
        print("Skipping warmup runs and using existing data")

    #execute and log the planned policy
    # for action in PLAN_1:
    #     print(f"Executing planned action: {action}")
    #     success,exec_time = executor.execute(action)
    #     if not success:
    #         print(f"Action failed ! time elapsed: {exec_time}")
    #         robot.leave_object(action=action)
    #     # break
    #     #update the scene state
    #     scene.update()
    #     next_state = scene.get_state()
    #     reward = compute_reward(state,action,next_state)
    #     done = scene.is_goal_achieved()
    #     #log the transition
    #     logger.log_transition(state,action,reward,next_state,done,exec_time)
    #     #update state
    #     state = next_state
        
    policy = build_exploration_policy("mongodb://localhost:27017/",state)

    print("Exploration policy built")
    #execute the exploration policy
    for step in range(5):
        print(f"Step {step}")
        action = policy.get_next_action(state)
        print(f"Action: {action}")
        if action is None:
            print("No action found, stopping")
            robot.leave_object(action=action)
        success = executor.execute(action)
        if not success:
            print(f"Action failed, stopping. Time elapsed: {exec_time}")
            robot.leave_object(action=action)
        #update the scene state
        scene.update()
        state = scene.get_state()
        #log the transition
        logger.log_transition(state, action, success)
    print("Exploration finished")
    robot.stop_simulation()

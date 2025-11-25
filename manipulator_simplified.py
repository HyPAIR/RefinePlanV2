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
# Define constants
collection_name ="manipulator-reduced-dataset-exploration"
connection_string="mongodb://localhost:27017/"
goal_objects = ["/column0","/column1","/column2"]
shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]
goal_objects = goal_objects 
objects_formatted =[obj.replace('/','') for obj in goal_objects] #Boolean conversion issue
EPISODE_LENGTH =20


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
    #Rule 1: place actions are only valid if one of the object state factor is "held" and none of the object state factors are the target slot
    if option[:5] == "place":
        enable = AndCondition(OrCondition(*[EqCondition(sf_dict[obj], "held") for obj in objects_formatted]), AndCondition(*[NeqCondition(sf_dict[obj], option[6:]) for obj in objects_formatted]))

    #Rule 2: pick actions can only be valid if none of the object state factors are "held"
    if option[:4] == "pick":
        enable = AndCondition(*[NeqCondition(sf_dict[obj], "held") for obj in objects_formatted])

    return enable
def state_to_policy_state(state):
    """Convert a SceneState to a State object for policy use.

    Args:
        state: The SceneState object
    Returns:
        The State object
    """

    #object and obstacle state factos # object slots in data
    possible_slots = goal_slots+shop_slots+["held","unknown"]
    possible_slots =[slot.replace('/','') for slot in possible_slots] #Boolean conversion issue
    object_sfs = [StateFactor(obj,possible_slots) for obj in objects_formatted]

    #define state as a state object
    object_sfs_dict = {sf:"unknown" for sf in object_sfs}
    for obj,slot in state["object_slots"].items():
        sf = next((s for s in object_sfs if s.get_name() == obj.replace('/','')),None)
        if sf:
            object_sfs_dict[sf]=slot.replace('/','')
    state_dict = {**object_sfs_dict }    
    policy_state = State(state_dict)
    return policy_state

def build_exploration_policy(initial_state,option_names,motion_params,connection_str="mongodb://localhost:27017/",collection_name=collection_name):
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




    #object and obstacle state factos # object slots in data
    possible_slots = goal_slots+shop_slots+["held","unknown"]
    possible_slots =[slot.replace('/','') for slot in possible_slots] #Boolean conversion issue
    object_sfs = [StateFactor(obj,possible_slots) for obj in objects_formatted]

    #compile state factor list    
    sf_list = object_sfs 

   #compile options
 
    option_names_formatted =[opt.replace('_/','.') for opt in option_names] #Boolean conversion issue

    #compile motion parameters


    enabled_conds = {}
    for option in option_names_formatted:
        enabled_conds[option] = _get_enabled_cond(sf_list,option)

    #define_initial state as a state object
    object_sfs_dict = {sf:"unknown" for sf in object_sfs}
    for obj,slot in initial_state["object_slots"].items():
        sf = next((s for s in object_sfs if s.get_name() == obj),None)
        if sf:
            object_sfs_dict[sf]=slot
    initial_state_dict = {**object_sfs_dict }    
    initial_state = State(initial_state_dict)
    exploration_policy = synthesise_exploration_policy(
        connection_str=connection_str,
        db_name="refine-plan-v2",
        collection_name=collection_name,
        sf_list=sf_list,
        option_names=option_names_formatted,
        ensemble_size=4,
        horizon=EPISODE_LENGTH,
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
            selected_motion_param = random.choice(motion_params["{}.{}".format(action.action_type.value,action.obj[1:])])
            picked_grasp = selected_motion_param
        else:
            selected_motion_param = random.choice(motion_params["{}.{}".format(action.action_type.value,action.obj[1:])])
            # selected_motion_param = picked_grasp #random.choice(motion_params["place"])
        print(f"Selected action: {action} with motion param: {selected_motion_param}")
        print("here")
        action.grasp = GraspType(selected_motion_param)
        return action ,picked_grasp
def run_plan_manually(plan:list,executor:ActionExecutor,state:SceneState):
 for action in []:
        print(f"Executing planned action: {action}")
        if state['gripper_status']['holding']==None and action.action_type.value =='place':
            #picking something to place
            tmp_pick = random.choice([PLAN_1[0],PLAN_1[2],PLAN_1[4]])
            executor.execute(tmp_pick)
            scene.update()
            state =scene.get_state()
        if state['gripper_status']['holding'] is not None and action.action_type.value =='pick':
            #place it some where
            tmp_place = random.choice([PLAN_1[1],PLAN_1[3],PLAN_1[5]])
            executor.execute(tmp_place)
            scene.update()
            state =scene.get_state()
        success,exec_time = executor.execute(action)
        if not success:
            print(f"Action failed ! time elapsed: {exec_time}")
            if not robot.test_motion_planner():
                print("Resetting scene because of OMPL failure")
                robot.reset_scene(goal_objects,initial_locations,initial_arm_config,domain_randomization=False)
                scene.update()
                state = scene.get_state()
                continue
            #robot.leave_object(action=action)#this changes the state without an action: not good
            #find where it was taken from
            
        #update the scene state
        scene.update()
        next_state = scene.get_state()
        reward = compute_reward(prev_state=state,action=action,next_state=next_state,duration=exec_time)
        done = scene.is_goal_achieved()
        #log the transition
        logger.log_transition(state,action,reward,next_state,done,exec_time)
        #update state
        state = next_state

if __name__ == "__main__":

    #setup the initial state
    initial_locations =[[0.225003473985302, 0.8750057601488297, 0.6249999972840121, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838],#column0
                        [0.6, 1.075, 0.6249999984821841, 3.7923564988209e-08, 6.836504668418399e-08, -0.0009820818013717147, 0.9999995177575484],#column1
                        # [0.375003473985302, 0.7250057601488303, 0.6249999972840121, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838],#column2
                        [0.425003473985302, 0.8000057601488304, 0.6249999972840121, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838]
                        ]

    initial_arm_config = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]

    #Initialize modules
    robot = RoboticsEnvironment()
    robot.connect()
    robot.initialize_params()
    scene = SceneState(robot)
    executor = ActionExecutor(robot)
    logger = TransitionLogger(connection_string=connection_string,database_name="refine-plan-v2", collection_name=collection_name)

    #Reset the simulation
    robot.reset_scene(goal_objects,initial_locations,initial_arm_config,domain_randomization=False)

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
        "pick.column0": ["top_0","left_0","right_0","front_270"],
        "pick.column1": ["top_0","left_0","right_0","front_270"],
        "pick.column2": ["top_0","left_0","right_0","front_270"],
        "place.goal_0": ["top_0","left_0","right_0","front_270"],#right_0 is physically not possible for goal 0 ? it seems to work
        "place.goal_1": ["top_0","left_0","right_0","front_270"],#left_0 is physically not possible for goal 1
        "place.goal_2": ["top_0","left_0","right_0","front_270"],
        "place.region_0": ["top_0","left_0","right_0","front_270"],#top_0,front_270,left_0 are physically not possible for region 0
        "place.region_1": ["top_0","left_0","right_0","front_270"],#top_0, right_0,front_270 are physically not possible for region 1
        "place.region_2": ["top_0","left_0","right_0","front_270"],#left_0 is physically not possible for region 2
    }
    ###RANDOM ACTION SET FOR EXPLORATION ####
    action_set = ActionSet(goal_objects=goal_objects,obstacle_objects=[],shop_slots=SHOP_SLOTS,goal_slots=GOAL_SLOTS)

    warmup = False
    picked_grasp = None
    #Run 3 pilot runs to have seed data for exploration and save them to the database
    if warmup:
        n_runs = 3
        action = None
        for run in range(n_runs):
            print(f"Pilot run {run}")
            #execute 50 random actions
            for step in range(50):
                print(f"Step {step}")
                #We should pick a random action from valid actions
                valid_actions,_ = action_set.valid_actions(state)
                if not valid_actions:
                    print("[Error] No valid actions found, object lost in scene")
                    # robot.leave_object(action=action)
                    print("Resetting scene due to no valid actions")
                    robot.reset_scene(goal_objects,initial_locations,initial_arm_config)
                    robot.sim.step()
                    robot.sim.wait(0.5)
                    scene.update()
                    state = scene.get_state()
                    continue
                else:
                    action, picked_grasp = select_random_action(valid_actions,motion_params,picked_grasp=picked_grasp)
                    print(f"Action: {action}")
                    success,exec_time = executor.execute(action)
                    if not success:
                        print(f"Action failed ! time elapsed: {exec_time}")
                        if not robot.test_motion_planner():
                            print("Resetting scene because of OMPL failure")
                            robot.reset_scene(goal_objects,initial_locations,initial_arm_config)
                            robot.sim.step()
                            robot.sim.wait(2.2)
                            scene.update()
                            state = scene.get_state()
                            continue
                    # break
                #update the scene state
                scene.update()
                next_state = scene.get_state()
                reward = compute_reward(prev_state=state,action=action,next_state=next_state,duration=exec_time)
                done = scene.is_goal_achieved()
                #log the transition
                logger.log_transition(state,action,reward,next_state,done,exec_time)
                #update state
                state = next_state
            print("Pilot run finished, resetting scene")
            print("Leaving object if held")
            robot.leave_object(action=action)
            robot.reset_scene(goal_objects,initial_locations,initial_arm_config)
            robot.sim.step()
            robot.sim.wait(2.2)
            scene.update()
            state = scene.get_state()

        print("Warmup runs complete")
    else:
        print("Skipping warmup runs and using existing data")
    

   

    
    
    try:
        policy = build_exploration_policy(initial_state=state,option_names=option_names,motion_params=motion_params,connection_str=connection_string,collection_name=collection_name)
        reset_limit = 50
        step =0
        while type(policy) == list:
            for action in policy:
                action = executor.policy_action_to_executor_action(action,state=state)
                print(f"Executing planned action: {action}")
                if state['gripper_status']['holding']==None and action.action_type.value =='place':
                    #picking something to place
                    tmp_pick = Action(
                        action_type=ActionType.PICK,
                        obj=random.choice(goal_objects),
                        grasp=action.grasp
                    )
                    executor.execute(tmp_pick)
                    scene.update()
                    state =scene.get_state()
                if state['gripper_status']['holding'] is not None and action.action_type.value =='pick':
                    #place it some where
                    target_slot =f'{random.choice(goal_slots+shop_slots)}'
                    tmp_place = Action(
                        action_type=ActionType.PLACE,
                        obj=action.obj,
                        target_slot=target_slot,
                        target_pos={**GOAL_SLOTS,**SHOP_SLOTS}[target_slot]
                    )
                    tmp_place.grasp = action.grasp
                    executor.execute(tmp_place)
                    scene.update()
                    state =scene.get_state()
                success,exec_time = executor.execute(action)
                if not success:
                    print(f"Action failed ! time elapsed: {exec_time}")
                    if not robot.test_motion_planner():
                        print("Resetting scene because of OMPL failure")
                        robot.reset_scene(goal_objects,initial_locations,initial_arm_config,domain_randomization=True)
                        scene.update()
                        state = scene.get_state()
                        continue
                    #robot.leave_object(action=action)#this changes the state without an action: not good
                    #find where it was taken from
                    
                #update the scene state
                scene.update()
                next_state = scene.get_state()
                reward = compute_reward(prev_state=state,action=action,next_state=next_state,duration=exec_time)
                done = scene.is_goal_achieved()
                #log the transition
                logger.log_transition(state,action,reward,next_state,done,exec_time)
                #update state
                state = next_state
                step+=1
                if step>= reset_limit:
                    robot.leave_object(action=action)
                    robot.reset_scene(goal_objects,initial_locations,initial_arm_config)
                    scene.update()
                    state = scene.get_state()
            policy = build_exploration_policy(initial_state=state,option_names=option_names,motion_params=motion_params,connection_str=connection_string,collection_name=collection_name)
    except Exception as e:
        if e == AssertionError:
            print("Not enough data to build exploration policy")
        else:
            print(f"[ERROR] Failed to build exploration policy due to {e}")
        robot.stop_simulation()
        exit(1)

    print("Exploration policy built")
    for episode in range(20):
        print('Resetting the scene for new episode')
        robot.reset_scene(goal_objects,initial_locations,initial_arm_config)
        #execute the exploration policy
        step =0
        episode_length =EPISODE_LENGTH
        #get the initial state
        scene.update()
        state = scene.get_state()
        while step<=episode_length:
            print(f"Step {step}")
            policy_state = state_to_policy_state(state)
            action = policy.get_action(state=policy_state,time=step)
            print(f'policy value {policy.get_value(policy_state,time=step)}')
            if policy.get_value(policy_state,time=step)==None:
                print("No more valid actions in policy")
                break
            print(policy_state)
            print(action)
            action = executor.policy_action_to_executor_action(action,state)
            print(f"Action: {action}")
            if action is None:
                print("No action found, stopping")
                robot.leave_object(action=action)
                robot.reset_scene(goal_objects,initial_locations,initial_arm_config)
            success,exec_time = executor.execute(action)
            print(f'Action duration: {exec_time}')

            #update the scene state
            scene.update()
            next_state = scene.get_state()
            reward = compute_reward(prev_state=state,action=action,next_state=next_state,duration=exec_time)
            done = scene.is_goal_achieved()
            #log the transition
            logger.log_transition(state,action,reward,next_state,done,exec_time)
            state = next_state
            step+=1
            if not success:
                print(f"Action failed, stopping. Time elapsed: {exec_time}")
                if not robot.test_motion_planner():
                    print("Resetting scene because of OMPL failure")
                    robot.leave_object(action=action)
                    robot.reset_scene(goal_objects,initial_locations,initial_arm_config)
                    scene.update()
                    state = scene.get_state()
                    break
            
        print(f"Episode {episode} ended")
        print("Revising policy")
        policy = build_exploration_policy(initial_state=state,option_names=option_names,motion_params=motion_params,connection_str=connection_string,collection_name=collection_name)
    print("Exploration finished")
    robot.stop_simulation()

    
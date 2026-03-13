from refine_plan.models.state_factor import StateFactor
from refine_plan.models.state import State

shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]
goal_objects = ["/column0","/column1","/column2"]
objects_formatted =[obj.replace('/','') for obj in goal_objects]

# def _get_enabled_cond(sf_list, option):
#     """Get the enabled condition for an option.

#     Args:
#         sf_list: The list of state factors
#         option: The option we want the condition for

#     Returns:
#         The enabled condition for the option
#     """
#     #we need to define the enabled conditions for the options as boolean condition expressions based on state factors
#     sf_dict = {sf.get_name(): sf for sf in sf_list}
#     enable = OrCondition()
#     #Rule 1: place actions are only valid if one of the object state factor is "held" and none of the object state factors are the target slot
#     if option[:5] == "place":
#         parts = option.split("_")
#         target_slot = parts[1]+'_'+parts[2]
#         enable = AndCondition(OrCondition(*[EqCondition(sf_dict[obj], "held") for obj in objects_formatted]), AndCondition(*[NeqCondition(sf_dict[obj], target_slot) for obj in objects_formatted]))

#     #Rule 2: pick actions can only be valid if none of the object state factors are "held"
#     if option[:4] == "pick":
#         enable = AndCondition(*[NeqCondition(sf_dict[obj], "held") for obj in objects_formatted])

#     return enable

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
import time
# Define constants
collection_name ="manipulator-informed-data"
connection_string="mongodb://localhost:27017/"
goal_objects = ["/column0","/column1","/column2"]
shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]
objects_formatted =[obj.replace('/','') for obj in goal_objects] #Boolean conversion issue
EPISODE_LENGTH =30
EPISIDE_COUNT = 20
FAILSAFE_LIMIT = 6


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
        parts = option.split("_")
        target_slot = parts[1]+'_'+parts[2]
        enable = AndCondition(OrCondition(*[EqCondition(sf_dict[obj], "held") for obj in objects_formatted]), AndCondition(*[NeqCondition(sf_dict[obj], target_slot) for obj in objects_formatted]))

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
 
    option_names_formatted =[opt.replace('_/','_') for opt in option_names] #Boolean conversion issue

    #compile motion parameters


    enabled_conds = {}
    for option in option_names_formatted:
        enabled_conds[option] = _get_enabled_cond(sf_list,option)

    #define_initial state as a state object
    # object_sfs_dict = {sf:"unknown" for sf in object_sfs}
    object_sfs_dict = dict()#{sf:"unknown" for sf in object_sfs}
    for sf in object_sfs:
        object_sfs_dict[sf]=initial_state["object_slots"].get('/'+sf.get_name()).replace('/','')
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
            selected_motion_param = random.choice(motion_params["{}_{}".format(action.action_type.value,action.obj[1:])])
            picked_grasp = selected_motion_param
        else:
            selected_motion_param = random.choice(motion_params["{}_{}".format(action.action_type.value,action.target_slot[1:])])
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
            # if not robot.test_motion_planner():
            #     print("Resetting scene because of OMPL failure")
            #     robot.reset_scene(goal_objects,initial_locations,initial_arm_config,domain_randomization=False)
            #     scene.update()
            #     state = scene.get_state()
            #     continue
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
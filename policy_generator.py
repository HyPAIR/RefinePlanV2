"""
Refine plan for manipulator environment
Author: Mohammed Saleeq Kolleth
"""
import sys
import os
from refine_plan.learning.option_learning import mongodb_to_yaml, learn_dbns
from refine_plan.models.state_factor import StateFactor
from refine_plan.models.state import State
from refine_plan.models.condition import Label,OrCondition,AndCondition,EqCondition
from refine_plan.models.dbn_option import DBNOption
from refine_plan.models.semi_mdp import SemiMDP
from refine_plan.models.policy import Policy,TimeDependentPolicy
from refine_plan.algorithms.semi_mdp_solver import synthesise_policy

from manipulator_utils import _get_enabled_cond,state_to_policy_state
from robot.robot_interface import RoboticsEnvironment
from robot.action_executor import ActionExecutor
from state.scene_state import SceneState
from rl.reward_function import compute_reward
from rl.transition_logger import TransitionLogger
import csv
from itertools import permutations
import argparse
MAX_EPISODE_LEGTH =30
SAMPLE_COUNT = 7
db_collection_name ="informed-exploration"#"cubic-objects-manipulator-exploration"
training_data_collection_name = "manipulator-informed-data"
connection_string="mongodb://localhost:27017/"
goal_objects = ["/column0","/column1","/column2"]
shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]
goal_objects 
objects_formatted =[obj.replace('/','') for obj in goal_objects]
 #object and obstacle state factos # object slots in data
possible_slots = goal_slots+shop_slots+["held"]
possible_slots =[slot.replace('/','') for slot in possible_slots] #Boolean conversion issue
object_sfs = [StateFactor(obj,possible_slots) for obj in objects_formatted]
logger = TransitionLogger(connection_string=connection_string,database_name="refine-plan-v2", collection_name=db_collection_name)

def write_mongodb_to_yaml(mongo_connection_str,collection_name =training_data_collection_name,limit=None):
    """Learn the DBNOptions from the database.

    Args:
        mongo_connection_str: The MongoDB conenction string"""
    print("writing mongo databse to yaml file")
  
    mongodb_to_yaml(
        connection_str=mongo_connection_str,
        db_name="refine-plan-v2",
        collection_name=collection_name,
        sf_list=object_sfs,
        out_file="./refine-plan/data/manipulator/dataset.yaml",
        split_by_motion=True,
        limit=limit,
        sort_by=[("timestamp", 1)]

    )
    print("YAML Dataset Created")
def learn_options():
    """Learn the options from the YAML file."""
    dataset_path = "./refine-plan/data/manipulator/dataset.yaml"
    output_dir = "./refine-plan/data/manipulator/"

    learn_dbns(dataset_path, output_dir, object_sfs)


def run_planner(initial_state:State, policy_path:str):
    """Run refine-plan and synthesise a BT.

    Returns:
        The refined BT
    """

    sf_list = object_sfs
    sf_dict = {sf.get_name(): sf for sf in sf_list}
    labels = [Label("goal",AndCondition(*[OrCondition(*[EqCondition(sf_dict[obj],goal_slot.replace('/',''))for goal_slot in goal_slots]) for obj in objects_formatted]) )]

    #compile motion parameters
    option_motion_params={
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
    options =list(option_motion_params.keys())
    option_names =[]
    for key,value in option_motion_params.items():
        option_names+=[f'{key}_{motion}' for motion in value]
    
    enabled_conds = {}
    for option in options:
        enabled_conds[option] = _get_enabled_cond(sf_list,option)
    #initial_state = { 'object_slots': {'column0': 'region_0', 'column1': 'region_1', 'column2': 'region_2'}, 'gripper_status': {'holding': None}, 'goal_region_occupancy': {'/goal_0': 'None', '/goal_1': 'None', '/goal_2': 'None'}, 'shop_region_occupancy': {'/region_0': '/column1', '/region_1': '/column0', '/region_2': '/column2'}}
    #define_initial state as a state object
    object_sfs_dict = dict()
    for sf in object_sfs:
        object_sfs_dict[sf] = initial_state['object_slots']['/'+sf.get_name()].replace('/','') if '/'+sf.get_name() in initial_state['object_slots'] else 'held' if initial_state['gripper_status']['holding'] == '/'+sf.get_name() else 'unknown'
    initial_state_dict = {**object_sfs_dict }    
    initial_state = State(initial_state_dict)
    print(initial_state)



    option_list = []
    for option in option_names:
        print("Reading in option: {}".format(option))
        t_path = "./refine-plan/data/manipulator/{}_transition.bifxml".format(option)
        r_path = "./refine-plan/data/manipulator/{}_reward.bifxml".format(option)
        option_list.append(
            DBNOption(
                option, t_path, r_path, sf_list, _get_enabled_cond(sf_list, option)
            )
        )

    print("Creating MDP...")
    semi_mdp = SemiMDP(sf_list, option_list, labels, initial_state=initial_state)
    print("Synthesising Policy...")
    policy = synthesise_policy(semi_mdp, prism_prop='Pmax=?[F "goal"]')
    policy.write_policy(policy_path)
    


if __name__ == "__main__":
    print("Starting Manipulator Policy Generation")
    training_dbs=['pick-place-random']#'informed-exploration','random-exploration']
    
    # Create policies directory if it doesn't exist
    if not os.path.exists('policies'):
        os.makedirs('policies')

    for training_data_collection_name in training_dbs:
        for limit in range(8000,15001,1000):
            print(f"Using first {limit} entries from {training_data_collection_name}")
            write_mongodb_to_yaml(connection_string,collection_name = training_data_collection_name,limit=limit)
            learn_options()

            # Define the objects and their initial slots
            objects = ["/column0", "/column1", "/column2"]
            initial_slots = ["/region_0", "/region_1", "/region_2"]
            
            # Generate all permutations of objects in initial slots
            initial_sate_permutations = list(permutations(initial_slots))
            
            for perm_index, perm in enumerate(initial_sate_permutations):
                policy_filename = f'policies/{training_data_collection_name}_{limit}_points_perm_{perm_index}_pmax.yaml'
                
                if os.path.isfile(policy_filename):
                    print(f"Policy already exists for permutation {perm_index}, at limit {limit}, skipping")
                    # continue
                
                print(f"Generating policy for permutation {perm_index}, at limit {limit}")

                # Construct the initial state for the planner
                object_slots = {objects[i]: perm[i] for i in range(len(objects))}
                initial_state = {
                    'object_slots': object_slots,
                    'gripper_status': {'holding': None}
                }

                # Generate and save the policy
                run_planner(initial_state=initial_state, policy_path=policy_filename)
                
                # Add the permutation to the generated policy file
                import yaml
                with open(policy_filename, 'r') as f:
                    policy_data = yaml.safe_load(f)
                
                # Add the permutation as a list
                policy_data['initial_state'] = initial_state["object_slots"]

                
                with open(policy_filename, 'w') as f:
                    yaml.dump(policy_data, f)

                print(f"Policy saved to {policy_filename} with permutation info")
                    
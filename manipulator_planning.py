"""
Refine plan for manipulator environment
Author: Mohammed Saleeq Kolleth
"""
import sys

from refine_plan.learning.option_learning import mongodb_to_yaml, learn_dbns
from refine_plan.models.state_factor import StateFactor
from refine_plan.models.state import State
from refine_plan.models.condition import Label,OrCondition,AndCondition,EqCondition
from refine_plan.models.dbn_option import DBNOption
from refine_plan.models.semi_mdp import SemiMDP
from refine_plan.models.policy import Policy,TimeDependentPolicy
from refine_plan.algorithms.semi_mdp_solver import synthesise_policy

from manipulator_exploration import _get_enabled_cond,state_to_policy_state
from robot.robot_interface import RoboticsEnvironment
from robot.action_executor import ActionExecutor
from state.scene_state import SceneState
from rl.reward_function import compute_reward
from rl.transition_logger import TransitionLogger

collection_name ="manipulator-refined-data"#"cubic-objects-manipulator-exploration"
connection_string="mongodb://localhost:27017/"
goal_objects = ["/column0","/column1","/column2"]
shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]
goal_objects 
objects_formatted =[obj.replace('/','') for obj in goal_objects]
 #object and obstacle state factos # object slots in data
possible_slots = goal_slots+shop_slots+["held","unknown"]
possible_slots =[slot.replace('/','') for slot in possible_slots] #Boolean conversion issue
object_sfs = [StateFactor(obj,possible_slots) for obj in objects_formatted]
logger = TransitionLogger(connection_string=connection_string,database_name="refine-plan-v2", collection_name=collection_name)

def write_mongodb_to_yaml(mongo_connection_str,limit=None):
    """Learn the DBNOptions from the database.

    Args:
        mongo_connection_str: The MongoDB conenction string"""
    print("writing mongo databse to yaml file")
  
    mongodb_to_yaml(
        connection_str=mongo_connection_str,
        db_name="refine-plan-v2",
        collection_name="manipulator-random-data",
        sf_list=object_sfs,
        out_file="./refine-plan/data/manipulator/dataset.yaml",
        split_by_motion=True,
        limit=limit

    )
    print("YAML Dataset Created")
def learn_options():
    """Learn the options from the YAML file."""
    dataset_path = "./refine-plan/data/manipulator/dataset.yaml"
    output_dir = "./refine-plan/data/manipulator/"

    learn_dbns(dataset_path, output_dir, object_sfs)


def run_planner(initial_state:State)->Policy:
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
    policy = synthesise_policy(semi_mdp, prism_prop='Rmin=?[F "goal"]')
    policy.write_policy("./refine-plan/data/manipulator/manipulator_refined_policy.yaml")
    return policy
    


if __name__ == "__main__":
    write_mongodb_to_yaml(connection_string,limit=500)
    learn_options()
    #policy = TimeDependentPolicy("./refine-plan/data/manipulator/manipulator_refined_policy.yaml")



    #run the refined policy
    #setup the initial state
     #setup the initial state
    initial_locations =[[0.35, 0.8, 0.5625, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838],#column0
                        [0.6, 1.075, 0.5625, 3.7923564988209e-08, 6.836504668418399e-08, -0.0009820818013717147, 0.9999995177575484],#column1
                        [0.6, 0.8000057601488304, 0.5625, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838]#column2
                        ]

    initial_arm_config = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]


    robot = RoboticsEnvironment()
    robot.connect()
    robot.initialize_params()
    scene = SceneState(robot)
    executor = ActionExecutor(robot)

    #reset simulation to statndard initial state
    robot.reset_scene(goal_objects,initial_locations,initial_arm_config,domain_randomization=True)

    #get the initial state
    scene.update()
    state = scene.get_state()
    #formulate the refined policy given initial state
    policy =run_planner(initial_state=state)
    # run the policy
    act_policy = True
    if act_policy:

        MAX_EPISODE_LEGTH =20
        step =0
        failsafe =0
        total_task_time =0
        while step<=MAX_EPISODE_LEGTH:
            print(f"Step {step}")
            policy_state = state_to_policy_state(state)
            print(f'policy state {policy_state}')
            #refined policy is not time dependent
            print(f'policy value {policy.get_value(policy_state)}')
            if policy.get_value(policy_state)==None or policy.get_action(policy_state)==None:
                print("No valid actions in policy for given state, stopping")
                break
            action = policy.get_action(state=policy_state)
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
            total_task_time +=exec_time
            #update the scene state
            scene.update()
            next_state = scene.get_state()
            reward = compute_reward(prev_state=state,action=action,next_state=next_state,duration=exec_time)
            print(f'reward {reward}')
            done = scene.is_goal_achieved()

            state = next_state
            step+=1
            #log the transition
            logger.log_transition(state,action,reward,next_state,done,exec_time)
            state = next_state
            step+=1
            if not success:
                print(f"Action failed, stopping. Time elapsed: {exec_time}")
                failsafe +=1
                if failsafe>=3:
                    print("Too many failures, resetting episode")
                    failsafe=0
                    break
                if not robot.test_motion_planner():
                    print("Resetting scene because of OMPL failure")
                    robot.leave_object(action=action)
                    robot.reset_scene(goal_objects,initial_locations,initial_arm_config,domain_randomization=True)
                    scene.update()
                    state = scene.get_state()
                    break
            else:
                failsafe =0
    print(f'Total task time: {total_task_time} sec')
    robot.stop_simulation()
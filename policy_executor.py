"""
Refine plan for manipulator environment
Author: Mohammed Saleeq Kolleth
"""
import sys
import os
from refine_plan.models.policy import Policy

from manipulator_utils import _get_enabled_cond,state_to_policy_state
from robot.robot_interface import RoboticsEnvironment
from robot.action_executor import ActionExecutor
from state.scene_state import SceneState
from state.slot_config import SHOP_SLOTS
from rl.reward_function import compute_reward
from rl.transition_logger import TransitionLogger
import csv
from itertools import permutations
import argparse
MAX_EPISODE_LEGTH =30
SAMPLE_COUNT = 10
db_collection_name ="manipulator-refined-data"#"cubic-objects-manipulator-exploration"
training_data_collection_name = "manipulator-informed-data"
connection_string="mongodb://localhost:27017/"
goal_objects = ["/column0","/column1","/column2"]
shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]

logger = TransitionLogger(connection_string=connection_string,database_name="refine-plan-v2", collection_name=db_collection_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run manipulator policy execution')
    parser.add_argument('-p','--port', type=int, required=True, help='Port number for CoppeliaSim remote API')
    parser.add_argument('-l','--limit', type=int, required=True, help='Data limit used for training the policy')
    parser.add_argument('-d','--training-data-collection-name', type=str, required=True, help='Name of the training data collection')
    args = parser.parse_args()

    print(f"Executing policy for {args.training_data_collection_name} with limit {args.limit} on port {args.port}")
    results_filename =""
    for run in range(SAMPLE_COUNT):
        print(f"Starting run {run + 1}/{SAMPLE_COUNT}")
        # Get all permutations of the goal objects
        object_permutations = list(permutations(range(len(goal_objects))))

        for perm_index, perm in enumerate(object_permutations):
            # Construct policy filename
            policy_filename = f'policies/{args.training_data_collection_name}_{args.limit}_points_perm_{perm_index}_pmax.yaml'
            if not os.path.isfile(policy_filename):
                print(f"Policy file not found: {policy_filename}")
                continue

            # Load the policy YAML to get the permutation and then load the policy object
            import yaml
            with open(policy_filename, 'r') as f:
                policy_data = yaml.safe_load(f)

            if 'initial_state' not in policy_data:
                print(f"Policy file {policy_filename} does not contain 'initial_state' key.")
                print("Please regenerate the policy file with the updated policy_generator.py script.")
                continue

            initial_state = policy_data['initial_state']
            print(initial_state)
            policy = Policy({}, policy_file=policy_filename)

            # Define initial locations to determine the permutation for the simulation
            initial_locations = [
                [0.35, 0.8, 0.5625, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838],  # Corresponds to region_0
                [0.6, 1.075, 0.5625, 3.7923564988209e-08, 6.836504668418399e-08, -0.0009820818013717147, 0.9999995177575484],   # Corresponds to region_1
                [0.6, 0.8000057601488304, 0.5625, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838] # Corresponds to region_2
            ]
            initial_arm_config = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]

            # Use the loaded permutation to determine the object locations for the simulation
            sim_objects = []
            sim_object_locations = []
            for key, value in initial_state.items():
                sim_objects.append(key)
                sim_object_locations.append(SHOP_SLOTS[value] + [0, 0, 0, 1])

            results_filename = f'results/{args.training_data_collection_name}_{args.limit}_points.csv'
            # Check if the file exists and already have more than SAMPLE_COUNT+1 items, if yes dont run  the combination again
            file_exists = os.path.isfile(results_filename)
            
            robot = RoboticsEnvironment(port=args.port)
            robot.connect()
            robot.initialize_params()
            scene = SceneState(robot)
            executor = ActionExecutor(robot)

            robot.reset_scene(sim_objects, sim_object_locations, initial_arm_config, domain_randomization=False)

            scene.update()
            state = scene.get_state()
            
            step = 0
            total_task_time = 0
            n_actions = 0
            visited_states = set()

            while step <= MAX_EPISODE_LEGTH:
                print(f"Step {step}")
                policy_state = state_to_policy_state(state)
                state_fingerprint = frozenset(state['object_slots'].items())
                
                if state_fingerprint in visited_states:
                    print("State has been visited before, stopping to avoid loops")
                    step = MAX_EPISODE_LEGTH + 1
                    continue
                visited_states.add(state_fingerprint)
                
                if policy.get_value(policy_state) is None or policy.get_action(policy_state) is None:
                    print("No valid actions in policy for a given state, stopping")
                    break
                    
                action = policy.get_action(state=policy_state)
                action = executor.policy_action_to_executor_action(action, state)
                print(f"Action: {action}")

                if action is None:
                    print("No action found, stopping")
                    break
                    
                success, exec_time = executor.execute(action)
                n_actions += 1
                total_task_time += exec_time

                scene.update()
                next_state = scene.get_state()
                reward = compute_reward(prev_state=state, action=action, next_state=next_state, duration=exec_time)
                done = scene.is_goal_achieved()
                logger.log_transition(state, action, reward, next_state, done, exec_time)
                
                state = next_state
                step += 1
                
                if not success:
                    print(f"Action failed, stopping. Time elapsed: {exec_time}")
                    break

            goal_achieved = scene.is_goal_achieved()
            goal_region_occupancy = list(scene.goal_region_occupancy.values())
            goal_percentage = 100 * (1 - (goal_region_occupancy.count('None') / len(goal_slots)))

            print(f"Run {run + 1} finished.")
            print(f"Goal achieved: {goal_achieved}")
            print(f"Goal percentage: {goal_percentage}%")
            print(f'Number of actions: {n_actions}')
            print(f'Total task time: {total_task_time} sec')

            with open(results_filename, mode='a') as results_file:
                results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                if not file_exists:
                    results_writer.writerow(['data limit', 'run', 'initial_permutation', 'goal_percentage', 'goal_achieved', 'number_of_actions', 'total_task_time', 'final_goal_region_occupancy'])
                    file_exists = True
                init_perm = f'permutation_{perm_index}'
                results_writer.writerow([args.limit, run, init_perm, goal_percentage, goal_achieved, n_actions, total_task_time, goal_region_occupancy])
            
            robot.stop_simulation()
    
    print(f"Finished all runs. Results saved to {results_filename}")
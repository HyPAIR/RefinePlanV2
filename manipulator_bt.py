from robot.robot_interface import RoboticsEnvironment
from robot.action_executor import ActionExecutor
from rl.transition_logger import TransitionLogger
from state.scene_state import SceneState
from rl.reward_function import compute_reward

#BT stuff
import py_trees
from trees.pick_place_tree import create_behaviour_tree


import argparse

goal_objects = ["/column0","/column1","/column2"]
shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]
connection_string="mongodb://localhost:27017/"
collection_name ="manipulator-bt-data"
MAX_STEPS = 50

logger = TransitionLogger(connection_string=connection_string,database_name="refine-plan-v2", collection_name=collection_name)

initial_locations =[[0.35, 0.8, 0.5625, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838],#region 0
                        [0.6, 1.075, 0.5625, 3.7923564988209e-08, 6.836504668418399e-08, -0.0009820818013717147, 0.9999995177575484],#region 1
                        [0.6, 0.8000057601488304, 0.5625, 3.071012527623134e-08, 2.2171811830454326e-08, 1.8385622863714705e-05, 0.9999999998309838]#region 2
                        ]

initial_arm_config = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run manipulator BT execution')
    parser.add_argument('-p','--port', type=int, required=True, help='Port number for CoppeliaSim remote API')
    args = parser.parse_args()
    print(f"Connecting to port {args.port}")
    robot = RoboticsEnvironment(port=args.port)
    exectutor = ActionExecutor(robot)
    scene = SceneState(robot)
    
    #connect and reset the simulation
    robot.connect()
    robot.initialize_params()
    robot.reset_scene(goal_objects,initial_locations,initial_arm_config,domain_randomization=True)

    scene.update()
    state = scene.get_state()

    #Init behaviour tree
    tree = create_behaviour_tree(scene_state=scene,goal_objects=goal_objects,shop_slots=shop_slots,goal_slots=goal_slots)
    bt = py_trees.trees.BehaviourTree(tree)
    bt.setup(timeout=3.0)

    #Render the behaviout tree
    py_trees.display.render_dot_tree(tree,with_blackboard_variables=True)

    #setup the blackboard client for bt
    blackboard = py_trees.blackboard.Client(name="bt")
    blackboard.register_key(key="current_action",access=py_trees.common.Access.READ)
    blackboard.register_key(key="current_action",access=py_trees.common.Access.WRITE)

    #Episode loop
    for step in range(MAX_STEPS):
        print(f"\n[INFO] Simulation action step: {step}")

        #Tick the BT
        bt.tick()
        action = blackboard.current_action
        print(py_trees.display.unicode_tree(tree,show_status=True))
        #save the bt image
        # py_trees.display.render_dot_tree(tree)

        if action is None:
            print("[WARN] No action produced by BT")
            continue
        else:
            print(f"[INFO] Executing {action}")
            success,exec_time = exectutor.execute(action)

            if success:
                blackboard.current_action = None
            
            #Observer next state and compute reward
            scene.update()
            next_state = scene.get_state()  
            reward = compute_reward(prev_state=state,action=action,next_state=next_state,duration=exec_time)
            done = scene.is_goal_achieved()

            #Log transition
            logger.log_transition(state, action, reward, next_state, done,exec_time)
            print(f"[INFO] Success: {success} | Reward: {reward} | Done: {done} | Execution Time: {exec_time:.2f} seconds")
            if done:
                print(f"\n[INFO] Goal Achieved in {step +1 } steps")
                #logger automatically saves episodes when done and resets
                break   
            if step >MAX_STEPS:
                print(f"\n[INFO] Max steps reached episode ended")
    robot.stop_simulation()






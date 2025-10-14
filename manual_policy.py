from rl.action_space import Action, ActionType,GraspType
from state.slot_config import GOAL_SLOTS
from robot.action_executor import ActionExecutor
from robot.robot_interface import RoboticsEnvironment
# 1. pick column0  in top grasp, place it in goal 5
act1 = Action(
    action_type=ActionType.PICK,
    obj='/column0',
    grasp=GraspType.TOP_0
)
act2 = Action(
    action_type=ActionType.PLACE,
    obj='/column0',
    target_slot='/goal_5',
    target_pos=GOAL_SLOTS['/goal_5'],
    grasp=GraspType.TOP_0
)
# 2. pick column 1 in top grasp again, place it in goal 1
act3 = Action(
    action_type=ActionType.PICK,
    obj='/column1',
    grasp=GraspType.LEFT_0
)
act4 = Action(
    action_type=ActionType.PLACE,
    obj='/column1',
    target_slot='/goal_2',
    target_pos=GOAL_SLOTS['/goal_2'],
    grasp=GraspType.LEFT_0
)
# 3. pick column 2 in left_0, place it in goal 2
act5 = Action(
    action_type=ActionType.PICK,
    obj='/column2',
    grasp='left_0'
)
act6 = Action(
    action_type=ActionType.PLACE,
    obj='/column2',
    target_slot='/goal_1',
    target_pos=GOAL_SLOTS['/goal_1']
)
# 4. pick column3 in top grasp, place it in goal 4
act7 = Action(
    action_type=ActionType.PICK,
    obj='/column3',
    grasp='top_0'
)
act8 = Action(
    action_type=ActionType.PLACE,
    obj='/column3',
    target_slot='/goal_4',
    target_pos=GOAL_SLOTS['/goal_4']
)

policy = [act1, act2, act5, act6, act3, act4, act7, act8]
robot = RoboticsEnvironment()
robot.connect()
robot.initialize_params()
robot.setConfig([-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667])
robot.sim.step()
executor = ActionExecutor(robot)
for action in policy:
    print(f"Executing action: {action}")
    executor.execute(action)
    print("Action executed.")


robot.stop_simulation()
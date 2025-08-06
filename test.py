from robot.robot_interface import RoboticsEnvironment
from robot.action_executor import ActionExecutor
from rl.action_space import Action, ActionType, GraspType
#these are objects to be picked up / manipulated
goal_objects = ["/column0","/column1","/column2","/column3"]
obstacle_objects=["/obs0","/obs1"]
shop_slots =[f"/region_{i}" for i in range(9)]
# goal_slots =[f"/goal_{i}" for i in range(5)]
goal_slots=["/goal_1","/goal_2","/goal_4","/goal_5"]
objects = goal_objects + obstacle_objects
initial_locations = [
    [0.5750000000000004, 0.7000000000000004, 0.5499999999999998],
    [0.3500000000000002, 0.7000000000000004, 0.5499999999999998],
    [0.30000000000000016, 0.9750000000000008, 0.5499999999999998],
    [0.5250000000000004, 0.8750000000000003, 0.5499999999999998], 
    [0.9000000000000006, 0.6249999999999993, 0.5499999999999999], 
    [0.8000076260094475, 0.9000043343419417, 0.5499999988422022]
    ]

initial_arm_config = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]



action = Action(    action_type=ActionType.PICK,
    obj="/column0",
    target_slot=None,
    target_pos=None,
    grasp=GraspType.RIGHT_0
)

robot = RoboticsEnvironment()
robot.connect()
robot.initialize_params()
robot.reset_scene(objects, initial_locations, initial_arm_config)
executor = ActionExecutor(robot)

success = executor.execute(action)
print(f"Action executed successfully: {success}")
robot.stop_simulation()
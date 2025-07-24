
import random
from time import sleep

from rl.transition_logger import TransitionLogger
from rl.reward_function import compute_reward
from rl.action_space import ActionSet
from robot.action_executor import ActionExecutor
from state.scene_state import SceneState
from robot.robot_interface import RoboticsEnvironment as RobotInterface


# Constants
MAX_STEPS = 100
EPSILON = 0.2  # exploration rate

# Init interfaces
robot = RobotInterface()
scene = SceneState(robot)
executor = ActionExecutor(robot)
logger = TransitionLogger()
action_set = ActionSet(goal_objects=["obj1", "obj2", "obj3", "obj4"],
                       obstacle_objects=["obs1", "obs2"],
                       shop_slots=[f"s{i}" for i in range(9)],
                       goal_slots=["g1", "g2", "g3", "g4"])

# TODO: Reset scene
robot.reset_scene()
scene.update()
state = scene.get_state()

for step in range(MAX_STEPS):
    print(f"\n🧠 Step {step}")

    # Pick action: BT logic or epsilon-greedy exploration
    if random.random() < EPSILON:
        print("[EXPLORE] Picking random action")
        action_index = random.choice(action_set.get_all_action_indices())
    else:
        print("[BT] Picking deterministic action")
        action_index = action_set.get_deterministic_bt_action(state)

    action = action_set.get_action(action_index)

    # Execute action
    success = executor.execute(action)
    sleep(0.2)  # wait for sim to update

    # Get next state and reward
    scene.update()
    next_state = scene.get_state()
    reward = compute_reward(state, action, next_state)
    done = scene.is_goal_achieved()

    # Log transition
    logger.log_transition(state, action, reward, next_state, done)

    if done:
        print(f"\n🎯 Task complete in {step+1} steps.")
        break

    state = next_state

else:
    print("\n⏹️ Max steps reached — episode ended.")

print("[DONE]")

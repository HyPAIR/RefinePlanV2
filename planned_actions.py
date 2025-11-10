from rl.action_space import Action, ActionType,GraspType
from state.slot_config import GOAL_SLOTS,SHOP_SLOTS

# Planned Actions
PLAN_1 = [
    Action(action_type=ActionType.PICK, obj="/column2", grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PLACE, obj="/column2", target_slot='/goal_2',target_pos=GOAL_SLOTS['/goal_2'],grasp=GraspType.TOP_0),

    


]
from rl.action_space import Action, ActionType,GraspType
from state.slot_config import GOAL_SLOTS,SHOP_SLOTS

# Planned Actions
PLAN_1 = [
    Action(action_type=ActionType.PICK, obj="/column2", grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PLACE, obj="/column2", target_slot='/goal_5',target_pos=GOAL_SLOTS['/goal_5'],grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PICK, obj="/column0", grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PLACE, obj="/column0", target_slot='/goal_2',target_pos=GOAL_SLOTS['/goal_2'],grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PICK, obj="/column1", grasp=GraspType.LEFT_0),
    Action(action_type=ActionType.PLACE, obj="/column1", target_slot='/region_7',target_pos=SHOP_SLOTS['/region_7'],grasp=GraspType.LEFT_0),
    # Action(action_type=ActionType.PICK, obj="/column3", grasp=GraspType.TOP_0),
    # Action(action_type=ActionType.PLACE, obj="/column3", target_slot='/goal_1',target_pos=GOAL_SLOTS['/goal_1'],grasp=GraspType.TOP_0),
    # Action(action_type=ActionType.PICK, obj="/obs1", grasp=GraspType.TOP_0),
    # Action(action_type=ActionType.PLACE, obj="/obs1", target_slot='/region_0',target_pos=SHOP_SLOTS['/region_0'],grasp=GraspType.TOP_0),
    # #do the region wise coverage
    # Action(action_type=ActionType.PICK, obj="/column0", grasp=GraspType.TOP_0),
    # #region 2
    # Action(action_type=ActionType.PLACE, obj="/column0", target_slot='/region_2',target_pos=SHOP_SLOTS['/region_2'],grasp=GraspType.TOP_0),
    # Action(action_type=ActionType.PICK, obj="/column0", grasp=GraspType.TOP_0),
    # #region 4
    # Action(action_type=ActionType.PLACE, obj="/column0", target_slot='/region_4',target_pos=SHOP_SLOTS['/region_4'],grasp=GraspType.TOP_0),
    # #region 5
    # Action(action_type=ActionType.PICK, obj="/column0", grasp=GraspType.TOP_0),
    # Action(action_type=ActionType.PLACE, obj="/column0", target_slot='/region_5',target_pos=SHOP_SLOTS['/region_5'],grasp=GraspType.TOP_0),
    #pick column 3 and place it in region 8 with top grasp
    Action(action_type=ActionType.PICK, obj="/column3", grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PLACE, obj="/column3", target_slot='/region_8',target_pos=SHOP_SLOTS['/region_8'],grasp=GraspType.TOP_0),
    #pick column2 and place it in region 6 with top grasp
    Action(action_type=ActionType.PICK, obj="/column2", grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PLACE, obj="/column2", target_slot='/region_6',target_pos=SHOP_SLOTS['/region_6'],grasp=GraspType.TOP_0),
    


]
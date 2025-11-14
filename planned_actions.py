from rl.action_space import Action, ActionType,GraspType
from state.slot_config import GOAL_SLOTS,SHOP_SLOTS

# Planned Actions
PLAN_1 = [
    #place column 2 in goal 2 with top grasp
    Action(action_type=ActionType.PICK, obj="/column2", grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PLACE, obj="/column2", target_slot='/goal_2',target_pos=GOAL_SLOTS['/goal_0'],grasp=GraspType.TOP_0),
    #place column 0 in goal 0 with right grasp
    Action(action_type=ActionType.PICK, obj="/column0", grasp=GraspType.RIGHT_0),
    Action(action_type=ActionType.PLACE, obj="/column0", target_slot='/goal_1',target_pos=GOAL_SLOTS['/goal_1'],grasp=GraspType.RIGHT_0),
    #place column 1 in goal 1 with left grasp
    Action(action_type=ActionType.PICK, obj="/column1", grasp=GraspType.LEFT_0),
    Action(action_type=ActionType.PLACE, obj="/column1", target_slot='/goal_2',target_pos=GOAL_SLOTS['/goal_2'],grasp=GraspType.LEFT_0),
]

PLAN_2 = [
     #place column 2 in goal 2 with top grasp
    Action(action_type=ActionType.PICK, obj="/column2", grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PLACE, obj="/column2", target_slot='/region_2',target_pos=SHOP_SLOTS['/region_2'],grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PICK, obj="/column2", grasp=GraspType.TOP_0),
    Action(action_type=ActionType.PLACE, obj="/column2", target_slot='/goal_0',target_pos=GOAL_SLOTS['/goal_0'],grasp=GraspType.TOP_0),
    #place column 0 in goal 0 with right grasp
    Action(action_type=ActionType.PICK, obj="/column0", grasp=GraspType.RIGHT_0),
    Action(action_type=ActionType.PLACE, obj="/column0", target_slot='/region_0',target_pos=SHOP_SLOTS['/region_0'],grasp=GraspType.RIGHT_0),
    Action(action_type=ActionType.PICK, obj="/column0", grasp=GraspType.RIGHT_0),
    Action(action_type=ActionType.PLACE, obj="/column0", target_slot='/goal_1',target_pos=GOAL_SLOTS['/goal_1'],grasp=GraspType.RIGHT_0),
    #place column 1 in goal 1 with left grasp
    Action(action_type=ActionType.PICK, obj="/column1", grasp=GraspType.LEFT_0),
    Action(action_type=ActionType.PLACE, obj="/column1", target_slot='/region_1',target_pos=SHOP_SLOTS['/region_1'],grasp=GraspType.LEFT_0),
    Action(action_type=ActionType.PICK, obj="/column1", grasp=GraspType.LEFT_0),
    Action(action_type=ActionType.PLACE, obj="/column1", target_slot='/goal_2',target_pos=GOAL_SLOTS['/goal_2'],grasp=GraspType.LEFT_0)
    ]

 #compile options
option_names =[
    "pick_/column0",
    "place_/goal_0",
    "pick_/column1",
    "place_/goal_1",
    "pick_/column2",
    "place_/goal_2",
    "pick_/column0",
    "place_/region_0",
    "pick_/column1",
    "place_/region_1",
    "pick_/column2",
    "place_/region_2",
]
PLAN_CUSTOM =[Action(ActionType.PICK, obj="/column2",grasp=GraspType.RIGHT_0),#compulsory pick
                Action(ActionType.PLACE, obj="/column2",target_slot='/region_2',target_pos=SHOP_SLOTS['/region_2'],grasp=GraspType.TOP_0)
]
#compile motion parameters
motions ={"top_0": GraspType.TOP_0,"left_0": GraspType.LEFT_0,"right_0": GraspType.RIGHT_0,"front_270": GraspType.FRONT_270}
#we need a plan with all option motion param combinations options are defined as action_type + object, motion params are defined as grasp types, available grasp types are TOP_0, LEFT_0, RIGHT_0, FRONT_270
PLAN_ALL_COMBOS = []
for opt in option_names:
    for motion in motions:
        parts = opt.split("_")
        if parts[0] == "pick":
            obj = "_".join(parts[1:])
            PLAN_ALL_COMBOS.append(
                Action(
                    action_type=ActionType.PICK,
                    obj=obj,
                    target_slot=None,
                    target_pos=None,
                    grasp=motions[motion]
                )
            )
        elif parts[0] == "place":
            slot = "_".join(parts[1:])
            #for place we need to define a target pos, we can use goal slots for goal placements and shop slots for region placements
            if slot in ['/goal_0','/goal_1','/goal_2']:
                target_pos = GOAL_SLOTS[slot]
            else:
                target_pos = SHOP_SLOTS[slot]
            PLAN_ALL_COMBOS.append(
                Action(
                    action_type=ActionType.PLACE,
                    obj=None,
                    target_slot=slot,
                    target_pos=target_pos,
                    grasp=motions[motion]
                )
            )


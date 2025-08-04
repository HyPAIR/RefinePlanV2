import py_trees

from behaviors.pick import Pick
from behaviors.place import Place
from behaviors.is_goal_achieved import IsGoalAchieved
from behaviors.is_obstacle_on_goal import IsObstacleOnGoal

def create_behaviour_tree(scene_state, goal_objects, obstacle_objects,shop_slots, goal_slots,):
    root = py_trees.composites.Selector(name="PickPlaceRoot",memory=True)

    blackboard = py_trees.blackboard.Client(name="bt")
    blackboard.register_key(key="current_action", access=py_trees.common.Access.WRITE)
    blackboard.register_key(key="current_action", access=py_trees.common.Access.READ)
    blackboard.current_action = None
    
    #check if goal is already complete
    goal_check = IsGoalAchieved("Check Goal", scene_state)
    root.add_child(goal_check)

    #obstacle removal branches
    for i, obs in enumerate(obstacle_objects):
        sequence = py_trees.composites.Sequence(name=f"Remove {obs}",memory=True)
        check = IsObstacleOnGoal(f"{obs} on goal?",scene_state,obs)
        pick = Pick(f"Pick {obs}",obs,blackboard)
        place = Place(f"Place {obs}",obs,shop_slots[i%len(shop_slots)],blackboard)
        sequence.add_children([check,pick,place])
        root.add_child(sequence)

    for i,obj in enumerate(goal_objects):
        sequence = py_trees.composites.Sequence(name=f"Place {obj}",memory=True)
        pick = Pick(f"Pick {obj}",obj,blackboard)
        place = Place(f"Place {obj}",obj,goal_slots[i%len(goal_slots)],blackboard)
        sequence.add_children([pick,place])
        root.add_child(sequence)
    
    return root

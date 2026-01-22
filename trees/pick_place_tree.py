import py_trees
from behaviors.action_behaviours import Pick,Place
from behaviors.observation_behaviours import IsObjectOnGoal, IsObjectHeld
def create_behaviour_tree(scene_state,goal_objects,obstacle_objects,shop_slots, goal_slots):
    root = py_trees.composites.Sequence(name='root',memory=True)

    #create a blackboard to keep the current proposed action
    blackboard = py_trees.blackboard.Client(name="bt")
    blackboard.register_key(key="current_action", access=py_trees.common.Access.WRITE)
    blackboard.register_key(key="current_action", access=py_trees.common.Access.READ)
    blackboard.current_action = None
    
    #Create a sequence for each object to check if its in goal and pick and place if not
    for obj in goal_objects:
        #each has two children child 1 : checks if obj is in goal, child 2: picks and places object if child 1 is unsuccessful
        object_sequence = py_trees.composites.Selector(name=f'{obj}_root',memory=True)
        #child 1:
        obj_on_goal = IsObjectOnGoal(name=f'{obj} on goal?',scene_state=scene_state,object_name=obj)
        #child 2: This one is a sequence of two childre, 1: pick the object 2:once pick is successful, place the object
        pick_place_sequence = py_trees.composites.Sequence(name=f'{obj}_pick_place',memory=True)
        #child 2_1:
        is_obj_held = IsObjectHeld(name=f'Is {obj} held?',scene_state=scene_state,object_name=obj)
import py_trees
from behaviors.action_behaviours import Pick,Place
from behaviors.observation_behaviours import IsObjectOnGoal, IsObjectHeld
def create_behaviour_tree(scene_state,goal_objects,shop_slots, goal_slots):
    root = py_trees.composites.Sequence(name='root',memory=True)

    #create a blackboard to keep the current proposed action
    blackboard = py_trees.blackboard.Client(name="bt")
    blackboard.register_key(key="current_action", access=py_trees.common.Access.WRITE)
    blackboard.register_key(key="current_action", access=py_trees.common.Access.READ)
    blackboard.current_action = None
    
    #Create a sequence for each object to check if its in goal and pick and place if not
    for i,obj in enumerate(goal_objects):
        #each has two children child 1 : checks if obj is in goal, child 2: picks and places object if child 1 is unsuccessful
        object_sequence = py_trees.composites.Selector(name=f'{obj}_root',memory=True)
        
        #child 1:
        obj_on_goal = IsObjectOnGoal(name=f'{obj} on goal?',scene_state=scene_state,object_name=obj)
        
        #child 2: This one is a sequence of two children, 1: pick the object 2:once pick is successful, place the object
        pick_place_sequence = py_trees.composites.Sequence(name=f'{obj}_pick_place',memory=True)
        #child 2_1: pick the object 
        pick_sequence = py_trees.composites.Sequence(name=f'{obj}_pick',memory=True)
        #check if objct is held
        is_obj_held = IsObjectHeld(name=f'Is {obj} not held?',scene_state=scene_state,object_name=obj)
        #if not held pick the object
        pick = Pick(name=f'Pick {obj}' ,obj_name=obj,blackboard=blackboard)
        pick_sequence.add_children([is_obj_held,pick])

        #child 2_2:once pick is successful, place the object
        place = Place(f"Place {obj}",obj,goal_slots[i%len(goal_slots)],blackboard)
        #add the childrent of child 2
        pick_place_sequence.add_children([pick_sequence,place])

        #add child1, child 2 to root
        object_sequence.add_children([obj_on_goal,pick_place_sequence])
        root.add_child(object_sequence)
    return root

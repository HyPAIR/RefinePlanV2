from refine_plan.models.state_factor import StateFactor
from refine_plan.models.state import State

shop_slots =["/region_0","/region_1","/region_2"]
goal_slots=["/goal_0","/goal_1","/goal_2"]
goal_objects = ["/column0","/column1","/column2"]
objects_formatted =[obj.replace('/','') for obj in goal_objects]

# def _get_enabled_cond(sf_list, option):
#     """Get the enabled condition for an option.

#     Args:
#         sf_list: The list of state factors
#         option: The option we want the condition for

#     Returns:
#         The enabled condition for the option
#     """
#     #we need to define the enabled conditions for the options as boolean condition expressions based on state factors
#     sf_dict = {sf.get_name(): sf for sf in sf_list}
#     enable = OrCondition()
#     #Rule 1: place actions are only valid if one of the object state factor is "held" and none of the object state factors are the target slot
#     if option[:5] == "place":
#         parts = option.split("_")
#         target_slot = parts[1]+'_'+parts[2]
#         enable = AndCondition(OrCondition(*[EqCondition(sf_dict[obj], "held") for obj in objects_formatted]), AndCondition(*[NeqCondition(sf_dict[obj], target_slot) for obj in objects_formatted]))

#     #Rule 2: pick actions can only be valid if none of the object state factors are "held"
#     if option[:4] == "pick":
#         enable = AndCondition(*[NeqCondition(sf_dict[obj], "held") for obj in objects_formatted])

#     return enable

def state_to_policy_state(state):
    """Convert a SceneState to a State object for policy use.

    Args:
        state: The SceneState object
    Returns:
        The State object
    """

    #object and obstacle state factos # object slots in data
    possible_slots = goal_slots+shop_slots+["held","unknown"]
    possible_slots =[slot.replace('/','') for slot in possible_slots] #Boolean conversion issue
    object_sfs = [StateFactor(obj,possible_slots) for obj in objects_formatted]

    #define state as a state object
    object_sfs_dict = {sf:"unknown" for sf in object_sfs}
    for obj,slot in state["object_slots"].items():
        sf = next((s for s in object_sfs if s.get_name() == obj.replace('/','')),None)
        if sf:
            object_sfs_dict[sf]=slot.replace('/','')
    state_dict = {**object_sfs_dict }    
    policy_state = State(state_dict)
    return policy_state
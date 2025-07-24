from rl.action_space import ActionType,Action

def compute_reward(prev_state,action:Action,next_state):
    reward =0.0
    goal_slots_before = prev_state["goal_region_occupancy"]
    goal_slots_after = next_state["goal_region_occupancy"]

    goal_objects = ['/column0', '/column1', '/column2', '/column3']
    obstacles = ['/obs0', '/obs1']

    if action.action_type == ActionType.PLACE:
        obj = action.obj

        #if object place in the goal slot
        goal_slot = _find_goal_slot(goal_slots_after,obj)
        goal_slot_prev = _find_goal_slot(goal_slots_before,obj)

        if obj in goal_objects:
            if goal_slot is not None and goal_slot_prev is None:
                reward += 1.0 #correctly placed object
        elif obj in obstacles:
            if goal_slot is not None:
                reward -=0.5 #placed obstacle on goal slot
        
    if action.action_type == ActionType.PICK:
        obj = action.obj
        if obj in obstacles:
            slot_brfore = _find_goal_slot(goal_slots_before,obj)
            slot_after = _find_goal_slot(goal_slots_after,obj)
            if slot_brfore is not None and slot_after is None:
                reward+=0.5 #removed obstacle from goal
    
    #if all goals are satisfied
    if _goal_achieved(goal_slots_after,goal_objects):
        reward+=5.0
    return reward

def _find_goal_slot(goal_region_occuppancy:dict,obj):
    for sid, occ in goal_region_occuppancy.items():
        if occ == obj:
            return sid
    return None

def _goal_achieved(goal_region_occuppancy:dict,goal_objects):
    for obj in goal_region_occuppancy.values():
        if obj not in goal_objects:
            return False
    return True


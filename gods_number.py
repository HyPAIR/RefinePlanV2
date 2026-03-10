from collections import deque

def get_gods_number():
    # Configuration: 3 items, 6 slots (0-5)
    # A state is a tuple of slot indices for (item1, item2, item3)
    
    # Define your 6 Goal States (example: items must be in slots 3, 4, 5)
    # We use all permutations of (3, 4, 5) because any item can be in any goal slot
    goals = {(3, 4, 5), (3, 5, 4), (4, 3, 5), (4, 5, 3), (5, 3, 4), (5, 4, 3)}
    
    # Define your 6 Starting States (example: items start in slots 0, 1, 2)
    starts = {(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)}

    queue = deque([(goal, 0) for goal in goals])
    visited = {goal: 0 for goal in goals}
    
    max_distance_to_start = 0

    while queue:
        current_state, dist = queue.popleft()
        
        # Check if this is one of our starting states
        if current_state in starts:
            max_distance_to_start = max(max_distance_to_start, dist)

        # Generate neighbors: Move any of the 3 items to an empty slot
        occupied = set(current_state)
        all_slots = set(range(6))
        empty_slots = all_slots - occupied

        for i in range(3): # For each item
            for empty_slot in empty_slots:
                # Create new state by moving item i to empty_slot
                new_state = list(current_state)
                new_state[i] = empty_slot
                new_state = tuple(new_state)
                
                if new_state not in visited:
                    visited[new_state] = dist + 1
                    queue.append((new_state, dist + 1))
                    
    return max_distance_to_start, max(visited.values())

dist_to_start, total_diameter = get_gods_number()
print(f"Max moves from start to goal: {dist_to_start}")
print(f"Absolute diameter of state space: {total_diameter}")

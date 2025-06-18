from pddlstream.language.generator import from_fn
from pddlstream.language.constants import PDDLProblem
from pddlstream.algorithms.incremental import solve_incremental
from pddlstream.utils import read

from coppelia_client import RoboticsEnvironment

#-----Connect to simulation--------------

# env= RoboticsEnvironment()
# env.connect()
# env.initialize_params()



#---------------------Fake functions-----
def sample_pick_location():
    yield('loc1')
def test_pick_feasibility(r,o,l):
    return True
def test_place_feasibility(r,o,l):
    return True
#-------------PDDLStream setup-----------

domain = read('simulation/src/simulation/simulation/domain.pddl')
problem = read('simulation/src/simulation/simulation/problem.pddl')

stream_map= {
    'sample-pick-loc':from_fn(sample_pick_location),
    'test-pick': from_fn(test_pick_feasibility),
    'test-place':from_fn(test_place_feasibility),
}

pddl_problem = PDDLProblem(domain,stream_map,problem)

#-----solve paln-------
solution = solve_incremental(pddl_problem)
plan,cost,evaluations = solution
print("plan:", plan)

#--Ecextue plan in coppeliasim--------
for action in plan:
    name,args = action[0],action[1:]
    if name=='pick':
        print("picking")
    elif name =='place':
        print('placing')
import py_trees
from simulation.config_planning import RoboticsEnvironment
    
class PickObject(py_trees.behaviour.Behaviour):
    '''
    Behaviour to pick and object
    '''
    def __init__(self,name='pickObject'):
        super().__init__(name=name)
        self.renv = RoboticsEnvironment()
        self.renv.connect()

    def setup(self, **kwargs):
        pass
    #get the object pose from object
    #get object type from object 
    #sample grasp for object
    #caluclate approacn and withdraw transform based on object type and grasp
    #create combined pose vector
    #call the ros action client

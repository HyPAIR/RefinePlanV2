import py_trees
from simulations.sim_interface import RoboticsEnvironment
class GoBackHome(py_trees.behaviour.Behaviour):
    def __init__(self, name="goBackHome"):
        super().__init__(name=name)
        self.renv = None
    def setup(self, **kwargs): 
        self.renv = RoboticsEnvironment()
        self.renv.connect()
        self.renv.initialize_params()
        self.homeConfig = self.renv.getConfig()
    
    def update(self):
        return super().update()
    def terminate(self, new_status):
        return super().terminate(new_status)
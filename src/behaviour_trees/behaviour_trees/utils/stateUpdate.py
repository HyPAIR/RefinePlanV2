import py_trees
class StateUpdate(py_trees.behaviour.Behaviour):
    def __init__(self,name="stateUpdate"):
        super(StateUpdate,self).__init__(name=name)
        self.blackboard = py_trees.blackboard.Client(name="stateUpdater")
        
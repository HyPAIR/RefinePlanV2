#check if all targets are filled
#Target stats free:0, filled:1, blocked:-1
class Target:
    def __init__(self,handle,pose,status):
        self.handle = handle
        self._pose = pose
        self._status = status
    
    def get_pose(self):
        return self._pose
    
    def get_status(self):
        return self.status
    
    def set_status(self,status):
        self._status = status
    
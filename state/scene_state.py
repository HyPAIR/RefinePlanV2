
class SceneState:
    def __init__(self,env):
        self.env = env #coppeliasim interface

        #objectnames from coppeliasim
        self.goal_objects =['/column0','/column1','/column2','/column3']
        self.obstacle_objects =['/obs0','/obs1']
        self.all_objects = self.goal_objects + self.obstacle_objects

        #predefined region slots
        from state.slot_config import SHOP_SLOTS, GOAL_SLOTS
        self.shop_slots = SHOP_SLOTS
        self.goal_slots = GOAL_SLOTS

        # Internal state containers
        self.object_poses = {} #name: (x,y,z,qx,qy,qw)
        self.object_status ={} #name: status_string
        self.gripper_status ={"holding":None}
        self.goal_region_occuppancy ={} # goal_slot_id: object_id or None

    def update(self):
        self._update_object_poses()
        self._update_gripper_status()
        self._update_object_statuses()
        self._update_goal_occuppancy()

    def _update_object_poses(self):
        for obj in self.all_objects:
            self.object_poses[obj] = self.env.get_object_pose(obj)

    def _update_gripper_status(self):
        self.gripper_status["holding"] = self.env.get_grasped_object()
    
    def _update_object_statuses(self):
        """ Determine if each object is held, on shop table, or on goal area"""
        for obj, pos in self.object_poses.items():
            if self.gripper_status["holding"] == obj:
                self.object_status[obj] = "held"
            elif self._is_in_slot(pos,self.shop_slots):
                self.object_status[obj]="shop"
            elif self._is_in_slot(pos,self.goal_slots):
                self.object_status[obj] = "goal"
            else:
                self.object_status[obj] ="unknown"
    
    def _update_goal_occuppancy(self):
        """Track what object (if any) is currently occupying each goal slot"""
        self.goal_region_occuppancy ={sid:None for sid in self.goal_slots}
        for obj,pos in self.object_poses.items():
            sid = self._closest_slots(pos,self.goal_slots)
            if sid is not None:
                self.goal_region_occuppancy[sid]=obj
    
    def _is_in_slot(self,pos,slots,threshold=0.05):
        return self._closest_slot(pos,slots,threshold) is not None
    
    def _closest_slot(self,pos,slots:dict,threshold=0.05):
        for sid, slot_pos in slots.items():
            if self._dist(pos,slot_pos) < threshold:
                return sid
        return None
    
    def _dist(self,p1,p2):
        position1 = p1[:3]
        position2 = p2[:3]
        return sum((a-b)**2 for a,b in zip(position1,position2))**0.5
    
    def get_state(self):
        return {
            "object_poses":self.object_poses.copy(),
            "object_status":self.object_status.copy(),
            "gripper_status":self.gripper_status.copy(),
            "goal_region_occuppancy":self.goal_region_occuppancy.copy()
        }
    
    def get_state_vector(self):
        vec=[]
        for obj in self.all_objects:
            pos = self.object_poses.get(obj,[0,0,0,0,0,0,1])
            vec+=list(pos)#should be list by default
            vec+=self._status_to_onehot(self.object_status.get(obj,"unknown"))
        vec += self._gripper_to_onehot()
        return vec
    
    def _status_to_onehot(self,status):
        mapping={
            "shop":[1,0,0,0],
            "goal":[0,1,0,0],
            "held":[0,0,1,0],
            "unknown":[0,0,0,1],
        }
        return mapping.get(status,[0,0,0,1])
    
    def _gripper_to_onehot(self):
        obj = self.gripper_status.get("holding",None)
        vec =[0]*len(self.all_objects)
        if obj and obj in self.all_objects:
            vec[self.all_objects.index(obj)]=1
        return vec
    
    def is_goal_achieved(self):
        """Returns True if all goal objects are placed correctly"""
        for sid,pos in self.goal_slots.items():
            obj = self.goal_region_occuppancy.get(sid)
            if obj not in self.goal_objects:
                return False
        return True

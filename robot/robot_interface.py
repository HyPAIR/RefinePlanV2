import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math
import random
import numpy as np
import copy
from scipy.spatial.transform import Rotation as R
import sys
try:
    from robot.gripper import Robotiq85F,RG2,Robotiq85New
    from robot.rotation_helper import rename_frame_top_is_world_up
except:
    from gripper import Robotiq85F,RG2,Robotiq85New
    from rotation_helper import rename_frame_top_is_world_up
initConfig = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]

class RoboticsEnvironment():
    def __init__(self,port = 23000):
        self.client = RemoteAPIClient('localhost',port)
        self.sim = self.client.getObject('sim')
        self.simIK = self.client.require('simIK')
        self.simOMPL =self.client.require('simOMPL')
        self.max_ik_attempts = 1
        self.task = None
        
    def connect(self):    
        '''
        Connects to coppeliasim and sets sim parameters
        '''
        self.sim.startSimulation()
        print('connected to simulation')
        self.sim.setStepping(True)
        print('simulation is explicitly stepped')
    
    def stop_simulation(self):
        '''
        stops simulation
        '''
        self.sim.stopSimulation()
    def getObject(self,handle):
        return self.sim.getObject(handle)
    def checkCollision(self,obj1,obj2):
        return self.sim.checkCollision(obj1,obj2)[0]
    def setObjectPhysics(self,obj_handle,enable:bool):
        '''
        Enable or disable physics for an object
        '''
        if enable:
            self.sim.setBoolProperty(obj_handle,'dynamic',True)
            self.sim.setBoolProperty(obj_handle,'respondable',True)
            self.sim.setBoolProperty(obj_handle,'collidable',True)
        else:
            self.sim.setBoolProperty(obj_handle,'dynamic',False)
            self.sim.setBoolProperty(obj_handle,'respondable',False)

    def initialize_params(self):
        '''
        Initialise robot parameters and solver configs
        '''
        self.gripper =RG2(self)##Robotiq85New(self)# Robotiq85F(self)#
        #start with gripper open
        self.gripper.openGripper()


        #get joint handles
        joint_names = ['/UR10/joint'+str(i) for i in range(1,7)]
        self.joints = [self.sim.getObject(joint) for joint in joint_names]
        print('Joint handles retrieved')
        #TODO: get gripper sensor handle
        self.grasped_object = None
        #get tip handle
        self.robotTip = self.sim.getObject('/UR10/tip')
        #get target handle
        self.robotTarget = self.sim.getObject('/UR10/target')
        #get base handle
        self.robotBase=self.sim.getObject('/UR10')
        #get robot left finger
        self.robotLeftFinger = self.gripper.robotLeftFinger#self.sim.getObject('/UR10/ROBOTIQ85/LfingerTipVisible')
        #get robot right finger
        self.robotRightFinger = self.gripper.robotRightFinger#self.sim.getObject('/UR10/ROBOTIQ85/RfingerTipVisible')
        #create a robot collection
        self.robotCollection = self.sim.createCollection()
        self.sim.addItemToCollection(self.robotCollection,self.sim.handle_tree,self.robotBase,0)
        self.pathPlanningMaxtime = 5.0
        self.pathPlanningSimplificationTime=5.0
        self.pathPlanningAlgo = self.simOMPL.Algorithm.RRTConnect#PRM#RRTstar

        #create an object collection for collision checking
        goal_objects = ["/column0","/column1","/column2"]
        # obstacle_objects=["/obs0","/MPO_700"]#
        obstacle_objects=["/obs0","/obs0_collisiondummy","/obs1","/obs1_collisiondummy","/obs2_collisiondummy","/assembly_table","/MPO_700"]
        shop_slots =[f"/region_{i}" for i in range(9)]
        goal_slots=["/goal_1","/goal_2","/goal_4","/goal_5"]
        objects = goal_objects + obstacle_objects
        self.objects = objects
        # self.objectCollection = self.sim.createCollection()
        # for obj in self.objects:
        #     obj_handle = self.sim.getObject(obj)
        #     self.sim.addItemToCollection(self.objectCollection,self.sim.handle_tree,obj_handle,0)

        #IK Motions
        self.ikMaxVel=[0.4,0.4,0.4,1.8] 
        self.ikMaxAccel=[0.8,0.8,0.8,0.9] 
        self.ikMaxJerk=[0.6,0.6,0.6,0.8]

        #FK Motions
        fkVel=80
        fkAccel=80
        fkJerk=80
        
        self.fkMaxVel = [fkVel*math.pi/180]*6
        self.fkMaxAccel = [fkAccel*math.pi/180]*6
        self.fkMaxJerk =[fkJerk*math.pi/180]*6
        # UR10e factory joint speed limits (deg/s)
        # fkVelDeg = [120, 120, 180, 180, 180, 180]

        # # Conservative accelerations for good tracking (deg/s^2)
        # fkAccelDeg = [200, 200, 300, 300, 300, 300]

        # self.fkMaxVel = [
        #     fkVelDeg[0] * math.pi / 180,
        #     fkVelDeg[1] * math.pi / 180,
        #     fkVelDeg[2] * math.pi / 180,
        #     fkVelDeg[3] * math.pi / 180,
        #     fkVelDeg[4] * math.pi / 180,
        #     fkVelDeg[5] * math.pi / 180
        # ]

        # self.fkMaxAccel = [
        #     fkAccelDeg[0] * math.pi / 180,
        #     fkAccelDeg[1] * math.pi / 180,
        #     fkAccelDeg[2] * math.pi / 180,
        #     fkAccelDeg[3] * math.pi / 180,
        #     fkAccelDeg[4] * math.pi / 180,
        #     fkAccelDeg[5] * math.pi / 180
        # ]

    
    def resetCollection(self):
        self.sim.destroyCollection(self.robotCollection)
        robotCollection = self.sim.createCollection()
        self.sim.addItemToCollection(robotCollection,self.sim.handle_tree,self.robotBase,0)
        self.robotCollection = robotCollection

    def enableGripperCollision(self,enable:bool):
        if isinstance(self.gripper,RG2):
            return
        else:
            if enable:
                self.sim.setBoolProperty(self.robotLeftFinger,'collidable',True)
                self.sim.setBoolProperty(self.robotRightFinger,'collidable',True)
            else:
                self.sim.setBoolProperty(self.robotLeftFinger,'collidable',False)
                self.sim.setBoolProperty(self.robotRightFinger,'collidable',False)
    def getConfig(self):
        '''
        gets current robot configuration 

        Input: None
        Output: c space variable configuration q of dimention 1xn_joints
        '''
        return [self.sim.getJointPosition(joint) for joint in self.joints]
    def getTipPose(self):
        '''
        gets the current robot Tip pose

        Input: None
        output: a pose vector for current robot tip pose
        '''
        return self.sim.getObjectPose(self.robotTip)
    

    def collides(self,target_configs):
        '''
        checks if any configuration self collides
        input: List of configurations
        output:bool collision 
        '''
        scriptHandle = self.sim.getScript(self.sim.scripttype_customization,'collisionCheck@Scene')
        collision = self.sim.callScriptFunction(
            'collides',
            scriptHandle,
            self.robotCollection,
            target_configs,
            self.joints
        )
        return collision

    def setConfig(self,config):
        '''
        sets joint position to given configuration
        '''
        scriptHandle = self.sim.getScript(self.sim.scripttype_customization,'collisionCheck@Scene')
        self.sim.callScriptFunction(
            'setConfig',
            scriptHandle,
            config,
            self.joints
        )

    def setTargetConfig(self,c):
        for i in range(len(self.joints)):
            self.sim.setJointTargetPosition(self.joints[i],c[i])
    
    def findConfigs(self,pose):
        '''
        returns configurations for the manipultor for given pose
        '''
        ikEnv = self.simIK.createEnvironment()
        ikGroup = self.simIK.createGroup(ikEnv)
        ikEl,simToIk,ikToSim = self.simIK.addElementFromScene(ikEnv,ikGroup,self.robotBase,self.robotTip,self.robotTarget,self.simIK.constraint_pose)
        ikJoints=[simToIk[joint] for joint in self.joints]
        self.sim.setObjectPose(self.robotTarget,pose)
        self.simIK.syncFromSim(ikEnv,[ikGroup])
        p={
            'maxDist':0.28,
            'maxTime':1,
            'cMetric':[8,8,8,0.8,0.6,0.3],
            'findMultiple': True
        }
        retVal = self.simIK.findConfigs(ikEnv,ikGroup,ikJoints,p)
        self.simIK.eraseEnvironment(ikEnv)
        return retVal
    
   
    def selectOneValidConfig(self, configs, approachIKTr, withdrawIkTr):
        """
        Picks the first valid configuration out of available IK configs.
        Stops at the first valid config and removes only tested invalid ones.

        input:
            configs: list of candidate configurations (modified in place)
            approachIKTr: approach IK transform (can be None)
            withdrawIkTr: withdraw IK transform (can be None)
        returns:    
            retVal: first valid configuration (or None if none found)
            passiveVizShape: visualization shape object (or None)
            configs: trimmed list containing the valid config and remaining untested ones
        """
        scriptHandle = self.sim.getScript(self.sim.scripttype_customization,'collisionCheck@Scene')
        # Call the Lua function
        retVal, passiveVizShape, remaining_configs = self.sim.callScriptFunction(
            'selectOneValidConfig',        # Lua function name
            scriptHandle,                 # script handle
            configs,                       # configs table
            approachIKTr or [],           # approach IK transform
            withdrawIkTr or [],            # withdraw IK transform
            self.robotCollection,          # robot collection handle
            self.joints,                   # joint handles
            self.robotBase,                # robot base handle
            self.robotTip,                 # robot tip handle
            self.robotTarget,              # robot target handle
            # self.gripper                   # robot gripper
            
        )

        #TODO: Convert Lua output to Python if something special is needed
        if retVal is None:
            return None, None, remaining_configs
        return list(retVal), passiveVizShape, remaining_configs


    def findPath(self,config):
        #set true for joints who's positions are to be used for default values
        useForProjection=[]
        for i in range(len(self.joints)):
            useForProjection.append(i<3 and 1 or 0)  

        self.objectCollection = self.sim.createCollection()
        for obj in self.objects:
            #ignore the object that is being picked or placed
            if self.grasped_object and obj==self.grasped_object:
                print(f'skipping grasped {self.grasped_object}')
                continue
            obj_handle = self.sim.getObject(obj)
            self.sim.addItemToCollection(self.objectCollection,self.sim.handle_tree,obj_handle,0) 
        self.gripperCollection = self.sim.createCollection()
        #add gripper to collection for collision checking if not already added
        self.sim.addItemToCollection(self.gripperCollection,self.sim.handle_tree,self.robotLeftFinger,0) 
        self.sim.addItemToCollection(self.gripperCollection,self.sim.handle_tree,self.robotRightFinger,0)
        gbase = self.sim.getObject('/UR10/RG2/baseVisible')   
        l4vis = self.sim.getObject('/UR10/link4_visible')

        task = self.simOMPL.createTask('task')
        self.task = task
        self.simOMPL.setAlgorithm(task,self.pathPlanningAlgo)
        self.simOMPL.setStateValidityCheckingResolution(task, 0.001)  
        self.simOMPL.setStateSpaceForJoints(task,self.joints,useForProjection)
        collision_pairs = [self.robotCollection,self.robotCollection,self.robotCollection,self.objectCollection,gbase,l4vis]
        if self.grasped_object:
            collision_pairs+=[self.sim.getObject(self.grasped_object),self.objectCollection]
        self.simOMPL.setCollisionPairs(task,collision_pairs)
        self.simOMPL.setStartState(task,self.getConfig())
        self.simOMPL.setGoalState(task,config)
        self.simOMPL.setup(task)
        #self.simOMPL.solve says wether the thing is intialized
        if self.simOMPL.solve(task,self.pathPlanningMaxtime) and self.simOMPL.hasExactSolution(task):
            self.simOMPL.simplifyPath(task,self.pathPlanningSimplificationTime)
            retVal = self.simOMPL.getPath(task)
        else:
            retVal = None
        self.simOMPL.destroyTask(task)
        # if self.dryRunTrajectoryCollision(path=retVal,extra_interp=0):
            # return None
        self.sim.destroyCollection(self.objectCollection)
        return retVal

    def dryRunTrajectoryCollision(self, path, extra_interp=10):
        scriptHandle = self.sim.getScript(self.sim.scripttype_customization,'dryRun@Scene')
        collision = self.sim.callScriptFunction(
            'dryRunTrajectoryCollision',
            scriptHandle,
            self.robotCollection,
            self.objectCollection,
            self.joints,
            path,
            self.fkMaxVel,
            self.fkMaxAccel,
            extra_interp,
        )
        
        return collision # True means collision-free


    def followPath(self, path):
        # Compute trajectory timing etc. (same as before)
        startTime =time.time()
        minMaxVel = []
        for vel in self.fkMaxVel:
            minMaxVel += [-vel, vel]
        minMaxAcc = []
        for acc in self.fkMaxAccel:
            minMaxAcc += [-acc, acc]

        pl, _ = self.sim.getPathLengths(path, 6)
        pathPts, times, _ = self.sim.generateTimeOptimalTrajectory(
            path, pl, minMaxVel, minMaxAcc, 5000, 'not-a-knot', 5, None
        )

        # Pack and send to Lua
        self.sim.setStringSignal('FollowPathSignal', self.sim.packTable(pathPts))
        self.sim.setStringSignal('FollowPathTimes', self.sim.packTable(times))

        # Wait for Lua to finish execution
        while not self.sim.getStringSignal('FollowPathDone'):
            self.sim.step()  # advance simulation manually if stepping
            if time.time() - startTime > 60:
                print('[ERROR] Timeout while waiting for FollowPath to complete.')
                self.sim.clearStringSignal('FollowPathSignal')
                self.sim.clearStringSignal('FollowPathTimes')
                self.sim.setStringSignal('FollowPathDone', '1')
                self.sim.clearStringSignal('FollowPathDone')
                self.sim.step()
                
                #
                #reset scene
                reset_status = False
                self.sim.stopSimulation()
                time.sleep(5)
                for joint,position in zip(self.joints,initConfig):
                    self.sim.setJointTargetPosition(joint,position)
                self.sim.startSimulation()
                self.sim.setStepping(True)
                reset_status = True
                if self.sim.getSimulationState() == self.sim.simulation_stopped:
                    time.sleep(1)
                    self.sim.startSimulation()
                    self.sim.setStepping(True)
                break
        self.sim.clearStringSignal('FollowPathDone')

        # Return total trajectory duration
        return times[-1]



    def moveToPose(self,pose):
        '''
        This works based on the rucking trajectory generator
        Interpolation between current pose and target pose. No planning
        '''
        p={
            'ik' :{
                'tip' : self.robotTip,
                'target' : self.robotTarget,
                'base' : self.robotBase,
                'joints' : self.joints
            },
            'targetPose' : pose,
            'maxVel' : self.ikMaxVel,
            'maxAccel' : self.ikMaxAccel,
            'maxJerk' : self.ikMaxJerk 
        }
        # self.sim.setStringSignal('moveToPoseSignal',self.sim.packTable(p))
        self.sim.moveToPose(p)

    def ActionPick(self, obj_name, pickPose, approachIKTr, withdrawIkTr):
        """
        Action to pick objects (does not close the gripper).
        Repeatedly queries selectOneValidConfig until a reachable config is found.
        """
        configs = self.findConfigs(pickPose)
        duration = 0.001
        if not configs:
            print('[ERROR] No IK configurations found for desired pick pose.')
            return 0,duration

        print(f'\n[INFO] Found {len(configs)} potential configurations.')

        passiveVizShape = None
        iteration = 0   
        while configs and iteration < self.max_ik_attempts:
            # get the first valid config (and trimmed configs list)
            pickConfig, passiveVizShape, configs = self.selectOneValidConfig(configs, approachIKTr, withdrawIkTr)

            if pickConfig is None:
                print('[WARN] No valid configuration found (all tested configs invalid).')
                return 0,duration

            # try to plan a path to this config
            path = self.findPath(pickConfig)
            if path and path is not None:
                # found a reachable config -> proceed with pick
                break


            # If path not found: discard this config and its viz, then retry
            print('[WARN] No path found to picked config, discarding and trying next valid config...')
            if passiveVizShape:
                try:
                    self.sim.removeObjects([passiveVizShape])

                except Exception:
                    pass
                passiveVizShape = None

            # remove the problematic config (first element) so next selectOneValidConfig won't return it
            if configs:
                # note: selectOneValidConfig returns configs starting with the returned valid config,
                # so after failing on pickConfig we should remove it (it would be configs[0])
                configs.pop(0)
            else:
                # no configs left
                print('[ERROR] No more configs to try.')
                return 0,duration
            iteration += 1
        if iteration >= self.max_ik_attempts:
            print('[ERROR] Max IK attempts reached, pick action failed.')
            return 0,duration
        if path is None:
            print('[ERROR] No reachable configuration found for pick action.')
            return 0,duration
        # if we reach here, path exists
        if passiveVizShape:
            # optional: keep or remove; remove to avoid clutter
            try:
                self.sim.removeObjects([passiveVizShape])
                
            except Exception:
                pass

        print(f'[INFO] Selected reachable configuration: {pickConfig}')
        print('[INFO] Executing path to pick position...')
        duration =self.followPath(path)
        self.sim.wait(0.1)

        # Approach and grasp sequence
        pose = self.sim.getObjectPose(self.robotTip)
        pose = self.sim.multiplyPoses(pose, approachIKTr)
        #gripper normally open
        gripper = self.gripper
        #TODO: comment this if the open again is not being selected
        gripper.openGripper()
        self.sim.wait(2.2)
        #disable gripper collision for approach
        self.enableGripperCollision(False)
        self.moveToPose(pose)

        # Close the gripper and attach object
        #close gripper
        target_obj = self.sim.getObject(obj_name)
        isGrasped =gripper.closeGripper(target_obj)
        #self.sim.wait(2.2)#not necesary when we dont close
        # gripper.openGripper()
        # self.sim.wait(0.00001)
        #fail the operation if grasp failed
        if not isGrasped:
            print('[ERROR] Grasping failed, object not within gripper.')
            self.gripper.openGripper()
            self.sim.wait(2.2)
            self.enableGripperCollision(True)
            return 0,duration
        # attach object to the collection tip to include it in further path planning calculations
        # parent to robottip
        target_obj = self.sim.getObject(obj_name)
        self.sim.setObjectParent(target_obj,self.robotTip,True)
        # Add to collection
        self.sim.addItemToCollection(self.robotCollection,self.sim.handle_tree, target_obj,0)
        #disable object physics

        self.setObjectPhysics(target_obj,False)
       

        # Withdraw
        pose = self.sim.getObjectPose(self.robotTip)
        pose = self.sim.multiplyPoses(pose, withdrawIkTr)
        self.moveToPose(pose)
        tip_position = self.sim.getObjectPosition(self.robotTip)
        target_obj_position = self.sim.getObjectPosition(target_obj)
        #if object is obstcle0 and grasp is top grasp use the dummy to get target obj position

        tip_distance = np.linalg.norm(np.array(tip_position) - np.array(target_obj_position))
        tip_distance_threshold = 0.15  # 15 cm threshold
        #print tip distance
        print(f'Tip distance after pick: {tip_distance}')
        if tip_distance > tip_distance_threshold:
            print('[ERROR] Grasped object lost during pick action.')
            #Unparent            
            self.sim.setObjectParent(target_obj,-1,True)
            # self.sim.setBoolProperty(target_obj,'dynamic',True)
            self.gripper.openGripper()
            self.sim.wait(2.2)
            self.enableGripperCollision(True)
            return 0,duration
        
        print('[INFO] Pick action completed successfully.')
        return 1,duration


    def ActionPlace(self, target_obj, placePose, approachIkTr, withdrawIkTr):
        """
        Action to place objects. Uses selectOneValidConfig repeatedly until a reachable config is found.
        """
        duration = 0.001
        #disable gripper collision for place
        self.enableGripperCollision(False)
        configs = self.findConfigs(placePose)
        if not configs:
            print('[ERROR] No IK configurations found for desired place pose.')
            return 0,duration

        print(f'\n[INFO] Found {len(configs)} potential configurations.')

        passiveVizShape = None
        #set a max iteration to avoid long loops
        iteration = 0
        while configs and iteration < self.max_ik_attempts:
            placeConfig, passiveVizShape, configs = self.selectOneValidConfig(configs, approachIkTr, withdrawIkTr)

            if placeConfig is None:
                print('[WARN] No valid configuration found (all tested configs invalid).')
                return 0,duration

            path = self.findPath(placeConfig)
            if path:
                break

            # no path -> discard this config and its viz, then retry
            print('[WARN] No path found to selected place config, discarding and trying next valid config...')
            if passiveVizShape:
                try:
                    self.sim.removeObjects([passiveVizShape])
                except Exception:
                    pass
                passiveVizShape = None

            if configs:
                configs.pop(0)
            else:
                print('[ERROR] No more configs to try.')
                return 0,duration
            iteration += 1

        # proceed with placement
        if passiveVizShape:
            try:
                self.sim.removeObjects([passiveVizShape])
                # pass
            except Exception:
                pass
        if path is None:
            print('[ERROR] No reachable configuration found for place action.')
            return 0,duration

        if path is None:
            print('[ERROR] No reachable configuration found for place action.')
            return 0,duration
        print(f'[INFO] Selected reachable configuration: {placeConfig}')
        print('[INFO] Executing path to place position...')
        #get the target handle
        target_handle = self.sim.getObject(target_obj)
        self.sim.wait(1)
        #turn of object physics
        self.sim.setBoolProperty(target_handle,'dynamic',False)
        duration =self.followPath(path)
        self.sim.wait(1)

        # Approach and release sequence
        pose = self.sim.getObjectPose(self.robotTip)
        pose = self.sim.multiplyPoses(pose, approachIkTr)
        gripper = self.gripper
        self.moveToPose(pose)
        #re enable object physics
        self.setObjectPhysics(target_handle,True)
        gripper.openGripper()
        self.sim.wait(2.2)
        # Remove object form the collision collection and parenting
        #Unparent
        self.sim.setObjectParent(target_handle,-1,True)
        # Re-enable gripper collision
        self.enableGripperCollision(True)
        # self.sim.removeItemFromCollection(self.robotCollection,self.sim.handle_tree,target_handle)
        self.resetCollection()

        # Withdraw from place
        pose = self.sim.getObjectPose(self.robotTip)
        pose = self.sim.multiplyPoses(pose, withdrawIkTr)
        self.moveToPose(pose)

        print('[INFO] Place action completed successfully.')
        return 1 , duration



    def GoToPose(self,targetPose):

        '''
        Action to pick objects (does not close the gripper )
        '''
        #fing possible configurations
        configs = self.findConfigs(targetPose)
        #if more than one configuration is present, pick a valid one 
        approachIKTr = [0,0,0,0,0,0,1]
        withdrawIktr = [0,0,0,0,0,0,1]
        n_configs=len(configs)
        if n_configs>0:
            #A funciton to select valid configurations
            print(f'\n[INFO]Found {n_configs} potential configurations')
            pickConfig,passiveVizShape = self.selectOneValidConfig(configs,approachIKTr,withdrawIktr)
            if pickConfig is None:
                path = None
                print('Failed to find a valid configuration for the desired pick')
                return 0
            # self.sim.step()
            print(f'selected configuration: {pickConfig}')
            #plan path to the selected configuration
            path = self.findPath(pickConfig)
            if passiveVizShape:
                self.sim.removeObjects([passiveVizShape])
            if path:
                print(f'\n[INFO]Found a path from current config to target config')
                #follow the path
                self.sim.wait(1)
                duration =self.followPath(path)
                self.sim.wait(1)
                #delete the visualization
            
            return 1
        else:
            print('[WARN] Failed to find a valid configuration for the desired pick')
            return 0   
    def HomeArm(self,initConfig):
        #initial configuaration is already valid 
        path = self.findPath(initConfig)
        if path:
            print("\n[INFO]Found a path to initial configuration")
            self.followPath(path)
            self.sim.wait(1)
            return 1
        print("[WARN]No valid path to initial config")
        return 0


    def PlotGrasp(self,graspPose):
        #find possible configs
        configs = self.findConfigs(graspPose)
        if len(configs)>500:
            configs = configs[:500]
        n_configs = len(configs)
        if n_configs>0:
            print(f'Found {n_configs} configurations')
            _, passiveVizshape = self.selectOneValidConfig(configs,[0,0,0,0,0,0,1],[])
            print(f'Ploted grasp Pose {graspPose}')
            self.sim.step()

    def GetTargetStats(self,TargetList:list,ObjectList:list,ObstacleList:list)->dict:
        #initialise all targets empty
        n_targets= len(TargetList)
        status_values= [0]*n_targets
        goal_status = dict(zip(TargetList,status_values))
        i=0
        while i < n_targets:
            #if collision with obstacle, set status to -1
            for obstacle in ObstacleList:
                target = TargetList[i]
                if self.checkCollision(obstacle,target):
                    goal_status[target]=-1
                    ObstacleList.remove(obstacle)
                    i+=1    
            #if collision with object, set status to 1
            for object in ObjectList:
                target= TargetList[i]
                if self.checkCollision(object,target):
                    goal_status[target]=1
                    ObjectList.remove(object)
                    i+=1
        return goal_status
    #State functions

    def reset_scene(self,objects,objectPoses,arm_config,domain_randomization=False):
        '''
        Reset the scene to starting state

        '''
        reset_status = False
        self.sim.stopSimulation()
        time.sleep(5)
        # self.sim.closeScene()
        # time.sleep(1)
        # import os
        # cwd = os.getcwd()
        # print(f'Current working directory: {cwd}')
        # self.sim.loadScene(f'{cwd}/scenes/cubic_objects_scene_new_problem.ttt')
        for joint,position in zip(self.joints,arm_config):
            self.sim.setJointTargetPosition(joint,position)
        self.sim.startSimulation()
        self.sim.setStepping(True)
        reset_status = True
        if self.sim.getSimulationState() == self.sim.simulation_stopped:
            time.sleep(1)
            self.sim.startSimulation()
            self.sim.setStepping(True)
        #reset the robot first before objects to avoid collisions
        # self.HomeArm(arm_config)
        #reset object poses
        #randomize domain
        if domain_randomization:
            random.shuffle(objectPoses) #For domain randomization
        object_handles = [self.sim.getObject(obj) for obj in objects]  
        reset_status =[self.sim.setObjectPose(handle,pose) for handle,pose in zip(object_handles,objectPoses)]
        self.gripper.openGripper()
        self.grasped_object = None
        self.sim.wait(2.2)
        self.sim.step()
      
        return reset_status
    
    def test_motion_planner(self):
        useForProjection=[]
        for i in range(len(self.joints)):
            useForProjection.append(i<3 and 1 or 0)  
        #get current config
        task = self.simOMPL.createTask('test_task')
        self.simOMPL.setAlgorithm(task,self.pathPlanningAlgo)
        self.simOMPL.setStateSpaceForJoints(task,self.joints,useForProjection)
        self.simOMPL.setCollisionPairs(task,[self.robotCollection,self.robotCollection])
        self.simOMPL.setStartState(task,self.getConfig())
        self.simOMPL.setGoalState(task,self.getConfig())
        self.simOMPL.setup(task)
        return self.simOMPL.solve(task,self.pathPlanningMaxtime)
        

    def get_object_pose(self,obj):
        '''
        Return quaternian object pose, given object name in coppeliasim scene
        input: String object name: /obj
        output: list [x,y,z,qx,qy,qz,qw]
        '''
        objectHandle = self.sim.getObject(obj)
        objectPose = self.sim.getObjectPose(objectHandle)
        return objectPose
    
    def set_object_pose(self,obj,pose):
        '''
        Set object pose, given object name in coppeliasim scene
        input: String object name: /obj
               list pose: [x,y,z,qx,qy,qz,qw]
        output: bool success
        '''
        objectHandle = self.sim.getObject(obj)
        success = self.sim.setObjectPose(objectHandle,pose)
        return success
    
    def get_grasped_object(self):
        return self.grasped_object

    
   
    def rotate_for_grasp(self, grasp_value: str, objPose):
        # Split grasp type into direction and roll
        direction_str, roll_str = grasp_value.split("_")
        roll = float(roll_str)

        # Base orientations relative to object frame
        base_orientations = {
            "top":    [0, 0, 0],      # approach from +Z of object
            "bottom": [180, 0, 0],    # approach from -Z
            "front":  [90, 0, 0],     # approach from +Y
            "back":   [-90, 0, 0],    # approach from -Y
            "left":   [0, -90, 0],    # approach from -X
            "right":  [0, 90, 0],     # approach from +X
        }

        # Object's current rotation
        R_obj = R.from_quat(objPose[3:7])
        
        # Grasp rotation relative to object
        R_grasp_rel = R.from_euler('xyz', base_orientations[direction_str], degrees=True) \
                    * R.from_euler('z', roll, degrees=True)

        # Final rotation = object rotation * grasp relative rotation
        R_final = R_obj * R_grasp_rel

        # Update pose quaternion
        objPose[3:7] = R_final.as_quat()
        return R_final,objPose

    def pick(self, obj_name, grasp_value: str):
        """
        Pick the object using a specified grasp type.
        """
        # Get object pose
        objHandle = self.sim.getObject(obj_name)
        direction_str, _ = grasp_value.split("_")
        objPose = self.sim.getObjectPose(objHandle)  # [x, y, z, qx, qy, qz, qw]
        [x, y, z, qx, qy, qz, qw] = objPose
        #this pose is not always local z up 
        q_world_cprime, R_c_to_cprime, best_face = rename_frame_top_is_world_up(qx=qx, qy=qy, qz=qz, qw=qw)
        objPose = objPose[:3]+list(q_world_cprime)
  

        # Rotate object pose based on grasp
        R_final, objPose = self.rotate_for_grasp(grasp_value, objPose)

        # Offset the pick position slightly above the object for path planning
        planned_path_offset = 0.060
        #Calculating approach at a distance for path plan
        objPose[:3] = R_final.apply([0,0,planned_path_offset])+objPose[:3]
        table_contact_tolerance =0.02
        objPose[2]+=table_contact_tolerance
    
        # Define approach and withdraw transforms in gripper-local frame
        # Approach along global -Z axis (in gripper-local frame)
        approachIKTr = [0, 0, -0.050, 0, 0, 0, 1]
        # Withdraw along global +Z axis (in gripper-local frame)
        withdraw_vec_world = np.array([0, 0, 0.1])
        withdraw_vec_local = R_final.inv().apply(withdraw_vec_world)

        withdrawIkTr = [
            withdraw_vec_local[0],
            withdraw_vec_local[1],
            withdraw_vec_local[2],
            0, 0, 0, 1
        ]

        #rotate withdraw transform to align with original object orientation
        outcome,duration = self.ActionPick(
            obj_name=obj_name,
            pickPose=objPose,
            approachIKTr=approachIKTr,
            withdrawIkTr=withdrawIkTr
        )
        if outcome:
            self.grasped_object = obj_name

        return outcome,duration



    def place(self, obj_name, target_pos, grasp_value: str):
        """
        Function to place object at a target position, always restoring the object's
        original upright orientation before approach.
        """
        #define the final pose assuming correct orientation based on traget position
        target_pose = target_pos+[0,0,0,1]
        #add offset to set object above place position
        target_pose[2]+=0.18
       
        #to correct for the grip taken, rotate the target pose to gripper coordinates
        R_final,target_pose = self.rotate_for_grasp(grasp_value,target_pose)
        direction_str, _ = grasp_value.split("_")
        
        # Approach along global -Z axis (in gripper-local frame)
        #top grasp has smaller approach distance
        approach_vec_world=np.array([0,0,-0.05])
        approach_vec_local = R_final.inv().apply(approach_vec_world)
        approachIkTr = [
            approach_vec_local[0],
            approach_vec_local[1],
            approach_vec_local[2],
            0, 0, 0, 1
        ]
        # Withdraw along global +Z axis (in gripper-local frame)
        withdraw_vec_world = np.array([0, 0, 0.3])
        withdraw_vec_local = R_final.inv().apply(withdraw_vec_world)

        withdrawIkTr = [
            withdraw_vec_local[0],
            withdraw_vec_local[1],
            withdraw_vec_local[2],
            0, 0, 0, 1
        ]
        # --- 5. Execute the place action ---
        outcome,duration = self.ActionPlace(
            target_obj = obj_name,
            placePose=target_pose,
            approachIkTr=approachIkTr,
            withdrawIkTr=withdrawIkTr
        )


        # --- 6. Cleanup ---
        if outcome:
            print(f'realigning placed object {obj_name} to target position')
            self.sim.setObjectPose(self.sim.getObject(obj_name),target_pos[:3]+[0,0,0,1])
            self.sim.step()
            self.grasped_object = None

        return outcome,duration
    def push(self,obj_name,target_pos):
        outcome=None
        duration=None
        return outcome,duration
    def leave_object(self, action):
        '''
        Function to leave the object being held without placing it at a target
        '''
        gripper = self.gripper
        if self.grasped_object is not None:
            target_obj = self.sim.getObject(self.grasped_object)
            #Unparent
            self.sim.setObjectParent(target_obj,-1,True)
            # self.sim.setBoolProperty(target_obj,'dynamic',True)
        gripper.openGripper()
        self.sim.wait(2)
        # Re-enable gripper collision
        self.enableGripperCollision(True)
        # Remove object form the collision collection and parenting
        self.resetCollection()
        self.grasped_object = None
        return 1

def main():
    env = RoboticsEnvironment(port=23000)
    env.connect()
    env.initialize_params()
    # initConfig = env.getConfig()
    initConfig = [-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]
    #get a pick pose
    # pickItem = env.sim.getObject('/pickPose')
    # pickPose = env.sim.getObjectPose(pickItem)
    # pickPose[2]+=0.1
    #the appoach and withdrawal transforms have distance as pose transform
    # print(f"pickPose {pickPose}")
    # outcome_pick = env.ActionPick(pickPose,[ 0,0,-0.10, 0, 0, 0, 1],[0,0,0.10, 0, 0, 0, 1])
    # placeTarget = env.sim.getObject('/placePose')
    # placePose =env.sim.getObjectPose(placeTarget)
    # placePose[0]+=0.6
    # outcome_place = env.ActionPlace(placePose,[ -0.10,0,0, 0, 0, 0, 1])
    #pick the item
    # env.setConfig(initConfig)
    # env.sim.step()
    # q = input('Quit ?')
    env.setConfig(initConfig)
    env.sim.step()
    GOAL_SLOTS ={
    '/goal_0': [-0.2749999999999999, 0.825, 0.5],
    '/goal_1': [-0.275, 1.0250000000000006, 0.5],
    '/goal_2': [-0.6000000000000001, 0.825, 0.5],
    }
    env.pick('/column2','front_270')
    # env.place('/column0',GOAL_SLOTS['/goal_0'],'front_270')
    # env.pick('/column0','right_0')
    # env.pick(obj_name='/column2',grasp_value='top_0')
    # env.place(obj_name='/column2',target_pos=GOAL_SLOTS['/goal_2'],grasp_value='right_0')
    # env.pick(obj_name='/column0',grasp_value='left_0')
    # env.place(obj_name='/column0',target_pos=GOAL_SLOTS['/goal_1'],grasp_value='top_0')
    # env.pick(obj_name='/column1',grasp_value='front_270')
    # env.place(obj_name='/column1',target_pos=GOAL_SLOTS['/goal_0'],grasp_value='top_0')
    env.stop_simulation()
    

if __name__ == '__main__':
    main()
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math
import random
import numpy as np
import copy
from scipy.spatial.transform import Rotation as R
try:
    from robot.gripper import Robotiq85F
except:
    from gripper import Robotiq85F

class RoboticsEnvironment():
    def __init__(self):
        self.client = RemoteAPIClient('localhost',23000)
        self.sim = self.client.getObject('sim')
        self.simIK = self.client.require('simIK')
        self.simOMPL =self.client.require('simOMPL')
        
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
    def initialize_params(self):
        '''
        Initialise robot parameters and solver configs
        '''

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
        #create a robot collectoin
        self.robotCollection = self.sim.createCollection()
        self.sim.addItemToCollection(self.robotCollection,self.sim.handle_tree,self.robotBase,0)
        self.pathPlanningMaxtime = 1.0
        self.pathPlanningSimplificationTime=2.0
        self.pathPlanningAlgo = self.simOMPL.Algorithm.RRTConnect#PRM#RRTstar

        self.gripper = Robotiq85F(self)

        #IK Motions
        self.ikMaxVel=[0.4,0.4,0.4,1.8]
        self.ikMaxAccel=[0.8,0.8,0.8,0.9]
        self.ikMaxJerk=[0.6,0.6,0.6,0.8]

        #FK Motions
        fkVel=180
        fkAccel=40
        fkJerk=80
        
        self.fkMaxVel = [fkVel*math.pi/180]*6
        self.fkMaxAccel = [fkAccel*math.pi/180]*6
        self.fkMaxJerk =[fkJerk*math.pi/180]*6

    def resetCollection(self):
        self.sim.destroyCollection(self.robotCollection)
        robotCollection = self.sim.createCollection()
        self.sim.addItemToCollection(robotCollection,self.sim.handle_tree,self.robotBase,0)
        self.robotCollection = robotCollection

    
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
        retVal = False
        bufferedConfig = self.getConfig()
        for target in target_configs:
            self.setConfig(target)
            res = self.sim.checkCollision(self.robotCollection,self.sim.handle_all)[0]
            if res >0:
                retVal = True
                break
            else:
                res= self.sim.checkCollision(self.robotCollection,self.robotCollection)[0]
                if res >0:
                    retVal = True
                    break
        self.setConfig(bufferedConfig)
        return retVal
    def setConfig(self,config):
        '''
        sets joint position to given configuration
        '''
        n_joints = len(self.joints)
        for i in range(n_joints):
            self.sim.setJointPosition(self.joints[i],config[i])
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
        import copy
        import numpy as np

        bufferedConfig = self.getConfig()
        retVal = None
        passiveVizShape = None

        i = 0
        while i < len(configs):
            target = configs[i]

            # --- Base collision check ---
            if self.collides([target]):
                print(f"[INFO] Collision in base config {i}, removing.")
                configs.pop(i)
                continue

            print(f"[INFO] Config {i}: no base collision")
            self.setConfig(target)
            target_valid = True

            # --- Approach path check ---
            if approachIKTr:
                pose = self.sim.getObjectPose(self.robotTip)
                targetPose = self.sim.multiplyPoses(pose, approachIKTr)
                self.sim.setObjectPose(self.robotTarget, targetPose)

                ikEnv = self.simIK.createEnvironment()
                ikGroup = self.simIK.createGroup(ikEnv)
                _, simToIk, _ = self.simIK.addElementFromScene(
                    ikEnv, ikGroup, self.robotBase, self.robotTip,
                    self.robotTarget, self.simIK.constraint_pose
                )
                ikJoints = [simToIk[j] for j in self.joints]
                path = self.simIK.generatePath(ikEnv, ikGroup, ikJoints, simToIk[self.robotTip], 4)
                self.simIK.eraseEnvironment(ikEnv)

                if not path:
                    print("[INFO] No valid approach path found, removing config.")
                    configs.pop(i)
                    continue

                path = np.array(path).reshape(-1, len(self.joints))
                if self.collides(path):
                    print("[INFO] Collision in approach path, removing config.")
                    configs.pop(i)
                    continue

            # --- Withdraw path check ---
            if withdrawIkTr:
                targetPose = self.sim.multiplyPoses(targetPose, withdrawIkTr)
                self.sim.setObjectPose(self.robotTarget, targetPose)

                ikEnv = self.simIK.createEnvironment()
                ikGroup = self.simIK.createGroup(ikEnv)
                _, simToIk, _ = self.simIK.addElementFromScene(
                    ikEnv, ikGroup, self.robotBase, self.robotTip,
                    self.robotTarget, self.simIK.constraint_pose
                )
                ikJoints = [simToIk[j] for j in self.joints]
                path = self.simIK.generatePath(ikEnv, ikGroup, ikJoints, simToIk[self.robotTip], 4)
                self.simIK.eraseEnvironment(ikEnv)

                if not path:
                    print("[INFO] No valid withdraw path found, removing config.")
                    configs.pop(i)
                    continue

                path = np.array(path).reshape(-1, len(self.joints))
                if self.collides(path):
                    print("[INFO] Collision in withdraw path, removing config.")
                    configs.pop(i)
                    continue

            # --- If we reach here, config is valid ---
            print(f"[INFO] Config {i} is valid.")
            retVal = target

            # Build visualization for the found config
            objectList = self.sim.getObjectsInTree(self.robotBase, self.sim.sceneobject_shape)
            objectList = [obj for obj in objectList if self.sim.getBoolProperty(obj, 'visible')]
            objectList = self.sim.copyPasteObjects(objectList)
            passiveVizShape = self.sim.groupShapes(objectList, True)

            for prop in ['respondable', 'dynamic', 'collidable', 'measurable', 'detectable']:
                self.sim.setBoolProperty(passiveVizShape, prop, False)
            mesh_handles = self.sim.getIntArrayProperty(passiveVizShape, 'meshes')
            if mesh_handles:
                self.sim.setColorProperty(mesh_handles[0], 'color.diffuse', [1, 0, 0])
            self.sim.setObjectAlias(passiveVizShape, 'passiveVisualizationShape')

            # Keep only this valid config and untested configs
            configs[:] = configs[i:]  
            break

        else:
            print("[WARN] No valid configuration found.")

        self.setConfig(bufferedConfig)
        return retVal, passiveVizShape, configs


    def findPath(self,config):
        #set true for joints who's positions are to be used for default values
        useForProjection=[]
        for i in range(len(self.joints)):
            useForProjection.append(i<3 and 1 or 0)       

        task = self.simOMPL.createTask('task')
        self.simOMPL.setAlgorithm(task,self.pathPlanningAlgo)
        self.simOMPL.setStateSpaceForJoints(task,self.joints,useForProjection)
        self.simOMPL.setCollisionPairs(task,[self.robotCollection,self.sim.handle_all,self.robotCollection,self.robotCollection])
        self.simOMPL.setStartState(task,self.getConfig())
        self.simOMPL.setGoalState(task,config)
        self.simOMPL.setup(task)

        if self.simOMPL.solve(task,self.pathPlanningMaxtime) and self.simOMPL.hasExactSolution(task):
            self.simOMPL.simplifyPath(task,self.pathPlanningSimplificationTime)
            retVal = self.simOMPL.getPath(task)
        else:
            retVal = None
        self.simOMPL.destroyTask(task)
        return retVal
    def followPath(self,path):
        minMaxVel=[]
        for vel in self.fkMaxVel:
            minMaxVel.append(-vel)
            minMaxVel.append(vel)
        minMaxAcc =[]
        for acc in self.fkMaxAccel:
            minMaxAcc.append(-acc)
            minMaxAcc.append(acc)
        pl,_ = self.sim.getPathLengths(path,6)
        try :
            followPathScript = followPathScript
        except:
            followPathScript =-1
        pathPts,times,followPathScript = self.sim.generateTimeOptimalTrajectory(path,pl,minMaxVel,minMaxAcc,1000,'not-a-knot',5,None)
        st = self.sim.getSimulationTime()
        dt =0
        while dt < times[-1]:
            p = self.sim.getPathInterpolatedConfig(pathPts,times,dt)
            self.setTargetConfig(p)
            self.sim.step()
            dt = self.sim.getSimulationTime() -st
        p = self.sim.getPathInterpolatedConfig(pathPts,times,times[-1])
        self.setTargetConfig(p)

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
        self.sim.moveToPose(p)


    def ActionPick(self, obj_name, pickPose, approachIKTr, withdrawIkTr):
        """
        Action to pick objects (does not close the gripper).
        Repeatedly queries selectOneValidConfig until a reachable config is found.
        """
        configs = self.findConfigs(pickPose)
        if not configs:
            print('[ERROR] No IK configurations found for desired pick pose.')
            return 0

        print(f'\n[INFO] Found {len(configs)} potential configurations.')

        passiveVizShape = None
        while configs:
            # get the first valid config (and trimmed configs list)
            pickConfig, passiveVizShape, configs = self.selectOneValidConfig(configs, approachIKTr, withdrawIkTr)

            if pickConfig is None:
                print('[WARN] No valid configuration found (all tested configs invalid).')
                return 0

            # try to plan a path to this config
            path = self.findPath(pickConfig)
            if path:
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
                return 0

        # if we reach here, path exists
        if passiveVizShape:
            # optional: keep or remove; remove to avoid clutter
            try:
                self.sim.removeObjects([passiveVizShape])
            except Exception:
                pass

        print(f'[INFO] Selected reachable configuration: {pickConfig}')
        print('[INFO] Executing path to pick position...')
        self.followPath(path)
        self.sim.wait(1)

        # Approach and grasp sequence
        pose = self.sim.getObjectPose(self.robotTip)
        pose = self.sim.multiplyPoses(pose, approachIKTr)
        gripper = self.gripper
        gripper.openGripper()
        self.sim.wait(2.2)
        self.moveToPose(pose)

        # Close the gripper and attach object
        #close gripper
        target_obj = self.sim.getObject(obj_name)
        gripper.closeGripper(target_obj)
        self.sim.wait(5)
        #TODO:attach object to the collection tip to include it in further path planning calcualtions
        #parent to robottip
        self.sim.setObjectParent(target_obj,self.robotTip,True)
        #Add to collection
        self.sim.addItemToCollection(self.robotCollection,self.sim.handle_single, target_obj,0)

        # Withdraw
        pose = self.sim.getObjectPose(self.robotTip)
        pose = self.sim.multiplyPoses(pose, withdrawIkTr)
        self.moveToPose(pose)

        print('[INFO] Pick action completed successfully.')
        return 1


    def ActionPlace(self, target_obj, placePose, approachIkTr, withdrawIkTr):
        """
        Action to place objects. Uses selectOneValidConfig repeatedly until a reachable config is found.
        """
        configs = self.findConfigs(placePose)
        if not configs:
            print('[ERROR] No IK configurations found for desired place pose.')
            return 0

        print(f'\n[INFO] Found {len(configs)} potential configurations.')

        passiveVizShape = None
        while configs:
            placeConfig, passiveVizShape, configs = self.selectOneValidConfig(configs, approachIkTr, withdrawIkTr)

            if placeConfig is None:
                print('[WARN] No valid configuration found (all tested configs invalid).')
                return 0

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
                return 0

        # proceed with placement
        if passiveVizShape:
            try:
                self.sim.removeObjects([passiveVizShape])
            except Exception:
                pass

        print(f'[INFO] Selected reachable configuration: {placeConfig}')
        print('[INFO] Executing path to place position...')
        self.followPath(path)
        self.sim.wait(1)

        # Approach and release sequence
        pose = self.sim.getObjectPose(self.robotTip)
        pose = self.sim.multiplyPoses(pose, approachIkTr)
        gripper = self.gripper
        self.moveToPose(pose)
        self.sim.wait(0.5)

        gripper.openGripper()
        self.sim.wait(2)
        #TODO: Remove object form the collision collection and parenting
        target_handle = self.sim.getObject(target_obj)
        #Unparent
        self.sim.setObjectParent(target_handle,-1,True)
        # self.sim.removeItemFromCollection(self.robotCollection,self.sim.handle_single,target_handle)
        self.resetCollection()

        # Withdraw from place
        pose = self.sim.getObjectPose(self.robotTip)
        pose = self.sim.multiplyPoses(pose, withdrawIkTr)
        self.moveToPose(pose)

        print('[INFO] Place action completed successfully.')
        return 1



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
                self.followPath(path)
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

    def reset_scene(self,objects,objectPositions,arm_config):
        '''
        Reset the scene to starting state

        '''
        object_handles = [self.sim.getObject(obj) for obj in objects]  
        reset_status =[self.sim.setObjectPosition(handle,position) for handle,position in zip(object_handles,objectPositions)]
        jointPositions = [self.sim.getJointPosition(joint) for joint in self.joints]
        self.setConfig(arm_config)
        self.sim.step()
        return reset_status

    def get_object_pose(self,obj):
        '''
        Return quaternian object pose, given object name in coppeliasim scene
        input: String object name: /obj
        output: list [x,y,z,qx,qy,qz,qw]
        '''
        objectHandle = self.sim.getObject(obj)
        objectPose = self.sim.getObjectPose(objectHandle)
        return objectPose
    
    def get_grasped_object(self):
        return self.grasped_object

    
    # Action functions
    # def pick(self,obj_name, grasp=None):
    #     """
    #     Function to pick the object, given object name
    #     """
    #     objHandle = self.sim.getObject(obj_name)
    #     objPose = self.sim.getObjectPose(objHandle)
    #     #estimating pick pose, approach and withdraw transforms baesd on object pose and grasp type
    #     if grasp is None or grasp == "top":
    #         #move the target to the top of the object and approach from above
    #         rot = Rotation.from_euler('xyz', [0, 0, 0], degrees=True)
    #         objPose[3:7] = rot.as_quat()  # Convert rotation to quaternion
    #         objPose[2] += 0.125  # Move approach target above the object
    #         approachIKTr = [0, 0, -0.10, 0, 0, 0, 1]
    #         withdrawIKTr = [0, 0, 0.10, 0, 0, 0, 1]
    #     elif grasp == "front":
    #         # Move the target to the front of the object and approach from the front
    #         rot = Rotation.from_euler('xyz', [0, 0, 90], degrees=True)
    #         objPose[3:7] = rot.as_quat()  # Convert rotation to quaternion
    #         objPose[2] += 0.125  #
    #     #TODO: This needs to be changed since the position of withdrawal should be based on the grasp as well
    #     objPose[2]+=0.125
    #     #TODO: replace approach and withdraw transforms with calulations based on grasp 
    #     outcome = self.ActionPick(obj_name=obj_name,pickPose=objPose,approachIKTr=[ 0,0,-0.10, 0, 0, 0, 1],withdrawIktr=[ 0,0,0.10, 0, 0, 0, 1])
    #     if outcome:
    #         self.grasped_object = obj_name
    #     return outcome
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
        objPose = self.sim.getObjectPose(objHandle)  # [x, y, z, qx, qy, qz, qw]

        # Rotate object pose based on grasp
        R_final, objPose = self.rotate_for_grasp(grasp_value, objPose)
        direction_str, _ = grasp_value.split("_")

        # Offset the pick position slightly above the object for path planning
        if direction_str == "top":
            planned_path_offset = 0.18
        elif direction_str in ["left", "right"]:
            planned_path_offset = 0.06
        #Calculating approach at a distance for path plan
        objPose[:3] = R_final.apply([0,0,planned_path_offset])+objPose[:3]
    
        # Define approach and withdraw transforms in gripper-local frame
        # Approach along global -Z axis (in gripper-local frame)
        approachIKTr = [0, 0, -0.07, 0, 0, 0, 1]
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
        outcome = self.ActionPick(
            obj_name=obj_name,
            pickPose=objPose,
            approachIKTr=approachIKTr,
            withdrawIkTr=withdrawIkTr
        )

        if outcome:
            self.grasped_object = obj_name

        return outcome


    # def place(self,obj_name,target_pos,grasp_value:str):
    #     """
    #     Function to place object, given name, target_pos
    #     """
        
    #     #we need to oritent the object based on the grasp used to pick it, using target pos as base
    #     Rfinal,target_pos = self.rotate_for_grasp(grasp_value,target_pos)
    #     direction_str, _ = grasp_value.split("_")
        
    #     #objects have to assume original orientation at placement
        
    #     # Offset the place position slightly above the target for path planning
  
        
    #     outcome = self.ActionPlace(
    #         placePose=target_pos,
    #         approachIkTr=[0,0,0.0, 0, 0, 0, 1],
    #         withdrawIkTr=[0,0,0.10, 0, 0, 0, 1]
    #     )
    #     if outcome:
    #         self.grasped_object = None
    #     return outcome
    def place(self, obj_name, target_pos, grasp_value: str):
        """
        Function to place object at a target position, always restoring the object's
        original upright orientation before approach.
        """
        #define the final pose assuming correct orientation based on traget position
        target_pose = target_pos+[0,0,0,1]
        #add offset to set object above place position
        target_pose[2]+=0.25
       
        #to correct for the grip taken, rotate the target pose to gripper coordinates
        R_final,target_pose = self.rotate_for_grasp(grasp_value,target_pose)
        approachIkTr=[0,0,0.0, 0, 0, 0, 1]
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
        outcome = self.ActionPlace(
            target_obj = obj_name,
            placePose=target_pose,
            approachIkTr=approachIkTr,
            withdrawIkTr=withdrawIkTr
        )

        # --- 6. Cleanup ---
        if outcome:
            self.grasped_object = None

        return outcome

def main():
    env = RoboticsEnvironment()
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
    env.pick(obj_name='/column2',grasp_value='left_0')
    # from state.slot_config import GOAL_SLOTS
    env.place(obj_name='/column0',target_pos=[-0.27499999999999986, 0.8250000000000005, 0.4],grasp_value='left_0')
    env.stop_simulation()
    

if __name__ == '__main__':
    main()
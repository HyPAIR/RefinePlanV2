from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math
import random
import numpy as np
import copy
from robot.gripper import Robotiq85F

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
        self.pathPlanningMaxtime = 4.0
        self.pathPlanningSimplificationTime=4.0
        self.pathPlanningAlgo = self.simOMPL.Algorithm.RRTstar

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
    
    def selectOneValidConfig(self,configs,approachIKTr,withdrawIkTr):
        '''
        Picks a valid configuration out of available ik configs

        input: list of configs, approach,withsraw IK transforms
        returns: a valid configuration, a visualisation object
        '''
        bufferedConfig = self.getConfig()
        i=0
        target = configs[i]
        retVal=None
        passiveVizShape = None
        for i in range(len(configs)):
            target = configs[i]
            if not self.collides([target]):
                print("found no collision")    
                self.setConfig(target)

                if approachIKTr:
                    pose = self.sim.getObjectPose(self.robotTip)
                    targetPose = self.sim.multiplyPoses(pose,approachIKTr)
                    self.sim.setObjectPose(self.robotTarget,targetPose)
                    ikEnv = self.simIK.createEnvironment()
                    ikGroup = self.simIK.createGroup(ikEnv)
                    ikEl,simToIk,ikToSim = self.simIK.addElementFromScene(ikEnv,ikGroup,self.robotBase,self.robotTip,self.robotTarget,self.simIK.constraint_pose)
                    ikJoints=[]
                    for joint in self.joints:
                        ikJoints.append(simToIk[joint])
                    
                    path = self.simIK.generatePath(ikEnv,ikGroup,ikJoints,simToIk[self.robotTip],4)
                    self.simIK.eraseEnvironment(ikEnv)
                    if path:
                        #convert path into a list of configs to check for collisions
                        path = np.array(path)
                        c_space_dim = len(self.joints)
                        path = np.resize(path,(path.size//c_space_dim,c_space_dim))
                        #if there is a collision in any of the configs in the path, invalidate target config
                        if self.collides(path):
                            print("Potential collision in projected path")
                            target=None
                        else:
                            #if there is no collision in any of the configs in the path check if witdraw transformation is valid
                            if withdrawIkTr:
                                targetPose = self.sim.multiplyPoses(targetPose,withdrawIkTr)
                                self.sim.setObjectPose(self.robotTarget,targetPose)
                                ikEnv = self.simIK.createEnvironment()
                                ikGroup = self.simIK.createGroup(ikEnv)
                                ikEl,simToIk,ikToSim = self.simIK.addElementFromScene(ikEnv,ikGroup,self.robotBase,self.robotTip,self.robotTarget,self.simIK.constraint_pose)
                                ikJoints=[]
                                for joint in self.joints:
                                    ikJoints.append(simToIk[joint])
                                path = self.simIK.generatePath(ikEnv,ikGroup,ikJoints,simToIk[self.robotTip],4)
                                self.simIK.eraseEnvironment(ikEnv)
                                if path:
                                    path = np.array(path)
                                    path = np.resize(path,(path.size//c_space_dim,c_space_dim))
                                    if self.collides(path):
                                        target=None
                                else:
                                    target = None
                    else:
                        #if there isn't a valid path invalidate target config
                        target = None
                        break
            else:
                print(f"collision in config {i}")
                #collision in base config invalidates target config
                target = None
            
            if target:
                retVal =target
                hand = self.sim.getObject('/UR10/ROBOTIQ85')
                # objectList = self.sim.getObjectsInTree(self.robotBase,self.sim.sceneobject_shape)
                objectList = self.sim.getObjectsInTree(hand,self.sim.sceneobject_shape)
                objectCloneList = copy.deepcopy(objectList)
                objectList =[]
                for obj in objectCloneList:
                    if self.sim.getBoolProperty(obj,'visible'):
                        objectList.append(obj)
                objectList = self.sim.copyPasteObjects(objectList)
                passiveVizShape = self.sim.groupShapes(objectList,True)
                self.sim.setBoolProperty(passiveVizShape, 'respondable',False)
                self.sim.setBoolProperty(passiveVizShape, 'dynamic',False)
                self.sim.setBoolProperty(passiveVizShape,'collidable',False)
                self.sim.setBoolProperty(passiveVizShape,'measurable',False)
                self.sim.setBoolProperty(passiveVizShape,'detectable',False)
                self.sim.setColorProperty(self.sim.getIntArrayProperty(passiveVizShape,'meshes')[0],'color.diffuse',[1,0,0])
                self.sim.setObjectAlias(passiveVizShape,'passiveVisualizationShape')
                break
        self.setConfig(bufferedConfig)
        return retVal,passiveVizShape
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

    #State functions

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

    def ActionPick(self,pickPose,approachIKTr,withdrawIktr):

        '''
        Action to pick objects (does not close the gripper )
        '''
        #fing possible configurations
        configs = self.findConfigs(pickPose)
        #if more than one configuration is present, pick a valid one 
        n_configs=len(configs)
        if n_configs>0:
            #A funciton to select valid configurations
            print(f'Found {n_configs} potential configurations')
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
                print('Found a path from current config to pick config')
                #follow the path
                self.followPath(path)
                self.sim.wait(1)
                #delete the visualization
            #Approach the object
            pose = self.sim.getObjectPose(self.robotTip)
            pose = self.sim.multiplyPoses(pose,approachIKTr)
            #TODO: open the gripper and wait
            gripper = self.gripper
            gripper.openGripper()
            self.sim.wait(2)
            self.moveToPose(pose)
            #close the gripper and hold the item
            gripper.closeGripper(self.sim.getObject('/pillar1'))
            self.sim.wait(5)
            #witdraw from position
            pose = self.sim.getObjectPose(self.robotTip)
            pose = self.sim.multiplyPoses(pose,withdrawIktr)
            self.moveToPose(pose)
            return 1
        else:
            print('Failed to find a valid configuration for the desired pick')
            return 0
    def ActionPlace(self,placePose,approachIkTr,witdrawIkTr):
        '''
        Action to pick objects (does not close the gripper )
        '''
        #fing possible configurations
        configs = self.findConfigs(placePose)
        #if more than one configuration is present, pick a valid one 
        n_configs=len(configs)
        if n_configs>0:
            #A funciton to select valid configurations
            print(f'Found {n_configs} potential configurations')
            placeConfig,passiveVizShape = self.selectOneValidConfig(configs,approachIkTr,witdrawIkTr)
            if placeConfig is None:
                path = None
                print('Failed to find a valid configuration for the desired pick')
                return 0
            # self.sim.step()
            print(f'selected configuration: {placeConfig}')
            #plan path to the selected configuration
            path = self.findPath(placeConfig)
            if passiveVizShape:
                self.sim.removeObjects([passiveVizShape])
            if path:
                print('Found a path from current config to place config')
                #follow the path
                self.followPath(path)
                self.sim.wait(1)
                #delete the visualization
            #Approach the object
            pose = self.sim.getObjectPose(self.robotTip)
            pose = self.sim.multiplyPoses(pose,approachIkTr)
            #TODO: open the gripper and wait
            gripper = self.gripper
            # gripper.disconnect()
            self.moveToPose(pose)
            gripper.openGripper()
            self.sim.wait(2)

            #witdraw from position
            pose = self.sim.getObjectPose(self.robotTip)
            pose = self.sim.multiplyPoses(pose,witdrawIkTr)
            self.moveToPose(pose)
            
            return 1
        else:
            print('Failed to find a valid configuration for the desired place')
            return 0

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
            print(f'Found {n_configs} potential configurations')
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
                print('Found a path from current config to target config')
                #follow the path
                self.followPath(path)
                self.sim.wait(1)
                #delete the visualization
            
            return 1
        else:
            print('Failed to find a valid configuration for the desired pick')
            return 0   
    def HomeArm(self,initConfig):
        #initial configuaration is already valid 
        path = self.findPath(initConfig)
        if path:
            print("Found a paht to inital configuration")
            self.followPath(path)
            self.sim.wait(1)
            return 1
        print("No valid path to initial config")
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
def main():
    env = RoboticsEnvironment()
    env.connect()
    env.initialize_params()
    #get initial robot configuration
    initConfig = env.getConfig()

    #get all regions
    region_handles = [f'/region_{i+1}' for i in range(9)]
    target_handles = [f'/place_plate{i}' for i in range(6)]
    object_handles =[
        '/column0',
        '/column1',
        '/column2',
        '/column3',
        '/Cuboid0',
        '/Cuboid1'   
    ]
    regions = [env.sim.getObject(handle) for handle in region_handles]
    targets = [env.sim.getObject(handle) for handle in target_handles]
    objects = [env.sim.getObject(handle) for handle in object_handles]
    region_positions =[env.sim.getObjectPosition(region) for region in regions]
    '''
    Pick and place something
    #get a pick pose
    pickItem = env.sim.getObject('/pickPose')
    pickPose = env.sim.getObjectPose(pickItem)
    #the appoach and withdrawal transforms have distance as pose transform
    outcome_pick = env.ActionPick(pickPose,[ -0.10,0,0, 0, 0, 0, 1],[0.10,0,0, 0, 0, 0, 1])
    placeTarget = env.sim.getObject('/placePose')
    placePose =env.sim.getObjectPose(placeTarget)
    # placePose[0]+=0.6
    outcome_place = env.ActionPlace(placePose,[ -0.10,0,0, 0, 0, 0, 1])
    #pick the item
    '''
    # for place in regions+targets:
    #     pose = env.sim.getObjectPose(place)
    #     pose[2]+=0.125
    #     outcome_picke = env.GoToPose(pose)

    # home_outcome =env.HomeArm(initConfig)
    def place_objects(objects,region_positions):
        for object,region_position in zip(objects,region_positions):
            env.sim.setObjectPosition(object,region_position)
    for i in range(5):
        random.shuffle(region_positions)
        place_objects(objects,region_positions)
        env.sim.wait(2)
    # q = input('Quit ?')
    env.stop_simulation()

if __name__ == '__main__':
    main()
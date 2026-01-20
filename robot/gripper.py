#Class robotiq pour controller la pince
#The gripper is divided in 2 parts
#a part is controlled in position and moves some dummy targets along
#those dummy targets are for the other part that is controlled with IK

import time 
import numpy as np

class Robotiq85F():

    __CLOSURE_DEFAULT = -0.019
    #contructor
    def __init__(self,API):
        
        self.API = API
        #Position control part
        self.robotiqParam1 = self.API.sim.getObject("/UR10/ROBOTIQ85/active1")
        self.robotiqParam2 = self.API.sim.getObject("/UR10/ROBOTIQ85/active2")
        self.robotLeftFinger = self.API.sim.getObject('/UR10/ROBOTIQ85/LfingerTipVisible')
        self.robotRightFinger = self.API.sim.getObject('/UR10/ROBOTIQ85/RfingerTipVisible')
        #value of closure and openning of the gripper
        #protected values
        self.closure = Robotiq85F.__CLOSURE_DEFAULT
        self.opening = 0
        self.joint_max_force = 5000

        #check that all the handles have been retrieved correctly
        if self.robotiqParam1 == -1 :
            if self.robotiqParam2 == -1 :
                raise Exception('No handle found for neither of robotiq parameters')
            else:
                raise Exception('No hanle found for first robotiq param (active1)')
        elif self.robotiqParam2==-1:
            raise Exception('No handle found for second robotiq param (active2)')
        
        self.simBaseRobotiq = self.API.sim.getObject("/UR10/ROBOTIQ85")
        if self.simBaseRobotiq==-1:
            raise Exception("No handle found for Robotiq")

        #IK control part and checking that the handles have been retrieved correctly
        self.simTip1Robotiq = self.API.sim.getObject("/UR10/ROBOTIQ85/LclosureDummyA")
        self.simTarget1Robotiq = self.API.sim.getObject("/UR10/ROBOTIQ85/LclosureDummyB")
        if self.simTip1Robotiq == -1 :
            if self.simTarget1Robotiq ==-1:
                raise Exception("No handle found for Left tip and target for Robotiq")
            else:
                raise Exception("No handle found for Left tip for Robotiq")
        elif self.simTarget1Robotiq ==-1:
            raise Exception("No handle found for Left target for Robotiq")


        self.simTip2Robotiq = self.API.sim.getObject("/UR10/ROBOTIQ85/RclosureDummyA")
        self.simTarget2Robotiq = self.API.sim.getObject("/UR10/ROBOTIQ85/RclosureDummyB")
        if self.simTip2Robotiq == -1 :
            if self.simTarget2Robotiq ==-1:
                raise Exception("No handle found for Right tip and target for Robotiq")
            else:
                raise Exception("No handle found forRight tip for Robotiq")
        elif self.simTarget2Robotiq ==-1:
            raise Exception("No handle found for Right target for Robotiq")
        
        #### extra handlers - for picking ########
        self.connector = self.API.sim.getObject("/UR10/ROBOTIQ85/attachPoint") #to connect and disconnet the bloc instead of relying on physics
        self.sensor = self.API.sim.getObject('/UR10/ROBOTIQ85/attachProxSensor') #proximity sensor
        
        self.robotiqRealLTip = self.API.sim.getObject('/UR10/ROBOTIQ85/LfingerTip') #Left finger of gripper to check if the gripper closed and touches the bloc
        self.robotiqRealRTip = self.API.sim.getObject('/UR10/ROBOTIQ85/RfingerTip') #Right finger of gripper 
        self.ikEnvRobotiq = self.API.simIK.createEnvironment()

        #A group is the kinematics chain
        #create undamped (the method with pseudo-inverse) and damped (method with least squares) groups for left and right 
        self.ikGroup_undampedRobotiq1 = self.API.simIK.createGroup(self.ikEnvRobotiq)
        self.API.simIK.setGroupCalculation(self.ikEnvRobotiq,self.ikGroup_undampedRobotiq1,self.API.simIK.method_pseudo_inverse,0,10)
        self.API.simIK.addElementFromScene(self.ikEnvRobotiq,self.ikGroup_undampedRobotiq1,self.simBaseRobotiq,self.simTip1Robotiq,self.simTarget1Robotiq,self.API.simIK.constraint_x+self.API.simIK.constraint_z)
        self.ikGroup_dampedRobotiq1 = self.API.simIK.createGroup(self.ikEnvRobotiq)
        self.API.simIK.setGroupCalculation(self.ikEnvRobotiq,self.ikGroup_dampedRobotiq1,self.API.simIK.method_damped_least_squares,0.3,99)
        self.API.simIK.addElementFromScene(self.ikEnvRobotiq,self.ikGroup_dampedRobotiq1,self.simBaseRobotiq,self.simTip1Robotiq,self.simTarget1Robotiq,self.API.simIK.constraint_x+self.API.simIK.constraint_z)

        self.ikGroup_undampedRobotiq2 = self.API.simIK.createGroup(self.ikEnvRobotiq)
        self.API.simIK.setGroupCalculation(self.ikEnvRobotiq,self.ikGroup_undampedRobotiq2,self.API.simIK.method_pseudo_inverse,0,10)
        self.API.simIK.addElementFromScene(self.ikEnvRobotiq,self.ikGroup_undampedRobotiq2,self.simBaseRobotiq,self.simTip2Robotiq,self.simTarget2Robotiq,self.API.simIK.constraint_x+self.API.simIK.constraint_z)
        self.ikGroup_dampedRobotiq2 = self.API.simIK.createGroup(self.ikEnvRobotiq)
        self.API.simIK.setGroupCalculation(self.ikEnvRobotiq,self.ikGroup_dampedRobotiq2,self.API.simIK.method_damped_least_squares,0.3,99)
        self.API.simIK.addElementFromScene(self.ikEnvRobotiq,self.ikGroup_dampedRobotiq2,self.simBaseRobotiq,self.simTip2Robotiq,self.simTarget2Robotiq,self.API.simIK.constraint_x+self.API.simIK.constraint_z)

    
    #Closing or openning the gripper
    #by default the gripper closes
    def closeGripper(self, object_handle):
        
        isClosed = False

        self.API.sim.setJointMaxForce(self.robotiqParam1, self.joint_max_force)  # Example value, adjust as needed
        self.API.sim.setJointMaxForce(self.robotiqParam2, self.joint_max_force)
        
    
        self.API.sim.setJointTargetPosition(self.robotiqParam1,self.closure)
        self.API.sim.setJointTargetPosition(self.robotiqParam2,self.closure)
    

        self.API.sim.step()

        if self.API.simIK.handleGroup(self.ikEnvRobotiq,self.ikGroup_undampedRobotiq1,{"syncWorlds":"true"})!= self.API.simIK.result_success:
            self.API.simIK.handleGroup(self.ikEnvRobotiq,self.ikGroup_dampedRobotiq1,{"syncWorlds":"true"})

        if self.API.simIK.handleGroup(self.ikEnvRobotiq,self.ikGroup_undampedRobotiq2,{"syncWorlds":"true"})!= self.API.simIK.result_success:
            self.API.simIK.handleGroup(self.ikEnvRobotiq,self.ikGroup_dampedRobotiq2,{"syncWorlds":"true"})
    
        # Perform the close operation as usual

        # Get positions of the object and the gripper fingers
        object_position = self.API.sim.getObjectPosition(object_handle, -1)
        ltip_position = self.API.sim.getObjectPosition(self.robotiqRealLTip, -1)
        rtip_position = self.API.sim.getObjectPosition(self.robotiqRealRTip, -1)
        virtual_tip_handle = self.API.sim.getObject("/UR10/tip")
        virtual_tip_position = self.API.sim.getObjectPosition(virtual_tip_handle, -1)
        object_width = 0.05
        # Compute distances between the object and each finger
        dist_left = np.linalg.norm(np.array(object_position) - np.array(ltip_position)) 
        dist_right = np.linalg.norm(np.array(object_position) - np.array(rtip_position))

        #compute distance between object and virtual tip
        dist_virtual_tip = np.linalg.norm(np.array(object_position) - np.array(virtual_tip_position)) 

        # Set a threshold for the grasp
        grasp_threshold = 0.2  # Adjust this value based on your scene scale

        # Check if both fingers are within the threshold distance from the object
        if dist_virtual_tip > grasp_threshold:
            # Fake the grasp by attaching the object to the gripper
            #self.API.sim.setObjectParent(object_handle, self.connector, True)
            
            print(f"Grasp failed: Distances - Left: {dist_left}, Right: {dist_right}")
            isClosed = False
        elif np.linalg.norm(np.array(ltip_position) - np.array(rtip_position)) <0.01:
            print("Grasp failed object could't be gripped")
            #print ltip position
            print(f'ltip position {ltip_position}')
            #print rtip position
            print(f'rtip position {rtip_position}')
            print(abs(dist_left-dist_right))
            isClosed = False

        else:
            print("Grasp confirmed, object attached to the gripper")
            isClosed = True
        
        return isClosed

        # Code for opening the gripper

    def openGripper(self):

        self.API.sim.setJointMaxForce(self.robotiqParam1, self.joint_max_force)  # Example value, adjust as needed
        self.API.sim.setJointMaxForce(self.robotiqParam2, self.joint_max_force)
        
        self.API.sim.setJointTargetPosition(self.robotiqParam1,self.opening)
        self.API.sim.setJointTargetPosition(self.robotiqParam2,self.opening)

        self.API.sim.step()

        if self.API.simIK.handleGroup(self.ikEnvRobotiq,self.ikGroup_undampedRobotiq1,{"syncWorlds":"true"})!= self.API.simIK.result_success:
            self.API.simIK.handleGroup(self.ikEnvRobotiq,self.ikGroup_dampedRobotiq1,{"syncWorlds":"true"})

        if self.API.simIK.handleGroup(self.ikEnvRobotiq,self.ikGroup_undampedRobotiq2,{"syncWorlds":"true"})!= self.API.simIK.result_success:
            self.API.simIK.handleGroup(self.ikEnvRobotiq,self.ikGroup_dampedRobotiq2,{"syncWorlds":"true"})
        # self.disconnect()
     



    def test_gripper_movement(self):
        print("Starting test for gripper movement...")

        # Open both fingers
        print(f"Opening both fingers: Param1 - {self.opening}, Param2 - {self.opening}")
        self.API.sim.setJointTargetPosition(self.robotiqParam1, self.opening)
        self.API.sim.setJointTargetPosition(self.robotiqParam2, self.opening)
        
        # Pause to allow movement
        time.sleep(1)
        
        # Check current positions after opening
        pos_param1 = self.API.sim.getJointPosition(self.robotiqParam1)
        pos_param2 = self.API.sim.getJointPosition(self.robotiqParam2)
        print(f"After opening: Param1 Position - {pos_param1}, Param2 Position - {pos_param2}")
        
        # Close both fingers
        print(f"Closing both fingers: Param1 - {self.closure}, Param2 - {self.closure}")
        self.API.sim.setJointTargetPosition(self.robotiqParam1, self.closure)
        self.API.sim.setJointTargetPosition(self.robotiqParam2, self.closure)
        
        # Pause to allow movement
        time.sleep(1)
        
        # Check current positions after closing
        pos_param1 = self.API.sim.getJointPosition(self.robotiqParam1)
        pos_param2 = self.API.sim.getJointPosition(self.robotiqParam2)
        print(f"After closing: Param1 Position - {pos_param1}, Param2 Position - {pos_param2}")
        
        print("Gripper movement test completed.")


    #Connect bloc to gripper - don't rely on physics for the picking
    def connected(self):

        res = 0
        timeout = 200
        t =0
        #check that block has been detected
        while res!=1 and t < timeout:
            res,_,_,obj,n = self.API.sim.checkProximitySensor(self.sensor,self.API.sim.handle_all)
            t += 1
       
        #Then connect - this connection is done by changing the hierarchy : the bloc will be a child of the gripper, so moves with it
        self.API.sim.setObjectParent(obj,self.connector,True)
        #close gripper
        resCollL = 0
        resCollR = 0
        t = 0
        while resCollL==0 and resCollR==0 and t<200:
            t+= 1
            resCollL,_ = self.API.sim.checkCollision(self.robotiqRealLTip,obj)
            resCollR,_ = self.API.sim.checkCollision(self.robotiqRealRTip,obj)
            #to be sure that it is not due to lack of closure or a too much closure
            if (timeout-t)%50 == 0 :
                self.closure -= 0.005
                #self.closure -= 0.1
            self.closeOrOpen()

        #open a bit to avoid some annoying dynamical effects
        self.closure = Robotiq85F.__CLOSURE_DEFAULT

        return n
        
    
    #Disconnect the bloc
    #To have no parent, parentHandle=-1
    def disconnect(self,parentHandle:int=-1):
        #check that the block is already connected to the connector 
        connectorCurrentChild = self.API.sim.getObjectChild(self.connector,0)
        self.API.sim.setObjectParent(connectorCurrentChild,parentHandle,True)
               


class RG2():
    """
    Class to interface RG2 gripper
    """
    def __init__(self,env):
        self.sim = env.sim
        self.gripper = self.sim.getObject('/UR10/RG2')
        self.velocity = 0.11
        self.force =20
        
        self.robotLeftFinger = self.sim.getObject('/UR10/RG2/leftLink0_visible')
        self.robotRightFinger = self.sim.getObject('/UR10/RG2/rightLink0_visible')
        self.sim.setBufferProperty(self.gripper,'customData.activity',self.sim.packTable({'velocity':self.velocity,'force':self.force}))
        self.sim.wait(4.0)
    def openGripper(self):
        self.sim.setBufferProperty(self.gripper,'customData.activity',self.sim.packTable({'velocity':self.velocity,'force':self.force}))
        return True
    def closeGripper(self,objectHandle):
        # self.sim.setBufferProperty(self.gripper,'customData.activity',self.sim.packTable({'velocity':-self.velocity,'force':self.force,'targetHandle':objectHandle}))
        return True

class PandaGripper():
    def __init__(self,env):
        self.sim = env.sim
        self.gripper = self.sim.getObject('/Panda/Panda_gripper')

        self.robotLeftFinger = self.sim.getObject('/Panda/Panda_leftfinger_respondable')
        self.robotRightFinger = self.sim.getObject('/Panda/Panda_rightfinger_respondable')
    def openGripper(self):
        self.sim.setInt32Signal( "Panda_gripper", 0)
        return True
    def closeGripper(self,objectHandle=None):
        self.sim.setInt32Signal( "Panda_gripper", 1)
        return True
    
class Robotiq85New:
    """
    Class to interface ROBOTIQ-85 gripper via signal-based command
    with optional fake grasping support.
    """
    def __init__(self, env):
        self.sim = env.sim
        self.gripper = self.sim.getObject('/UR10/ROBOTIQ85')   # adjust path
        self.cmd_signal = 'robotiq85_cmd'
        self.robotLeftFinger = self.sim.getObject('/UR10/ROBOTIQ85/LfingerTipVisible')
        self.robotRightFinger = self.sim.getObject('/UR10/ROBOTIQ85/RfingerTipVisible')

    # -------------------------------
    # LOW-LEVEL SETTERS
    # -------------------------------
    def _send_cmd(self, close: bool):
        """
        Send 1=close, 0=open to CoppeliaSim.
        """
        self.sim.setInt32Signal(self.cmd_signal, 1 if close else 0)

    # -------------------------------
    # PUBLIC API
    # -------------------------------
    def openGripper(self):
        """
        Opens the gripper and automatically DETACHES any object.
        Lua script handles the detach.
        """
        self._send_cmd(False)
        return True

    def closeGripper(self, objectHandle=None):
        """
        Closes gripper. Fake grasp handled in Lua.
        objectHandle ignored unless you want an explicit attach.
        """
        self._send_cmd(True)

        # OPTIONAL: explicit attach (if you want deterministic behavior)
        if objectHandle is not None:
            try:
                connector = self.sim.getObject('/UR10/ROBOTIQ85/attachPoint')
                self.sim.setObjectParent(objectHandle, connector, True)
            except:
                pass   # silently ignore if not needed

        return True

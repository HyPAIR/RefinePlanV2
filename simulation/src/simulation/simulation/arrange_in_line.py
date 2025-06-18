from config_planning import RoboticsEnvironment

#Initialize the environment
env = RoboticsEnvironment()
#connect to the remote API
env.connect()
#Initilize robot parameters
env.initialize_params()

#initial configuration 
initConfig =env.getConfig() 
initcfg =[-1.5708021642299306, 1.5708124107873083, -2.443460952792223, 0.8726616556125304, 1.5707974398473405, 1.0471975511966667]
env.setConfig(initcfg)

#Assuming the perception gives us the locations of all the items to pick retrieve pick item poses
# items =['/pillar2','/pillar1','/pillar3','/column0','/column1']
items =['/column0','/column1','/column2','/column3','/column2']
pickPoses = [env.sim.getObjectPose(env.sim.getObject(item)) for item in items]
#put the pick target above approach distance
for pose in pickPoses:
    pose[2]+=0.125 

#define drop targets
# dropPoses =[env.sim.getObjectPose(env.sim.getObject(f'/place{i}')) for i in range(len(items))]
dropPoses=['/place4','/place5','/place1','/place4','/place2']
dropPoses = [env.sim.getObjectPose(env.sim.getObject(obj)) for obj in dropPoses]
for pose in dropPoses:
    pose[2]+=0.19 # 0.17
print(pickPoses)
print(dropPoses)

approachTr = [ 0,0,-0.10, 0, 0, 0, 1]
withdrawTr = [0,0,0.10, 0, 0, 0, 1]
# env.gripper.openGripper()
# env.sim.wait(3)
# for pick,drop in zip(pickPoses,dropPoses):
#     outcome_pick = env.ActionPick(pick,approachTr,withdrawTr)
#     outcome_place = env.ActionPlace(drop,approachTr,withdrawTr)
sidePose =[0.6499999999999997, 0.9500000000000014, 0.5499999999999998, -1.649540451313252e-18, 1.2209181669764628e-17, -0.7071067811865841, 0.7071067811865109]
sidePose[2]+=0.125
pickPoses[-1]=sidePose
for i in range(len(pickPoses)):
    pick = pickPoses[i]
    drop = dropPoses[i]
    if i==2:
        pick = env.sim.getObjectPose(env.sim.getObject('/column0'))
        pick[2]+=0.125
    outcome_pick = env.ActionPick(pick,approachTr,withdrawTr)
    outcome_place = env.ActionPlace(drop,approachTr,withdrawTr)
#Go back home
pathBackHome = env.findPath(initcfg)
print("back to homing config")
env.followPath(pathBackHome)
env.sim.wait(3)
# env.stop_simulation()
col2po=[0.6499999999999997, 0.9500000000000014, 0.5499999999999998, 1.2209181669764799e-17, 1.6495404513119886e-18, 0.7071067811865841, 0.7071067811865109]

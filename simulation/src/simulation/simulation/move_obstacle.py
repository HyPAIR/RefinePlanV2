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
items =['/column3','/Cuboid1','/column1','/Cuboid0','/column0','/column2']
pickPoses = [env.sim.getObjectPose(env.sim.getObject(item)) for item in items]

#put the pick target above approach distance
for pose in pickPoses:
    pose[2]+=0.125 
pickPoses[3][0]+=0.2

#define drop targets
# dropPoses =[env.sim.getObjectPose(env.sim.getObject(f'/place{i}')) for i in range(len(items))]
dropPoses=['/place1','/place6','/place4','/place7','/place5','/place2']
dropPoses = [env.sim.getObjectPose(env.sim.getObject(obj)) for obj in dropPoses]
for pose in dropPoses:
    pose[2]+=0.19 # 0.17
print(pickPoses)
print(dropPoses)
approachTr = [ 0,-0.02,-0.10, 0, 0, 0, 1]
withdrawTr = [0,0,0.2, 0, 0, 0, 1]


for pick,drop in zip(pickPoses,dropPoses):
    outcome_pick = env.ActionPick(pick,approachTr,withdrawTr)
    outcome_place = env.ActionPlace(drop,approachTr,withdrawTr)


pathBackHome = env.findPath(initConfig)
# print("back to homing config")
# env.followPath(pathBackHome)
# env.sim.wait(3)
env.stop_simulation()

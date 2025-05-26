from config_planning import RoboticsEnvironment

#Initialize the environment
env = RoboticsEnvironment()
#connect to the remote API
env.connect()
#Initilize robot parameters
env.initialize_params()

#initial configuration 
initConfig =env.getConfig()
#Assuming the perception gives us the locations of all the items to pick retrieve pick item poses
# items =['/pillar2','/pillar1','/pillar3','/column0','/column1']
items =['/column0','/column1','/column2']
pickPoses = [env.sim.getObjectPose(env.sim.getObject(item)) for item in items]
#put the pick target above approach distance
for pose in pickPoses:
    pose[2]+=0.125 

#define drop targets
dropPoses =[env.sim.getObjectPose(env.sim.getObject(f'/place{i}')) for i in range(len(items))]
for pose in dropPoses:
    pose[2]+=0.17
print(pickPoses)
print(dropPoses)

approachTr = [ 0,0,-0.10, 0, 0, 0, 1]
withdrawTr = [0,0,0.10, 0, 0, 0, 1]
for pick,drop in zip(pickPoses,dropPoses):
    outcome_pick = env.ActionPick(pick,approachTr,withdrawTr)
    outcome_place = env.ActionPlace(drop,approachTr)
#Go back home
pathBackHome = env.findPath(initConfig)
print("back to homing config")
env.followPath(pathBackHome)
env.sim.wait(1)
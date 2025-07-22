from robot.robot_interface import RoboticsEnvironment
print("Hello from refine plan")
env = RoboticsEnvironment()
env.connect()

shot_slot_handles = [f'/place_plate{i}' for i in range(6)]
shop_slots =[env.sim.getObject(handle) for handle in shot_slot_handles]
shop_slot_poses = [env.sim.getObjectPosition(slot) for slot in shop_slots]
for pose in shop_slot_poses:
    pose[2]+=0.05
print(shop_slot_poses)
SHOP_SLOTS =dict(zip(range(9),shop_slot_poses))
print(SHOP_SLOTS)
from config_planning import RoboticsEnvironment
import pddlstream
import numpy as np
from scipy.spatial.transform import Rotation as R

env = RoboticsEnvironment()
env.connect()
env.initialize_params()

#calculating Poses
subjectHandle = env.sim.getObject('/pillar2')
subjectInitPose = env.sim.getObjectPose(subjectHandle)
subjectInitPose[2]+=0.05


def sample_grasps(base_pose,num_samples=10,max_angle_deg=90):
    """
    Generate new poses with different orientations around all axes.

    Args:
        base_pose: list or array of shape (7,) - [x, y, z, qx, qy, qz, qw]
        num_samples: number of different orientations to sample
        max_angle_deg: maximum rotation angle in degrees (uniformly sampled up to this angle)

    Returns:
        List of poses with new orientations [x, y, z, qx, qy, qz, qw]
    """
    sampled_poses = []

    # Extract base position and orientation
    position = np.array(base_pose[:3])
    base_quat = np.array(base_pose[3:])

    base_rot = R.from_quat(base_quat)

    for _ in range(num_samples):
        # Sample a random axis (normalized)
        axis = np.random.randn(3)
        axis /= np.linalg.norm(axis)

        # Sample a random angle between -max_angle and +max_angle degrees
        angle_rad = np.deg2rad(np.random.uniform(-max_angle_deg, max_angle_deg))

        # Create rotation around sampled axis
        delta_rot = R.from_rotvec(axis * angle_rad)

        # Apply rotation: new_rot = delta * base (left-multiplication → world frame)
        new_rot = delta_rot * base_rot

        # Get quaternion
        new_quat = new_rot.as_quat()  # [x, y, z, w]

        # Combine with base position
        new_pose = np.concatenate([position, new_quat])
        sampled_poses.append(list(new_pose))

    return sampled_poses
def sample_90deg_orientations(base_pose, num_samples=10):
    """
    Sample orientations biased around 90-degree rotations about principal axes.
    """
    sampled_poses = []
    position = np.array(base_pose[:3])
    base_rot = R.from_quat(base_pose[3:])

    # Define 90-degree rotations around X, Y, Z and combinations
    axes = [
        [1, 0, 0], [0, 1, 0], [0, 0, 1],
        [1, 1, 0], [1, 0, 1], [0, 1, 1],
        [1, 1, 1]
    ]

    angles = [np.pi/2, -np.pi/2, np.pi, 3*np.pi/2]  # 90°, -90°, 180°, 270°

    for _ in range(num_samples):
        axis = axes[np.random.randint(len(axes))]
        axis = np.array(axis) / np.linalg.norm(axis)

        angle = np.random.choice(angles)

        delta_rot = R.from_rotvec(axis * angle)
        new_rot = delta_rot * base_rot
        new_quat = new_rot.as_quat()

        new_pose = np.concatenate([position, new_quat])
        sampled_poses.append(list(new_pose))

    return sampled_poses

#Define the grasps
#graspPoses=sample_grasps(subjectInitPose,10,90)
graspPoses =sample_90deg_orientations(subjectInitPose,6)

#we use place since it doesn't close gripper
#open the gripper
env.gripper.openGripper()
env.sim.wait(3)

for grasp in graspPoses:
    env.ActionPlace(grasp,[0,0,0,0,0,0,1])
    env.sim.wait(1)
env.stop_simulation()




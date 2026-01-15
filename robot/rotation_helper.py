import numpy as np
from scipy.spatial.transform import Rotation as R

FACES = {
    "+x": np.array([ 1, 0, 0]),
    "-x": np.array([-1, 0, 0]),
    "+y": np.array([ 0, 1, 0]),
    "-y": np.array([ 0,-1, 0]),
    "+z": np.array([ 0, 0, 1]),
    "-z": np.array([ 0, 0,-1]),
}
WORLD_UP = np.array([0.0, 0.0, 1.0])

def normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def rotation_from_a_to_b(a, b):
    a = normalize(a); b = normalize(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.linalg.norm(v) < 1e-12:
        if c > 0:
            return R.identity()
        axis = normalize(np.cross(a, np.array([1,0,0]) if abs(a[0]) < 0.9 else np.array([0,1,0])))
        return R.from_rotvec(np.pi * axis)
    s = np.linalg.norm(v)
    axis = v / s
    angle = np.arctan2(s, c)
    return R.from_rotvec(angle * axis)

def rename_frame_top_is_world_up(qx, qy, qz, qw):
    """
    Returns:
      - q_world_cprime: quaternion of the renamed frame C' in world
      - R_c_to_cprime: rotation mapping vectors in old cube frame -> renamed cube frame
      - up_face: which original face is now 'top'
    """
    R_w_c = R.from_quat([qx, qy, qz, qw])

    # find which local face is most aligned with world +Z
    best_face, best_dot = None, -1e9
    for name, n_local in FACES.items():
        n_world = R_w_c.apply(n_local)
        d = np.dot(n_world, WORLD_UP)
        if d > best_dot:
            best_dot = d
            best_face = name

    n_up_local = FACES[best_face]

    # local relabeling rotation: makes that face become +Z in the new frame
    R_to_top = rotation_from_a_to_b(n_up_local, FACES["+z"])

    # Renamed frame orientation in world
    R_w_cprime = R_w_c * R_to_top
    q_world_cprime = R_w_cprime.as_quat()  # [x,y,z,w]

    # Mapping old local -> new local (change of basis)
    R_c_to_cprime = R_to_top

    return q_world_cprime, R_c_to_cprime, best_face

import numpy as np

def translate(x, y, z):
    """Return a 4x4 translation matrix."""
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ], dtype=np.float64)


def scale(sx, sy, sz):
    """Return a 4x4 scaling matrix."""
    return np.array([
        [sx, 0,  0, 0],
        [0, sy,  0, 0],
        [0,  0, sz, 0],
        [0,  0,  0, 1],
    ], dtype=np.float32)

def rotate_z(angle_radians):
    c = np.cos(angle_radians)
    s = np.sin(angle_radians)
    return np.array([
        [ c, -s, 0, 0],
        [ s,  c, 0, 0],
        [ 0,  0, 1, 0],
        [ 0,  0, 0, 1],
    ], dtype=np.float32)

def rotate_x(angle_radians):
    c = np.cos(angle_radians)
    s = np.sin(angle_radians)
    return np.array([
        [1, 0, 0, 0],
        [0, c,-s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1],
    ], dtype=np.float32)

def rotate_y(angle_radians):
    c = np.cos(angle_radians)
    s = np.sin(angle_radians)
    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1],
    ], dtype=np.float32)

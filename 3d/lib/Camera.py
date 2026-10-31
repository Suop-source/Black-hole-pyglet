import numpy as np
from pyglet.math import Mat4, Vec3
import math


class Camera:
    def __init__(self, width, height, fov, near, far):
        self.x: float = 0
        self.y: float = 0
        self.z: float = 0

        self.width = width
        self.height = height
        self.fov = math.radians(fov)
        self.near = near
        self.far = far
        self.perspective: np.array = object
        self.view: np.array = object

    def _get_position_pyglet(self) -> Vec3:
        """For internal use"""
        return Vec3(self.x, self.y, self.z)
    
    def get_position(self) -> np.ndarray:
        """Return a Numpy array of the camera's position."""
        return np.array([self.x, self.y, self.z])

    def get_projection(self) -> Mat4:
        # Translated from GLU's source code:
        # https://gitlab.freedesktop.org/mesa/glu/-/blob/master/src/libutil/project.c#L66
        half_fov = self.fov/2
        aspect = self.width/self.height
        delta_z = self.far - self.near
        sine = math.sin(half_fov)

        if delta_z == 0.0 or sine == 0.0 or aspect == 0.0:
            raise ValueError("Invalid perspective parameters")

        cotangent = math.cos(half_fov) / sine

        return Mat4(
            cotangent / aspect, 0, 0, 0,
            0, cotangent, 0, 0,
            0, 0, -(self.far + self.near) / delta_z, -1,
            0, 0, -(2.0 * self.near * self.far) / delta_z, 1,
        )
        
        # return Mat4.perspective_projection(fov=self.fov,
        #                                    aspect=self.width/self.height,
        #                                    z_near=self.near, z_far=self.far)

    def get_look_at(self) -> Mat4:
        # Pyglet's own implementation:
        # https://github.com/pyglet/pyglet/blob/master/pyglet/math.py#L1212
        target = Vec3(0, 0, 0)

        f = (target - self._get_position_pyglet()).normalize()
        u = Vec3(0, 1, 0).normalize()
        s = f.cross(u).normalize()
        u = s.cross(f)

        return Mat4(s.x, u.x, -f.x, 0.0,
                   s.y, u.y, -f.y, 0.0,
                   s.z, u.z, -f.z, 0.0,
                   -s.dot(self._get_position_pyglet()), -u.dot(self._get_position_pyglet()), f.dot(self._get_position_pyglet()), 1.0)


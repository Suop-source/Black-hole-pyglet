from pyglet.graphics import Batch, Group
import pyglet
from typing import Sequence
from pyglet.graphics.shader import ShaderProgram
import random
from pyglet.gl import GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA
from icosphere import icosphere
from .model_importer import *
import math
import numpy as np

from .shaders import *
from .states import bind_scene_block

shader = create3DShader()
shader_with_lighting = create3DShader(enable_lighting=True)
bind_scene_block(shader_with_lighting)


class Sphere(pyglet.shapes.ShapeBase):
    def __init__(
        self,
        x: float, y: float, z: float,
        radius: float,
        color: tuple,
        batch: Batch | None = None
    ):
        """Create a square or rectangle grid.

        The grid's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.
        Args:
        x:
            The X coordinate of the grid.
        y:
            The Y coordinate of the grid.
        z:
            The Z coordinate of the grid.
        width:
            The width of the grid.
        height:
            The height of the grid.
        color:
            The RGB or RGBA color of the circle, specified as a
            tuple of 3 or 4 ints in the range of 0-255. RGB colors
            will be treated as having an opacity of 255.
        blend_src:
            OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
        blend_dest:
            OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
        batch:
            Optional batch to add the shape to.
        group:
            Optional parent group of the shape.
        program:
            Optional shader program of the shape.
        """

        self._x = x
        self._y = y
        self._z = z
        self._color = color
        self._radius = radius

        subdivision_frequency = 6
        vertices, indices = icosphere(subdivision_frequency)
        vertices *= self._radius
        num_vertices = vertices.shape[0]
        indices = indices.flatten().tolist()
        vertices = vertices.flatten().tolist()

        self._verts = vertices
        self._indices = indices
        super().__init__(
            num_vertices,
            pyglet.gl.GL_SRC_ALPHA,
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
            batch,
            None,
            shader,
        )

    def _create_vertex_list(self) -> None:
        # --- FIX: Expand color to RGBA ---
        if len(self._color) == 3:
            r, g, b = self._color
            a = 255
        else:
            r, g, b, a = self._color

        rgba = (r, g, b, a) * self._num_verts

        # --- Create the vertex list ---
        self._vertex_list = self._program.vertex_list_indexed(
            self._num_verts,
            self._draw_mode,
            self._indices,
            self._batch,
            self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', rgba),
            translation=('f', (self._x, self._y, self._z) * self._num_verts)
        )


    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0, 0) * self._num_verts
        else:
            return self._verts

    def _update_vertices(self):
        self._vertex_list.position[:] = self._get_vertices()

    def _update_translation(self) -> None:
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()


class CustomModel(pyglet.shapes.ShapeBase):
    def __init__(
        self,
        x: float, y: float, z: float,
        scale: float = 1,
        filepath: str = "data/spaceship.obj",
        base_color: tuple[int, int, int, int] = (155, 155, 155, 255),
        batch: Batch | None = None,
    ):
        """Import an OBJ model.

        This model is affected by lighting. That means to make it work properly,
        a GlobalState must be configured. Please read the README for more info.

        Note: When setting the positions x, y and z, it is based on the origin
        defined in the 3D software that the model was created in.

        Note: Only Wavefront (OBJ) file format is suppported.

        Arguments:
        ----------
        - x: The model's X position.
        - y: The model's Y position.
        - z: The model's Z positin.
        - scale: Scale up the original size of the model.
        - filepath: Set the filepath where the model is in.
        - base_color: The diffuse colour that all of the model's surfaces will
                      use. This makes the diffuse colour of the Phong model.
        - batch: A Pyglet Batch to be associated with.
        """

        self._x = x
        self._y = y
        self._z = z
        self._base_color = base_color

        self._rotation_matrix = np.identity(4)

        positions, self._normals, indices = pywavefront_obj_loader(filepath)

        self._verts = positions * scale
        self._indices = indices

        # Build vertex list structure (just like Rectangle)
        super().__init__(
            len(positions) // 3,
            pyglet.gl.GL_SRC_ALPHA,
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
            batch,
            None,
            shader_with_lighting,
        )

    @property
    def rotation_matrix(self) -> np.ndarray:
        return self._rotation_matrix

    @rotation_matrix.setter
    def rotation_matrix(self, value: np.ndarray) -> None:
        self._rotation_matrix = value

    def upload_rotation_matrix(self):
        """Must be called before drawing the model.

        The method updates the shader's `m_rotation` uniform. This is more
        memory efficient than setting vertex attributes, but requires refinement
        to support uploading unique rotation matrices to multiple CustomModel
        shapes.
        """
        global shader_with_lighting
        shader_with_lighting["m_rotation"] = self._rotation_matrix.flatten()

    def _create_colours(self):
        c = []
        for i in range(self._num_verts):
            c.extend(self._base_color)

            # Use the following code to generate random colours instead.
            # c.extend((random.randint(0, 255), random.randint(
            #     0, 255), random.randint(0, 255), 255))
        return c

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list_indexed(
            self._num_verts, self._draw_mode,
            self._indices,
            self._batch, self._group,
            position=('f', self._get_vertices()),
            # self._rgba * self._num_verts),
            colors=('Bn', self._create_colours()),
            translation=('f', (self._x, self._y, self._z) * self._num_verts),
            normal=('f', self._normals))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts
        else:
            return self._verts

    def _update_vertices(self):
        self._vertex_list.position[:] = self._get_vertices()

    def _update_translation(self) -> None:
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()


class Rectangle3D(pyglet.shapes.ShapeBase):
    def __init__(
            self,
            x: float, y: float, z: float,
            width: float, height: float,
            color: tuple[int, int, int, int] | tuple[int,
                                                     int, int] = (255, 255, 255, 255),
            batch: Batch | None = None,
            program: ShaderProgram | None = None
    ):
        """Create a rectangle or square. It is created in the XZ plane.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            z:
                The Z coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            program:
                Override the shader program. Usually, this must not be defined.
        """
        self._x = x
        self._y = y
        self._z = z
        self._width = width
        self._height = height
        self._rotation = 0

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        if program is None:
            program = shader

        super().__init__(6,
                         GL_SRC_ALPHA,
                         GL_ONE_MINUS_SRC_ALPHA,
                         batch,
                         None,
                         program)

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            6, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y, self._z) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts
        else:
            x1 = self.x
            y1 = self.y
            x2 = x1 + self._width
            y2 = y1 + self._height
            z = self.z

            return x1, y1, 0, x2, y1, 0, x2, y2, 0, x1, y1, 0, x2, y2, 0, x1, y2, 0

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def width(self) -> float:
        """Get/set width of the rectangle.

        The new left and right of the rectangle will be set relative to
        its :py:attr:`.anchor_x` value.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._update_vertices()

    @property
    def height(self) -> float:
        """Get/set the height of the rectangle.

        The bottom and top of the rectangle will be positioned relative
        to its :py:attr:`.anchor_y` value.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._update_vertices()

    def _update_translation(self) -> None:
        """Overwrite this method to support 3d position"""
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()


class WorldGrid(Rectangle3D):
    def __init__(self, batch):
        shader = createWorldGridShader()

        super().__init__(x=-10, y=-10, z=0,
                         width=20, height=20,
                         color=(255, 255, 255, 255),
                         batch=batch,
                         program=shader)


class Circle3D(pyglet.shapes.ShapeBase):
    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        radius: float,
        segments: int | None = None,
        color: tuple[int, int, int, int] | tuple[int,
                                                 int, int] = (255, 255, 255, 255),
        batch: Batch | None = None,
    ) -> None:
        """Create a circle.

        The circle's anchor point (x, y) defaults to the center of the circle.

        Args:
            x:
                X coordinate of the circle.
            y:
                Y coordinate of the circle.
            z:
                Z coordinate of the circle.
            radius:
                The desired radius.
            segments:
                You can optionally specify how many distinct triangles
                the circle should be made from. If not specified it will
                be automatically calculated using the formula:
                `max(14, int(radius / 1.25))`.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
            program:
                Optional shader program of the shape.
        """
        self._x = x
        self._y = y
        self._z = z
        self._radius = radius
        self._segments = segments or max(14, int(radius / 1.25))
        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(
            self._segments * 3,
            GL_SRC_ALPHA,
            GL_ONE_MINUS_SRC_ALPHA,
            batch,
            None,
            shader,
        )

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._segments * 3,
            self._draw_mode,
            self._batch,
            self._group,
            position=("f", self._get_vertices()),
            colors=("Bn", self._rgba * self._num_verts),
            translation=("f", (self._x, self._y, self._z) * self._num_verts),
        )

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0, 0) * self._num_verts

        x = -self._anchor_x
        y = -self._anchor_y
        r = self._radius
        tau_segs = math.pi * 2 / self._segments

        # 3D points on the circle in local XY plane (z=0)
        points = [
            (x + r * math.cos(i * tau_segs), y + r * math.sin(i * tau_segs), 0.0)
            for i in range(self._segments)
        ]

        vertices = []
        for i, point in enumerate(points):
            # Center vertex + two edge vertices, all with z=0
            triangle = (x, y, 0.0, *points[i - 1], *point)
            vertices.extend(triangle)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    def _update_translation(self) -> None:
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def radius(self) -> float:
        """Gets/set radius of the circle."""
        return self._radius

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()

    @radius.setter
    def radius(self, value: float) -> None:
        self._radius = value
        self._update_vertices()


class Line3D(pyglet.shapes.ShapeBase):
    def __init__(
            self,
            x0: float, y0: float, z0: float,
            x1: float, y1: float, z1: float,
            thickness: float,
            color: tuple[int, int, int, int] | tuple[int,
                                                     int, int] = (255, 255, 255, 255),
            batch: Batch | None = None
    ):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            batch:
                Optional batch to add the shape to.
        """
        self._x1 = x0
        self._y1 = y0
        self._z1 = z0
        self._x2 = x1
        self._y2 = y1
        self._z2 = z1
        self._thickness = thickness

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        if program is None:
            program = shader
        super().__init__(24,
                         GL_SRC_ALPHA,
                         GL_ONE_MINUS_SRC_ALPHA,
                         batch,
                         None,
                         shader)

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            24, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y, self._z) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0.0, 0.0, 0.0) * self._num_verts
        else:
            t = self._thickness * 0.5

            p0 = np.array([self._x1, self._y1, self._z1], dtype=np.float32)
            p1 = np.array([self._x2, self._y2, self._z2], dtype=np.float32)

            length = np.linalg.norm(p1 - p0)
            length = length if length > 0 else 0.01
            direction = (p1-p0) / length

            up = np.array([0, 1, 0], dtype=np.float32)
            x = direction
            z = np.cross(x, up)
            z = np.array([0.001]*3) if np.linalg.norm(z) == 0 else z
            z /= np.linalg.norm(z)
            y = np.cross(z, x)

            R = np.column_stack((x, y, z))

            local_vertices = np.array([
                [0, -t,  t],
                [length, -t,  t],
                [length,  t,  t],
                [0,  t,  t],
                [0, -t, -t],
                [length, -t, -t],
                [length,  t, -t],
                [0,  t, -t],
            ], dtype=np.float32)

            world_vertices = (R @ local_vertices.T).T + p0
            v0, v1, v2, v3, v4, v5, v6, v7 = world_vertices

            return (
                *v0, *v1, *v2,  # Front
                *v0, *v2, *v3,

                *v4, *v5, *v6,  # Rear
                *v4, *v6, *v7,

                *v3, *v2, *v6,  # Top
                *v3, *v6, *v7,

                *v0, *v1, *v5,  # Bottom
                *v0, *v5, *v4,
            )

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    def _update_translation(self) -> None:
        """Overwrite this method to support 3d position"""
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()


class Prism3D(pyglet.shapes.ShapeBase):
    def __init__(
            self,
            x: float, y: float, z: float,
            width: float, height: float, depth: float,
            color: tuple[int, int, int, int] | tuple[int,
                                                     int, int] = (255, 255, 255, 255),
            batch: Batch | None = None,
    ):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            batch:
                Optional batch to add the shape to.
        """
        self._x = x
        self._y = y
        self._z = z
        self._width = width
        self._height = height
        self._depth = depth
        self._rotation = 0

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(36,
                         GL_SRC_ALPHA,
                         GL_ONE_MINUS_SRC_ALPHA,
                         batch,
                         None,
                         shader)

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._num_verts, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y, self._z) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        # Centralise the rectangle
        w = self._width/2
        h = self._height/2
        d = self._depth/2

        v0 = (self._x - w, self.height - h, d)
        v1 = (self._x + w, self.height - h, d)
        v2 = (self._x + w, self.height + h, d)
        v3 = (self._x - w, self.height + h, d)
        v4 = (self._x - w, self.height - h, -d)
        v5 = (self._x + w, self.height - h, -d)
        v6 = (self._x + w, self.height + h, -d)
        v7 = (self._x - w, self.height + h, -d)

        return (
            *v0, *v1, *v2,  # Front
            *v0, *v2, *v3,  # Front
            *v4, *v5, *v6,  # Rear
            *v4, *v6, *v7,  # Rear
            *v3, *v2, *v6,  # Top
            *v3, *v6, *v7,  # Top
            *v0, *v1, *v5,  # Bottom
            *v0, *v5, *v4,  # Bottom
            *v1, *v5, *v6,  # Right
            *v1, *v6, *v3,  # Right
            *v0, *v4, *v7,  # Left
            *v0, *v7, *v3  # Left
        )

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def width(self) -> float:
        """Get/set width of the rectangle.

        The new left and right of the rectangle will be set relative to
        its :py:attr:`.anchor_x` value.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._update_vertices()

    @property
    def height(self) -> float:
        """Get/set the height of the rectangle.

        The bottom and top of the rectangle will be positioned relative
        to its :py:attr:`.anchor_y` value.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._update_vertices()

    def _update_translation(self) -> None:
        """Overwrite this method to support 3d position"""
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()

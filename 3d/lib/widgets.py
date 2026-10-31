import pyglet

from .linalg import lerp


class Slider:
    """
    The slider widget is a knob that goes between two points. It's useful to
    change a continous value between 0.0 and 1.0.
    """

    def __init__(self,
                 x: float,
                 y: float,
                 width: float,
                 height: float,
                 knob_width: float,
                 knob_height: float,
                 color: tuple,
                 knob_color: tuple,
                 batch: pyglet.graphics.Batch,
                 starting_value: float = 0):
        """
        Initialises the slider with some starter value.

        The slider's value ranges between 0.0 and 1.0. The value is determined
        using linear interpolation: lerp(a,b,t) = a*(1-t)+b*t where a is the
        start value, b is the end value and t is a fraction between 0 and 1.
        t is basically the slider's value.

        Parameters
        ---------
        x : the slider's starting position in pixel value
        y : the slider's starting position in pixel value
        width : how wide the slider is. Value is in pixels
        height : how tall the slider is. Value is in pixels
        knob_width : the knob's width in pixels
        knob_height : the knob's height in pixels
        color : the base's color
        knob_color : the knob's color
        starting_value : a value between 0.0 and 1.0 that determines its starting
                        t value.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = starting_value  # This is the t in the lerp function

        # The slider consists of two shapes: the base and the knob
        self.base_shape = pyglet.shapes.Rectangle(
            x=x,
            y=y,
            width=width,
            height=height,
            color=color,
            batch=batch)
        
        self.base_shape.z = 4
        # self.base_shape.anchor_y = height/2

        # The knob's position is a function of t
        knob_pos_x = self.get_knob_position()

        self.knob_shape = pyglet.shapes.Rectangle(
            x=knob_pos_x,
            y=self.y - knob_height/4,
            width=knob_width,
            height=knob_height,
            color=knob_color,
            batch=batch)
        
        self.knob_shape.z = 5

    # TODO implement setters and getters

    def get_knob_position(self):
        start_x = self.x
        end_x = self.x + self.width
        return lerp(start_x, end_x, self.value)

    def update_clicked(self, mouse_x, mouse_y):
        """
        Drag the mouse if the mouse is hovered and clicked

        Parameters
        ----------
        mouse_x : the mouse cursor's position x
        mouse_y : the mouse cursor's position y

        Returns
        -------
        true the t value is changed to queue changes to the planet
        """
        # We use AABB to check for mouse collision
        knob_start_x = self.knob_shape.x
        knob_end_x = knob_start_x + self.knob_shape.width

        knob_start_y = self.knob_shape.y
        knob_end_y = knob_start_y + self.knob_shape.height

        # Mouse is not detected
        if not(mouse_x > knob_start_x and mouse_x < knob_end_x and \
            mouse_y > knob_start_y and mouse_y < knob_end_y):
            return False
        
        # Check if mouse is within bounds
        #
        # We can use linear interpolation for this. If t < 0 or t > 1, then it
        # is outside bounds.
        dx = (self.x + self.width) - self.x

        # Avoid division by zero
        if dx == 0:
            return False
        
        t = (mouse_x - self.x) / dx
        if t >= 0.0 and t <= 1.0:
            self.knob_shape.x = mouse_x - self.knob_shape.width/2
            self.value = t
            return True
        
        return False

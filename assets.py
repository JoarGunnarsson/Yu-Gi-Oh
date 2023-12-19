from constants import *
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from game_engine import environment
import game_engine
import utility_functions as utils

# TODO: Change external_process_function functionality into a GameScript object instead.


class GameScript:
    """
    Represents a game script.
    """
    def __init__(self):
        pass

    def process(self):
        pass


class GameObject:
    """
    A Class for representing a GameObject.

    Attributes:
        x (int): X-coordinate of the object.
        y (int): Y-coordinate of the object.
        z (float): Z-coordinate of the object.
        width (int): Width of the object.
        height (int): Height of the object.
        alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
        name (str): Name of the object.
        destroyed (bool): Indicates whether the object has been destroyed.
        parent: Parent object to which this object is attached.
        static (bool): Indicates whether the object is static (does not move together with its parent).
        displayable (bool): Indicates whether the object is visible.
        opaque (bool): Indicates whether the object blocks objects earlier in the processing order from
            being clicked.
        children (list): List of child objects.
        rect (pygame.Rect): Rectangular area occupied by the object.
        rotation_angle (int): Rotation angle of the object in degrees.
        relative_x (int): The x-coordinate of the object in relation to it's parent, if applicable.
        relative_y (int): The y-coordinate of the object in relation to it's parent, if applicable.
   """
    def __init__(self, x=0, y=0, z=0, width=0, height=0, alpha=255, parent=None, static=True, opaque=True,
                 displayable=False, name=""):
        """
        Initializes a GameObject.

        Args:
            x (int): The x-coordinate of the object.
            y (int): The y-coordinate of the object.
            z (float): The z-coordinate of the object.
            width (int): The width of the object.
            height (int): The height of the object.
            alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
            name (str): The name of the object.
            parent: The parent object to which this object is attached.
            static (bool): Indicates whether the object is static (does not move together with its parent).
            displayable (bool): Indicates whether the object is visible.
            opaque (bool): Indicates whether the object blocks objects earlier in the processing order from
                being clicked.
        """
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.name = name
        self.destroyed = False
        self.parent = parent
        self.static = static
        self.displayable = displayable
        self.children = []
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.rotation_angle = 0
        self.alpha = alpha
        self.opaque = opaque
        if self.parent is None:
            self.relative_x, self.relative_y = 0, 0
        else:
            self.relative_x, self.relative_y = self.x - self.parent.x, self.y - self.parent.y

    def get_rect(self):
        """
        Get rect

        Returns:
            - Pygame.rect: The value of the object's rect attribute
        """
        return self.rect

    def set_x(self, x):
        """
        Sets the x-coordinate of the object and updates its position relative to it's parent (if applicable), as well
        as updates the position of its children.

        Args:
            x (int): The new x-coordinate of the object.
        """
        self.x = x
        self.get_rect().update(self.x, self.y, self.width, self.height)
        self.update_relative_position()
        for child in self.children:
            if hasattr(child, "update_position"):
                child.update_position()

    def set_y(self, y):
        """
        Sets the x-coordinate of the game object and updates its position relative to it's parent (if applicable),
        as well as updates the position of its children.

        Args:
            y (int): The new y-coordinate of the object.
        """
        self.y = y
        self.get_rect().update(self.x, self.y, self.width, self.height)
        self.update_relative_position()
        for child in self.children:
            if hasattr(child, "update_position"):
                child.update_position()

    def set_z(self, z):
        """
        Sets the z-coordinate of the game object and shifts the z-coordinate of its children by the change in the
        z-coordinate.

        Args:
            z (float): The new z-coordinate of the object
        """
        delta_z = self.z - z
        self.z = z
        for child in self.children:
            child.shift_z(delta_z)

    def set_pos(self, x, y):
        """
        Sets the x and y coordinates of the game object.

        Args:
            x (int): The new x-coordinate.
            y (int): The new y-coordinate.
        """
        self.set_x(x)
        self.set_y(y)

    def shift_x(self, delta_x):
        """
        Shift the game object's x-coordinate by a given amount.

        Args:
            delta_x (int): The change in the x-coordinate of the object.
        """
        self.set_x(self.x + delta_x)

    def shift_y(self, delta_y):
        """
        Shift the game object's x-coordinate by a given amount.

        Args:
            delta_y (int): The change in the y-coordinate of the object.
        """
        self.set_y(self.y + delta_y)

    def shift_z(self, delta_z):
        """
        Shifts the game object's z-coordinate by a given amount.

        Args:
            delta_z (float): The change in the z-coordinate of the object.
        """
        self.set_z(self.z + delta_z)

    def shift_pos(self, delta_x, delta_y):
        """Shift the game object's position by a given amount in both x and y directions.

        Args:
            delta_x (int): The amount to shift the x-coordinate.
            delta_y (int): The amount to shift the y-coordinate.
        """
        self.shift_x(delta_x)
        self.shift_y(delta_y)

    def set_relative_x(self, x):
        """Sets the relative x-coordinate of the game object relative to its parent.

         Args:
             x (int): The relative x-coordinate.
         """
        self.relative_x = x

    def set_relative_y(self, y):
        """Sets the relative y-coordinate of the game object relative to its parent.

         Args:
             y (int): The relative x-coordinate.
         """
        self.relative_y = y

    def set_pos_relative_to_parent(self, x, y):
        """Sets the relative position of the game object in relation to the parent.

        The coordinates (x, y) refer to the position in the parent's coordinate system.

        Args:
            x (int): The relative x-coordinate.
            y (int): The relative y-coordinate.
        """
        if self.static:
            return

        self.set_relative_x(x)
        self.set_relative_y(y)
        self.set_pos(x=self.parent.x + self.relative_x, y=self.parent.y + self.relative_y)

    def update_relative_position(self):
        """Updates the relative position attributes of the game object relative to its parent."""
        if self.static or self.parent is None:
            return
        self.set_relative_x(self.x - self.parent.x)
        self.set_relative_y(self.y - self.parent.y)

    def update_position(self):
        """Updates the position of the game object."""
        if self.parent is not None:
            self.update_pos_relative_to_parent()

    def update_pos_relative_to_parent(self):
        """Updates the position of the game object relative to its parent."""
        if self.static or self.parent is None:
            return

        self.set_pos(x=self.relative_x + self.parent.x, y=self.relative_y + self.parent.y)

    def set_width(self, width):
        """Sets the width of the game object.

        Args:
            width (int): The new width.
        """
        self.width = width
        self.get_rect().update(self.x, self.y, self.width, self.height)

    def set_height(self, height):
        """Sets the height of the game object.

        Args:
            height (int): The new width.
        """
        self.height = height
        self.get_rect().update(self.x, self.y, self.width, self.height)

    def set_size(self, width, height):
        """Sets the width and height of the game object.

        Args:
            width (int): The new height.
            height (int): The new width.
        """
        self.set_width(width)
        self.set_height(height)

    def set_width_relative(self, delta_w):
        """Change the width of the game object by a given amount.

        Args:
            delta_w (int): The change to the width.
        """
        self.set_width(self.width + delta_w)

    def set_height_relative(self, delta_h):
        """Change the height of the game object by a given amount.

        Args:
            delta_h (int): The change to the height.
        """
        self.set_height(self.height + delta_h)

    def get_rotation(self):
        """Gets the rotation angle of the game object.

        Returns:
            int: The rotation angle in degrees.
        """
        return self.rotation_angle

    def set_rotation(self, angle):
        """Sets the rotation angle of the game object, and changes the size of the game object if necessary.

        Args:
            angle (int): The new rotation angle in degrees.
        """
        if ((self.rotation_angle - angle) // 90) % 2 == 1:
            self.height, self.width = self.width, self.height
            self.get_rect().update(self.x, self.y, self.width, self.height)

        self.rotation_angle = angle

    def rotate(self, angle):
        """Rotate the game object by a given angle.

         Args:
             angle (int): The change to the rotation angle in degrees.
         """
        self.set_rotation(self.rotation_angle + angle)

    def set_alpha(self, alpha):
        """Sets the alpha value of the game object.

         Args:
             alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
         """
        self.alpha = alpha

    def destroy(self):
        """Destroy the game object, hiding it in the current scene and notifying its parent if applicable."""
        if self.destroyed:
            return
        self.destroyed = True
        game_engine.get_scene_manager().current_scene.hide_object(self)
        if self.parent is not None and hasattr(self.parent, "destroy_child"):
            self.parent.destroy_child(self)

    def add_child(self, child):
        """Adds a child game object to this game object's children, and notifies the child object of its new parent.

        Args:
            child (GameObject): The new child game object.
        """
        self.children.append(child)
        child.set_parent(self)

    def set_parent(self, parent):
        """Sets the parent of the game object and updates relative position attributes if applicable.

        Args:
            parent: The game object's new parent
        """
        self.parent = parent
        if not self.static and self.parent is not None:
            self.set_relative_x(self.x - self.parent.x)
            self.set_relative_y(self.y - self.parent.y)

    def add_multiple_children(self, children):
        """Adds multiple child game objects to this game object's children.

        Args:
            children (list): List of game object's to add as children.
        """
        for child in children:
            self.add_child(child)

    def destroy_child(self, child):
        """Destroys a specific child game object.

        Args:
            child (GameObject): The child game object to destroy.
        """
        if child in self.children:
            self.children.remove(child)

    def clear_children(self):
        """Removes all child game objects."""
        self.children = []

    def schedule_processing(self):
        """Schedules the game object and its children for processing in the game loop.

        Returns:
            list: List of game objects to be processed in the game loop.
        """
        items_to_be_processed = [self]
        for child in self.children:
            items_to_be_processed.extend(child.schedule_processing())

        items_to_be_processed.sort(key=lambda x: x.z)
        return items_to_be_processed

    def process(self):
        """Process the game object, updating its position relative to its parent if applicable."""
        if self.parent is not None and not self.static:
            self.update_pos_relative_to_parent()

    def get_displayable_objects(self):
        """Gets a list of displayable game objects corresponding to the game object itself or it's children.

        Returns:
            list: List of displayable game objects.
        """
        displayable_objects = []
        if self.destroyed:
            return displayable_objects

        if self.displayable:
            displayable_objects.append(self)

        for child in self.children:
            if hasattr(child, "get_displayable_objects"):
                displayable_objects.extend(child.get_displayable_objects())

        return displayable_objects


class Box(GameObject):
    """
    A class representing boxes, inheriting from the base class GameObject.

    Attributes:
        x (int): X-coordinate of the box.
        y (int): Y-coordinate of the box.
        z (float): Z-coordinate of the box.
        width (int): Width of the box.
        height (int): Height of the box.
        alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
        name (str): Name of the box.
        destroyed (bool): Indicates whether the box has been destroyed.
        parent: Parent object to which this box is attached.
        static (bool): Indicates whether the box is static (does not move together with its parent).
        displayable (bool): Indicates whether the box is visible.
        opaque (bool): Indicates whether the box blocks objects earlier in the processing order from
            being clicked.
        children (list): List of child objects.
        rect (pygame.Rect): Rectangular area occupied by the object.
        rotation_angle (int): Rotation angle of the box in degrees.
        relative_x (int): The x-coordinate of the box in relation to it's parent, if applicable.
        relative_y (int): The y-coordinate of the box in relation to it's parent, if applicable.
        text (str): The string to be displayed on the box
        text_color (tuple): The color of the text.
        font_size (int): The font size of the text.
        text_surface_id (int): The id corresponding to the text surface of the box.
        update_text_func (func): The function responsible for updating the box text.
        surface_id (int): The id corresponding to the surface of the box.
    """

    def __init__(self, x=0, y=0, z=0, width=100, height=100, color=WHITE, alpha=255, source_image=None, text="",
                 text_color=BLACK, font_size=40, update_text_func=None, parent=None, static=True, name=None):
        """
        Initializes a Box object.

        Args:
            x (int): The x-coordinate of the box.
            y (int): The y-coordinate of the box.
            z (float): The z-coordinate of the box.
            width (int): The width of the box.
            height (int): The Height of the box.
            color (tuple): The color of the box
            alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
            source_image (Pygame.image): The source image of the box.
            text (str): The string to be displayed on the box
            text_color (tuple): The color of the text.
            font_size (int): The font size of the text
            update_text_func (func): The function responsible for updating the box text.
            parent: The parent object to which this object is attached.
            static (bool): Indicates whether the object is static (does not move together with its parent).
            name (str): The name of the object.
        """
        super().__init__(x=x, y=y, z=z, width=width, height=height, alpha=alpha, parent=parent, static=static,
                         displayable=True, name=name)
        self.color = color
        self.image_id = None
        if source_image is None:
            self.source_image_id = None
        else:
            self.source_image_id = game_engine.get_surface_manager().set_image(source_image)
            self.image_id = game_engine.get_surface_manager().scale_image(self.source_image_id,
                                                                          (self.width, self.height))

        self.text = text
        self.text_color = text_color
        self.font_size = font_size
        if self.text == "":
            self.text_surface_id = None
        else:
            self.text_surface_id = game_engine.get_surface_manager().create_font_surface(self.text, self.text_color,
                                                                                         self.font_size)

        self.update_text_func = update_text_func

        self.surface_id = game_engine.get_surface_manager().create_surface(self.width, self.height, self.alpha)
        self.set_alpha(self.alpha)

    def set_width(self, width):
        """Sets the width of the Box and updates the Box's image and surface.

        Args:
            width (int): The new width of the Box.
        """
        super().set_width(width)
        self.get_rect().update(self.x, self.y, self.width, self.height)
        if self.source_image_id is not None:
            game_engine.get_surface_manager().scale_image(self.source_image_id, (self.width, self.height),
                                                          new_id=self.image_id)

        # Updates the surface corresponding to self.surface_id
        game_engine.get_surface_manager().scale_surface(self.surface_id, (self.width, self.height),
                                                        new_id=self.surface_id)

    def set_height(self, height):
        """Sets the height of the Box and updates the Box's image and surface.

        Args:
            height (int): The new height of the Box.
        """
        super().set_height(height)
        self.get_rect().update(self.x, self.y, self.width, self.height)
        if self.source_image_id is not None:
            game_engine.get_surface_manager().scale_image(self.source_image_id, (self.width, self.height),
                                                          new_id=self.image_id)

        # Updates the surface corresponding to self.surface_id
        game_engine.get_surface_manager().scale_surface(self.surface_id, (self.width, self.height),
                                                        new_id=self.surface_id)

    def set_rotation(self, angle):
        """Sets the rotation angle of the Box and updates the Box's image and surface.

        Args:
            angle (int): The new rotation angle in degrees.
        """
        theta = angle - self.rotation_angle
        super().set_rotation(angle)

        if self.image_id is not None:
            game_engine.get_surface_manager().rotate_image(self.image_id, theta, new_id=self.image_id)

        game_engine.get_surface_manager().rotate_surface(self.surface_id, theta, new_id=self.surface_id)

    def set_image(self, image):
        """Sets the image of the Box by updating the source_image_id attribute, then rotates and scales the image.

         Args:
             image (Pygame.image): The new image for the Box.
         """
        self.source_image_id = game_engine.get_surface_manager().set_image(image, self.source_image_id)

        self.image_id = game_engine.get_surface_manager().rotate_image(self.source_image_id, self.rotation_angle,
                                                                       self.image_id)
        self.image_id = game_engine.get_surface_manager().scale_image(self.image_id, (self.width, self.height),
                                                                      self.image_id)

    def set_text(self, new_text):
        """Sets the text of the Box and updates the text surface id.

        Args:
            new_text (str): The new text for the Box.
        """
        self.text = new_text
        self.text_surface_id = game_engine.get_surface_manager().create_font_surface(self.text, self.text_color,
                                                                                     self.font_size,
                                                                                     self.text_surface_id)

    def set_color(self, color):
        """Sets the color of the Box.

        Args:
            color (tuple): The new color for the Box.
        """
        self.color = color

    def set_alpha(self, alpha):
        """Sets the alpha value of the Box, and sets the alpha of the Box's surface to the same value.

        Args:
            alpha (int): The new alpha value.
        """
        self.alpha = alpha
        game_engine.get_surface_manager().fetch_surface(self.surface_id).set_alpha(self.alpha)

    def hug_text(self, offset):
        """Adjusts the size of the Box to fit the text with an additional offset.

        Args:
            offset (int): The additional offset to apply.
        """
        text_surface = game_engine.get_surface_manager().fetch_text_surface(self.text_surface_id)
        self.set_width(text_surface.get_width() + 2 * offset)
        self.set_height(text_surface.get_height() + 2 * offset)

    def get_display_surface(self):
        """Return a tuple containing the surface to be displayed and the object's rect.

        Returns:
            tuple: The first element is the surface to be displayed, and the second element is the object's rect.
        """
        if self.image_id is not None:
            image = game_engine.get_surface_manager().fetch_image(self.image_id)
            game_engine.get_surface_manager().fetch_surface(self.surface_id).blit(image, (0, 0))
        else:
            game_engine.get_surface_manager().fetch_surface(self.surface_id).fill(self.color)

        if self.update_text_func is not None:
            self.text = self.update_text_func()
            game_engine.get_surface_manager().create_font_surface(self.text, self.text_color, self.font_size,
                                                                  self.text_surface_id)

        if self.text != "":
            text_surface = game_engine.get_surface_manager().fetch_text_surface(self.text_surface_id)
            surface = game_engine.get_surface_manager().fetch_surface(self.surface_id)
            surface_middle = [(self.width - text_surface.get_width()) / 2,
                              (self.height - text_surface.get_height()) / 2]
            surface.blit(text_surface, surface_middle)

        return game_engine.get_surface_manager().fetch_surface(self.surface_id), self.get_rect()


class Border(GameObject):
    """A class for displaying a rectangular border.

    Attributes:
        x (int): X-coordinate of the object.
        y (int): Y-coordinate of the object.
        z (float): Z-coordinate of the object.
        width (int): Width of the object.
        height (int): Height of the object.
        alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
        name (str): Name of the object.
        destroyed (bool): Indicates whether the object has been destroyed.
        parent: Parent object to which this object is attached.
        static (bool): Indicates whether the object is static (does not move together with its parent).
        displayable (bool): Indicates whether the object is visible.
        opaque (bool): Indicates whether the object blocks objects earlier in the processing order from
            being clicked.
        children (list): List of child objects.
        rect (pygame.Rect): Rectangular area occupied by the object.
        rotation_angle (int): Rotation angle of the object in degrees.
        relative_x (int): The x-coordinate of the object in relation to it's parent, if applicable.
        relative_y (int): The y-coordinate of the object in relation to it's parent, if applicable.
        thickness (int): The thickness of the border.
    """
    def __init__(self, x=0, y=0, z=1, width=100, height=100, color=BLACK, thickness=1, alpha=255, parent=None,
                 name=None):
        """Initialize a Border object.

        Args:
            x (int): The x-coordinate of the Border.
            y (int): The y-coordinate of the Border.
            z (float): The z-coordinate of the Border.
            width (int): The width of the Border.
            height (int): The height of the Border.
            color (tuple): The color of the Border (default is BLACK).
            thickness (int): The thickness of the Border.
            alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
            parent: The parent object to which this object is attached.
            name (str): The name of the Border.
        """
        super().__init__(x=x, y=y, z=z, width=width, height=height, alpha=alpha, parent=parent, static=False,
                         opaque=False, name=name)

        self.color = color
        self.thickness = thickness

        top_box = Box(x=self.x, y=self.y, z=z, width=self.width, height=self.thickness, color=self.color,
                      alpha=self.alpha,
                      parent=self, static=False)

        bottom_box = Box(x=self.x, y=self.y + self.height - self.thickness, z=z, width=self.width,
                         height=self.thickness,
                         color=self.color, alpha=self.alpha, parent=self, static=False)

        left_box = Box(x=self.x, y=self.y + self.thickness, width=self.thickness, z=z,
                       height=self.height - 2 * self.thickness, color=self.color, alpha=self.alpha, parent=self,
                       static=False)

        right_box = Box(x=self.x + self.width - self.thickness, y=self.y + self.thickness, z=z, width=self.thickness,
                        height=self.height - 2 * self.thickness, color=self.color, alpha=self.alpha, parent=self,
                        static=False)

        side_boxes = [top_box, bottom_box, left_box, right_box]

        for box in side_boxes:
            self.add_child(box)

    def set_width(self, width):
        """Sets the width of the Border and updates the side boxes to match.

        Args:
            width (int): The new width of the Border.
        """
        width_difference = width - self.width
        side_boxes = self.get_side_boxes()
        side_boxes[3].shift_x(width_difference)
        side_boxes[0].set_width_relative(width_difference)
        side_boxes[1].set_width_relative(width_difference)

        super().set_width(width)

    def set_height(self, height):
        """Sets the height of the Border and updates the side boxes to match.

        Args:
            height (int): The new height of the Border.
        """
        height_difference = height - self.height
        side_boxes = self.get_side_boxes()
        side_boxes[1].shift_y(height_difference)
        side_boxes[2].set_height_relative(height_difference)
        side_boxes[3].set_height_relative(height_difference)

        super().set_height(height)

    def set_rotation(self, angle):
        """Sets the rotation angle of the Border and updates the size of the Border.

        Args:
            angle (int): The new rotation angle in degrees.
        """
        if ((self.rotation_angle - angle) // 90) % 2 == 1:
            self.set_size(width=self.height, height=self.width)
            self.get_rect().update(self.x, self.y, self.width, self.height)

        self.rotation_angle = angle

    def set_color(self, color):
        """Sets the color of the Border.

        Args:
            color (tuple): The new color for the Border.
        """
        self.color = color

    def set_alpha(self, alpha):
        """Sets the alpha value of the Border.

        Args:
            alpha (int): The new alpha value.
        """
        self.alpha = alpha
        for box in self.get_side_boxes():
            box.set_alpha(self.alpha)

    def get_side_boxes(self):
        """Gets a list of side boxes that make up the Border.

        Returns:
            list: List of side boxes.
        """
        side_boxes = [x for x in self.children if isinstance(x, Box)]
        return side_boxes

    def process(self):
        """Processes the Border, updating its position relative to its parent if applicable."""
        self.update_pos_relative_to_parent()


class Button(Box):
    """A customizable button with various interactive features, such as click and hover events.

    Attributes:
        x (int): X-coordinate of the box.
        y (int): Y-coordinate of the box.
        z (float): Z-coordinate of the box.
        width (int): Width of the box.
        height (int): Height of the box.
        alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
        name (str): Name of the box.
        destroyed (bool): Indicates whether the box has been destroyed.
        parent: Parent object to which this box is attached.
        static (bool): Indicates whether the box is static (does not move together with its parent).
        displayable (bool): Indicates whether the box is visible.
        opaque (bool): Indicates whether the box blocks objects earlier in the processing order from
            being clicked.
        children (list): List of child objects.
        rect (pygame.Rect): Rectangular area occupied by the object.
        rotation_angle (int): Rotation angle of the box in degrees.
        relative_x (int): The x-coordinate of the box in relation to it's parent, if applicable.
        relative_y (int): The y-coordinate of the box in relation to it's parent, if applicable.
        text (str): The string to be displayed on the box
        text_color (tuple): The color of the text.
        font_size (int): The font size of the text.
        text_surface_id (int): The id corresponding to the text surface of the box.
        update_text_func (func): The function responsible for updating the box text.
        surface_id (int): The id corresponding to the surface of the box.
        left_click_function (func):
        right_click_function (func):
    """

    # TODO: Change left_click_args etc to args and kwargs.
    def __init__(self, x=0, y=0, z=1, width=200, height=120, colors=None, alpha=255, image=None, text="", font_size=40,
                 text_color=BLACK, name=None, parent=None, static=False, left_trigger_keys=None,
                 right_trigger_keys=None,
                 left_click_function=None, left_click_args=None, left_hold_function=None, left_hold_args=None,
                 right_click_function=None, right_click_args=None, right_hold_function=None, right_hold_args=None,
                 key_functions=None, external_process_function=None, external_process_arguments=None):
        """Creates a new button.

        Args:
            x (int): The x-coordinate of the button.
            y (int): The y-coordinate of the button.
            z (float): The z-coordinate of the button.
            width (int): The width of the button.
            height (int): The height of the button.
            colors (dict): Dictionary containing color information for different button states.
            alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
            image (Pygame.image): The image used for the button (default is None).
            text (str): The text displayed on the button (default is an empty string).
            font_size (int): The font size of the text (default is 40).
            text_color: The color of the text (default is BLACK).
            name (str): The name of the button (default is None).
            parent: The parent object (default is None).
            static (bool): Indicates whether the object is static (does not move together with its parent).
            left_trigger_keys (list): List of keys triggering left-click events (default is None).
            right_trigger_keys (list): List of keys triggering right-click events (default is None).
            left_click_function (func): The function to be called on left-click (default is None).
            left_click_args: The arguments for the left-click function (default is None).
            left_hold_function (func): The function to be called while left-click is held (default is None).
            left_hold_args: The arguments for the left-hold function (default is None).
            right_click_function (func): The function to be called on right-click (default is None).
            right_click_args: The arguments for the right-click function (default is None).
            right_hold_function: The function to be called while right-click is held (default is None).
            right_hold_args: The arguments for the right-hold function (default is None).
            key_functions (dict): Dictionary mapping keys to functions and their arguments (default is None).
            external_process_function (func): External function to be called during the button's processing
                (default is None).
            external_process_arguments: Arguments for the external process function (default is None).
        """

        # TODO: Perhaps change the format for the colors, use a list or something.

        standard_colors = {"normal": (100, 100, 100), "hover": (150, 150, 150), "pressed": (200, 200, 200)}
        if colors is None:
            colors = standard_colors

        if external_process_arguments is None:
            self.external_process_arguments = []
        else:
            self.external_process_arguments = external_process_arguments

        if left_trigger_keys is None:
            self.left_trigger_keys = []
        else:
            self.left_trigger_keys = left_trigger_keys

        if right_trigger_keys is None:
            self.right_trigger_keys = []
        else:
            self.right_trigger_keys = right_trigger_keys

        if left_click_args is None:
            self.left_click_args = {}
        else:
            self.left_click_args = left_click_args

        if left_hold_args is None:
            self.left_hold_args = {}
        else:
            self.left_hold_args = left_hold_args

        if right_click_args is None:
            self.right_click_args = {}
        else:
            self.right_click_args = right_click_args

        if right_hold_args is None:
            self.right_hold_args = {}
        else:
            self.right_hold_args = right_hold_args

        if key_functions is None:
            self.key_functions = {}
        else:
            self.key_functions = key_functions

        super().__init__(x=x, y=y, z=z, width=width, height=height, color=colors["normal"], alpha=alpha,
                         source_image=image, text=text, font_size=font_size, text_color=text_color, parent=parent,
                         static=static, name=name)

        self.left_click_function = left_click_function
        self.left_hold_function = left_hold_function
        self.right_click_function = right_click_function
        self.right_hold_function = right_hold_function

        self.colors = colors

        self.static = False

        self.external_process_function = external_process_function
        self.status = "normal"

        self.click_detector = ClickDetector(self.get_rect())

        border = Border(x=self.x, y=self.y, z=self.z, width=self.width, height=self.height, parent=self,
                        name="btn_border")
        self.add_child(border)

    def get_border(self):
        """Gets the border object associated with the button.

        Returns:
            Border: The border object of the button.
        """
        return utils.find_object_from_name(self.children, "btn_border")

    def set_width(self, width):
        """Sets the width of the button and its associated Border.

        Args:
            width (int): The new width of the button.
        """
        super().set_width(width)
        self.get_border().set_width(width)

    def set_height(self, height):
        """Sets the height of the button and its associated Border.

        Args:
            height (int): The new height of the button.
        """
        super().set_height(height)
        self.get_border().set_height(height)

    def set_rotation(self, angle):
        """Sets the rotation angle of the button and rotates its associated Border.

        Args:
            angle (int): The new rotation angle in degrees.
        """
        super().set_rotation(angle)
        self.get_border().set_rotation(angle)

    def set_colors(self, colors):
        """Sets the colors of the button for the different states.

        Args:
            colors (dict): Dictionary containing color information for the different button states.
        """
        super().set_color(self.colors[self.status])
        self.colors = colors

    def set_left_click_function(self, new_function, new_arguments=None):
        """Sets the function to be called when the button is left-clicked.

        Args:
            new_function: The new left-click function.
            new_arguments: The new arguments for the left-click function.
        """
        if new_arguments is None:
            new_arguments = []
        self.left_click_function = new_function
        self.left_click_args = new_arguments

    def set_left_hold_function(self, new_function, new_arguments=None):
        """Sets the function to be called when the button is left-held.

        Args:
            new_function (func): The new left-hold function.
            new_arguments: The new arguments for the left-hold function.
        """
        if new_arguments is None:
            new_arguments = []
        self.left_hold_function = new_function
        self.left_hold_args = new_arguments

    def set_right_click_function(self, new_function, new_arguments=None):
        """Sets the function to be called when the button is right-clicked.

        Args:
            new_function (func): The new right-clicked function.
            new_arguments: The new arguments for the right-clicked function.
        """
        if new_arguments is None:
            new_arguments = []
        self.right_click_function = new_function
        self.right_click_args = new_arguments

    def set_right_hold_function(self, new_function, new_arguments=None):
        """Sets the function to be called when the button is right-held.

        Args:
            new_function (func): The new right-hold function.
            new_arguments: The new arguments for the right-hold function.
        """
        if new_arguments is None:
            new_arguments = []
        self.right_hold_function = new_function
        self.right_hold_args = new_arguments

    def get_external_process_function(self):
        """Gets the external process function.

        Returns:
            func: The external process function.
        """
        return self.external_process_function

    def set_external_process_function(self, new_function):
        """Sets a new external process function.

        Returns:
            new_function (func): The new external process function.
        """
        self.external_process_function = new_function

    def get_external_process_arguments(self):
        """Gets the arguments for the external process function.

        Returns:
            list: List of arguments for the external process function.
        """
        return self.external_process_arguments

    def set_external_process_arguments(self, args):
        """Set the arguments for the external process function.

        Args:
            args (list): List of arguments for the external process function.
        """
        self.external_process_arguments = args

    def click_blocked(self, click_position):
        """Checks if the button click is blocked by other objects.

        Args:
            click_position: The position of the click.

        Returns:
            bool: True if the click is blocked, False otherwise.
        """
        blocking_objects_list = game_engine.get_scene_manager().current_scene.get_object_mask(self)
        for obj in blocking_objects_list:
            if obj.get_rect().collidepoint(click_position):
                return True
        return False

    def set_require_continuous_hovering(self, boolean):
        """Sets whether the button requires the mouse to be on it for button interaction.

        Args:
            boolean (bool): True if continuous hovering is required, False otherwise.
        """
        self.click_detector.require_continuous_hovering = boolean

    def check_button_presses(self):
        """Check for button presses/key presses and executes corresponding functions. Can execute any combination of
        different click events in the same tick."""
        mouse_position = environment.get_mouse_position()

        if not self.click_blocked(mouse_position):
            button_left_clicked = self.click_detector.left_clicked or environment.key_press in self.left_trigger_keys
            button_left_held = self.click_detector.left_clicked_long

            button_right_clicked = self.click_detector.right_clicked or environment.key_press in self.right_trigger_keys
            button_right_held = self.click_detector.right_clicked_long

            hovering = (not self.click_detector.left_clicked and not self.click_detector.right_clicked and
                        self.get_rect().collidepoint(mouse_position))

        else:
            button_left_clicked = False
            button_left_held = False
            button_right_clicked = False
            button_right_held = False
            hovering = False

        self.status = "normal"

        key_function, key_args = None, []
        for key in self.key_functions:
            if environment.key_press == key:
                key_function = self.key_functions[key][0]
                key_args = self.key_functions[key][1]
                break

        if button_left_clicked and self.left_click_function is not None:
            self.status = "pressed"
            if isinstance(self.left_click_args, dict):
                self.left_click_function(**self.left_click_args)
            else:
                self.left_click_function(*self.left_click_args)

        if button_left_held and self.left_hold_function is not None:
            self.status = "pressed"
            if isinstance(self.left_hold_args, dict):
                self.left_hold_function(**self.left_hold_args)
            else:
                self.left_hold_function(*self.left_hold_args)

        if button_right_clicked and self.right_click_function is not None:
            self.status = "pressed"

            if isinstance(self.right_click_args, dict):
                self.right_click_function(**self.right_click_args)
            else:
                self.right_click_function(*self.right_click_args)

        if button_right_held and self.right_hold_function is not None:
            self.status = "pressed"
            if isinstance(self.right_hold_args, dict):
                self.right_hold_function(**self.right_hold_args)
            else:
                self.right_hold_function(*self.right_hold_args)

        if key_function is not None:
            if isinstance(key_args, dict):
                key_function(**key_args)
            else:
                key_function(*key_args)

        if hovering and self.status != "pressed":
            self.status = "hover"

    def process(self):
        """Process the button, updating its click_detector checking for click-events  and updating it's color."""
        super().process()

        self.click_detector.update()

        self.check_button_presses()

        if self.external_process_function is not None:
            self.external_process_function(*self.external_process_arguments)

        self.set_color(self.colors[self.status])


class ClickDetector:
    """A class dedicated to detecting clicks for buttons

    Attributes:
        rect (Pygame.rect): The rect inside which the click detector detects clicks.
        left_clicked (bool):
        left_clicked_long (bool):
        right_clicked (bool):
        right_clicked_long (bool):
        require_continuous_hovering (bool):
    """
    def __init__(self, rect):
        """Initialize the ClickDetector with the specified rectangle.

        Args:
            rect (pygame.Rect): The rect inside which the click detector detects clicks.
        """
        self.rect = rect

        self.left_clicked = False
        self.left_clicked_long = False

        self.right_clicked = False
        self.right_clicked_long = False

        self.require_continuous_hovering = True

    def _left_clicked(self):
        """Detects new left clicks.

        Returns:
            bool: True if the related rectangle is left-clicked, False otherwise.
        """
        left_mouse_down = environment.get_left_mouse_click_this_tick()
        mouse_above_rect = self.rect.collidepoint(environment.get_mouse_position())
        if left_mouse_down and mouse_above_rect and not environment.get_left_mouse_click_last_tick():
            return True

        return False

    def _left_clicked_long(self):
        """Detects long left clicks, that is if the mouse button continually being pressed.

        Returns:
            bool: True if the related rectangle is long left-clicked, False otherwise.
        """
        left_mouse_down = environment.get_left_mouse_click_this_tick()
        mouse_above_rect = self.rect.collidepoint(environment.get_mouse_position())
        excuse_non_hovering = not self.require_continuous_hovering and (self.left_clicked or self.left_clicked_long)

        if left_mouse_down and (mouse_above_rect or excuse_non_hovering):
            return True

        return False

    def _right_clicked(self):
        """Detects new right clicks.

        Returns:
            bool: True if the related rectangle is right-clicked, False otherwise.
        """
        right_mouse_down = environment.get_right_mouse_click_this_tick()
        mouse_above_rect = self.rect.collidepoint(environment.get_mouse_position())
        if right_mouse_down and mouse_above_rect and not environment.get_right_mouse_click_last_tick():
            return True

        return False

    def _right_clicked_long(self):
        """Detects long right clicks, that is if the mouse button continually being pressed.

        Returns:
            bool: True if the related rectangle is long right-clicked, False otherwise.
        """
        right_mouse_down = environment.get_right_mouse_click_this_tick()
        mouse_above_rect = self.rect.collidepoint(environment.get_mouse_position())
        excuse_non_hovering = not self.require_continuous_hovering and (self.right_clicked or self.right_clicked_long)

        if right_mouse_down and (mouse_above_rect or excuse_non_hovering):
            return True

        return False

    def update(self):
        """Updates the click detector's attributes based on the current mouse click events."""
        self.left_clicked = self._left_clicked()
        self.left_clicked_long = self._left_clicked_long()

        self.right_clicked_long = self._right_clicked_long()
        self.right_clicked = self._right_clicked()


class MobileButton(Button):
    """A class for button that can be moved using the mouse.

    Attributes:
        x (int): The x-coordinate of the button.
        y (int): The y-coordinate of the button.
        z (float): The z-coordinate of the button.
        width (int): The width of the button.
        height (int): The height of the button.
        alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
        name (str): The name of the button.
        destroyed (bool): Indicates whether the button has been destroyed.
        parent: The parent object to which this button is attached.
        static (bool): Indicates whether the button is static (does not move together with its parent).
        displayable (bool): Indicates whether the button is visible.
        opaque (bool): Indicates whether the button blocks objects earlier in the processing order from
            being clicked.
        children (list): List of child objects.
        rect (pygame.Rect): The rectangular area occupied by the object.
        rotation_angle (int): The rotation angle of the button in degrees.
        relative_x (int): The x-coordinate of the button in relation to its parent, if applicable.
        relative_y (int): The y-coordinate of the button in relation to its parent, if applicable.
        text (str): The string to be displayed on the button.
        text_color (tuple): The color of the text.
        font_size (int): The font size of the text.
        text_surface_id (int): The id corresponding to the text surface of the button.
        update_text_func (func): The function responsible for updating the button text.
        surface_id (int): The id corresponding to the surface of the button.
        left_click_function (func): Function to be called on left-click.
        right_click_function (func): Function to be called on right-click.
        moving (bool): Indicates whether the button is currently moving.
        click_x (int): The x-coordinate of the mouse click in the button's coordinate system.
        click_y (int): The y-coordinate of the mouse click in the button's coordinate system.
    """
    def __init__(self, x=0, y=0, z=1, width=200, height=120, color=(100, 100, 100), alpha=255, static=False,
                 image=None, text="", font_size=40,
                 text_color=BLACK, name=None, parent=None, left_trigger_keys=None, right_trigger_keys=None,
                 right_click_function=None, right_click_args=None, right_hold_function=None, right_hold_args=None,
                 key_functions=None, external_process_function=None, external_process_arguments=None):
        """Creates a new mobile button with movement support.

        Args:
            x (int): The x-coordinate of the button.
            y (int): The y-coordinate of the button.
            z (float): The z-coordinate of the button.
            width (int): The width of the button.
            height (int): The height of the button.
            color (tuple): The color of the button.
            alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
            static (bool): Indicates whether the button is static (does not move together with its parent).
            image (Pygame.image): The image used for the button (default is None).
            text (str): The text displayed on the button (default is an empty string).
            font_size (int): The font size of the text (default is 40).
            text_color: The color of the text (default is BLACK).
            name (str): The name of the button (default is None).
            parent: The parent object (default is None).
            left_trigger_keys (list): List of keys triggering left-click events (default is None).
            right_trigger_keys (list): List of keys triggering right-click events (default is None).
            right_click_function (func): The function to be called on right-click (default is None).
            right_click_args: The arguments for the right-click function (default is None).
            right_hold_function: The function to be called while right-click is held (default is None).
            right_hold_args: The arguments for the right-hold function (default is None).
            key_functions (dict): Dictionary mapping keys to functions and their arguments (default is None).
            external_process_function (func): External function to be called during the button's processing
                (default is None).
            external_process_arguments: Arguments for the external process function (default is None).
        """

        colors = {"normal": color, "hover": color, "pressed": color}
        self.moving = False
        self.click_x = None
        self.click_y = None
        super().__init__(x=x, y=y, z=z, width=width, height=height, colors=colors, alpha=alpha, image=image, text=text,
                         font_size=font_size, text_color=text_color, name=name, parent=parent, static=static,
                         left_trigger_keys=left_trigger_keys, right_trigger_keys=right_trigger_keys,
                         left_click_function=self.start_movement, left_hold_function=self.move,
                         right_click_function=right_click_function, right_click_args=right_click_args,
                         right_hold_function=right_hold_function, right_hold_args=right_hold_args,
                         key_functions=key_functions, external_process_function=external_process_function,
                         external_process_arguments=external_process_arguments)
        super().set_require_continuous_hovering(False)

    def process(self):
        """Processes the mobile button, resetting the attributes related to movement if the button is not being
         left-held.
         """

        if not self.click_detector.left_clicked_long:
            self.moving = False
            self.click_x, self.click_y = None, None
        super().process()

    def move(self):
        """Handles the movement of the mobile button."""
        if not self.moving:
            return
        mouse_position = environment.get_mouse_position()
        self.set_pos(mouse_position[0] - self.click_x, mouse_position[1] - self.click_y)

    def start_movement(self):
        """Starts the movement of the mobile button."""
        mouse_position = environment.get_mouse_position()
        self.moving = True
        self.click_x, self.click_y = mouse_position[0] - self.x, mouse_position[1] - self.y


class Overlay(GameObject):
    """A graphical overlay with a customizable appearance and optional close button.

    Attributes:
        x (int): The x-coordinate of the overlay.
        y (int): The y-coordinate of the overlay.
        z (float): The z-coordinate of the overlay.
        width (int): The width of the overlay.
        height (int): The height of the overlay.
        alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
        static (bool): Indicates whether the overlay is static (does not move together with its parent).
        name (str): The name of the overlay.
        destroyed (bool): Indicates whether the object has been destroyed.
        parent: Parent object to which this overlay is attached.
        close_btn_size (int): Size of the close button on the overlay.
        close_btn_offset (int): Offset of the close button from the top-right corner of the overlay.
        external_process_function (func): External function to be called during the overlay's processing.
        external_process_arguments: Arguments for the external process function.
        displayable (bool): Indicates whether the object is visible.
        opaque (bool): Indicates whether the object blocks objects earlier in the processing order from
            being clicked.
        children (list): List of child objects.
        rotation_angle (int): Rotation angle of the object in degrees.
        relative_x (int): The x-coordinate of the object in relation to it's parent, if applicable.
        relative_y (int): The y-coordinate of the object in relation to it's parent, if applicable.
    """
    def __init__(self, x=0, y=0, z=2, width=1540, height=760, alpha=255, static=True, name=None, background_color=WHITE,
                 close_btn_size=30, close_btn_offset=5, parent=None,
                 external_process_function=None, external_process_arguments=None):
        """Creates a new overlay with an optional close button.

         Args:
             x (int): The x-coordinate of the overlay.
             y (int): The y-coordinate of the overlay.
             z (float): The z-coordinate of the overlay.
             width (int): The width of the overlay.
             height (int): The height of the overlay.
             alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
             static (bool): Indicates whether the overlay is static (does not move together with its parent).
             name (str): The name of the overlay.
             background_color (tuple): The color of the overlay background.
             close_btn_size (int): Size of the close button on the overlay.
             close_btn_offset (int): Offset of the close button from the top-right corner of the overlay.
             parent: The parent object to which this overlay is attached.
             external_process_function (func): External function to be called during the overlay's processing.
             external_process_arguments: Arguments for the external process function.
         """

        super().__init__(x=x, y=y, z=z, width=width, height=height, parent=parent, static=static,
                         alpha=alpha, opaque=False, name=name)
        if external_process_arguments is None:
            self.external_process_arguments = []
        else:
            self.external_process_arguments = external_process_arguments
        self.external_process_function = external_process_function

        box = Box(x=self.x, y=self.y, z=self.z, width=self.width, height=self.height, color=background_color,
                  alpha=self.alpha, name="overlay_box")
        self.add_child(box)

        border = Border(x=self.x, y=self.y, z=self.z, width=self.width, height=self.height, color=BLACK, parent=self,
                        name="overlay_border")
        self.add_child(border)

        self.parent = parent

        self.close_btn_size = close_btn_size
        self.close_btn_offset = close_btn_offset
        close_btn = Button(x=self.x + self.width - close_btn_size - close_btn_offset,
                           y=self.y + close_btn_offset, z=self.z, width=close_btn_size, height=close_btn_size,
                           image=pygame.image.load("Images/close_button.png"), font_size=15, parent=self,
                           left_click_function=self.destroy, left_trigger_keys=["escape"],
                           name="close_btn")
        self.add_child(close_btn)

    def get_rect(self):
        """Gets the rectangular area occupied by the overlay.

         Returns:
             pygame.Rect: The rectangular area of the overlay.
         """
        return self.get_box().get_rect()

    def get_box(self):
        """Gets the underlying box object of the overlay.

        Returns:
            Box: The box object of the overlay.
        """
        return utils.find_object_from_name(self.children, "overlay_box")

    def get_buttons(self):
        """Gets a list of button objects present in the overlay.

        Returns:
            list: List of Button objects in the overlay.
        """
        return utils.find_objects_from_type(self.children, Button)

    def set_background_color(self, color):
        """Sets the background color of the overlay.

        Args:
            color (tuple): The color to set as the background color.
        """
        self.get_box().set_color(color)

    def process(self):
        """Processes the overlay, including external processing and the standard processing routine."""

        if self.external_process_function is not None:
            self.external_process_function(*self.external_process_arguments)

        super().process()

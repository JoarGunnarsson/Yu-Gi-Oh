from constants import *
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from game_engine import environment
import game_engine
import utility_functions as utils


class GameScript:
    def __init__(self):
        pass

    def process(self):
        pass


class GameObject:
    def __init__(self, x=0, y=0, z=0, alpha=255, width=0, height=0, parent=None, static=False, name=""):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.name = name
        self.destroyed = False
        self.parent = parent
        self.static = static
        self.children = []
        self.rect = None
        self.rotation_angle = 0
        self.alpha = alpha
        if self.parent is None:
            self.relative_x, self.relative_y = 0, 0
        else:
            self.relative_x, self.relative_y = self.x - self.parent.x, self.y - self.parent.y

    def get_rect(self):
        return self.rect

    def set_x(self, x):
        self.x = x
        self.get_rect().update(self.x, self.y, self.width, self.height)
        self.update_relative_position()

    def set_y(self, y):
        self.y = y
        self.get_rect().update(self.x, self.y, self.width, self.height)
        self.update_relative_position()

    def set_pos(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def shift_x(self, delta_x):
        self.set_x(self.x + delta_x)

    def shift_y(self, delta_y):
        self.set_y(self.y + delta_y)

    def shift_pos(self, delta_x, delta_y):
        self.shift_x(delta_x)
        self.shift_y(delta_y)

    def set_relative_x(self, x):
        self.relative_x = x

    def set_relative_y(self, y):
        self.relative_y = y

    def set_pos_relative_to_parent(self, x, y):
        """Sets the relative position of the button in relation to the parent. The coordinates (x,y) refer to the
        coordinates of the button in the coordinate system where the parents position is the origin."""
        if self.static:
            return

        self.relative_x, self.relative_y = x, y
        self.set_pos(x=self.relative_x + self.parent.x, y=self.relative_y + self.parent.y)

    def update_relative_position(self):
        if self.static or self.parent is None:
            return
        self.set_relative_x(self.x - self.parent.x)
        self.set_relative_y(self.y - self.parent.y)

    def update_position(self):
        if self.parent is not None:
            self.update_pos_relative_to_parent()

    def update_pos_relative_to_parent(self):
        if self.static:
            return

        self.set_pos(x=self.relative_x + self.parent.x, y=self.relative_y + self.parent.y)

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_size(self, width, height):
        self.set_width(width)
        self.set_height(height)

    def set_width_relative(self, delta_w):
        self.set_width(self.width + delta_w)

    def set_height_relative(self, delta_h):
        self.set_height(self.height + delta_h)

    def get_rotation(self):
        return self.rotation_angle

    def set_rotation(self, angle):
        if ((self.rotation_angle - angle) // 90) % 2 == 1:
            self.width, self.height = self.height, self.width
        self.rotation_angle = angle
        self.get_rect().update(self.x, self.y, self.width, self.height)

    def rotate(self, angle):
        self.set_rotation(self.rotation_angle + angle)

    def set_alpha(self, alpha):
        self.alpha = alpha

    def destroy(self):
        if self.destroyed:
            return
        self.destroyed = True
        game_engine.get_scene_manager().current_scene.hide_object(self)
        if self.parent is not None and hasattr(self.parent, "destroy_child"):
            game_engine.schedule_end_of_tick_function(self.parent.destroy_child, [self])

    def add_child(self, child):
        self.children.append(child)
        if child.parent is None:
            child.set_parent(self)

    def set_parent(self, parent):
        self.parent = parent
        if not self.static and self.parent is not None:
            self.relative_x, self.relative_y = self.x - self.parent.x, self.y - self.parent.y

    def add_multiple_children(self, children):
        for child in children:
            self.add_child(child)

    def destroy_child(self, child):
        if child in self.children:
            self.children.remove(child)

    def clear_children(self):
        self.children = []

    def schedule_processing(self):
        items_to_be_processed = [self]

        for child in self.children:
            items_to_be_processed.extend(child.schedule_processing())

        return items_to_be_processed

    def process(self):
        if self.parent is not None and not self.static:
            self.update_pos_relative_to_parent()


class Box(GameObject):
    def __init__(self, x=0, y=0, z=0, width=100, height=100, color=WHITE, alpha=255, source_image=None, text="",
                 text_color=BLACK,
                 font_size=40, update_text_func=None, parent=None, name=None):
        super().__init__(x=x, y=y, z=z, width=width, height=height, alpha=alpha, parent=parent, name=name)
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

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.surface_id = game_engine.get_surface_manager().create_surface(self.width, self.height, self.alpha)
        self.static = True
        self.rotation_angle = 0
        self.set_alpha(self.alpha)

    def set_width(self, width):
        self.width = width
        self.get_rect().update(self.x, self.y, self.width, self.height)
        if self.source_image_id is not None:
            game_engine.get_surface_manager().scale_image(self.source_image_id, (self.width, self.height),
                                                          new_id=self.image_id)

        # Updates the surface corresponding to self.surface_id
        game_engine.get_surface_manager().scale_surface(self.surface_id, (self.width, self.height),
                                                        new_id=self.surface_id)

    def set_height(self, height):
        self.height = height
        self.get_rect().update(self.x, self.y, self.width, self.height)
        if self.source_image_id is not None:
            game_engine.get_surface_manager().scale_image(self.source_image_id, (self.width, self.height),
                                                          new_id=self.image_id)

        # Updates the surface corresponding to self.surface_id
        game_engine.get_surface_manager().scale_surface(self.surface_id, (self.width, self.height),
                                                        new_id=self.surface_id)

    def set_rotation(self, angle):
        theta = angle - self.rotation_angle

        if self.image_id is not None:
            game_engine.get_surface_manager().rotate_image(self.image_id, theta, new_id=self.image_id)

        game_engine.get_surface_manager().rotate_surface(self.surface_id, theta, new_id=self.surface_id)

        super().set_rotation(angle)

    def set_image(self, image):
        self.source_image_id = game_engine.get_surface_manager().set_image(image, self.source_image_id)
        self.image_id = game_engine.get_surface_manager().scale_image(self.source_image_id, (self.width, self.height),
                                                                      self.image_id)

    def set_text(self, new_text):
        self.text = new_text
        game_engine.get_surface_manager().create_font_surface(self.text, self.text_color, self.font_size,
                                                              self.text_surface_id)

    def set_color(self, color):
        self.color = color

    def set_alpha(self, alpha):
        self.alpha = alpha
        game_engine.get_surface_manager().fetch_surface(self.surface_id).set_alpha(self.alpha)

    def get_displayable_objects(self):
        return [self]

    def hug_text(self, offset):
        text_surface = game_engine.get_surface_manager().fetch_text_surface(self.text_surface_id)
        self.set_width(text_surface.get_width() + 2 * offset)
        self.set_height(text_surface.get_height() + 2 * offset)

    def get_display_surface(self):
        """Returns a tuple, where the first element is the surface to be displayed, and the second element
         being the object's rect."""
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
    def __init__(self, x=0, y=0, z=0, width=100, height=100, color=BLACK, thickness=1, alpha=255, parent=None,
                 name=None):
        super().__init__(x=x, y=y, z=z, width=width, height=height, parent=parent, alpha=alpha, name=name)

        self.color = color
        self.thickness = thickness
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        top_box = Box(x=self.x, y=self.y, width=self.width, height=self.thickness, color=self.color, alpha=self.alpha,
                      parent=self)

        bottom_box = Box(x=self.x, y=self.y + self.height - self.thickness, width=self.width, height=self.thickness,
                         color=self.color, alpha=self.alpha, parent=self)

        left_box = Box(x=self.x, y=self.y + self.thickness, width=self.thickness,
                       height=self.height - 2 * self.thickness, color=self.color, alpha=self.alpha, parent=self)

        right_box = Box(x=self.x + self.width - self.thickness, y=self.y + self.thickness, width=self.thickness,
                        height=self.height - 2 * self.thickness, color=self.color, alpha=self.alpha, parent=self)

        side_boxes = [top_box, bottom_box, left_box, right_box]

        for box in side_boxes:
            box.static = True

        self.children.extend(side_boxes)

    def set_pos(self, x, y):
        for box in self.get_side_boxes():
            box.set_pos(x=box.x + (x - self.x), y=box.y + (y - self.y))
        super().set_pos(x, y)

    def set_width(self, width):
        width_difference = width - self.width
        side_boxes = self.get_side_boxes()
        side_boxes[3].shift_x(width_difference)
        side_boxes[0].set_width_relative(width_difference)
        side_boxes[1].set_width_relative(width_difference)

        super().set_width(width)

    def set_height(self, height):
        height_difference = height - self.height
        side_boxes = self.get_side_boxes()
        side_boxes[1].shift_y(height_difference)
        side_boxes[2].set_height_relative(height_difference)
        side_boxes[3].set_height_relative(height_difference)

        super().set_height(height)

    def set_rotation(self, angle):
        if ((self.rotation_angle - angle) // 90) % 2 == 1:
            self.set_size(width=self.height, height=self.width)

        self.rotation_angle = angle

        self.get_rect().update(self.x, self.y, self.width, self.height)

    def set_color(self, color):
        self.color = color

    def set_alpha(self, alpha):
        self.alpha = alpha
        for box in self.get_side_boxes():
            box.set_alpha(self.alpha)

    def get_side_boxes(self):
        side_boxes = [x for x in self.children if type(x) == Box]
        return side_boxes

    def get_displayable_objects(self):
        return self.get_side_boxes()

    def process(self):
        self.update_pos_relative_to_parent()


class Button(Box):
    # TODO: Change left_click_args etc to args and kwargs.
    def __init__(self, x=0, y=0, z=0, width=200, height=120, colors=None, alpha=255, image=None, text="", font_size=40,
                 text_color=BLACK, name=None, parent=None, left_trigger_keys=None, right_trigger_keys=None,
                 left_click_function=None, left_click_args=None, left_hold_function=None, left_hold_args=None,
                 right_click_function=None, right_click_args=None, right_hold_function=None, right_hold_args=None,
                 key_functions=None, external_process_function=None, external_process_arguments=None):
        """Creates a new button. X and y refers to the upper left corner of the button"""

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
                         name=name)

        self.left_click_function = left_click_function
        self.left_hold_function = left_hold_function
        self.right_click_function = right_click_function
        self.right_hold_function = right_hold_function

        self.colors = colors

        self.static = False

        self.external_process_function = external_process_function
        self.status = "normal"

        self.click_detector = ClickDetector(self.get_rect())

        border = Border(x=self.x, y=self.y, z=z, width=self.width, height=self.height, parent=self,
                        name="btn_border")
        self.add_child(border)

    def get_border(self):
        return utils.find_object_from_name(self.children, "btn_border")

    def set_pos(self, x, y):
        super().set_pos(x, y)

        for child in self.children:
            child.update_position()

    def set_width(self, width):
        super().set_width(width)
        self.get_border().set_width(width)

    def set_height(self, height):
        super().set_height(height)
        self.get_border().set_height(height)

    def set_rotation(self, angle):
        super().set_rotation(angle)
        self.get_border().set_rotation(angle)

    def get_displayable_objects(self):
        displayable_objects = [self]
        displayable_objects.extend(self.get_border().get_displayable_objects())
        return displayable_objects

    def set_colors(self, colors):
        super().set_color(self.colors[self.status])
        self.colors = colors

    def set_left_click_function(self, new_function, new_arguments=None):
        if new_arguments is None:
            new_arguments = []
        self.left_click_function = new_function
        self.left_click_args = new_arguments

    def set_left_hold_function(self, new_function, new_arguments=None):
        if new_arguments is None:
            new_arguments = []
        self.left_hold_function = new_function
        self.left_hold_args = new_arguments

    def set_right_click_function(self, new_function, new_arguments=None):
        if new_arguments is None:
            new_arguments = []
        self.right_click_function = new_function
        self.right_click_args = new_arguments

    def set_right_hold_function(self, new_function, new_arguments=None):
        if new_arguments is None:
            new_arguments = []
        self.right_hold_function = new_function
        self.right_hold_args = new_arguments

    def get_external_process_arguments(self):
        return self.external_process_arguments

    def set_external_process_arguments(self, args):
        self.external_process_arguments = args

    def click_blocked(self, click_position):
        masking_types = [Button, Overlay, Box]
        blocking_objects_list = game_engine.get_scene_manager().current_scene.get_object_mask(self, masking_types)
        for obj in blocking_objects_list:
            if obj.get_rect().collidepoint(click_position):
                return True
        return False

    def toggle_continuous_hovering(self):
        self.click_detector.require_continuous_hovering = not self.click_detector.require_continuous_hovering

    def check_button_presses(self):
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

        key_function, key_args = None, None
        for key in self.key_functions:
            if environment.key_press == key:
                key_function = self.key_functions[key][0]
                key_args = self.key_functions[key][1]
                break

        if button_left_clicked and self.left_click_function is not None:
            self.status = "pressed"
            if type(self.left_click_args) is dict:
                self.left_click_function(**self.left_click_args)
            else:
                self.left_click_function(*self.left_click_args)

        if button_left_held and self.left_hold_function is not None:
            self.status = "pressed"
            if type(self.left_hold_args) is dict:
                self.left_hold_function(**self.left_hold_args)
            else:
                self.left_hold_function(*self.left_hold_args)

        if button_right_clicked and self.right_click_function is not None:
            self.status = "pressed"

            if type(self.right_click_args) is dict:
                self.right_click_function(**self.right_click_args)
            else:
                self.right_click_function(*self.right_click_args)

        if button_right_held and self.right_hold_function is not None:
            self.status = "pressed"
            if type(self.right_hold_args) is dict:
                self.right_hold_function(**self.right_hold_args)
            else:
                self.right_hold_function(*self.right_hold_args)

        if key_function is not None:
            if type(key_args) is dict:
                key_function(**key_args)
            else:
                key_function(*key_args)

        if hovering and self.status != "pressed":
            self.status = "hover"

    def process(self):
        super().process()

        self.click_detector.update()

        self.check_button_presses()

        if self.external_process_function is not None:
            self.external_process_function(*self.external_process_arguments)

        self.set_color(self.colors[self.status])


class ClickDetector:
    def __init__(self, rect):
        self.rect = rect
        self.left_mouse_down_last_update = pygame.mouse.get_pressed(num_buttons=3)[0]
        self.right_mouse_down_last_update = pygame.mouse.get_pressed(num_buttons=3)[2]

        self.left_clicked = False
        self.left_clicked_long = False

        self.right_clicked = False
        self.right_clicked_long = False

        self.require_continuous_hovering = True

    def _left_clicked(self):
        """Detects left clicks. Returns true if the related rectangle is left-clicked, and false otherwise.
                A click requires the mouse button not having been pressed before the check."""
        left_mouse_down = pygame.mouse.get_pressed(num_buttons=3)[0]
        mouse_above_rect = self.rect.collidepoint(environment.get_mouse_position())
        if left_mouse_down and mouse_above_rect and not self.left_mouse_down_last_update:
            return True

        return False

    def _left_clicked_long(self):
        """Detects long left clicks. Returns true if the related rectangle is long left-clicked, and false otherwise.
                A long click requires the mouse button continually depressed."""

        left_mouse_down = pygame.mouse.get_pressed(num_buttons=3)[0]
        mouse_above_rect = self.rect.collidepoint(environment.get_mouse_position())
        excuse_non_hovering = not self.require_continuous_hovering and (self.left_clicked or self.left_clicked_long)

        if left_mouse_down and (mouse_above_rect or excuse_non_hovering):
            return True

        return False

    def _right_clicked(self):
        """Detects right clicks. Returns true if the related rectangle is left-clicked, and false otherwise.
                A click requires the mouse button not having been pressed before the check."""
        right_mouse_down = pygame.mouse.get_pressed(num_buttons=3)[2]
        mouse_above_rect = self.rect.collidepoint(environment.get_mouse_position())
        if right_mouse_down and mouse_above_rect and not self.right_mouse_down_last_update:
            return True

        return False

    def _right_clicked_long(self):
        """Detects long right clicks. Returns true if the related rectangle is long right-clicked, and false otherwise.
                A long click requires the mouse button continually depressed."""

        right_mouse_down = pygame.mouse.get_pressed(num_buttons=3)[2]
        mouse_above_rect = self.rect.collidepoint(environment.get_mouse_position())
        excuse_non_hovering = not self.require_continuous_hovering and (self.right_clicked or self.right_clicked_long)

        if right_mouse_down and (mouse_above_rect or excuse_non_hovering):
            return True

        return False

    def update(self):
        self.left_clicked = self._left_clicked()
        self.left_clicked_long = self._left_clicked_long()
        left_mouse_down = pygame.mouse.get_pressed(num_buttons=3)[0]
        self.left_mouse_down_last_update = left_mouse_down

        self.right_clicked_long = self._right_clicked_long()
        self.right_clicked = self._right_clicked()
        right_mouse_down = pygame.mouse.get_pressed(num_buttons=3)[2]
        self.right_mouse_down_last_update = right_mouse_down


class MobileButton(Button):
    def __init__(self, x=0, y=0, z=0, width=200, height=120, color=(100, 100, 100), alpha=255, image=None, text="",
                 font_size=40,
                 text_color=BLACK, name=None, parent=None, left_trigger_keys=None, right_trigger_keys=None,
                 right_click_function=None, right_click_args=None, right_hold_function=None, right_hold_args=None,
                 key_functions=None, external_process_function=None, external_process_arguments=None):

        colors = {"normal": color, "hover": color, "pressed": color}
        self.moving = False
        self.is_movable = True
        self.click_x = None
        self.click_y = None
        super().__init__(x=x, y=y, z=z, width=width, height=height, colors=colors, alpha=alpha, image=image, text=text,
                         font_size=font_size, text_color=text_color, name=name, parent=parent,
                         left_trigger_keys=left_trigger_keys, right_trigger_keys=right_trigger_keys,
                         left_click_function=self.start_movement, left_hold_function=self.move,
                         right_click_function=right_click_function, right_click_args=right_click_args,
                         right_hold_function=right_hold_function, right_hold_args=right_hold_args,
                         key_functions=key_functions, external_process_function=external_process_function,
                         external_process_arguments=external_process_arguments)
        super().toggle_continuous_hovering()
        self.static = False

    def process(self):
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
        mouse_position = environment.get_mouse_position()
        self.moving = True
        self.click_x, self.click_y = mouse_position[0] - self.x, mouse_position[1] - self.y


class Overlay(GameObject):
    def __init__(self, x=0, y=0, z=0, width=1540, height=760, alpha=255, name=None, background_color=WHITE,
                 close_btn_size=30, close_btn_offset=5, parent=None, anchored=False,
                 external_process_function=None, external_process_arguments=None):
        super().__init__(x=x, y=y, z=z, width=width, height=height, parent=parent, alpha=alpha, name=name)
        if external_process_arguments is None:
            self.external_process_arguments = []
        else:
            self.external_process_arguments = external_process_arguments
        self.external_process_function = external_process_function

        self.box = Box(x=self.x, y=self.y, z=self.z + 1, width=self.width, height=self.height, color=background_color,
                       alpha=self.alpha, name="overlay_box")
        self.box.static = False
        self.parent = parent
        self.anchored = anchored

        self.close_btn_size = close_btn_size
        self.close_btn_offset = close_btn_offset
        close_btn = Button(x=self.x + self.width - close_btn_size - close_btn_offset,
                           y=self.y + close_btn_offset, width=close_btn_size, height=close_btn_size,
                           image=pygame.image.load("Images/close_button.png"), font_size=15, parent=self,
                           left_click_function=self.destroy, left_trigger_keys=["escape"],
                           name="close_btn")
        self.add_child(close_btn)

    def get_rect(self):
        return self.box.get_rect()

    def get_box(self):
        return utils.find_object_from_name(self.children, "overlay_box")

    def get_buttons(self):
        return utils.find_objects_from_type(self.children, Button)

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.box.set_pos(x, y)
        for btn in self.get_buttons():
            btn.update_pos_relative_to_parent()

    def set_background_color(self, color):
        self.box.set_color(color)

    def get_displayable_objects(self):
        displayable_objects = [self.box]
        for obj in self.children:
            displayable_objects.extend(obj.get_displayable_objects())

        return displayable_objects

    def schedule_processing(self):
        items_to_be_processed = [self]
        items_to_be_processed.extend(self.box.schedule_processing())

        for obj in self.children:
            items_to_be_processed.extend(obj.schedule_processing())

        return items_to_be_processed

    def process(self):
        if self.external_process_function is not None:
            self.external_process_function(*self.external_process_arguments)

        super().process()

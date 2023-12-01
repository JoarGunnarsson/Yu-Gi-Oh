from constants import *
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from environment import environment, scene_manager, placeholder, surface_manager
import utility_functions as utils
# TODO: Add children to all classes etc?


class GameObject:
    def __init__(self, x=0, y=0, width=0, height=0, name=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.destroyed = False
        self.parent = None
        self.children = []
        self.rect = None

    def get_rect(self):
        return self.rect

    def set_x(self, x):
        self.x = x
        self.get_rect().update(self.x, self.y, self.width, self.height)

    def set_y(self, y):
        self.y = y
        self.get_rect().update(self.x, self.y, self.width, self.height)

    def set_pos(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def set_x_relative(self, delta_x):
        self.set_x(self.x + delta_x)

    def set_y_relative(self, delta_y):
        self.set_y(self.y + delta_y)

    def set_pos_relative(self, delta_x, delta_y):
        self.set_x_relative(delta_x)
        self.set_y_relative(delta_y)

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_width_relative(self, delta_w):
        self.set_width(self.width + delta_w)

    def set_height_relative(self, delta_h):
        self.set_height(self.height + delta_h)

    def update_position(self):
        pass

    def destroy(self):
        if self.destroyed:
            return
        self.destroyed = True
        if self.parent is not None and hasattr(self.parent, "destroy_child"):
            placeholder.schedule_end_of_tick_function(self.parent.destroy_child, [self])

    def add_child(self, child):
        self.children.append(child)
        if child.parent is None:
            child.parent = self

    def destroy_child(self, child):
        if child in self.children:
            self.children.remove(child)

    def schedule_processing(self):
        items_to_be_processed = []
        for child in self.children:
            items_to_be_processed.extend(child.schedule_processing())
        items_to_be_processed.append(self)
        return items_to_be_processed

    def save(self):
        save_dict = self.__dict__
        return save_dict


class Box(GameObject):
    def __init__(self, x=0, y=0, width=100, height=100, color=WHITE, alpha=255, source_image=None, text="",
                 text_color=BLACK,
                 font_size=40, update_text_func=None, name=None):
        super().__init__(name=name)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.alpha = alpha
        self.image_id = None
        if source_image is None:
            self.source_image_id = None
        else:
            self.source_image_id = surface_manager.set_image(source_image)
            source_image = surface_manager.fetch_image(self.source_image_id)
            scaled_image = pygame.transform.smoothscale(source_image, (self.width, self.height))
            self.image_id = surface_manager.set_image(scaled_image)

        self.text = text
        self.text_color = text_color
        self.font_size = font_size
        if self.text == "":
            self.text_surface_id = None  # TODO: Why do this instead of none?
        else:
            self.text_surface_id = surface_manager.create_font_surface(self.text, self.text_color, self.font_size)

        self.update_text_func = update_text_func  # TODO: Could all of these things be handled in a Script GameObject?

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.surface_id = surface_manager.create_surface(self.width, self.height, self.alpha)
        self.static = True
        self.rotation_angle = 0
        self.set_alpha(self.alpha)

    def get_rect(self):
        return self.rect

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.get_rect().update(x, y, self.width, self.height)

    def set_size(self, width, height):
        self.set_width(width)
        self.set_height(height)

    def set_width(self, width):
        self.width = width
        self.get_rect().update(self.x, self.y, self.width, self.height)
        if self.source_image_id is not None:
            surface_manager.scale_image(self.source_image_id, (self.width, self.height), new_id=self.image_id)

        # Updates the surface corresponding to self.surface_id
        surface_manager.scale_surface(self.surface_id, (self.width, self.height), new_id=self.surface_id)

    def set_height(self, height):
        self.height = height
        self.get_rect().update(self.x, self.y, self.width, self.height)
        if self.source_image_id is not None:
            surface_manager.scale_image(self.source_image_id, (self.width, self.height), new_id=self.image_id)

        # Updates the surface corresponding to self.surface_id
        surface_manager.scale_surface(self.surface_id, (self.width, self.height), new_id=self.surface_id)

    def set_rotation(self, angle):
        if ((self.rotation_angle - angle) // 90) % 2 == 1:
            self.width, self.height = self.height, self.width

        self.get_rect().update(self.x, self.y, self.width, self.height)

        theta = angle - self.rotation_angle
        self.rotation_angle = angle

        if self.image_id is not None:
            surface_manager.rotate_image(self.image_id, theta, new_id=self.image_id)

        surface_manager.rotate_surface(self.surface_id, theta, new_id=self.surface_id)

    def set_image(self, image):
        self.source_image_id = surface_manager.set_image(image, self.source_image_id)
        self.image_id = surface_manager.scale_image(self.source_image_id, (self.width, self.height), self.image_id)

    def set_text(self, new_text):
        self.text = new_text
        surface_manager.create_font_surface(self.text, self.text_color, self.font_size, self.text_surface_id)

    def set_color(self, color):
        self.color = color

    def set_alpha(self, alpha):
        self.alpha = alpha
        surface_manager.fetch_surface(self.surface_id).set_alpha(self.alpha)

    def get_displayable_objects(self):
        return [self]

    def hug_text(self, offset):
        text_surface = surface_manager.fetch_text_surface(self.text_surface_id)
        self.set_width(text_surface.get_width() + 2 * offset)
        self.set_height(text_surface.get_height() + 2 * offset)

    def rotate(self, angle):
        self.set_rotation(self.rotation_angle + angle)

    def schedule_processing(self):
        """Returns a list, containing only the box itself, for process scheduling."""
        return [self]

    def get_display_surface(self):
        """Returns a tuple, where the first element is the surface to be displayed, and the second element
         being the object's rect."""
        if self.image_id is not None:
            image = surface_manager.fetch_image(self.image_id)
            surface_manager.fetch_surface(self.surface_id).blit(image, (0, 0))
        else:
            surface_manager.fetch_surface(self.surface_id).fill(self.color)

        if self.update_text_func is not None:
            self.text = self.update_text_func()

        if self.text != "":
            text_surface = surface_manager.fetch_text_surface(self.text_surface_id)

            surface_manager.fetch_surface(self.surface_id).blit(text_surface,
                                                                [(self.width - text_surface.get_width()) / 2,
                                                                 (self.height - text_surface.get_height()) / 2])

        return surface_manager.fetch_surface(self.surface_id), self.get_rect()

    def __repr__(self):
        return "Class Box: " + str(self.name)


class Border(GameObject):
    def __init__(self, x=0, y=0, width=100, height=100, color=BLACK, thickness=1, alpha=255, parent=None, name=None):
        super().__init__(name=name)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.thickness = thickness
        self.alpha = alpha
        self.name = name
        self.rotation_angle = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        top_box = Box(x=self.x, y=self.y, width=self.width, height=self.thickness, color=self.color, alpha=self.alpha)
        bottom_box = Box(x=self.x, y=self.y + self.height - self.thickness, width=self.width, height=self.thickness,
                         color=self.color, alpha=self.alpha)
        left_box = Box(x=self.x, y=self.y + self.thickness, width=self.thickness,
                       height=self.height - 2 * self.thickness, color=self.color, alpha=self.alpha)

        right_box = Box(x=self.x + self.width - self.thickness, y=self.y + self.thickness, width=self.thickness,
                        height=self.height - 2 * self.thickness, color=self.color, alpha=self.alpha)
        self.side_boxes = [top_box, bottom_box, left_box, right_box]
        self.parent = parent
        if self.parent is not None:
            self.relative_x = self.parent.x - self.x
            self.relative_y = self.parent.y - self.y

    def get_rect(self):
        return self.rect

    def set_pos(self, x, y):
        for box in self.side_boxes:
            box.set_pos(x=box.x + (x - self.x), y=box.y + (y - self.y))
        self.x = x
        self.y = y
        self.get_rect().update(x, y, self.width, self.height)

        if hasattr(self, "block_button"):
            self.block_button.set_pos(x, y)

    def set_width(self, width):
        width_difference = width - self.width
        self.width = width
        self.side_boxes[3].set_x_relative(width_difference)
        self.side_boxes[0].set_width_relative(width_difference)
        self.side_boxes[1].set_width_relative(width_difference)
        self.get_rect().update(self.x, self.y, self.width, self.height)

    def set_height(self, height):
        height_difference = height - self.height
        self.height = height
        self.side_boxes[1].set_y_relative(height_difference)
        self.side_boxes[2].set_height_relative(height_difference)
        self.side_boxes[3].set_height_relative(height_difference)

        self.get_rect().update(self.x, self.y, self.width, self.height)

    def set_size(self, width, height):
        self.set_width(width)
        self.set_height(height)

    def set_rotation(self, angle):
        if ((self.rotation_angle - angle) // 90) % 2 == 1:
            self.set_size(width=self.height, height=self.width)

        self.rotation_angle = angle

        self.get_rect().update(self.x, self.y, self.width, self.height)

    def set_color(self, color):
        self.color = color

    def set_alpha(self, alpha):
        self.alpha = alpha
        for box in self.side_boxes:
            box.set_alpha(self.alpha)

    def get_displayable_objects(self):
        return self.side_boxes

    def update_position(self):
        self.update_relative_position()

    def update_relative_position(self):
        if self.parent is None:
            return
        self.set_pos(x=self.parent.x + self.relative_x, y=self.parent.y + self.relative_y)

    def rotate(self, angle):
        self.set_rotation(self.rotation_angle + angle)

    def schedule_processing(self):
        items_to_be_processed = []
        for box in self.side_boxes:
            items_to_be_processed.extend(box.schedule_processing())
        items_to_be_processed.append(self)
        return items_to_be_processed

    def process(self):
        self.update_relative_position()

    def __repr__(self):
        return "Class Border: " + str(self.name)


class Button(GameObject):
    # TODO: Add get_pos_relative method.
    def __init__(self, x=0, y=0, width=200, height=120, colors=None, alpha=255, image=None, text="", font_size=40,
                 text_color=BLACK, name=None, parent=None, left_trigger_keys=None, right_trigger_keys=None,
                 left_click_function=None, left_click_args=None, left_hold_function=None, left_hold_args=None,
                 right_click_function=None, right_click_args=None, right_hold_function=None, right_hold_args=None,
                 key_functions=None, external_process_function=None, external_process_arguments=None):
        """Creates a new button. X and y refers to the upper left corner of the button"""
        super().__init__(name=name)
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

        self.left_click_function = left_click_function
        self.left_hold_function = left_hold_function
        self.right_click_function = right_click_function
        self.right_hold_function = right_hold_function

        if colors is None:
            self.colors = {"normal": (100, 100, 100), "hover": (150, 150, 150), "pressed": (200, 200, 200)}
        else:
            self.colors = colors

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.alpha = alpha
        if image is None:
            self.image_id = None
        else:
            self.image_id = surface_manager.set_image(image)
            surface_manager.scale_image(self.image_id, (self.width, self.height), self.image_id)

        self.name = name
        self.parent = parent
        self.static = True

        if self.parent is not None:
            self.x_relative_to_parent = self.x - self.parent.x
            self.y_relative_to_parent = self.y - self.parent.y
            self.static = False

        self.external_process_function = external_process_function
        self.status = "normal"
        self.box = Box(x=self.x, y=self.y, width=self.width, height=self.height, color=self.colors[self.status],
                       alpha=alpha, source_image=image, text=self.text,
                       font_size=font_size, text_color=text_color)

        self.add_child(self.box)
        self.set_alpha(alpha)
        self.click_detector = ClickDetector(self.get_rect())
        self.rotation_angle = 0

        self.border = Border(x=self.x, y=self.y, width=self.width, height=self.height, parent=self)
        self.add_child(self.border)

    def get_rect(self):
        return self.box.get_rect()

    def set_pos(self, x, y):
        if self.static:
            return
        self.x = x
        self.y = y
        self.box.set_pos(self.x, self.y)
        for child in self.children:
            child.update_position()

    def set_pos_relative_to_parent(self, x, y):
        """Sets the relative position of the button in relation to the parent. The coordinates (x,y) refer to the
        coordinates of the button in the coordinate system where the parents position is the origin."""
        if self.static:
            return

        self.x_relative_to_parent, self.y_relative_to_parent = x, y
        self.set_pos(x=self.x_relative_to_parent + self.parent.x, y=self.y_relative_to_parent + self.parent.y)

    def update_pos_relative_to_parent(self):
        if self.static:
            return

        self.set_pos(x=self.x_relative_to_parent + self.parent.x, y=self.y_relative_to_parent + self.parent.y)

    def set_size(self, width, height):
        self.width, self.height = width, height
        self.box.set_size(width, height)
        self.border.set_size(width, height)

    def set_rotation(self, angle):
        if ((self.rotation_angle - angle) // 90) % 2 == 1:
            self.width, self.height = self.height, self.width
        self.rotation_angle = angle
        self.box.set_rotation(angle)
        self.border.set_rotation(angle)

    def rotate(self, angle):
        self.set_rotation(self.rotation_angle + angle)

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.box.set_alpha(alpha)
        for key in self.colors.keys():
            self.colors[key] = (self.colors[key][0], self.colors[key][1], self.colors[key][1])

    def set_image(self, image):
        self.image_id = surface_manager.set_image(image)
        self.box.set_image(image)

    def set_colors(self, colors):
        self.colors = colors
        self.box.set_color(self.colors[self.status])

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

    def get_displayable_objects(self):
        return [self.box]

    def hug_text(self, offset):
        self.box.hug_text(offset)
        self.set_size(width=self.box.width, height=self.box.height)

    def click_blocked(self, click_position):
        masking_types = [Button, Overlay, Box]
        blocking_objects_list = scene_manager.current_scene.get_object_mask(self, masking_types)
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
        if self.parent is not None and not self.static:
            self.set_pos(x=self.parent.x + self.x_relative_to_parent, y=self.parent.y + self.y_relative_to_parent)

        self.click_detector.update()

        self.check_button_presses()

        if self.external_process_function is not None:
            self.external_process_function(*self.external_process_arguments)

        self.box.color = self.colors[self.status]

    def __repr__(self):
        return "Class Button: " + str(self.name)


class ClickDetector(GameObject):
    def __init__(self, rect):
        super().__init__()
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


class Card(GameObject):
    def __init__(self, x=0, y=0, card_id="423585", parent=None):
        # TODO: Don't store images here.
        super().__init__()
        self.image_id = None
        self.width = standard_card_width
        self.height = standard_card_height
        self.x = x
        self.y = y

        self.moving = False
        self.is_movable = True
        self.click_x = None
        self.click_y = None
        self.buttons = []
        self.overlays = []
        self.card_id = card_id
        self.parent = parent

        self.original_image_id = surface_manager.create_image(card_image_location + '{}.jpg'.format(self.card_id))
        self.image_id = surface_manager.scale_image(self.original_image_id, (self.width, self.height))

        self.card_type = self.get_card_type()
        button = Button(x=self.x, y=self.y, width=self.width, height=self.height,
                        image=surface_manager.fetch_image(self.image_id), name="card_btn",
                        parent=self, left_click_function=self.start_movement,
                        left_hold_function=self.move,
                        right_click_function=self.create_card_overlay)
        self.button = button
        self.button.toggle_continuous_hovering()
        self.buttons.append(button)
        self.rotation_angle = 0
        self.location = None
        self.has_been_processed = False

    def get_card_type(self):
        image = surface_manager.fetch_image(self.image_id)
        card_colors = {"normal": (200, 169, 105),
                       "effect": (196, 127, 86),
                       "spell": (42, 170, 155),
                       "trap": (182, 62, 133),
                       "ritual": (106, 141, 197),
                       "xyz": (56, 58, 47),
                       "synchro": (235, 234, 232),
                       "fusion": (150, 90, 162),
                       "link": (51, 105, 165),
                       "token": (145, 145, 145)}
        width_fraction = 0.05463182897
        height_fraction = 0.34853420195
        x = int(width_fraction * image.get_width())
        y = int(height_fraction * image.get_height())
        pixel_value = image.get_at((x, y))
        best_match = utils.closest_color(card_colors, pixel_value)
        return best_match

    def get_rect(self):
        return self.button.get_rect()

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.button.set_pos(x, y)

    def get_pos(self):
        return self.x, self.y

    def clamp_pos(self, rect):
        self.get_rect().clamp_ip(rect)
        self.x = utils.clamp(self.x, rect.x, rect.x + rect.width - self.width)
        self.y = utils.clamp(self.y, rect.y, rect.y + rect.height - self.height)

    def set_size(self, width, height):
        self.width, self.height = width, height
        self.button.set_size(width, height)

    def set_rotation(self, angle):
        """Sets the rotation of the card. Only supports rotation with integer multiples of 90 degrees."""
        if self.rotation_angle == angle:
            return

        if ((self.rotation_angle - angle) // 90) % 2 == 1:
            self.width, self.height = self.height, self.width

        self.rotation_angle = angle
        self.button.set_rotation(angle)
        self.update_card_overlay_anchor()

    def get_rotation(self):
        return self.rotation_angle

    def rotate(self):
        if self.location != "field":
            return

        if self.rotation_angle == 0:
            self.set_rotation(90)
        else:
            self.set_rotation(0)

    def set_alpha(self, alpha):
        self.button.set_alpha(alpha)

    def get_alpha(self):
        return self.button.alpha

    def set_left_click_function(self, new_function, new_arguments=None):
        if new_arguments is None:
            new_arguments = []
        self.button.set_left_click_function(new_function, new_arguments)

    def set_left_hold_function(self, new_function, new_arguments=None):
        if new_arguments is None:
            new_arguments = []
        self.button.set_left_hold_function(new_function, new_arguments)

    def set_right_click_function(self, new_function, new_arguments=None):
        if new_arguments is None:
            new_arguments = []
        self.button.set_right_click_function(new_function, new_arguments)

    def set_right_hold_function(self, new_function, new_arguments=None):
        if new_arguments is None:
            new_arguments = []
        self.button.set_right_hold_function(new_function, new_arguments)

    def destroy_child(self, child):
        # TODO: Rename this to something more appropriate?

        if child in self.buttons:
            placeholder.schedule_end_of_tick_function(self.buttons.remove, [child])
        elif child in self.overlays:
            placeholder.schedule_end_of_tick_function(self.overlays.remove, [child])

    def update_in_hand(self):
        # TODO: Should all of this happen in the Board class?
        scene = scene_manager.current_scene
        board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
        if board is None or self not in board.hand:
            return
        hand_box = utils.find_object_from_name(scene.boxes, "hand_box")
        if hand_box is None:
            return
        in_hand = hand_box.get_rect().colliderect(self.get_rect())

        if not in_hand:
            board.move_to_field(self, board.hand)
            return

        if self.check_deck_collision(board, board.hand):
            return

    def update_on_field(self):
        scene = scene_manager.current_scene
        board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
        if board is None or self not in board.field:
            return

        hand_box = utils.find_object_from_name(scene.boxes, "hand_box")
        field_box = utils.find_object_from_name(scene.boxes, "field_box")
        if hand_box is None or field_box is None:
            return
        in_hand = hand_box.get_rect().colliderect(self.get_rect())

        if in_hand:
            board.add_to_hand(self, board.field)
            return

        if self.check_deck_collision(board, board.field):
            return
        if not self.moving:
            self.clamp_pos(field_box)

    def check_deck_collision(self, board, previous_location):
        scene = scene_manager.current_scene
        draw_btn = utils.find_object_from_name(scene.buttons, "draw_btn")
        extra_deck_btn = utils.find_object_from_name(scene.buttons, "show_extra_deck_btn")
        on_the_deck = draw_btn.get_rect().colliderect(self.get_rect())
        on_the_extra_deck = extra_deck_btn.get_rect().colliderect(self.get_rect())

        starting_location = utils.card_starting_location(self.card_type)

        if on_the_deck and not self.moving and starting_location == "main_deck":
            board.add_to_the_deck(self, previous_location)
            return True

        elif on_the_extra_deck and not self.moving and starting_location == "extra_deck":
            board.add_to_the_extra_deck(self, previous_location)
            return True
        return False

    def schedule_processing(self):
        items_to_be_processed = []
        for overlay in self.overlays:
            items_to_be_processed.extend(overlay.schedule_processing())

        for btn in self.buttons:
            items_to_be_processed.extend(btn.schedule_processing())

        items_to_be_processed.append(self)
        return items_to_be_processed

    def process(self):
        if not self.button.click_detector.left_clicked_long:
            self.moving = False
            self.click_x, self.click_y = None, None

        self.update_in_hand()
        self.update_on_field()
        self.has_been_processed = True

    def move(self):
        """Handles the movement of a card."""
        if not self.moving:
            return
        mouse_position = environment.get_mouse_position()
        self.set_pos(mouse_position[0] - self.click_x, mouse_position[1] - self.click_y)

    def start_movement(self):
        mouse_position = environment.get_mouse_position()
        card_overlay = utils.find_object_from_name(self.overlays, "card_overlay")
        if card_overlay is not None:
            card_overlay.destroy()
        board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
        if board is not None:
            board.bump(self)
        self.moving = True
        self.click_x, self.click_y = mouse_position[0] - self.x, mouse_position[1] - self.y

        self.make_large_card_button()

    def new_location(self, location=None):
        # TODO: Maybe add remove_from_display_order(self) instead.
        previous_location = self.location
        self.location = location
        self.set_rotation(0)
        self.remove_card_overlay()
        if location in ["hand", "field"]:
            self.set_alpha(255)
            self.parent = None
            self.change_to_movable_card()
            if previous_location not in ["hand", "field"]:
                scene_manager.current_scene.remove_object(self.button)
                self.remove_large_card_button()

        elif location in ["main_deck", "extra_deck", "gy", "banished"]:
            self.remove_large_card_button()
            self.remove_card_overlay()
            scene_manager.current_scene.remove_object(self.button)
            self.set_alpha(255)

    def change_to_movable_card(self):
        self.set_left_click_function(self.start_movement)
        self.set_left_hold_function(self.move)
        self.set_size(standard_card_width, standard_card_height)

    def create_card_overlay(self):
        # TODO: Change names
        # TODO: This is too reliant on play_testing scene...
        # TODO: Fix positioning of the buttons.
        # TODO: Perhaps add functionality for the overlay class to "add" buttons, which gives them automatic placement,
        #  if no placement is specified.

        card_overlay = utils.find_object_from_name(self.overlays, "card_overlay")

        if card_overlay is not None:
            return

        if self.get_rotation() == 0:
            overlay_width = self.width
            overlay_height = int(overlay_width * card_aspect_ratio)
        else:
            overlay_width = self.height
            overlay_height = int(overlay_width * card_aspect_ratio)

        button_space = 5
        overlay_close_button_size = 15
        number_of_buttons = 4
        total_height = overlay_height - button_space * (2 + number_of_buttons) - overlay_close_button_size
        button_height = total_height // number_of_buttons
        button_width = overlay_width - 2 * button_space

        overlay = Overlay(x=self.x + self.width, y=self.y, width=overlay_width, height=overlay_height,
                          name="card_overlay",
                          close_btn_size=overlay_close_button_size, parent=self, anchored=True,
                          position_relative_to_parent=(self.width, 0),
                          external_process_function=utils.remove_on_external_clicks)
        overlay.external_process_arguments = [overlay, [overlay.get_rect(), self.get_rect()]]
        button_parent = overlay
        self.overlays.append(overlay)
        board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
        board.bump(self)
        starting_location = utils.card_starting_location(self.card_type)
        card_location = board.get_location(self)

        large_card_btn = utils.find_object_from_name(self.buttons, "large_card_btn")
        if large_card_btn is None:
            large_card_btn = self.make_large_card_button()

        [large_card_btn_arg, large_card_btn_allowed_rect_list] = large_card_btn.get_external_process_arguments()
        large_card_btn_allowed_rect_list.append(overlay.get_rect())
        large_card_btn.set_external_process_arguments([large_card_btn_arg, large_card_btn_allowed_rect_list])

        # TODO: Modify the large_card_button remove on external clicks hitbox, to include the overlay box.
        # However, perhaps include the buttons as a non-allowed area, which requires modifying the remove_on_external_
        # _clicks function
        if self.card_type == "token":
            remove_btn_height = int(overlay_height - button_space * 4 - overlay_close_button_size)
            remove_btn = Button(x=overlay.x + button_space, y=overlay.y + overlay_close_button_size + 2 * button_space,
                                width=button_width, height=remove_btn_height, text="Remove", font_size=15,
                                parent=button_parent, name="token_remove_btn",
                                left_click_function=self.destroy, left_trigger_keys=["g", "b", "d"])
            overlay.buttons.append(remove_btn)
            return

        gy_btn = Button(width=button_width, height=button_height, text="Graveyard", name="gy_btn", font_size=15,
                        parent=button_parent, left_trigger_keys=["g"], left_click_function=board.send_to_gy,
                        left_click_args=[self, card_location])

        banish_btn = Button(width=button_width,
                            height=button_height, text="Banish", font_size=15, name="banish_btn",
                            parent=button_parent,
                            left_trigger_keys=["b"], left_click_function=board.banish,
                            left_click_args=[self, card_location])

        hand_btn = Button(width=button_width,
                          height=button_height, font_size=15, text="Hand", name="hand_btn",
                          parent=button_parent,
                          left_trigger_keys=["h"], left_click_function=board.add_to_hand,
                          left_click_args=[self, card_location])

        field_btn = Button(width=button_width,
                           height=button_height, font_size=15, text="Field", name="field_btn",
                           parent=button_parent,
                           left_trigger_keys=["f"], left_click_function=board.move_to_field,
                           left_click_args=[self, card_location])

        if starting_location == "main_deck":
            deck_btn = Button(width=button_width,
                              height=button_height, font_size=15, text="Deck", name="send_to_deck_btn",
                              parent=button_parent,
                              left_trigger_keys=["d"], left_click_function=board.add_to_the_deck,
                              left_click_args=[self, card_location])
        else:
            deck_btn = Button(width=button_width, height=button_height, font_size=15, text="Extra Deck",
                              name="send_to_extra_deck_btn", parent=button_parent,
                              left_trigger_keys=["d"], left_click_function=board.add_to_the_extra_deck,
                              left_click_args=[self, card_location])

        if self.location == "main_deck" or self.location == "extra_deck":
            location_buttons = [gy_btn, banish_btn, hand_btn, field_btn]

        elif self.location == "gy":
            location_buttons = [hand_btn, banish_btn, deck_btn, field_btn]

        elif self.location == "banished":
            location_buttons = [gy_btn, hand_btn, deck_btn, field_btn]

        elif self.location == "field":
            location_buttons = [gy_btn, banish_btn, deck_btn, hand_btn]

        elif self.location == "hand":
            location_buttons = [gy_btn, banish_btn, deck_btn, field_btn]

        else:
            location_buttons = [gy_btn, banish_btn, deck_btn, hand_btn]

        y = overlay_close_button_size + 2 * button_space

        for btn in location_buttons:
            btn.static = False
            btn.set_pos_relative_to_parent(button_space, y)
            y += btn.height + button_space

        overlay.buttons.extend(location_buttons)

    def remove_card_overlay(self):
        card_overlay = utils.find_object_from_name(self.overlays, "card_overlay")
        if card_overlay is None:
            return
        card_overlay.destroy()

    def update_card_overlay_anchor(self):
        card_overlay = utils.find_object_from_name(self.overlays, "card_overlay")
        if card_overlay is not None:
            card_overlay.set_relative_position_to_parent(self.width, 0)

    def make_large_card_button(self):
        large_card_btn = utils.find_object_from_name(self.buttons, "large_card_btn")
        if large_card_btn is not None:
            return

        scene = scene_manager.current_scene
        left_side_box = utils.find_object_from_name(scene.boxes, "left_side_box")
        if left_side_box is None:
            return
        large_card_offset = (left_side_box.width - large_card_width) // 2
        card_btn = utils.find_object_from_name(self.buttons, "card_btn")

        large_card_btn = Button(x=left_side_box.x + large_card_offset, y=left_side_box.y + large_card_offset,
                                width=large_card_width,
                                height=int(large_card_width * card_aspect_ratio),
                                image=surface_manager.fetch_image(self.original_image_id), name="large_card_btn",
                                left_click_function=create_large_card_overlay, left_click_args=[self],
                                key_functions={"r": [self.rotate, []]})

        large_card_btn.toggle_continuous_hovering()
        large_card_btn.external_process_function = utils.remove_on_external_clicks
        large_card_btn.static = True
        large_card_btn.parent = self
        allowed_rect_list = [card_btn.get_rect(), large_card_btn.get_rect()]
        card_overlay = utils.find_object_from_name(self.overlays, "card_overlay")
        if card_overlay is not None:
            allowed_rect_list.append(card_overlay.get_rect())
        large_card_btn.external_process_arguments = [large_card_btn, allowed_rect_list]

        self.buttons.insert(0, large_card_btn)
        return large_card_btn

    def remove_large_card_button(self):
        large_card_btn = utils.find_object_from_name(self.buttons, "large_card_btn")
        if large_card_btn is None:
            return
        large_card_btn.destroy()

    def __repr__(self):
        return "Class Card: " + self.card_id


class Overlay(GameObject):
    def __init__(self, x=0, y=0, width=1540, height=760, alpha=255, name=None, background_color=WHITE,
                 close_btn_size=30, close_btn_offset=5, parent=None, anchored=False, position_relative_to_parent=(0, 0),
                 external_process_function=None, external_process_arguments=None):
        super().__init__(name=name)
        if external_process_arguments is None:
            self.external_process_arguments = []
        else:
            self.external_process_arguments = external_process_arguments
        self.external_process_function = external_process_function

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alpha = alpha
        self.name = name

        self.buttons = []
        self.objects = []

        self.box = Box(x=self.x, y=self.y, width=self.width, height=self.height, color=background_color,
                       alpha=self.alpha)
        self.box.static = False
        self.parent = parent
        self.anchored = anchored
        self.position_relative_to_parent = position_relative_to_parent

        self.close_btn_size = close_btn_size
        self.close_btn_offset = close_btn_offset
        self.close_btn = Button(x=self.x + self.width - close_btn_size - close_btn_offset,
                                y=self.y + close_btn_offset, width=close_btn_size, height=close_btn_size,
                                image=pygame.image.load("Images/close_button.png"), font_size=15, parent=self,
                                left_click_function=self.destroy, left_trigger_keys=["escape"],
                                name="close_btn")
        self.buttons.append(self.close_btn)

    def get_rect(self):
        return self.box.get_rect()

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.box.set_pos(x, y)
        for btn in self.buttons:
            btn.update_pos_relative_to_parent()

    def set_relative_position_to_parent(self, x, y):
        self.position_relative_to_parent = (x, y)

    def set_background_color(self, color):
        self.box.set_color(color)

    def get_displayable_objects(self):
        displayable_objects = [self.box]
        for btn in self.buttons:
            displayable_objects.extend(btn.get_displayable_objects())
        for obj in self.objects:
            displayable_objects.extend(obj.get_displayable_objects())

        return displayable_objects

    def schedule_processing(self):
        items_to_be_processed = [self]
        items_to_be_processed.extend(self.box.schedule_processing())

        for obj in self.objects:
            items_to_be_processed.extend(obj.schedule_processing())

        for btn in self.buttons:
            items_to_be_processed.extend(btn.schedule_processing())

        return items_to_be_processed

    def process(self):
        if self.external_process_function is not None:
            self.external_process_function(*self.external_process_arguments)

        if self.parent is not None and self.anchored:
            relative_x, relative_y = self.position_relative_to_parent
            new_x = relative_x + self.parent.x
            new_y = relative_y + self.parent.y
            self.set_pos(new_x, new_y)

    def __repr__(self):
        return "Class Overlay: " + str(self.name)


def create_large_card_overlay(card):
    scene = scene_manager.current_scene
    large_card_btn = utils.find_object_from_name(scene.overlays, "large_card_overlay")
    if large_card_btn is not None:
        return
    field_box = utils.find_object_from_name(scene.boxes, "field_box")
    large_card_btn = utils.find_object_from_name(card.buttons, "large_card_btn")
    dummy_overlay = Overlay()
    close_btn_size = dummy_overlay.close_btn_size
    close_btn_offset = dummy_overlay.close_btn_offset

    height = field_box.height
    width = int((height - close_btn_size - close_btn_offset) / card_aspect_ratio)

    overlay = Overlay(x=field_box.x, y=field_box.y, width=width, height=height, name="large_card_overlay")
    overlay.parent = scene
    close_btn = utils.find_object_from_name(overlay.buttons, "close_btn")
    offset = 15

    card_height = overlay.height - 3 * offset - close_btn.height
    card_width = int(card_height / card_aspect_ratio)

    large_card_box = Box(x=overlay.x + offset,
                         y=close_btn.y + offset + close_btn.height,
                         width=card_width,
                         height=card_height,
                         source_image=surface_manager.fetch_image(card.original_image_id))

    large_card_box.parent = overlay
    large_card_box.static = True
    allowed_rect_list = [overlay.box.get_rect(), large_card_btn.get_rect()]
    overlay.external_process_function = utils.remove_on_external_clicks
    overlay.external_process_arguments = [overlay, allowed_rect_list]

    large_card_btn.external_process_arguments[1].append(overlay.box.get_rect())

    overlay.objects.append(large_card_box)

    scene.overlays.append(overlay)

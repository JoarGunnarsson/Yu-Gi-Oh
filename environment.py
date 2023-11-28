from constants import *
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


class Environment:
    def __init__(self):
        self.scale_factor = 1
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        self.key_press = None
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.size = (self.width, self.height)
        self.screen = pygame.Surface(self.size)
        self.screen.set_alpha(255)
        self.clock = pygame.time.Clock()
        self.previous_scene = None
        self.current_scene = None
        self.standard_offset = 15
        self.deck = None
        self.fonts = {}
        self.start_of_tick_functions = []
        self.start_of_tick_arguments = []

    def get_mouse_position(self):
        """Returns the current position of the mouse in screen-space coordinates, not window-space,
        as a 2-dimensional tuple of floats."""
        x, y = pygame.mouse.get_pos()
        window_width = pygame.display.Info().current_w
        window_height = pygame.display.Info().current_h
        scale_x = self.screen.get_width() / window_width
        scale_y = self.screen.get_height() / window_height
        return x * scale_x, y * scale_y

    def set_deck(self, deck):
        self.deck = deck

    def create_font(self, size):
        font = pygame.font.SysFont("Arial", size)
        self.fonts[size] = font
        return font

    def get_font(self, size):
        if size in self.fonts:
            font = self.fonts[size]
        else:
            font = self.create_font(size)

        return font

    def change_scene(self, scene):
        self.clear_current_scene()
        self.current_scene = scene

    def clear_current_scene(self):
        if self.current_scene is not None:
            self.current_scene.clear()

    def schedule_scene_change(self, scene_function, scene_arguments=None):
        if scene_arguments is None:
            scene_arguments = []
        self.schedule_start_of_tick_function(scene_function, scene_arguments)

    def schedule_start_of_tick_function(self, function, arguments):
        self.start_of_tick_functions.append(function)
        self.start_of_tick_arguments.append(arguments)

    def start_tick(self):
        execute_multiple_functions(self.start_of_tick_functions, self.start_of_tick_arguments)
        self.start_of_tick_functions = []
        self.start_of_tick_arguments = []

    def handle_events(self):
        """Checks if the user tries to close the program window, or resize the window."""
        is_running = True
        self.key_press = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.KEYDOWN:
                self.key_press = pygame.key.name(event.key)
        return is_running

    def draw_screen(self):
        resized_screen = pygame.transform.scale(self.screen, self.window.get_rect().size)
        environment.window.blit(resized_screen, (0, 0))
        pygame.display.flip()


class Scene:
    def __init__(self, name=""):
        self.name = name
        self.boxes = []
        self.buttons = []
        self.cards = []
        self.overlays = []
        self.others = []
        self.processing_order = []
        self.display_order = []
        self.background_color = WHITE

    def get_default_position(self):
        return environment.width // 2, environment.height // 2

    def get_object_mask(self, obj, masking_types):
        # TODO: Rename this method.
        index = self.processing_order.index(obj)
        blocking_object_list = []
        for masking_object in self.processing_order[index + 1:]:
            if not hasattr(masking_object, "get_rect") or type(masking_object) not in masking_types:
                continue
            if obj.get_rect().colliderect(masking_object.get_rect()):
                blocking_object_list.append(masking_object)

        return blocking_object_list

    def add_button(self, button):
        self.buttons.append(button)

    def clear(self):
        self.boxes = []
        self.buttons = []
        self.cards = []
        self.others = []
        self.overlays = []
        self.processing_order = []
        self.display_order = []

    def schedule_processing(self):
        self.processing_order = []

        object_lists = [self.boxes, self.buttons, self.cards, self.others, self.overlays]

        for object_list in object_lists:
            for obj in object_list:
                items_to_be_processed = obj.schedule_processing()
                self.processing_order.extend(items_to_be_processed)

    def process_given_objects(self, objects):
        for obj in objects:
            self.process_object(obj)

    def process_object(self, obj):
        if not hasattr(obj, "process") or obj not in self.processing_order:
            return
        obj.process()

    def remove_object(self, source_object):
        self.remove_from_processing_order(source_object)
        self.remove_from_display_order(source_object)

    def remove_from_processing_order(self, source_object):
        # TODO: This method should take an object as input, and then ask the object for which objects should get removed
        # so that entire overlays can be removed etc
        if source_object in self.processing_order:
            self.processing_order.remove(source_object)

    def remove_from_display_order(self, source_object):
        # TODO: This method should take an object as input, and then ask the object for which objects should get removed
        # so that entire overlays can be removed etc
        objects_to_remove = source_object.get_displayable_objects()
        for obj in objects_to_remove:
            if obj in self.display_order:
                self.display_order.remove(obj)

    def add_to_display_order(self, obj, index=-1):
        if index == -1:
            self.display_order.append(obj)
            return
        self.display_order.insert(index, obj)

    def process(self):
        environment.screen.fill(self.background_color)

        self.schedule_processing()
        self.display_order = self.processing_order
        for obj in reversed(self.processing_order.copy()):
            self.process_object(obj)

        for obj in self.processing_order:
            if hasattr(obj, "get_surface") and callable(obj.get_surface):
                surface, rect = obj.get_surface()
                environment.screen.blit(surface, rect)


def execute_multiple_functions(functions, argument_list):
    for i, function in enumerate(functions):
        if type(argument_list[i]) is dict:
            function(**argument_list[i])
        else:
            function(*argument_list[i])


def find_object_from_name(obj_list, name):
    for obj in obj_list:
        if hasattr(obj, "name") and obj.name == name:
            return obj
    return None


environment = Environment()

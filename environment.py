import assets
from constants import *
import os
import pickle
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
        self.end_of_tick_functions = []
        self.end_of_tick_arguments = []
        self.scenes = []
        self.current_max_id = 0
        self.surfaces = {}
        self.images = {}

    def get_mouse_position(self):
        """Returns the current position of the mouse in screen-space coordinates, not window-space,
        as a 2-dimensional tuple of floats."""
        x, y = pygame.mouse.get_pos()
        window_width = pygame.display.Info().current_w
        window_height = pygame.display.Info().current_h
        scale_x = self.screen.get_width() / window_width
        scale_y = self.screen.get_height() / window_height
        return x * scale_x, y * scale_y

    def get_new_id(self):
        new_id = self.current_max_id + 1
        self.current_max_id += 1
        return new_id

    def create_image(self, image_path, image_id=None):
        if image_id is None:
            image_id = self.get_new_id()
        image = pygame.image.load(image_path)
        self.set_image(image, image_id)
        return image_id

    def set_image(self, image, image_id=None):
        if image_id is None:
            image_id = self.get_new_id()
        self.images[image_id] = image
        return image_id

    def fetch_image(self, image_id):
        return self.images[image_id]

    def set_surface(self, surface, surface_id=None):
        # TODO: Fix these methods. Rename, refactor etc.
        if surface_id is None:
            surface_id = self.get_new_id()
        self.surfaces[surface_id] = surface
        return surface_id

    def fetch_surface(self, surface_id):
        return self.surfaces[surface_id]

    def create_surface(self, width, height, surface_id=None):
        surface = pygame.Surface((width, height))
        if surface_id is None:
            surface_id = self.set_surface(surface)
        else:
            self.set_surface(surface, surface_id)
        return surface_id

    def create_font_surface(self, text, text_color, font_size, font_surface_id=None):
        font = self.get_font(font_size)
        font_surface = font.render(text, True, text_color)
        if font_surface_id is None:
            font_surface_id = self.set_surface(font_surface)
        else:
            self.set_surface(font_surface, font_surface_id)

        return font_surface_id

    def set_deck(self, deck):
        # TODO: This should NOT be in environment.
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

    def schedule_start_of_tick_function(self, function, arguments):
        self.start_of_tick_functions.append(function)
        self.start_of_tick_arguments.append(arguments)

    def schedule_end_of_tick_function(self, function, arguments):
        self.end_of_tick_functions.append(function)
        self.end_of_tick_arguments.append(arguments)

    def start_tick(self):
        execute_multiple_functions(self.start_of_tick_functions, self.start_of_tick_arguments)
        self.start_of_tick_functions = []
        self.start_of_tick_arguments = []

    def end_tick(self):
        execute_multiple_functions(self.end_of_tick_functions, self.end_of_tick_arguments)
        self.end_of_tick_functions = []
        self.end_of_tick_arguments = []

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

    def save(self, save_number=0):
        with open('save{}.txt'.format(save_number), 'wb') as save_file:
            new_scene = Scene()
            new_scene.buttons.append(assets.Button())
            new_scene.cards.append(assets.Card())
            pickle.dump(new_scene, save_file)

            """
            scene_dict = {}
            for scene in self.scenes:
                scene_dict[scene.id] = scene.save()
            save_string = str(scene_dict)
            save_file.write(save_string)"""

    def load(self, save_number=0):
        pass


class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current_scene = None
        # TODO: Implement scene switching. For example, tag a scene as persistent or temporary, and clear it only if
        # it is temporary.

    def change_scene(self, scene):
        self.clear_current_scene()
        # TODO: Clearing the scene removes all saved data, sure clear processing queue, but
        # not everything. Do something else here.
        self.current_scene = scene
        self.scenes[scene.name] = scene

    def clear_current_scene(self):
        if self.current_scene is not None:
            self.current_scene.clear()

    def schedule_scene_change(self, scene_function, scene_arguments=None):
        if scene_arguments is None:
            scene_arguments = []
        environment.schedule_start_of_tick_function(scene_function, scene_arguments)


class Scene:
    def __init__(self, name=""):
        self.name = name
        self.boxes = []
        self.buttons = []
        self.cards = []  # TODO: This is bad.
        self.overlays = []
        self.others = []
        self.processing_order = []
        self.display_order = []
        self.background_color = WHITE
        self.id = "Scene" + str(environment.get_new_id())

    def get_object_list(self):
        return [self.boxes, self.buttons, self.cards, self.others, self.overlays]

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

        for object_list in self.get_object_list():
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
        """Removes the object from the processing order this tick."""
        self.remove_from_processing_order(source_object)
        self.remove_from_display_order(source_object)

    def remove_from_processing_order(self, source_object):
        # TODO: This method should take an object as input, and then ask the object for which objects should get removed
        # so that entire overlays can be removed etc.
        # Could ask the object for it's children.
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

        # Display objects.
        for obj in self.processing_order:
            if hasattr(obj, "get_display_surface") and callable(obj.get_display_surface):
                surface, rect = obj.get_display_surface()
                environment.screen.blit(surface, rect)

        self.display_order = self.processing_order
        for obj in reversed(self.processing_order.copy()):
            self.process_object(obj)

        # Remove destroyed objects
        for object_list in self.get_object_list():
            for obj in object_list:
                if hasattr(obj, "destroyed") and obj.destroyed:
                    object_list.remove(obj)

    def save(self):
        save_dict = {}
        for object_list in self.get_object_list():
            for obj in object_list:
                save_dict[obj.id] = obj.save()  # TODO: Name doesn't have to be unique, use ID here instead.
        return save_dict


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
scene_manager = SceneManager()

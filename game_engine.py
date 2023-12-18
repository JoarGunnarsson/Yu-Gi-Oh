from constants import *
import os
import pickle

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


# TODO: Add get_current_scene() function


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
        self.standard_offset = 15
        self.events_last_tick = {"left_mouse_button": False, "right_mouse_button": False, "key_press": None}
        self.events_this_tick = {"left_mouse_button": False, "right_mouse_button": False, "key_press": None}

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def get_mouse_position(self):
        """Returns the current position of the mouse in screen-space coordinates, not window-space,
        as a 2-dimensional tuple of floats."""
        x, y = pygame.mouse.get_pos()
        window_width = pygame.display.Info().current_w
        window_height = pygame.display.Info().current_h
        scale_x = self.screen.get_width() / window_width
        scale_y = self.screen.get_height() / window_height
        return x * scale_x, y * scale_y

    def set_events_this_tick(self, events):
        self.events_this_tick = events

    def set_events_last_tick(self, events):
        self.events_last_tick = events

    def get_events_this_tick(self):
        return self.events_this_tick

    def get_events_last_tick(self):
        return self.events_last_tick

    def get_left_mouse_click_this_tick(self):
        return self.events_this_tick["left_mouse_button"]

    def get_right_mouse_click_this_tick(self):
        return self.events_this_tick["right_mouse_button"]

    def get_left_mouse_click_last_tick(self):
        return self.events_last_tick["left_mouse_button"]

    def get_right_mouse_click_last_tick(self):
        return self.events_last_tick["right_mouse_button"]

    def get_key_press_this_tick(self):
        return self.events_last_tick["key_press"]

    def get_key_press_last_tick(self):
        return self.events_last_tick["key_press"]

    def handle_events(self):
        """Checks if the user tries to close the program window, or resize the window."""
        is_running = True
        self.key_press = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.KEYDOWN and self.key_press is None:
                self.key_press = pygame.key.name(event.key)

        left_mouse_down = pygame.mouse.get_pressed(num_buttons=3)[0]
        right_mouse_down = pygame.mouse.get_pressed(num_buttons=3)[2]
        self.set_events_this_tick({"left_mouse_button": left_mouse_down, "right_mouse_button": right_mouse_down,
                                   "key_press": self.key_press})
        return is_running

    def draw_screen(self):
        resized_screen = pygame.transform.scale(self.screen, self.window.get_rect().size)
        environment.window.blit(resized_screen, (0, 0))
        pygame.display.flip()


class GameState:
    def __init__(self):
        self.surface_manager = SurfaceManager()
        self.surface_size_dict = self.surface_manager.surface_size_dict
        self.surface_image_dict = self.surface_manager.surface_image_dict
        self.surface_type_dict = self.surface_manager.surface_type_dict
        self.images = self.surface_manager.images
        self.surface_font_dict = self.surface_manager.surface_font_dict
        self.current_max_id = self.surface_manager.current_max_id

        self.scene_manager = SceneManager()

        self.placeholder = Placeholder()

    def load_from_surface_manager(self):
        self.surface_size_dict = self.surface_manager.surface_size_dict
        self.surface_image_dict = self.surface_manager.surface_image_dict
        self.surface_type_dict = self.surface_manager.surface_type_dict
        self.images = self.surface_manager.images
        self.surface_font_dict = self.surface_manager.surface_font_dict
        self.current_max_id = self.surface_manager.current_max_id


class Placeholder:
    def __init__(self):
        self.start_of_tick_functions = []
        self.start_of_tick_arguments = []
        self.end_of_tick_functions = []
        self.end_of_tick_arguments = []


class SurfaceManager:
    # TODO: Need some way to remove surfaces that are no longer used. Could do this for scene changes?
    def __init__(self):
        self.current_max_id = 0
        self.fonts = {}
        self.surfaces = {}
        self.images = {}
        self.surface_size_dict = {}
        self.surface_image_dict = {}
        self.surface_font_dict = {}
        self.surface_type_dict = {}

    def get_new_id(self):
        new_id = self.current_max_id + 1
        self.current_max_id += 1
        return new_id

    def set_surface(self, surface, alpha=255, surface_id=None, surface_type="surface"):
        # TODO: Fix these methods. Rename, refactor etc.
        if surface_id is None:
            surface_id = self.get_new_id()
        self.surface_size_dict[surface_id] = surface.get_width(), surface.get_height(), alpha
        self.surfaces[surface_id] = surface
        self.surface_type_dict[surface_id] = surface_type
        return surface_id

    def fetch_surface(self, surface_id):
        if surface_id not in self.surfaces:
            self.restore_surface(surface_id)
        return self.surfaces[surface_id]

    def create_surface(self, width, height, alpha=255, surface_id=None):
        surface = pygame.Surface((width, height))
        surface.set_alpha(alpha)
        surface_id = self.set_surface(surface, alpha=alpha, surface_id=surface_id)
        return surface_id

    def create_image(self, image_path, image_id=None):
        if image_id is None:
            image_id = self.get_new_id()
        image = pygame.image.load(image_path)
        self.set_image(image, image_id)
        return image_id

    def set_image(self, image, image_id=None):
        if image_id is None:
            image_id = self.get_new_id()

        self.images[image_id] = pygame.image.tostring(image, 'RGBA')
        self.surface_image_dict[image_id] = pygame.image.tostring(image, 'RGBA')
        self.set_surface(image, alpha=255, surface_id=image_id, surface_type="image")
        return image_id

    def fetch_image(self, image_id):
        image_string = self.images[image_id]
        width, height, _ = self.surface_size_dict[image_id]
        size = (width, height)
        return pygame.image.fromstring(image_string, size, "RGBA")

    def scale_image(self, image_id, size, new_id=None):
        """Fetches the image with id 'image_id' and scales it. If new_id is given, a new entry in the image dictionary
        is created with this new id."""
        # TODO: Perhaps all of the surface transformation logic can be simplified.
        image = self.fetch_image(image_id)
        if new_id is not None:
            image_id = new_id
        else:
            image_id = self.get_new_id()
        scaled_image = pygame.transform.smoothscale(image, size)
        self.set_image(scaled_image, image_id)
        return image_id

    def rotate_image(self, image_id, theta, new_id=None):
        """Fetches the image with id 'image_id' and rotates it. If new_id is given, a new entry in the image dictionary
        is created with this new id."""
        image = self.fetch_image(image_id)
        if new_id is not None:
            image_id = new_id
        else:
            image_id = self.get_new_id()
        scaled_image = pygame.transform.rotate(image, theta)
        self.set_image(scaled_image, image_id)
        return image_id

    def scale_surface(self, surface_id, size, new_id=None):
        """Fetches the surface with id 'surface_id' and scales it. If new_id is given, a new entry in the surface
        dictionary is created with this new id."""
        surface = self.fetch_surface(surface_id)
        if new_id is not None:
            surface_id = new_id
        else:
            surface_id = self.get_new_id()
        scaled_surface = pygame.transform.smoothscale(surface, size)
        self.set_surface(scaled_surface, alpha=255, surface_id=surface_id)
        return surface_id

    def rotate_surface(self, surface_id, theta, new_id=None):
        """Fetches the surface with id 'surface_id' and rotates it. If new_id is given, a new entry in the surface
        dictionary is created with this new id."""
        surface = self.fetch_surface(surface_id)
        if new_id is not None:
            surface_id = new_id
        else:
            surface_id = self.get_new_id()
        scaled_surface = pygame.transform.rotate(surface, theta)
        self.set_surface(scaled_surface, alpha=255, surface_id=surface_id)
        return surface_id

    def restore_image(self, image_id):
        image = self.fetch_image(image_id)
        self.set_surface(image, alpha=255, surface_id=image_id, surface_type="image")

    def restore_surface(self, surface_id):
        # TODO: This probably doesn't work for rotated, scaled, images etc.
        width, height, alpha = self.surface_size_dict[surface_id]
        self.create_surface(width, height, alpha, surface_id)

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

    def create_font_surface(self, text, text_color, font_size, font_surface_id=None):
        font = self.get_font(font_size)
        font_surface = font.render(text, True, text_color)
        if font_surface_id is None:
            font_surface_id = self.get_new_id()

        self.set_surface(font_surface, alpha=255, surface_id=font_surface_id, surface_type="font")
        self.surface_font_dict[font_surface_id] = [text, text_color, font_size]
        return font_surface_id

    def fetch_text_surface(self, surface_id):
        if surface_id not in self.surfaces:
            self.restore_text_surface(surface_id)
        return self.surfaces[surface_id]

    def restore_text_surface(self, surface_id):
        text, color, font_size = self.surface_font_dict[surface_id]
        self.create_font_surface(text, color, font_size, surface_id)

    def load_surfaces(self, loaded_game_state):
        self.surface_size_dict = loaded_game_state.surface_size_dict
        self.surface_image_dict = loaded_game_state.surface_image_dict
        self.surface_font_dict = loaded_game_state.surface_font_dict
        self.surface_type_dict = loaded_game_state.surface_type_dict
        self.images = loaded_game_state.images
        self.current_max_id = loaded_game_state.current_max_id
        self.surfaces = {}
        self.fonts = {}
        for surface_id in self.surface_type_dict.keys():
            surface_type = self.surface_type_dict[surface_id]
            if surface_type == "surface":
                self.restore_surface(surface_id)
            elif surface_type == "image":
                self.restore_image(surface_id)
            elif surface_type == "font":
                self.restore_text_surface(surface_id)


class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current_scene = None
        # TODO: Implement scene switching. For example, tag a scene as persistent or temporary, and clear it only if
        # it is temporary.

    def get_current_scene(self):
        return self.current_scene

    def set_current_scene(self, new_scene):
        self.current_scene = new_scene

    def create_scene(self, scene_function, scene_name, scene_arguments):
        get_surface_manager().surfaces = {}  # TODO: Enable the clearing of old images too...
        if scene_name in self.scenes and self.scenes[scene_name].persistent:
            return self.change_scene_by_name(scene_name)

        if type(scene_arguments) is dict:
            scene = scene_function(**scene_arguments)
        else:
            scene = scene_function(*scene_arguments)

        return self.change_scene(scene)

    def change_scene_by_name(self, name):
        self.clear_current_scene()
        self.set_current_scene(self.scenes[name])
        return self.get_current_scene()

    def change_scene(self, scene):
        self.clear_current_scene()
        self.set_current_scene(scene)
        self.scenes[scene.name] = scene
        return scene

    def clear_current_scene(self):
        if self.get_current_scene() is not None and not self.get_current_scene().persistent:
            self.get_current_scene().clear()

    def schedule_scene_change(self, scene_function, scene_name="", scene_arguments=None):
        if scene_arguments is None:
            scene_arguments = []

        schedule_start_of_tick_function(self.create_scene, [scene_function, scene_name, scene_arguments])


class Scene:
    def __init__(self, name=""):
        self.name = name
        self.objects = []
        self.processing_order = []
        self.display_order = []
        self.background_color = WHITE
        self.persistent = False
        self.hidden_objects = []

    def get_objects(self):
        return self.objects

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    def add_multiple_objects(self, object_list):
        self.objects.extend(object_list)

    def get_default_position(self):
        return environment.width // 2, environment.height // 2

    def get_object_mask(self, obj):
        # TODO: Rename this method.
        index = self.processing_order.index(obj)
        blocking_object_list = []
        for masking_object in self.processing_order[index + 1:]:
            not_opaque = hasattr(masking_object, "opaque") and not masking_object.opaque
            if not hasattr(masking_object, "get_rect") or not_opaque:
                continue
            if obj.get_rect().colliderect(masking_object.get_rect()):
                blocking_object_list.append(masking_object)

        return blocking_object_list

    def clear(self):
        self.objects = []
        self.processing_order = []
        self.display_order = []

    def schedule_processing(self):
        self.processing_order = []

        self.objects.sort(key=lambda x: x.z)

        for obj in self.objects:
            items_to_be_processed = obj.schedule_processing()
            self.processing_order.extend(items_to_be_processed)

    def process_given_objects(self, objects):
        for obj in objects:
            self.process_object(obj)

    def process_object(self, obj):
        if not hasattr(obj, "process") or obj not in self.processing_order:
            return
        obj.process()

    def hide_object(self, source_object):
        """Removes the object from the processing order this tick."""
        self.remove_from_processing_order(source_object)
        self.remove_from_display_order(source_object)

    def remove_from_processing_order(self, source_object):
        """Removes an object from the processing order."""
        self.hidden_objects.append(source_object)
        if source_object in self.processing_order:
            self.processing_order.remove(source_object)

    def remove_from_display_order(self, source_object):
        """Removes an object from the display order. This is not currently doing anything"""
        if hasattr(source_object, "get_displayable_objects"):
            objects_to_remove = source_object.get_displayable_objects()
        else:
            objects_to_remove = [source_object]
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

        # Process objects.
        for obj in reversed(self.processing_order.copy()):
            self.process_object(obj)

        # Generate display order
        self.display_order = []
        for obj in self.objects:
            if hasattr(obj, "get_displayable_objects"):
                self.display_order.extend(obj.get_displayable_objects())

        # Display objects.
        for obj in self.display_order:
            if hasattr(obj, "get_display_surface") and callable(obj.get_display_surface):
                surface, rect = obj.get_display_surface()
                environment.screen.blit(surface, rect)

        # Remove destroyed objects
        for obj in self.objects:
            if hasattr(obj, "destroyed") and obj.destroyed:
                self.objects.remove(obj)


def get_placeholder():
    return game_state.placeholder


def get_scene_manager():
    return game_state.scene_manager


def set_scene_manager(scene_manager):
    game_state.scene_manager = scene_manager


def get_surface_manager():
    return game_state.surface_manager


def set_surface_manager(surface_manager):
    game_state.surface_manager = surface_manager


def schedule_start_of_tick_function(function, arguments):
    game_state.placeholder.start_of_tick_functions.append(function)
    game_state.placeholder.start_of_tick_arguments.append(arguments)


def schedule_end_of_tick_function(function, arguments):
    game_state.placeholder.end_of_tick_functions.append(function)
    game_state.placeholder.end_of_tick_arguments.append(arguments)


def start_tick():
    execute_multiple_functions(game_state.placeholder.start_of_tick_functions,
                               game_state.placeholder.start_of_tick_arguments)
    game_state.placeholder.start_of_tick_functions = []
    game_state.placeholder.start_of_tick_arguments = []


def end_tick():
    execute_multiple_functions(game_state.placeholder.end_of_tick_functions,
                               game_state.placeholder.end_of_tick_arguments)
    game_state.placeholder.end_of_tick_functions = []
    game_state.placeholder.end_of_tick_arguments = []

    environment.set_events_last_tick(environment.events_this_tick)
    environment.set_events_this_tick({"left_mouse_button": False, "right_mouse_button": False, "key_press": None})


def create_scene(scene_function, scene_name, scene_arguments):
    get_scene_manager().create_scene(scene_function, scene_name, scene_arguments)


def schedule_scene_change(scene_function, scene_name, scene_arguments=None):
    get_scene_manager().schedule_scene_change(scene_function, scene_name, scene_arguments)


def save(save_number=0):
    schedule_end_of_tick_function(_save, [save_number])


def _save(save_number):
    with open('save{}.txt'.format(save_number), 'wb') as save_file:
        game_state.load_from_surface_manager()
        surface_manager = get_surface_manager()
        set_surface_manager(None)
        pickle.dump(game_state, save_file)
        set_surface_manager(surface_manager)


def load(save_number=0):
    schedule_end_of_tick_function(_load, [save_number])


def _load(save_number):
    with open('save{}.txt'.format(save_number), 'rb') as save_file:
        loaded_game_state = pickle.load(save_file)
        get_surface_manager().load_surfaces(loaded_game_state)
        set_scene_manager(loaded_game_state.scene_manager)
        game_state.load_from_surface_manager()


def execute_multiple_functions(functions, argument_list):
    for i, function in enumerate(functions):
        if type(argument_list[i]) is dict:
            function(**argument_list[i])
        else:
            function(*argument_list[i])


environment = Environment()
game_state = GameState()

from constants import *
import os
import pickle

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


class Environment:
    """Initializes the Environment instance.

    The Environment manages various aspects of the game environment, such as the display window, mouse events,
    and screen dimensions.

    Attributes:
        scale_factor (int): The scaling factor for the game window.
        window (pygame.Surface): The resizable game window.
        key_press (str): The key pressed during the current tick.
        width (int): The width of the game window.
        height (int): The height of the game window.
        size (tuple): The size of the game window (width, height).
        screen (pygame.Surface): The main drawing surface for the game.
        clock (pygame.time.Clock): The Pygame clock for managing frame rates.
        standard_offset (int): A standard offset value used in various calculations.
        events_last_tick (dict): Dictionary storing mouse and key events from the last tick.
        events_this_tick (dict): Dictionary storing mouse and key events for the current tick.
    """

    def __init__(self):
        """Creates the Environment object."""
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
        """Returns the height of the game window.

        Returns:
            int: The height of the game window.
        """
        return self.height

    def get_width(self):
        """Returns the width of the game window.

        Returns:
            int: The width of the game window.
        """
        return self.width

    def get_mouse_position(self):
        """Returns the current mouse position in screen-space coordinates, not window-space.

        Returns:
            tuple: A tuple of floats representing the mouse position.
        """
        x, y = pygame.mouse.get_pos()
        window_width = pygame.display.Info().current_w
        window_height = pygame.display.Info().current_h
        scale_x = self.screen.get_width() / window_width
        scale_y = self.screen.get_height() / window_height
        return int(x * scale_x), int(y * scale_y)

    def set_events_this_tick(self, events):
        """Sets the recorded events for the current tick.

        Args:
            events (dict): A dictionary containing mouse and key events.

        """
        self.events_this_tick = events

    def set_events_last_tick(self, events):
        """Sets the recorded events for the last tick.

        Args:
            events (dict): A dictionary containing mouse and key events.

        """
        self.events_last_tick = events

    def get_events_this_tick(self):
        """Gets the events dictionary for the current tick.

        Returns:
            dict: A dictionary containing recorded mouse and key events for the current tick.

        """
        return self.events_this_tick

    def get_events_last_tick(self):
        """Gets the events dictionary for the last tick.

        Returns:
            dict: A dictionary containing recorded mouse and key events for the last tick.

        """
        return self.events_last_tick

    def get_left_mouse_click_this_tick(self):
        """Returns whether the left mouse button was clicked during the current tick.

        Returns:
            bool: True if the left mouse button was clicked, False otherwise.

        """
        return self.events_this_tick["left_mouse_button"]

    def get_right_mouse_click_this_tick(self):
        """Returns whether the right mouse button was clicked during the current tick.

        Returns:
            bool: True if the right mouse button was clicked, False otherwise.

        """
        return self.events_this_tick["right_mouse_button"]

    def get_left_mouse_click_last_tick(self):
        """Returns whether the left mouse button was clicked during the last tick.

        Returns:
            bool: True if the left mouse button was clicked last tick, False otherwise.

        """
        return self.events_last_tick["left_mouse_button"]

    def get_right_mouse_click_last_tick(self):
        """Returns whether the right mouse button was clicked during the last tick.

        Returns:
            bool: True if the right mouse button was clicked last tick, False otherwise.

        """
        return self.events_last_tick["right_mouse_button"]

    def get_key_press_this_tick(self):
        """Returns whether the key that was pressed during the current tick, if any.

        Returns:
            str or None: The string representing the key that was pressed this tick, or None if no key was pressed.
        """
        return self.events_last_tick["key_press"]

    def get_key_press_last_tick(self):
        """Returns whether the key that was pressed during the last tick, if any.

        Returns:
            str or None: The string representing the key that was pressed last tick, or None if no key was pressed.
        """
        return self.events_last_tick["key_press"]

    def handle_events(self):
        """Checks for detected pygame events, such as if the user tries to close the program window or if the
        user clicks the mouse or presses any keys.

        Returns:
            bool: True if the program should continue running, False if the user closed the window.
        """
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
        """Draws the screen by scaling the surface and updating the window display."""
        resized_screen = pygame.transform.scale(self.screen, self.window.get_rect().size)
        environment.window.blit(resized_screen, (0, 0))
        pygame.display.flip()


class GameState:
    """An object representing the current game state.

    Attributes:
        surface_manager (SurfaceManager): Manager for surfaces, images, fonts, and their metadata.
        surface_objects (dict): A dictionary relating surface ids and SurfaceHelper objects.
        current_max_id (int): The current maximum ID used for surface and image identification.
        scene_manager (SceneManager): Manager for scenes and scene transitions.
        tick_manager (TickManager): TickManager object for storing start and end of tick functions.
    """

    def __init__(self):
        """Creates a GameState object."""
        self.surface_manager = SurfaceManager()
        self.current_max_id = self.surface_manager.current_max_id
        self.surface_objects = self.surface_manager.surface_objects
        self.image_path_id_dict = self.surface_manager.image_path_id_dict = {}

        self.scene_manager = SceneManager()

        self.tick_manager = TickManager()

    def load_from_surface_manager(self):
        """Load surface-related attributes from the SurfaceManager."""
        self.current_max_id = self.surface_manager.current_max_id
        self.surface_objects = self.surface_manager.surface_objects
        self.image_path_id_dict = self.surface_manager.image_path_id_dict = {}

    def get_savable_copy(self):
        new_game_state = GameState()
        new_game_state.surface_manager = self.surface_manager.copy()
        new_game_state.scene_manager = self.scene_manager
        new_game_state.load_from_surface_manager()
        for surface_object in new_game_state.surface_objects.values():
            surface_object.prepare_for_saving()
        return new_game_state


class TickManager:
    """This class serves as a data storage for functions and arguments to be executed
    at the start and end of each game tick.

    Attributes:
        start_of_tick_functions (list): List to store functions to be executed at the start of a tick.
        start_of_tick_arguments (list): List to store arguments for functions to be executed at the start of a tick.
        end_of_tick_functions (list): List to store functions to be executed at the end of a tick.
        end_of_tick_arguments (list): List to store arguments for functions to be executed at the end of a tick.
    """

    def __init__(self):
        """Initialize the TickManager object."""
        self.start_of_tick_functions = []
        self.start_of_tick_arguments = []
        self.end_of_tick_functions = []
        self.end_of_tick_arguments = []


class SurfaceHelper:
    def __init__(self, surface, surface_id=None, size=(0, 0), alpha=255, image_path="", image_string="",
                 font_data=("", BLACK, 30),
                 surface_type="surface"):

        self.surface = surface
        if surface_id is None:
            self.surface_id = get_surface_manager().get_new_id()
        else:
            self.surface_id = surface_id
        self.size = size[0], size[1]
        self.alpha = alpha
        self.image_path = image_path
        self.image_string = image_string
        self.font_data = font_data
        self.surface_type = surface_type

    def get_surface(self):
        if self.surface is not None:
            return self.surface

    def get_surface_id(self):
        return self.surface_id

    def get_size(self):
        return self.size

    def get_alpha(self):
        return self.alpha

    def get_image_path(self):
        return self.image_path

    def get_image_string(self):
        return self.image_string

    def get_font_data(self):
        return self.font_data

    def get_surface_type(self):
        return self.surface_type

    def set_size(self, size):
        self.size = size

    def set_image_path(self, image_path):
        self.image_path = image_path

    def prepare_for_saving(self):
        self.surface = None

    def copy(self):
        new_surface_helper = SurfaceHelper(self.get_surface(), self.get_surface_id(), self.get_size(),
                                           self.get_alpha(),
                                           self.get_image_path(), self.get_image_string(), self.get_font_data(),
                                           self.get_surface_type())

        return new_surface_helper


class SurfaceManager:
    # TODO: Need some way to remove surfaces that are no longer used.
    def __init__(self):
        self.current_max_id = 0
        self.fonts = {}
        self.image_path_id_dict = {}
        self.surface_objects = {}

    def get_new_id(self):
        new_id = self.current_max_id + 1
        self.current_max_id += 1
        return new_id

    def add_surface(self, surface, surface_id=None, alpha=255, image_path="", image_string="",
                    font_data=("", BLACK, 30),
                    surface_type="surface"):
        surface_object = SurfaceHelper(surface, surface_id=surface_id, size=surface.get_size(), alpha=alpha,
                                       image_path=image_path, image_string=image_string,
                                       font_data=font_data, surface_type=surface_type)
        self.surface_objects[surface_object.get_surface_id()] = surface_object
        return surface_object.get_surface_id()

    def fetch_surface(self, surface_id):
        return self.surface_objects[surface_id].get_surface()

    def create_surface(self, width, height, alpha=255, surface_id=None):
        surface = pygame.Surface((width, height))
        surface.set_alpha(alpha)
        surface_id = self.add_surface(surface, surface_id=surface_id, alpha=alpha)
        return surface_id

    def restore_surface(self, surface_id):
        surface_object = self.surface_objects[surface_id]
        width, height = surface_object.get_size()
        self.create_surface(width, height, surface_object.get_alpha(), surface_id)

    def transform_surface(self, surface_id, size, rotation_angle, new_id=None):
        surface = self.fetch_surface(surface_id)
        rotated_and_scaled_surface = self._transform_surface(surface, size, rotation_angle)
        new_id = self.add_surface(rotated_and_scaled_surface, alpha=surface.get_alpha(), surface_id=new_id)
        return new_id

    @staticmethod
    def _transform_surface(surface, size, rotation_angle):
        rotated_surface = pygame.transform.rotate(surface, rotation_angle)
        rotated_and_scaled_surface = pygame.transform.smoothscale(rotated_surface, size)
        return rotated_and_scaled_surface

    def load_image(self, image_path):
        """Loads the image with the specified image path and returns it.

        Args:
            image_path (str): The image path of the image to be loaded.

        Returns:
            int: The id of the image.
        """
        if image_path in self.image_path_id_dict:
            return self.image_path_id_dict[image_path]

        image = pygame.image.load(image_path)
        image.set_alpha(255)
        image_id = self.set_image(image, image_path)
        return image_id

    def set_image(self, image, image_path, image_id=None):
        image_string = pygame.image.tostring(image, 'RGBA')
        image_id = self.add_surface(image, alpha=image.get_alpha(), surface_id=image_id, image_path=image_path,
                                    image_string=image_string,
                                    surface_type="image")
        return image_id

    def fetch_image(self, image_id):
        surface_object = self.surface_objects[image_id]
        image_string = surface_object.get_image_string()
        size = surface_object.get_size()
        return pygame.image.fromstring(image_string, size, "RGBA")

    def transform_image(self, image_id, size, rotation_angle, new_id=None):
        """Fetches the image with id 'image_id' and scales it. If new_id is given, a new entry in the image dictionary
        is created with this new id."""
        image = self.fetch_image(image_id)
        scaled_and_rotated_image = self._transform_surface(image, size, rotation_angle)
        surface_object = self.surface_objects[image_id]
        new_id = self.set_image(scaled_and_rotated_image, surface_object.get_image_path(), image_id=new_id)
        return new_id

    def restore_image(self, image_id):
        image = self.fetch_image(image_id)
        surface_object = self.surface_objects[image_id]
        self.add_surface(image, surface_id=image_id, alpha=image.get_alpha(),
                         image_path=surface_object.get_image_path(),
                         image_string=surface_object.get_image_string(), surface_type="image")

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
        font_data = (text, text_color, font_size)
        font_surface_id = self.add_surface(font_surface, surface_id=font_surface_id, alpha=255, font_data=font_data,
                                           surface_type="font")
        return font_surface_id

    def fetch_text_surface(self, font_surface_id):
        if font_surface_id not in self.surface_objects:
            self.restore_text_surface(font_surface_id)

        return self.surface_objects[font_surface_id].get_surface()

    def restore_text_surface(self, surface_id):
        surface_object = self.surface_objects[surface_id]
        text, color, font_size = surface_object.get_font_data()
        self.create_font_surface(text, color, font_size, surface_id)

    def load_surfaces(self, loaded_game_state):
        self.current_max_id = loaded_game_state.current_max_id
        self.surface_objects = loaded_game_state.surface_objects
        self.image_path_id_dict = loaded_game_state.image_path_id_dict
        self.fonts = {}
        for surface_id, surface_object in self.surface_objects.items():
            surface_type = surface_object.get_surface_type()
            if surface_type == "surface":
                self.restore_surface(surface_id)
            elif surface_type == "image":
                self.restore_image(surface_id)
            elif surface_type == "font":
                self.restore_text_surface(surface_id)

    def copy(self):
        new_surface_manager = SurfaceManager()
        new_surface_manager.current_max_id = self.current_max_id
        for surface_id, surface_object in self.surface_objects.items():
            new_surface_manager.surface_objects[surface_id] = surface_object.copy()
        new_surface_manager.image_path_id_dict = self.image_path_id_dict.copy()
        new_surface_manager.fonts = {}
        return new_surface_manager


class SceneManager:
    """A class for managing the scenes.

    Attributes:
        scenes (dict): A dictionary to store scenes by name.
        current_scene: The currently active scene.
    """

    def __init__(self):
        """Initializes the SceneManager."""
        self.scenes = {}
        self.current_scene = None

    def get_current_scene(self):
        """Get the currently active scene.

        Returns:
            Scene: The currently active scene.
        """
        return self.current_scene

    def set_current_scene(self, new_scene):
        """Set the currently active scene.

        Args:
            new_scene (Scene): The scene to set as the active scene.
        """
        self.current_scene = new_scene

    def create_scene(self, scene_function, scene_name, scene_arguments):
        """Create and change to a new scene.

        Args:
            scene_function (callable): The function to create the new scene.
            scene_name (str): The name to identify the scene.
            scene_arguments (list or dict): Arguments to pass to the scene function.

        Returns:
            Scene: The newly created scene.
        """
        get_surface_manager().surfaces = {}
        if scene_name in self.scenes and self.scenes[scene_name].persistent:
            return self.change_scene_by_name(scene_name)

        if isinstance(scene_arguments, dict):
            scene = scene_function(**scene_arguments)
        else:
            scene = scene_function(*scene_arguments)

        return self.change_scene(scene)

    def change_scene_by_name(self, name):
        """Change to a scene by using its name.

        Args:
            name (str): The name of the scene to change to.

        Returns:
            Scene: The newly active scene.
        """
        return self.change_scene(self.scenes[name])

    def change_scene(self, scene):
        """Change to a new scene.

        Args:
            scene (Scene): The scene to change to.

        Returns:
            Scene: The newly active scene.
        """
        self.clear_current_scene()
        self.set_current_scene(scene)
        self.scenes[scene.name] = scene
        return scene

    def clear_current_scene(self):
        """Clear the currently active scene, if it is not persistent."""
        if self.get_current_scene() is not None and not self.get_current_scene().persistent:
            self.get_current_scene().clear()

    def schedule_scene_change(self, scene_function, scene_name="", scene_arguments=None):
        """Schedule a scene change at the start of the next tick.

        Args:
            scene_function (callable): The function to create the new scene.
            scene_name (str): The name to identify the scene.
            scene_arguments (list or dict): Arguments to pass to the scene function.
        """
        if scene_arguments is None:
            scene_arguments = []

        schedule_start_of_tick_function(self.create_scene, [scene_function, scene_name, scene_arguments])


class Scene:
    """A class representing a scene in the application.

    Attributes:
        name (str): The name of the scene.
        objects (list): A list of objects within the scene. Does not include all objects, only the root objects, so
        these objects can have
            children etc.
        processing_order (list): The order in which objects are processed.
        display_order (list): The order in which objects are displayed.
        background_color (tuple): The background color of the scene.
        persistent (bool): Whether the scene is persistent across scene changes.
    """

    def __init__(self, name=""):
        """Initialize a Scene object.

        Args:
            name (str): The name of the scene.
        """
        self.name = name
        self.objects = []
        self.processing_order = []
        self.display_order = []
        self.background_color = WHITE
        self.persistent = False

    def get_objects(self):
        """Get the list of root objects in the scene.

        Returns:
            list: The list of root objects in the scene.
        """
        return self.objects

    def add_object(self, obj):
        """Add a root object to the scene.

        Args:
            obj: The object to add.
        """
        self.objects.append(obj)

    def remove_object(self, obj):
        """Remove a root object from the scene.

        Args:
            obj: The object to remove.
        """
        if obj in self.objects:
            self.objects.remove(obj)

    def add_multiple_objects(self, object_list):
        """Add multiple root objects to the scene.

        Args:
            object_list (list): The list of root objects to add to the scene.
        """
        self.objects.extend(object_list)

    def get_default_position(self):
        """Get the default position in the scene.

        Returns:
            tuple: The default position in the scene as (x, y).
        """
        return environment.width // 2, environment.height // 2

    def get_object_mask(self, obj):
        """Get a list of objects that could block the given object.

        Args:
            obj: The object to check for blocking.

        Returns:
            list: The list of objects that could be blocking the given object.
        """
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
        """Clear all objects from the scene."""
        self.objects = []
        self.processing_order = []
        self.display_order = []

    def schedule_processing(self):
        """Schedule the processing order of objects."""
        self.processing_order = []

        self.objects.sort(key=lambda x: x.z)

        for obj in self.objects:
            items_to_be_processed = obj.schedule_processing()
            self.processing_order.extend(items_to_be_processed)

    def process_given_objects(self, objects):
        """Process a given list of objects.

        Args:
            objects (list): The list of objects to process.
        """
        for obj in objects:
            self.process_object(obj)

    def process_object(self, obj):
        """Process a specific object.

        Args:
            obj: The object to process.
        """
        cant_be_processed = not hasattr(obj, "process") or obj not in self.processing_order
        obj_destroyed = hasattr(obj, "destroyed") and obj.destroyed
        if cant_be_processed or obj_destroyed:
            return

        obj.process()

    def process(self):
        """Process and display objects in the scene."""
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
        self.display_order.sort(key=lambda x: x.z)

        # Display objects.
        for obj in self.display_order:
            if hasattr(obj, "get_display_surface") and callable(obj.get_display_surface):
                surface, rect = obj.get_display_surface()
                environment.screen.blit(surface, rect)

        # Remove destroyed objects
        for obj in self.objects:
            if hasattr(obj, "destroyed") and obj.destroyed:
                self.objects.remove(obj)


def get_tick_manager():
    """Returns the current tick manager.

    Returns:
        TickManager or None: The tick manager of the current game state.
    """
    return game_state.tick_manager


def get_scene_manager():
    """Returns the surface manager associated with the current game state.

    Returns:
        SceneManager or None: The surface manager of the current game state.
    """
    return game_state.scene_manager


def set_scene_manager(scene_manager):
    """Sets the scene manager for the game state.

    Args:
        scene_manager (SceneManager or None): The surface manager to be set.
    """
    game_state.scene_manager = scene_manager


def get_surface_manager():
    """Returns the surface manager associated with the current game state.

    Returns:
        SurfaceManager or None: The surface manager of the current game state.
    """
    return game_state.surface_manager


def set_surface_manager(surface_manager):
    """Sets the surface manager for the game state.

    Args:
        surface_manager (SurfaceManager or None): The surface manager to be set.
    """
    game_state.surface_manager = surface_manager


def schedule_start_of_tick_function(function, arguments):
    """Schedules a function to be executed at the start of the next game tick.

    Args:
        function (callable): The function to be executed.
        arguments (list): The list of arguments to be passed to the function.
    """
    game_state.tick_manager.start_of_tick_functions.append(function)
    game_state.tick_manager.start_of_tick_arguments.append(arguments)


def schedule_end_of_tick_function(function, arguments):
    """Schedules a function to be executed at the end of the current game tick.

    Args:
        function (callable): The function to be executed.
        arguments (list): The list of arguments to be passed to the function.
    """
    game_state.tick_manager.end_of_tick_functions.append(function)
    game_state.tick_manager.end_of_tick_arguments.append(arguments)


def start_tick():
    """Executes start-of-tick functions."""
    execute_multiple_functions(game_state.tick_manager.start_of_tick_functions,
                               game_state.tick_manager.start_of_tick_arguments)
    game_state.tick_manager.start_of_tick_functions = []
    game_state.tick_manager.start_of_tick_arguments = []


def end_tick():
    """Executes end-of-tick functions and resets environment events."""
    execute_multiple_functions(game_state.tick_manager.end_of_tick_functions,
                               game_state.tick_manager.end_of_tick_arguments)
    game_state.tick_manager.end_of_tick_functions = []
    game_state.tick_manager.end_of_tick_arguments = []

    environment.set_events_last_tick(environment.events_this_tick)
    environment.set_events_this_tick({"left_mouse_button": False, "right_mouse_button": False, "key_press": None})


def schedule_scene_change(scene_function, scene_name, scene_arguments=None):
    """Schedules a scene change with the scene manager.

    Args:
        scene_function (callable): The function responsible for creating the new scene.
        scene_name (str): The name of the new scene.
        scene_arguments (list): A list of arguments to pass to the scene function. Defaults to None.
    """
    get_scene_manager().schedule_scene_change(scene_function, scene_name, scene_arguments)


def save(save_number=0):
    """Schedules the asynchronous saving of the game state at the end of the current tick.

    Args:
        save_number (int): The identifier for the save file. Defaults to 0.
    """
    schedule_end_of_tick_function(_save, [save_number])


def _save(save_number):
    """Saves the game state to a file. Should be called at the end of the tick.

    Args:
        save_number (int): The identifier for the save file.
    """
    with open(f'save{save_number}.txt', 'wb') as save_file:
        savable_game_state = game_state.get_savable_copy()
        pickle.dump(savable_game_state, save_file)


def load(save_number=0):
    """Schedules the asynchronous loading of the game state at the end of the current tick.

    Args:
        save_number (int): The identifier of the save file. Defaults to 0.
    """
    schedule_end_of_tick_function(_load, [save_number])


def _load(save_number):
    """Load a saved game state from a file.

    Args:
        save_number (int): The identifier of the save file.

    Notes:
        This function loads the game state from the specified save file, including surface manager data and the
        scene manager. It updates the current game state accordingly.
    """
    with open(f'save{save_number}.txt', 'rb') as save_file:
        loaded_game_state = pickle.load(save_file)
        get_surface_manager().load_surfaces(loaded_game_state)
        set_scene_manager(loaded_game_state.scene_manager)
        game_state.load_from_surface_manager()


def execute_multiple_functions(functions, argument_list):
    """Executes multiple functions with corresponding argument lists.

    Args:
        functions (list): List of functions to be executed.
        argument_list (list): List of argument lists corresponding to the functions.
    """
    for i, function in enumerate(functions):
        if isinstance(argument_list[i], dict):
            function(**argument_list[i])
        else:
            function(*argument_list[i])


def load_image(image_path):
    return get_surface_manager().load_image(image_path)


environment = Environment()
game_state = GameState()

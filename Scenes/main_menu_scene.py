from game_engine import environment, Scene
import game_engine
from constants import *
import sys
import assets
from Scenes import test_scene, deck_selection_scene, scenes


class MainMenuScene(Scene):
    """Creates a scene used displaying the main menu.

    Inherits all attributes from the Scene class, and implements the create_scene method.
    """

    def __init__(self):
        super().__init__(name=scenes.MAIN_MENU_SCENE)

    def create_scene(self):
        """Creates the main menu scene.

        Returns:
            Scene: The main menu scene containing buttons for starting, loading, testing, and exiting the game.
        """
        self.background_color = WHITE
        width = 200
        height = 100
        font_size = 35
        start_button = assets.Button(y=environment.get_height() // 2, width=width,
                                     height=height, text="Start", font_size=font_size,
                                     left_click_function=game_engine.schedule_scene_change,
                                     left_click_args=[deck_selection_scene.DeckSelectionScene()])

        load_button = assets.Button(y=environment.get_height() // 2, width=width, font_size=font_size,
                                    height=height, text="Load Save", left_click_function=game_engine.load_state)

        test_button = assets.Button(y=environment.get_height() // 2, width=width, height=height,
                                    text="Testing", font_size=font_size,
                                    left_click_function=game_engine.schedule_scene_change,
                                    left_click_args=[test_scene.TestScene()])

        exit_button = assets.Button(y=environment.get_height() // 2, width=width,
                                    height=height, text="Exit", font_size=font_size,
                                    left_click_function=sys.exit)

        buttons = [start_button, load_button, test_button, exit_button]
        number_of_buttons = len(buttons)
        x_offset = (environment.get_width() - number_of_buttons * width) // (number_of_buttons + 1)
        for i, button in enumerate(buttons):
            button.set_pos((i + 1) * x_offset + i * width, button.y)
            button.set_z(1)
            self.add_object(button)

        return self

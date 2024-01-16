from game_engine import Scene
import game_engine
import assets
from constants import *
from Scenes import main_menu_scene, scenes
import time


class TestScene(Scene):
    """Creates a scene used for testing.

    Inherits all attributes from the Scene class, and implements the create_scene method.
    """

    def __init__(self):
        super().__init__(name=scenes.TEST_SCENE)

    def create_scene(self):
        """Creates a test scene for testing different functionality.

        Returns:
            Scene: The test scene.
        """
        self.background_color = SIENNA
        exit_button = assets.Button(text="Main Menu", alpha=255,
                                    left_click_function=game_engine.schedule_scene_change,
                                    left_click_args=[main_menu_scene.MainMenuScene()],
                                    name="exit_button")
        self.add_object(exit_button)
        button = assets.Button(x=500, y=500, width=200, height=100, text="Create confirmation overlay",
                               resize_to_fit_text=True,
                               left_click_function=self.create_object,
                               left_click_args=[assets.ConfirmationOverlay, 700, 700, test_button, []],
                               color=SADDLE_BROWN, alpha=175,
                               name="test_button")
        movable_button = assets.MobileButton(x=100, y=100, z=1, name="mobile_button")

        follow_mobile = assets.MobileButton(x=200, y=125, z=1, parent=movable_button, static=False,
                                            source_image_id=game_engine.load_image(
                                                image_location + "transparent_card.png"),
                                            name="follow_mobile")

        movable_button.add_child(follow_mobile)
        follow_mobile.opaque_to_ancestor = True

        self.add_object(movable_button)
        self.add_object(button)
        transparent_box = assets.Box(x=600, y=600, source_image_id=game_engine.load_image(
            image_location + "transparent_card.png"),
                                     name="transparent_box")
        self.add_object(transparent_box)
        text_box = assets.InputField(x=400, y=400)
        self.add_object(text_box)

        return self


def test_button():
    """Prints a test message with the current time.

    This function serves as a test button action. It prints a message indicating the execution of the button test
    along with the current timestamp.
    """
    print("BUTTON TEST AT TIME:", time.time())

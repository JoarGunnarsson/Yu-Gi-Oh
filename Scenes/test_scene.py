from game_engine import Scene
import game_engine
import assets
from constants import *
from Scenes import main_menu_scene
import time


class TestScene(Scene):
    def __init__(self):
        super().__init__(name="test_scene")

    def create_scene(self):
        """Creates a test scene for testing different functionality.

        Returns:
            Scene: The test scene.
        """
        self.background_color = SIENNA
        exit_btn = assets.Button(text="Main Menu", alpha=255,
                                 left_click_function=game_engine.schedule_scene_change,
                                 left_click_args=[main_menu_scene.MainMenuScene()],
                                 name="exit_btn")
        self.add_object(exit_btn)
        button = assets.Button(x=500, y=500, width=200, height=100, text="Create confirmation overlay",
                               left_click_function=self.create_object,
                               left_click_args=[assets.ConfirmationOverlay, 700, 700, test_button, []],
                               colors={assets.ButtonState.NORMAL: SADDLE_BROWN, assets.ButtonState.HOVER: SIENNA,
                                       assets.ButtonState.PRESSED: BLACK}, alpha=175,
                               name="test_btn")
        button.hug_text(15)
        movable_btn = assets.MobileButton(x=100, y=100, z=1, name="mobile_btn")

        follow_mobile = assets.MobileButton(x=200, y=125, z=1, parent=movable_btn, static=False,
                                            image_id=game_engine.load_image("./Images/card_back.png"),
                                            name="follow_mobile")

        movable_btn.add_child(follow_mobile)

        self.add_object(movable_btn)
        self.add_object(button)
        return self


def test_button():
    """Prints a test message with the current time.

    This function serves as a test button action. It prints a message indicating the execution of the button test
    along with the current timestamp.
    """
    print("BUTTON TEST AT TIME:", time.time())
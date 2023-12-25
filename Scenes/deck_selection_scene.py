from game_engine import environment, Scene
import game_engine
import assets
from constants import *
import utility_functions as utils
from Scenes import playtesting_scene
from decks import DECKS


class DeckSelectionScene(Scene):
    """Creates a scene used for selecting a Yu-Gi-Oh! deck.

    Inherits all attributes from the Scene class, and implements the create_scene method.
    """
    def __init__(self):
        super().__init__(name="deck_selection_scene")

    def create_scene(self):
        """Creates a scene for deck selection.

        Returns:
            Scene: The scene with deck selection options.
        """

        deck_selection_overlay = assets.Overlay(z=1, width=environment.get_width(), height=environment.get_height(),
                                                background_color=WHITE)

        close_btn = utils.find_object_from_name(deck_selection_overlay.get_buttons(), "close_btn")
        deck_selection_overlay.destroy_child(close_btn)

        for i, deck in enumerate(DECKS):
            deck_btn = assets.Button(text=deck.name, x=i * large_card_width, y=500, z=1, width=large_card_width,
                                     height=large_card_height,
                                     left_click_function=self.create_object,
                                     left_click_args=[assets.ConfirmationOverlay, i * large_card_width, 500,
                                                      choose_deck, [deck]])
            deck_btn.set_image(deck.get_image_id())
            deck_selection_overlay.add_child(deck_btn)

        self.add_object(deck_selection_overlay)
        return self


def choose_deck(deck):
    """Chooses a deck for playtesting.

    Sets the specified deck as the active deck using the deck manager and schedules a scene change to the playtesting
    scene.

    Args:
        deck: The deck to be set as the active deck for playtesting.
    """
    game_engine.schedule_scene_change(playtesting_scene.PlaytestingScene(deck))

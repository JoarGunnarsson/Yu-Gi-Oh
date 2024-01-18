from game_engine import environment, Scene
import game_engine
import assets
from constants import *
import utility_functions as utils
from Scenes import playtesting_scene, scenes
from decks import DECKS


class DeckSelectionScene(Scene):
    """Creates a scene used for selecting a Yu-Gi-Oh! deck.

    Inherits all attributes from the Scene class, and implements the create_scene method.
    """

    def __init__(self):
        super().__init__(name=scenes.DECK_SELECTION_SCENE)

    def create_scene(self):
        """Creates a scene for deck selection.

        Returns:
            Scene: The scene with deck selection options.
        """
        self.background_color = GREY

        x_offset = (environment.get_width() - len(DECKS) * large_card_width) / (2 + len(DECKS) - 1)
        y_offset = (environment.get_height() - large_card_height) / 2

        deck_options_overlay = assets.Overlay(x=x_offset / 2, y=y_offset / 2, z=1,
                                              width=environment.get_width() - x_offset,
                                              height=environment.get_height() - y_offset, background_color=SIENNA,
                                              include_close_button=False)
        self.add_object(deck_options_overlay)

        centered_x = utils.center_rectangle(deck_options_overlay.x, deck_options_overlay.x + deck_options_overlay.width,
                                            300)
        centered_y = utils.center_rectangle(deck_options_overlay.y, y_offset, 30)
        instruction_box = assets.Box(x=centered_x,
                                     y=centered_y,
                                     z=1,
                                     width=300, height=30, text="Choose a deck", resize_to_fit_text=True,
                                     color=SADDLE_BROWN, y_centering=assets.CenteringOptions.CENTER,
                                     include_border=True)
        deck_options_overlay.add_child(instruction_box)

        for i, deck in enumerate(DECKS):
            button_x = x_offset + i * (large_card_width + x_offset)
            button_y = y_offset
            deck_button = assets.Button(x=button_x,
                                        y=button_y, z=1,
                                        width=large_card_width,
                                        height=large_card_height,
                                        left_click_function=self.create_object,
                                        left_click_args=[assets.ConfirmationOverlay, button_x, None,
                                                         choose_deck, [deck]])
            deck_button.set_image(deck.get_image_id())

            text_box_width, text_box_height = 100, 40
            text_box_x = utils.center_rectangle(deck_button.x, deck_button.x + deck_button.width, text_box_width)
            deck_button_bottom_y = deck_button.y + deck_button.height
            options_overlay_bottom_y = deck_options_overlay.y + deck_options_overlay.height
            text_box_y = utils.center_rectangle(deck_button_bottom_y, options_overlay_bottom_y, text_box_height)

            deck_text_box = assets.Box(x=text_box_x,
                                       y=text_box_y, z=1,
                                       width=100, height=40, text=deck.name, resize_to_fit_text=True,
                                       x_centering=assets.CenteringOptions.CENTER,
                                       y_centering=assets.CenteringOptions.CENTER,
                                       include_border=True)

            deck_options_overlay.add_child(deck_button)
            deck_button.add_child(deck_text_box)
        return self


def choose_deck(deck):
    """Chooses a deck for playtesting.

    Sets the specified deck as the active deck using the deck manager and schedules a scene change to the playtesting
    scene.

    Args:
        deck: The deck to be set as the active deck for playtesting.
    """
    game_engine.schedule_scene_change(playtesting_scene.PlaytestingScene(deck))

from Scenes import main_menu_scene
import game_engine
from game_engine import environment
from constants import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# TODO: Implement text fields, dice, etc? For randomness, life points etc.

# TODO: Perhaps implement a place to enter commands, such as shuffle deck etc.

# TODO: Make small_card_overlay into a sub-class of Overlay?

# TODO: Some bug with create_overlay_card, FileNotFoundError. Can't seem to reproduce this reliably.

# TODO: Fix the deck selection scene

# TODO: Add support for pendulum monsters.
# This include show if a card is face-up or face-down (only has to be in the extra deck, but could as well include
# this functionality for any card). Also add pendulum types for the get_card_type. Pendulum cards should be able
# to be sent to the extra_deck.

# TODO: There are many "magic values", such as scene.name == "playtesting_scene", which has caused trouble before.
# Fix this by for example using an Enum for scenes.

# TODO: Improve utils file structure, move change_overlay_limits into a method.

# TODO: Perhaps merge the card lists of the board to a single list, instead using an Enum to set the location.

# TODO: Change the file structure further, so that assets can be imported without creating a game window?

# TODO: Fix the remove_on_external_clicks functionality -> GameScript.

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("A tool for playtesting Yu-Gi-Oh!")

    game_engine.schedule_scene_change(main_menu_scene.MainMenuScene())
    running = True
    while running:
        running = environment.handle_events()
        game_engine.start_tick()
        game_engine.process_current_scene()

        environment.draw_screen()

        game_engine.end_tick()

        environment.clock.tick(FPS)
    pygame.quit()

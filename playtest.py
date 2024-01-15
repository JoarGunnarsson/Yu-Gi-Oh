#!/usr/bin/env python3
from Scenes import main_menu_scene
import game_engine
from game_engine import environment
from constants import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# TODO: Implement text fields, dice, etc? For randomness, life points etc.

# TODO: Perhaps implement a place to enter commands, such as shuffle deck etc.

# TODO: Add support for pendulum monsters.
# This include show if a card is face-up or face-down (only has to be in the extra deck, but could as well include
# this functionality for any card). Could be done by blitting a semi transparent card-back image to the card surface.
# Also add pendulum types for the get_card_type. Pendulum cards should be able
# to be sent to the extra_deck face-up only if they start in the main-deck, otherwise both face-up and face-down.

# TODO: There are many "magic values", such as scene.name == "playtesting_scene", which has caused trouble before.
# Fix this by for example using an Enum for scenes.

# TODO: Perhaps merge the card lists of the board to a single list, instead using an Enum to set the location.

# TODO: Change the file structure further, so that assets can be imported without creating a game window?

# TODO: Fix the remove_on_external_clicks functionality -> GameScript.

# TODO: Rescale all size constants, it should be possible to use a lower resolution.

# TODO: Make the large card overlay look better.

# TODO: Perhaps clamp cards that are placed to the field using default_position.

# TODO: Rescale deck selection deck images. Or use scrolling function.

# TODO: Perhaps use color detection in order to figure out the level of a card, rank, or link rating. Could then
# be used for sorting.

# TODO: Add deck view?

# TODO: Move some functionality out from game_engine.py. For example, loading files etc. Everything that is not
# used for the game screen.

# TODO: Implement multiple centering options, left-centering, center centering, right centering. Currently,
# everything is center centered.


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("A tool for playtesting Yu-Gi-Oh!")
    game_engine.load_all_images()
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

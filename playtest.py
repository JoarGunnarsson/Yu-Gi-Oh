import os
import sys
import random
import math
import time
import assets
import constants
from game_engine import environment, Scene
import game_engine
import utility_functions as utils
from constants import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# TODO: Implement text fields, dice, etc? For randomness, life points etc.

# TODO: Perhaps implement a place to enter commands, such as shuffle deck etc.

# TODO: Fix comments, code, documentation.

# TODO: Find a way to highlight buttons even when they use images.
# could work with always highlighting a border around the button, or using a transparent white layer above the button.

# TODO: Fix classes, functions etc so that things work without knowing how everything works in detail.
# That is, fix the api, so that you can create a new scene easily.

# TODO: Overlay exit button only looks good on white overlays. Make buttons transparent?

# TODO: Make small_card_overlay into a sub-class of Overlay?

# TODO: Make button colors easier to use. Specify one main color, and then the highlighting is done either by
# opacity or increasing (or decreasing) the brightness by a certain amount.

# TODO: Some bug with create_overlay_card, FileNotFoundError. Can't seem to reproduce this reliably.

# TODO: Fix the deck selection scene

# TODO: Add support for pendulum monsters.
# This include show if a card is face-up or face-down (only has to be in the extra deck, but could as well include
# this functionality for any card). Also add pendulum types for the get_card_type. Pendulum cards should be able
# to be sent to the extra_deck.

# TODO: Move scenes etc to another file. Create a standard file with the game loop etc.


class Deck:
    """
    A class representing a Yu-Gi-Oh! deck.

    Attributes:
        - name
        - cards: a list of card_ids representing the cards in the deck
        - image_id: the id of the deck cover image

    Methods:
        - __init__(name, cards, main_card_id): Initializes the deck object
        - get_image(): returns the image corresponding to the image_id attribute
    """

    def __init__(self, name="", cards=None, main_card_id=None):
        """

        Parameters
        ----------
        name
        cards
        main_card_id
        """
        if cards is None:
            self.cards = []
        else:
            self.cards = cards
        if main_card_id is None:
            main_card_id = cards[0]

        self.name = name
        self.image_id = game_engine.get_surface_manager().create_image(card_image_location + main_card_id + ".jpg")

    def get_image(self):
        """

        Returns
        -------
        The image corresponding to the image_id attribute
        """
        return game_engine.get_surface_manager().fetch_image(self.image_id)


class DeckManager:
    """A class to manage the current deck"""

    def __init__(self):
        """Initialises the deck."""
        self.deck = None

    def get_deck(self):
        """Returns the current selected deck."""
        return self.deck

    def set_deck(self, deck):
        """Sets the deck to a new deck"""
        self.deck = deck


class Card(assets.MobileButton):
    """A class representing cards."""

    def __init__(self, x=0, y=0, card_id="423585", parent=None):

        card_img_id = game_engine.get_surface_manager().create_image(card_image_location + f'{card_id}.jpg')
        card_image = game_engine.get_surface_manager().fetch_image(card_img_id)
        super().__init__(x=x, y=y, z=1, width=standard_card_width, height=standard_card_height, image=card_image,
                         name=card_id, static=False,
                         right_click_function=self.create_card_overlay)

        self.parent = parent

        self.card_type = self.get_card_type()

        self.location = None
        self.has_been_processed = False

    def get_card_type(self):
        image = game_engine.get_surface_manager().fetch_image(self.image_id)
        card_colors = {"normal": (200, 169, 105),
                       "effect": (196, 127, 86),
                       "spell": (42, 170, 155),
                       "trap": (182, 62, 133),
                       "ritual": (106, 141, 197),
                       "xyz": (56, 58, 47),
                       "synchro": (235, 234, 232),
                       "fusion": (150, 90, 162),
                       "link": (51, 105, 165),
                       "token": (145, 145, 145)}
        width_fraction = 0.05463182897
        height_fraction = 0.34853420195
        x = int(width_fraction * image.get_width())
        y = int(height_fraction * image.get_height())
        pixel_value = image.get_at((x, y))
        best_match = utils.closest_color(card_colors, pixel_value)
        return best_match

    def clamp_pos(self, rect):
        self.get_rect().clamp_ip(rect)
        x = utils.clamp(self.x, rect.x, rect.x + rect.width - self.width)
        y = utils.clamp(self.y, rect.y, rect.y + rect.height - self.height)
        self.set_pos(x, y)

    def set_rotation(self, angle):
        """Sets the rotation of the card. Only supports rotation with integer multiples of 90 degrees."""
        if self.rotation_angle == angle:
            return

        super().set_rotation(angle)
        self.update_card_overlay_anchor()

    def rotate(self, angle=90):
        if self.location != "field":
            return

        if self.get_rotation() == 0:
            self.set_rotation(90)
        else:
            self.set_rotation(0)

        scene = game_engine.get_scene_manager().get_current_scene()
        field_box = utils.find_object_from_name(scene.get_objects(), "field_box")
        if not self.moving and field_box is not None:
            self.clamp_pos(field_box)

    def update_in_hand(self):
        # TODO: Should all of this happen in the Board class?
        scene = game_engine.get_scene_manager().get_current_scene()
        board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
        if board is None or self not in board.hand:
            return
        hand_box = utils.find_object_from_name(scene.get_objects(), "hand_box")
        if hand_box is None:
            return
        in_hand = hand_box.get_rect().colliderect(self.get_rect())

        if not in_hand:
            board.move_to_field(self, board.hand)
            return

        if self.check_deck_collision(board, board.hand):
            return

    def update_on_field(self):
        scene = game_engine.get_scene_manager().get_current_scene()
        board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
        if board is None or self not in board.field:
            return

        hand_box = utils.find_object_from_name(scene.get_objects(), "hand_box")
        field_box = utils.find_object_from_name(scene.get_objects(), "field_box")
        if hand_box is None or field_box is None:
            return
        in_hand = hand_box.get_rect().colliderect(self.get_rect())

        if in_hand:
            board.add_to_hand(self, board.field)
            return

        if self.check_deck_collision(board, board.field):
            return
        if not self.moving:
            self.clamp_pos(field_box)

    def check_deck_collision(self, board, previous_location):
        scene = game_engine.get_scene_manager().get_current_scene()
        draw_btn = utils.find_object_from_name(scene.get_objects(), "draw_btn")
        extra_deck_btn = utils.find_object_from_name(scene.get_objects(), "show_extra_deck_btn")
        on_the_deck = draw_btn.get_rect().colliderect(self.get_rect())
        on_the_extra_deck = extra_deck_btn.get_rect().colliderect(self.get_rect())

        starting_location = utils.card_starting_location(self.card_type)

        if on_the_deck and not self.moving and starting_location == "main_deck":
            board.add_to_the_deck(self, previous_location)
            return True

        elif on_the_extra_deck and not self.moving and starting_location == "extra_deck":
            board.add_to_the_extra_deck(self, previous_location)
            return True
        return False

    def process(self):
        super().process()

        self.update_in_hand()
        self.update_on_field()
        self.has_been_processed = True

    def start_movement(self):
        card_overlay = utils.find_object_from_name(self.children, "card_overlay")
        if card_overlay is not None:
            card_overlay.destroy()
        board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
        if board is not None:
            board.bump(self)

        super().start_movement()

        self.make_large_card_button()

    def new_location(self, location=None):
        # TODO: Maybe add remove_from_display_order(self) instead.
        previous_location = self.location
        self.location = location
        self.set_rotation(0)
        self.remove_card_overlay()
        if location in ["hand", "field"]:
            self.set_alpha(255)
            if self.parent is not None:
                self.parent.cards.remove(self)  # TODO: Use a method here instead?
            self.set_parent(None)
            self.change_to_movable_card()
            if previous_location not in ["hand", "field"]:
                self.remove_large_card_button()

        elif location in ["main_deck", "extra_deck", "gy", "banished"]:
            if self.parent is not None:
                self.parent.cards.remove(self)  # TODO: Use a method here instead?
            self.remove_large_card_button()
            self.remove_card_overlay()
            self.set_alpha(255)

    def change_to_movable_card(self):
        self.set_left_click_function(self.start_movement)
        self.set_left_hold_function(self.move)
        self.set_size(standard_card_width, standard_card_height)
        self.set_z(1)

    def create_card_overlay(self):
        # TODO: Change names
        # TODO: This is too reliant on play_testing scene...
        # TODO: Fix positioning of the buttons.
        # TODO: Perhaps add functionality for the overlay class to "add" buttons, which gives them automatic placement,
        #  if no placement is specified.

        card_overlay = utils.find_object_from_name(self.children, "card_overlay")

        if card_overlay is not None:
            return

        if self.get_rotation() == 0:
            overlay_width = self.width
            overlay_height = int(overlay_width * card_aspect_ratio)
        else:
            overlay_width = self.height
            overlay_height = int(overlay_width * card_aspect_ratio)

        button_space = 5
        overlay_close_button_size = 15
        number_of_buttons = 4
        total_height = overlay_height - button_space * (2 + number_of_buttons) - overlay_close_button_size
        button_height = total_height // number_of_buttons
        button_width = overlay_width - 2 * button_space

        overlay = assets.Overlay(x=self.x + self.width, y=self.y, z=self.z, width=overlay_width, height=overlay_height,
                                 name="card_overlay",
                                 close_btn_size=overlay_close_button_size, parent=self, static=False,
                                 external_process_function=utils.destroy_on_external_clicks)
        overlay.external_process_arguments = [overlay, [overlay.get_rect(), self.get_rect()]]
        self.add_child(overlay)
        board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
        board.bump(self)
        starting_location = utils.card_starting_location(self.card_type)
        card_location = board.get_location(self)

        large_card_btn = utils.find_object_from_name(self.children, "large_card_btn")
        if large_card_btn is None:
            large_card_btn = self.make_large_card_button()

        [large_card_btn_arg, large_card_btn_allowed_rect_list] = large_card_btn.get_external_process_arguments()
        large_card_btn_allowed_rect_list.append(overlay.get_rect())
        large_card_btn.set_external_process_arguments([large_card_btn_arg, large_card_btn_allowed_rect_list])

        remove_btn_height = int(overlay_height - button_space * 4 - overlay_close_button_size)
        remove_btn = assets.Button(width=button_width, height=remove_btn_height, text="Remove", font_size=15,
                                   parent=overlay, name="token_remove_btn",
                                   left_click_function=self.destroy, left_trigger_keys=["g", "b", "d"])

        gy_btn = assets.Button(width=button_width, height=button_height, text="Graveyard", name="gy_btn", font_size=15,
                               parent=overlay, left_trigger_keys=["g"], left_click_function=board.send_to_gy,
                               left_click_args=[self, card_location])

        banish_btn = assets.Button(width=button_width,
                                   height=button_height, text="Banish", font_size=15, name="banish_btn",
                                   parent=overlay,
                                   left_trigger_keys=["b"], left_click_function=board.banish,
                                   left_click_args=[self, card_location])

        hand_btn = assets.Button(width=button_width,
                                 height=button_height, font_size=15, text="Hand", name="hand_btn",
                                 parent=overlay,
                                 left_trigger_keys=["h"], left_click_function=board.add_to_hand,
                                 left_click_args=[self, card_location])

        field_btn = assets.Button(width=button_width,
                                  height=button_height, font_size=15, text="Field", name="field_btn",
                                  parent=overlay,
                                  left_trigger_keys=["f"], left_click_function=board.move_to_field,
                                  left_click_args=[self, card_location])

        main_deck_btn = assets.Button(width=button_width,
                                      height=button_height, font_size=15, text="Deck", name="send_to_deck_btn",
                                      parent=overlay,
                                      left_trigger_keys=["d"], left_click_function=board.add_to_the_deck,
                                      left_click_args=[self, card_location])

        extra_deck_btn = assets.Button(width=button_width, height=button_height, font_size=15, text="Extra Deck",
                                       name="send_to_extra_deck_btn", parent=overlay,
                                       left_trigger_keys=["d"], left_click_function=board.add_to_the_extra_deck,
                                       left_click_args=[self, card_location])

        if self.card_type == "token":
            location_button_dict = {
                "": remove_btn
            }

        elif starting_location == "extra_deck":
            location_button_dict = {
                "extra_deck": extra_deck_btn,
                "gy": gy_btn,
                "banished": banish_btn,
                "field": field_btn,
            }
        else:
            location_button_dict = {
                "main_deck": main_deck_btn,
                "gy": gy_btn,
                "banished": banish_btn,
                "field": field_btn,
                "hand": hand_btn
            }

        location_buttons = []
        for location in location_button_dict:
            if location != self.location:
                location_buttons.append(location_button_dict[location])

        y = overlay_close_button_size + 2 * button_space
        location_button_space = sum([button.height + button_space for button in location_buttons])
        close_button_space = 2 * button_space + overlay_close_button_size
        used_space = location_button_space + close_button_space
        extra_height = overlay.height - used_space
        extra_button_height = extra_height // len(location_buttons)
        for btn in location_buttons:
            btn.set_pos_relative_to_parent(button_space, y)
            btn.set_z(overlay.z)
            btn.set_height_relative(extra_button_height)
            y += btn.height + button_space

        overlay.add_multiple_children(location_buttons)

    def remove_card_overlay(self):
        card_overlay = utils.find_object_from_name(self.children, "card_overlay")
        if card_overlay is None:
            return
        card_overlay.destroy()

    def update_card_overlay_anchor(self):
        card_overlay = utils.find_object_from_name(self.children, "card_overlay")
        if card_overlay is not None:
            card_overlay.set_pos_relative_to_parent(self.width, 0)

    def make_large_card_button(self):
        large_card_btn = utils.find_object_from_name(self.children, "large_card_btn")
        if large_card_btn is not None:
            return

        scene = game_engine.get_scene_manager().get_current_scene()
        left_side_box = utils.find_object_from_name(scene.get_objects(), "left_side_box")
        if left_side_box is None:
            return
        large_card_offset = (left_side_box.width - large_card_width) // 2

        large_card_btn = assets.Button(x=left_side_box.x + large_card_offset, y=left_side_box.y + large_card_offset,
                                       z=self.z-0.1,
                                       width=large_card_width,
                                       height=int(large_card_width * card_aspect_ratio),
                                       image=game_engine.get_surface_manager().fetch_image(self.source_image_id),
                                       name="large_card_btn",
                                       left_click_function=create_large_card_overlay, left_click_args=[self],
                                       key_functions={"r": [self.rotate, []]})

        large_card_btn.set_require_continuous_hovering(False)
        large_card_btn.set_external_process_function(utils.destroy_on_external_clicks)
        large_card_btn.static = True
        allowed_rect_list = [self.get_rect(), large_card_btn.get_rect()]
        card_overlay = utils.find_object_from_name(self.children, "card_overlay")
        if card_overlay is not None:
            allowed_rect_list.append(card_overlay.get_rect())
        large_card_btn.set_external_process_arguments([large_card_btn, allowed_rect_list])

        self.add_child(large_card_btn)
        return large_card_btn

    def remove_large_card_button(self):
        large_card_btn = utils.find_object_from_name(self.children, "large_card_btn")
        if large_card_btn is None:
            return
        large_card_btn.destroy()


class CardOverlay(assets.Overlay):
    def __init__(self, x=0, y=0, z=2, width=1540, height=760, alpha=255, static=True, name=None, background_color=WHITE,
                 close_btn_size=30, close_btn_offset=5, parent=None, external_process_function=None,
                 external_process_arguments=None, card_list_function=None):
        super().__init__(x=x, y=y, z=z, width=width, height=height, alpha=alpha, static=static, name=name,
                         background_color=background_color, close_btn_size=close_btn_size,
                         close_btn_offset=close_btn_offset, parent=parent,
                         external_process_function=external_process_function,
                         external_process_arguments=external_process_arguments)

        self.card_list_function = card_list_function

        self.cards_per_row = 7
        self.number_of_rows = 4
        self.start_index = 0
        self.stop_index = self.start_index + self.cards_per_row * self.number_of_rows - 1

        self.card_list = self.card_list_function()
        self.cards = []
        for i, card in enumerate(self.card_list):
            self.set_overlay_card(self.create_overlay_card(card, i), i)

    def create_overlay_card(self, card, i):
        card.set_parent(self)
        x, y, card_width, card_height = self.get_card_info(i)
        card.set_pos(x, y)
        card.set_z(self.z)
        card.set_size(card_width, card_height)
        card.set_left_click_function(card.make_large_card_button)
        card.set_left_hold_function(None)
        return card

    def set_overlay_card(self, card, i):
        if i == len(self.cards):
            self.cards.append(card)
        elif i < len(self.cards):
            self.cards[i] = card
        else:
            raise IndexError("Cannot set self.cards[i] to card, to few cards in the list")

    def update_card_list(self):
        for i, card in enumerate(self.card_list):
            if card not in self.cards:
                self.set_overlay_card(self.create_overlay_card(card, i), i)
            else:
                self.set_overlay_card(card, i)

    def update_card_positions(self):
        for i, card in enumerate(self.cards[self.start_index:self.stop_index + 1]):
            x, y, _, _ = self.get_card_info(i)
            card.set_pos(x=x, y=y)

    def get_card_info(self, i):
        max_cards_to_show = self.cards_per_row * self.number_of_rows
        min_x_offset = 10
        min_y_offset = 10
        card_space = 5
        aspect_ratio = card_aspect_ratio

        card_width = int(
            min((self.get_box().height - 2 * min_y_offset - (math.ceil(max_cards_to_show / self.cards_per_row) - 1)
                 * card_space) / (math.ceil(max_cards_to_show / self.cards_per_row) * aspect_ratio),
                (self.get_box().width - 2 * min_x_offset - (self.cards_per_row - 1) * card_space)
                / self.cards_per_row))

        card_height = int(aspect_ratio * card_width)

        x_offset = int(
            (self.get_box().width - (self.cards_per_row - 1) * card_space - self.cards_per_row * card_width) / 2)

        y_offset = int((self.get_box().height - math.ceil(max_cards_to_show / self.cards_per_row - 1) * card_space
                        - math.ceil(max_cards_to_show / self.cards_per_row) * card_height) / 2)

        x = self.get_box().x + x_offset + int(i % self.cards_per_row * (card_space + card_width))
        y = self.get_box().y + y_offset + int(i // self.cards_per_row * (card_space + card_height))
        return x, y, card_width, card_height

    def schedule_processing(self):
        self.pre_process()
        items_to_be_processed = [self]
        items_to_be_processed.extend(self.get_box().schedule_processing())
        for btn in self.get_buttons():
            items_to_be_processed.extend(btn.schedule_processing())

        for j, card in enumerate(reversed(self.cards.copy())):
            i = len(self.cards) - 1 - j
            if i < self.start_index or i > self.stop_index:
                continue
            items_to_be_processed.extend(card.schedule_processing())

        return items_to_be_processed

    def process(self):
        self.card_list = self.card_list_function()

        for i, card in enumerate(self.card_list[self.start_index:self.stop_index + 1]):
            x, y, _, _ = self.get_card_info(i)
            card.set_pos(x, y)
            if not card.has_been_processed:
                items_to_be_processed = card.schedule_processing()
                game_engine.get_scene_manager().get_current_scene().process_given_objects(items_to_be_processed)

    def pre_process(self):
        self.card_list = self.card_list_function()

        self.stop_index = self.start_index + self.cards_per_row * self.number_of_rows - 1

        self.update_card_list()

        self.update_card_positions()

    def get_displayable_objects(self):
        displayable_objects = []

        if self.destroyed:
            return displayable_objects

        displayable_objects.extend(super().get_displayable_objects())

        self.stop_index = self.start_index + self.cards_per_row * self.number_of_rows - 1

        self.update_card_list()

        self.update_card_positions()

        for j, card in enumerate(reversed(self.cards)):
            i = len(self.cards) - 1 - j
            if self.start_index <= i <= self.stop_index:
                displayable_objects.extend(card.get_displayable_objects())

        return displayable_objects


class LargeCardOverlay(assets.Overlay):
    def __init__(self, x=0, y=0, z=0, width=1540, height=760, alpha=255, name=None, background_color=WHITE,
                 close_btn_size=30, close_btn_offset=5, parent=None, card=None,
                 external_process_function=None, external_process_arguments=None):
        super().__init__(x=x, y=y, z=z, width=width, height=height, alpha=alpha, name=name,
                         background_color=background_color,
                         close_btn_size=close_btn_size, close_btn_offset=close_btn_offset, parent=parent,
                         external_process_function=external_process_function,
                         external_process_arguments=external_process_arguments)
        self.card = card

    def destroy(self):
        large_card_btn = utils.find_object_from_name(self.card.children, "large_card_btn")
        allowed_rects = large_card_btn.get_external_process_arguments()
        allowed_rects[1].remove(self.get_rect())
        large_card_btn.set_external_process_arguments(allowed_rects)
        super().destroy()


class Board:
    def __init__(self, card_ids=None, name="", scene=None):
        self.z = 2
        if card_ids is None:
            card_ids = []

        self.deck = []
        self.extra_deck = []
        for card_id in card_ids:
            new_card = Card(card_id=card_id, parent=None)
            card_start_location = utils.card_starting_location(new_card.card_type)
            new_card.location = card_start_location
            if card_start_location == "main_deck":
                self.deck.append(new_card)
            else:
                self.extra_deck.append(new_card)

        utils.card_sort_card_type(self.extra_deck)

        random.shuffle(self.deck)
        self.hand = []
        self.gy = []
        self.banished = []
        self.field = []
        self.card_processing_order = []
        self.name = name
        self.scene = scene
        card_space = 10  # TODO: This is hard-coded.
        if self.scene.name == "play_testing":
            scene_objects = self.scene.get_objects()
            hand_box_width = utils.find_object_from_name(scene_objects, "hand_box").width
            self.display_hand_number = hand_box_width // (constants.standard_card_width + card_space)
        else:
            self.display_hand_number = 10
        self.display_hand_start_index = 0

        self.old_hand = [card.x for card in self.hand]

    def set_display_hand_start_index(self, new_index):
        max_display_index = utils.clamp(len(self.hand) - self.display_hand_number, 0, len(self.hand))
        self.display_hand_start_index = utils.clamp(new_index, 0, max_display_index)

    def set_display_hand_start_index_relative(self, index_change):
        self.set_display_hand_start_index(self.display_hand_start_index + index_change)

    def get_location(self, card):
        location_list = [self.hand, self.field, self.gy, self.banished, self.deck, self.extra_deck]
        for location in location_list:
            for comparison_card in location:
                if card == comparison_card:
                    return location

        return None

    def get_card_in_hand_pos(self, card, card_index=None):
        if card_index is None:
            card_index = self.hand.index(card)

        card_width = self.hand[0].width
        hand_box = utils.find_object_from_name(self.scene.get_objects(), "hand_box")
        y_offset = (hand_box.get_rect().height - card.get_rect().height) // 2
        card_space = 10

        cards_to_the_left_width = (card_width + card_space) * (card_index - self.display_hand_start_index)

        all_cards_in_hand_width = self.display_hand_number * (card_width + card_space)

        x_offset = (hand_box.width - all_cards_in_hand_width) // 2
        x = hand_box.x + x_offset + cards_to_the_left_width
        y = hand_box.y + y_offset

        return x, y

    def shuffle_the_deck(self):
        random.shuffle(self.deck)

    def draw(self):
        if len(self.deck) == 0:
            return
        drawn_card = self.deck[0]
        self.add_to_hand(drawn_card, self.deck)

    def send_to_gy(self, card, previous_location):
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        card.new_location(location="gy")
        self.stop_processing(card)
        self.gy.insert(0, card)
        previous_location.remove(card)

    def banish(self, card, previous_location):
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        card.new_location(location="banished")
        self.stop_processing(card)
        self.banished.insert(0, card)
        previous_location.remove(card)

    def add_to_the_deck(self, card, previous_location):
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        self.stop_processing(card)
        card.new_location(location="main_deck")
        self.deck.insert(0, card)
        card.moving = False
        previous_location.remove(card)

    def add_to_the_extra_deck(self, card, previous_location):
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        self.stop_processing(card)
        card.new_location(location="extra_deck")
        self.extra_deck.insert(0, card)

        card.moving = False
        previous_location.remove(card)

    def add_to_hand(self, card, previous_location):
        if card not in previous_location:
            raise IndexError("Card not found in previous location")

        card.new_location(location="hand")
        self.hand.append(card)
        if not card.moving:
            x, y = self.get_card_in_hand_pos(card)
            card.set_pos(x, y)

        previous_location.remove(card)

    def move_to_field(self, card, previous_location):
        """Moves a card to the field."""
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        if card.location != "hand":
            default_x, default_y = game_engine.get_scene_manager().get_current_scene().get_default_position()
            card.set_pos(default_x, default_y)
        card.new_location(location="field")
        self.field.append(card)
        self.begin_processing(card)
        if not card.moving:
            x, y = game_engine.get_scene_manager().get_current_scene().get_default_position()
            card.set_pos(x, y)
        previous_location.remove(card)

    def bump(self, card):
        if card not in self.card_processing_order:
            return
        self.card_processing_order.remove(card)
        self.card_processing_order.append(card)

    def remove_card(self, card):
        card_location = self.get_location(card)
        if card_location is None:
            return
        card_location.remove(card)
        self.stop_processing(card)

    def begin_processing(self, card):
        if card not in self.card_processing_order:
            self.card_processing_order.append(card)

    def stop_processing(self, card):
        if card in self.card_processing_order:
            self.card_processing_order.remove(card)

    def schedule_processing(self):
        for i, card in enumerate(self.hand):
            if card.moving:
                continue
            display_stop_index = self.display_hand_start_index + self.display_hand_number
            is_visible_in_hand = self.display_hand_start_index <= i < display_stop_index
            x, y = self.get_card_in_hand_pos(card, i)
            card.set_pos(x, y)
            if is_visible_in_hand:
                self.begin_processing(card)
            else:
                self.stop_processing(card)

        items_to_be_processed = [self]
        moving_card = None
        for card in self.card_processing_order:
            if card.moving:
                moving_card = card
                continue
            items_to_be_processed.extend(card.schedule_processing())
        if moving_card is not None:
            items_to_be_processed.extend(moving_card.schedule_processing())
        return items_to_be_processed

    def process(self):
        for j in range(len(self.hand)):
            for i in range(len(self.hand) - 1):
                if self.hand[i].x > self.hand[i + 1].x:
                    self.hand[i], self.hand[i + 1] = self.hand[i + 1], self.hand[i]

        all_cards = []
        all_cards.extend(self.hand)
        all_cards.extend(self.field)
        all_cards.extend(self.deck)
        all_cards.extend(self.extra_deck)
        all_cards.extend(self.gy)
        all_cards.extend(self.banished)

        for card in all_cards:
            card.has_been_processed = False

    def destroy_child(self, child):
        self.remove_card(child)

    def get_displayable_objects(self):
        displayable_objects = []
        for card in self.card_processing_order:
            if card in self.field:
                displayable_objects.extend(card.get_displayable_objects())

        for i, card in enumerate(self.hand):
            if card.moving:
                continue
            x, y = self.get_card_in_hand_pos(card, i)
            card.set_pos(x, y)

        visible_hand = self.hand[self.display_hand_start_index:self.display_hand_start_index + self.display_hand_number]
        moving_card = None
        for card in reversed(visible_hand):
            if card.moving:
                moving_card = card
                continue
            displayable_objects.extend(card.get_displayable_objects())

        if moving_card is not None:
            displayable_objects.extend(moving_card.get_displayable_objects())

        return displayable_objects


def generate_board(scene):
    """Generates a game board for the specified scene.

    Args:
        scene: The scene to which the board will be added.

    Returns:
        Board: The newly generated game board.
    """
    existing_board = utils.find_object_from_name(scene.get_objects(), "board")
    if existing_board is not None:
        scene.remove_object(existing_board)

    board = Board(card_ids=deck_manager.get_deck().cards, name="board", scene=scene)
    scene.add_object(board)
    return board


def cards_in_deck_string(scene=None):
    """Generates a string indicating the number of cards in the deck for the specified scene.

    Args:
        scene: The scene containing the board with the deck (default is the current scene).

    Returns:
        str: A string in the format "Cards: {number_of_cards}".
    """
    if scene is None:
        scene = game_engine.get_scene_manager().get_current_scene()
    board = utils.find_object_from_name(scene.get_objects(), "board")
    return f"Cards: {len(board.deck)}"


def choose_deck(deck):
    """Chooses a deck for playtesting.

    Sets the specified deck as the active deck using the deck manager and schedules a scene change to the playtesting
    scene.

    Args:
        deck: The deck to be set as the active deck for playtesting.
    """
    deck_manager.set_deck(deck)
    game_engine.schedule_scene_change(create_play_testing, scene_name="play_testing")


def change_overlay_limits(overlay, change_in_limits):
    """Changes the start index of an overlay within specified limits.

    Args:
        overlay: The overlay object whose start index needs to be modified.
        change_in_limits (int): The change in start index. A positive value moves forward, and a negative value moves
        backward.
    """
    new_start_index = overlay.start_index + change_in_limits
    if new_start_index + (overlay.number_of_rows - 1) * overlay.cards_per_row + 1 > len(overlay.card_list):
        return

    elif new_start_index < 0:
        overlay.start_index = 0

    else:
        overlay.start_index += change_in_limits


def create_main_menu():
    """Creates the main menu scene.

    Returns:
        Scene: The main menu scene containing buttons for starting, loading, testing, and exiting the game.
    """
    scene = Scene(name="main_menu")
    scene.persistent = True
    scene.background_color = WHITE
    width = 200
    height = 100

    start_btn = assets.Button(y=environment.get_height() // 2, width=width,
                              height=height, text="Start",
                              left_click_function=game_engine.schedule_scene_change,
                              left_click_args=[create_deck_selection_scene, "deck_selection"])

    load_btn = assets.Button(y=environment.get_height() // 2, width=width,
                             height=height, text="Load Save", left_click_function=game_engine.load)

    test_btn = assets.Button(y=environment.get_height() // 2, width=width, height=height,
                             text="Testing", font_size=35,
                             left_click_function=game_engine.schedule_scene_change,
                             left_click_args=[create_test_scene, "test_scene"])

    exit_btn = assets.Button(y=environment.get_height() // 2, width=width,
                             height=height, text="Exit", left_click_function=sys.exit)

    buttons = [start_btn, load_btn, test_btn, exit_btn]
    number_of_buttons = len(buttons)
    x_offset = (environment.get_width() - number_of_buttons * width) // (number_of_buttons + 1)
    for i, btn in enumerate(buttons):
        btn.set_pos((i + 1) * x_offset + i * width, btn.y)
        btn.set_z(1)
        scene.add_object(btn)

    return scene


def create_test_scene():
    """Creates a test scene for testing different functionality.

    Returns:
        Scene: The test scene.
    """
    scene = Scene(name="test_scene")
    scene.background_color = SIENNA
    exit_btn = assets.Button(text="Main Menu", alpha=255,
                             left_click_function=game_engine.schedule_scene_change,
                             left_click_args=[create_main_menu, "main_menu"])
    scene.add_object(exit_btn)
    button = assets.Button(x=500, y=500, width=200, height=100, text="Create confirmation overlay",
                           left_click_function=create_confirmation_overlay,
                           left_click_args=[(700, 700), test_button, []],
                           colors={"normal": SADDLE_BROWN, "hover": SIENNA, "pressed": BLACK}, alpha=175)
    button.hug_text(15)
    movable_btn = assets.MobileButton(x=100, y=100, z=1, name="mobile_btn")

    follow_mobile = assets.MobileButton(x=200, y=125, z=1, parent=movable_btn, static=False, name="follow_mobile")

    movable_btn.add_child(follow_mobile)

    scene.add_object(movable_btn)
    scene.add_object(button)
    return scene


def create_play_testing():
    """Creates a playtesting scene for playtesting a Yu-Gi-Oh! deck.

    Returns:
        Scene: The playtesting scene.
    """
    scene = Scene(name="play_testing")

    scene.background_color = GREY

    button_width = 200
    button_height = 100
    deck_width = button_width
    deck_height = int(button_width * card_aspect_ratio)
    offset = 15
    side_width = max(button_width, deck_width) + 2 * offset
    card_height = standard_card_width * card_aspect_ratio

    left_side_box = assets.Box(x=0, y=0, width=large_card_width + 2 * offset,
                               height=environment.get_height(), color=GREY, name="left_side_box")

    right_side_box = assets.Box(x=environment.get_width() - side_width, width=side_width,
                                height=environment.get_height(),
                                color=GREY,
                                name="right_side_box")

    field_box = assets.Box(x=left_side_box.x + left_side_box.width,
                           width=environment.get_width() - left_side_box.width - right_side_box.width,
                           height=environment.get_height() - int(card_height) - offset, color=SADDLE_BROWN,
                           name="field_box")

    hand_box = assets.Box(x=left_side_box.width + button_width, y=environment.get_height() - int(card_height) - offset,
                          width=environment.get_width() - left_side_box.width - right_side_box.width - 2 * button_width,
                          height=int(card_height) + offset, color=GREY, name="hand_box")

    hand_border = assets.Border(x=hand_box.x, y=hand_box.y, width=hand_box.width, height=hand_box.height,
                                parent=hand_box)

    scene.add_multiple_objects([field_box, hand_box, left_side_box, right_side_box])
    scene.add_object(hand_border)
    board = generate_board(scene)

    draw_btn = assets.Button(x=environment.get_width() - button_width - offset,
                             y=environment.get_height() - deck_height - offset,
                             width=deck_width, height=deck_height, image=pygame.image.load("Images/card_back.png"),
                             name="draw_btn", left_click_function=board.draw)

    deck_text_box = assets.Box(text=cards_in_deck_string(scene), font_size=25, color=LIGHT_GREY,
                               update_text_func=cards_in_deck_string)
    deck_text_box.hug_text(5)

    deck_text_box.set_pos(x=right_side_box.x + (right_side_box.width - deck_text_box.width) // 2,
                          y=draw_btn.y - deck_text_box.height - offset)

    show_deck_btn = assets.Button(x=draw_btn.x, y=deck_text_box.y - button_height - offset, width=button_width // 2,
                                  height=button_height, image=pygame.image.load("Images/millennium_eye.png"),
                                  name="show_deck_btn", left_click_function=create_deck_overlay)

    show_extra_deck_btn = assets.Button(x=left_side_box.x + offset, y=environment.get_height() - deck_height - offset,
                                        width=deck_width, height=deck_height,
                                        image=pygame.image.load("Images/card_back.png"),
                                        name="show_extra_deck_btn", left_click_function=create_extra_deck_overlay)

    shuffle_deck_btn = assets.Button(x=draw_btn.x + button_width // 2, y=deck_text_box.y - button_height - offset,
                                     width=button_width // 2, height=button_height,
                                     image=pygame.image.load("Images/shuffle.png"), name="shuffle_deck_btn",
                                     left_click_function=board.shuffle_the_deck)

    show_gy_btn = assets.Button(x=draw_btn.x, y=deck_text_box.y - 2 * button_height - offset, width=button_width // 2,
                                height=button_height, image=pygame.image.load("Images/gy_icon.png"),
                                name="show_gy_btn", left_click_function=create_gy_overlay)

    show_banished_btn = assets.Button(x=draw_btn.x + button_width // 2, y=deck_text_box.y - 2 * button_height - offset,
                                      width=button_width // 2,
                                      height=button_height, image=pygame.image.load("Images/banished_icon.png"),
                                      name="show_banished_btn", left_click_function=create_banished_overlay)

    main_menu_btn = assets.Button(x=draw_btn.x, y=offset, width=button_width, height=button_height,
                                  text="Main Menu", name="main_menu_btn",
                                  left_click_function=game_engine.schedule_scene_change,
                                  left_click_args=[create_main_menu, "main_menu"])

    save_btn = assets.Button(x=main_menu_btn.x, y=main_menu_btn.y + main_menu_btn.height + offset,
                             text="SAVE", name="save_btn",
                             left_click_function=game_engine.schedule_end_of_tick_function,
                             left_click_args=[game_engine.save, []])

    """assets.Button(x=main_menu_btn.x, y=main_menu_btn.y + main_menu_btn.height + offset,
                              text="Reset", name="reset_btn", 
                              left_click_function=game_engine.schedule_scene_change,
                              left_click_args=[create_play_testing])"""

    token_btn = assets.Button(x=show_extra_deck_btn.x, y=show_extra_deck_btn.y - offset - button_height,
                              width=button_width,
                              height=button_height,
                              text="Token", name="token_btn", left_click_function=generate_token)

    # hand_overlay_button = assets.Button(text="Show hand", name="hand_overlay_btn",
    # left_click_function=create_hand_overlay)
    small_button_size = 50

    hand_index_button_offset = int((hand_box.height - button_height / 2) // 2)
    hand_index_increment_btn = assets.Button(x=hand_box.x + hand_box.width + offset,
                                             y=hand_box.y + hand_index_button_offset,
                                             height=small_button_size,
                                             width=small_button_size, text="+", font_size=35,
                                             name="index_increment_btn",
                                             left_click_function=board.set_display_hand_start_index_relative,
                                             left_click_args=[board.display_hand_number])
    hand_index_decrement_btn = assets.Button(x=hand_box.x - small_button_size - 2 * offset,
                                             y=hand_box.y + hand_index_button_offset,
                                             height=small_button_size, width=small_button_size, text="-",
                                             font_size=35,
                                             name="index_decrement_btn",
                                             left_click_function=board.set_display_hand_start_index_relative,
                                             left_click_args=[-board.display_hand_number])

    scene.add_multiple_objects([main_menu_btn, draw_btn, show_deck_btn, save_btn, shuffle_deck_btn, show_extra_deck_btn,
                                show_gy_btn, show_banished_btn, token_btn, hand_index_increment_btn,
                                hand_index_decrement_btn])

    scene.add_multiple_objects([deck_text_box])

    for _ in range(5):
        board.draw()

    return scene


def create_large_card_overlay(card):
    """Creates a large card overlay for displaying a larger version of the card image for better readability.

    Args:
        card (Card): The card for which the overlay is created.
    """
    scene = game_engine.get_scene_manager().get_current_scene()
    large_card_overlay = utils.find_object_from_name(scene.get_objects(), "large_card_overlay")
    if large_card_overlay is not None:
        return
    field_box = utils.find_object_from_name(scene.get_objects(), "field_box")
    large_card_btn = utils.find_object_from_name(card.children, "large_card_btn")
    dummy_overlay = assets.Overlay()
    close_btn_size = dummy_overlay.close_btn_size
    close_btn_offset = dummy_overlay.close_btn_offset

    height = field_box.height
    width = int((height - close_btn_size - close_btn_offset) / card_aspect_ratio)

    overlay = LargeCardOverlay(x=field_box.x, y=field_box.y, z=2, width=width, height=height, name="large_card_overlay",
                               card=card)
    # overlay.set_parent(scene)
    close_btn = utils.find_object_from_name(overlay.get_buttons(), "close_btn")
    offset = 15

    card_height = overlay.height - 3 * offset - close_btn.height
    card_width = int(card_height / card_aspect_ratio)

    large_card_box = assets.Box(x=overlay.x + offset,
                                y=close_btn.y + offset + close_btn.height,
                                z=overlay.z,
                                width=card_width,
                                height=card_height,
                                source_image=game_engine.get_surface_manager().fetch_image(card.source_image_id))
    large_card_box.set_parent(overlay)

    allowed_rect_list = [overlay.get_box().get_rect(), large_card_btn.get_rect()]
    overlay.external_process_function = utils.destroy_on_external_clicks
    overlay.external_process_arguments = [overlay, allowed_rect_list]

    large_card_btn.external_process_arguments[1].append(overlay.get_rect())

    overlay.add_child(large_card_box)

    scene.add_object(overlay)


def create_deck_selection_scene():
    """Creates a scene for deck selection.

    Returns:
        Scene: The scene with deck selection options.
    """
    scene = Scene(name="deck_selection")

    deck_selection_overlay = assets.Overlay(z=1, width=environment.get_width(), height=environment.get_height(),
                                            background_color=WHITE)

    close_btn = utils.find_object_from_name(deck_selection_overlay.get_buttons(), "close_btn")
    deck_selection_overlay.destroy_child(close_btn)

    for i, deck in enumerate(DECKS):
        deck_btn = assets.Button(text=deck.name, x=i * large_card_width, y=500, z=1, width=large_card_width,
                                 height=large_card_height,
                                 left_click_function=create_confirmation_overlay,
                                 left_click_args=[(i * large_card_width, 500), choose_deck, [deck]])
        deck_btn.set_image(deck.get_image())
        deck_selection_overlay.add_child(deck_btn)

    # deck_selection_overlay.parent = scene
    scene.add_object(deck_selection_overlay)
    return scene


def cards_in_deck():
    """Gets the cards in the current game board's deck.

    Returns:
        list: A list of the cards in the deck.
    """
    board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
    return board.deck


def cards_in_extra_deck():
    """Gets the cards in the current game board's extra deck.

    Returns:
        list: A list of the cards in the extra deck.
    """
    board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
    return board.extra_deck


def cards_in_gy():
    """Gets the cards in the current game board's graveyard.

    Returns:
        list: A list of the cards in the graveyard.
    """
    board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
    return board.gy


def cards_in_banished():
    """Gets the cards that are currently banished.

    Returns:
        list: A list of the cards that are banished.
    """
    board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
    return board.banished


def cards_in_hand():
    """Gets the cards in the hand.

    Returns:
        list: A list of the cards in the hand .
    """
    board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
    return board.hand


def generate_token():
    """Generates a token card and adds it to the game board."""
    scene = game_engine.get_scene_manager().get_current_scene()
    board = utils.find_object_from_name(scene.get_objects(), "board")

    token = Card(card_id="token", parent=board)
    token.static = True
    x, y = scene.get_default_position()  # TODO: Change this to something else?
    token.set_pos(x, y)
    token.location = "field"
    board.field.append(token)
    board.card_processing_order.append(token)  # TODO: Perhaps add a method in class Board for the adding of cards.


def create_deck_overlay():
    """Creates an overlay displaying cards in the main deck."""
    create_location_overlay("main_deck", cards_in_deck)


def create_extra_deck_overlay():
    """Creates an overlay displaying cards in the extra deck."""
    create_location_overlay("extra_deck", cards_in_extra_deck)


def create_gy_overlay():
    """Creates an overlay displaying cards in the graveyard."""
    create_location_overlay("gy", cards_in_gy)


def create_banished_overlay():
    """Creates an overlay displaying cards that are banished."""
    create_location_overlay("banished", cards_in_banished)


def create_hand_overlay():
    """Creates an overlay displaying cards in the hand.

    Does not currently work, since it moves the cards in the hand.
    """
    create_location_overlay("hand", cards_in_hand)


def test_button():
    """Prints a test message with the current time.

    This function serves as a test button action. It prints a message indicating the execution of the button test
    along with the current timestamp.
    """
    print("BUTTON TEST AT TIME:", time.time())


def create_location_overlay(location_name, card_list_function):
    """Create an overlay displaying cards from a specific location in the game.

    Args:
        location_name (str): The name of the location to display.
        card_list_function (callable): A function returning the list of cards to be displayed.
    """
    scene = game_engine.get_scene_manager().get_current_scene()
    while True:
        same_location_overlay = utils.find_object_from_name(scene.get_objects(), location_name)
        overlays = [obj for obj in scene.get_objects() if isinstance(obj, CardOverlay) and not obj.destroyed]
        number_of_overlays = len(overlays)
        if number_of_overlays == 0:
            break

        for overlay_to_remove in overlays:
            overlay_to_remove.destroy()

        if same_location_overlay is not None:
            return

    field_box = utils.find_object_from_name(scene.get_objects(), "field_box")
    x_offset = 10
    y_offset = 10
    overlay_width = field_box.width - 2 * x_offset
    overlay_height = field_box.height - 2 * y_offset
    overlay = CardOverlay(x=field_box.x + x_offset, y=field_box.y + y_offset, z=2, width=overlay_width,
                          height=overlay_height, alpha=180, name=location_name, card_list_function=card_list_function)
    small_button_width = 50
    small_button_height = small_button_width

    close_btn = utils.find_object_from_name(overlay.get_buttons(), "close_btn")
    scroll_up_btn = assets.Button(x=overlay.x + overlay_width - small_button_width - x_offset,
                                  y=overlay.y + 2 * y_offset + close_btn.height,
                                  z=overlay.z,
                                  width=small_button_width, height=small_button_height,
                                  image=pygame.image.load("Images/up_arrow.png"), name="scroll_up_btn",
                                  left_trigger_keys=["up"],
                                  left_click_function=change_overlay_limits,
                                  left_click_args=[overlay, -overlay.cards_per_row])

    scroll_down_btn = assets.Button(x=overlay.x + overlay_width - small_button_width - x_offset,
                                    y=overlay.y + overlay_height - small_button_height - y_offset,
                                    z=overlay.z,
                                    width=small_button_width, height=small_button_height,
                                    image=pygame.image.load("Images/down_arrow.png"), name="scroll_down_btn",
                                    left_trigger_keys=["down"],
                                    left_click_function=change_overlay_limits,
                                    left_click_args=[overlay, overlay.cards_per_row])

    overlay.add_multiple_children([scroll_up_btn, scroll_down_btn])
    scene.add_object(overlay)


def create_confirmation_overlay(position, func, args):
    """Create a confirmation overlay with Yes and No buttons.

     Args:
         position (tuple): The (x, y) position to place the overlay.
         func (callable): The function to execute if the "Yes" button is clicked.
         args (list): The arguments to pass to the function.
     """
    # TODO: Make this into a sub-class of Overlay?
    scene_objects = game_engine.get_scene_manager().get_current_scene().get_objects()
    scene_overlays = utils.find_objects_from_type(scene_objects, assets.Overlay)
    existing_confirmation_overlay = utils.find_object_from_name(scene_overlays, "confirmation_overlay")
    if existing_confirmation_overlay is not None:
        return
    # TODO: Perhaps remove the above.
    x, y = position
    overlay_z = 10
    overlay = assets.Overlay(x=x, y=y, z=overlay_z, width=300, height=150, name="confirmation_overlay",
                             external_process_function=utils.destroy_on_external_clicks)  # ,
    # parent=game_engine.get_scene_manager().get_current_scene())
    # overlay.set_parent(game_engine.get_scene_manager().get_current_scene())

    allowed_click_rects = [overlay, [overlay.get_rect()]]
    overlay.external_process_arguments = allowed_click_rects

    close_btn = utils.find_object_from_name(overlay.get_buttons(), "close_btn")
    overlay.destroy_child(close_btn)

    button_size = 50
    offset = 7
    font_size = 30
    text_box = assets.Box(y=y + offset, z=overlay.z, text="Are you sure?")
    text_box.hug_text(offset)
    text_box.set_pos(x + (overlay.width - text_box.width) // 2, text_box.y)
    overlay.add_child(text_box)
    yes_btn = assets.Button(x=x, y=y + overlay.height - offset - button_size, width=button_size, height=button_size,
                            text="Yes", font_size=font_size,
                            left_click_function=utils.execute_multiple_functions,
                            left_click_args=[[overlay.destroy, func], [[], args]], name="overlay_yes_btn")
    yes_btn.hug_text(offset)
    no_btn = assets.Button(x=x + 50, y=y + overlay.height - offset - button_size, width=button_size, height=button_size,
                           text="No", font_size=font_size,
                           left_click_function=overlay.destroy, left_trigger_keys=["escape"], name="overlay_no_btn")
    no_btn.hug_text(offset)

    buttons = [yes_btn, no_btn]
    number_of_buttons = len(buttons)
    x_offset = (overlay.width - number_of_buttons * button_size) // (number_of_buttons + 1)
    for i, btn in enumerate(buttons):
        btn.set_z(overlay.z)
        overlay.add_child(btn)
        btn.set_pos(x + (i + 1) * x_offset + i * button_size, btn.y)

    game_engine.get_scene_manager().get_current_scene().add_object(overlay)


if __name__ == "__main__":
    spellcaster_cards = ["1003840", "1003840", "12744567", "14087893", "14087893", "17315396", "17315396", "24634594",
                         "28553439", "2956282", "3040496", "3084730", "35726888", "35726888", "36857073", "37520316",
                         "37675907", "40139997", "41999284", "423585", "423585", "423585", "42632209", "48739166",
                         "49816630", "5376159", "57734012", "57916305", "57916305", "57995165", "62849088", "64756282",
                         "64756282", "64756282", "66337215", "70226289", "70226289", "70368879", "70368879", "77683371",
                         "77683371", "77683371", "78552773", "82489470", "82489470", "83308376", "83764719", "84523092",
                         "84664085", "87804747", "89907227", "91592030", "91592030", "93125329", "94553671", "94553671",
                         "97268402", "97631303"]

    darklord_cards = ["14517422", "14517422", "14517422", "18168997", "18168997", "22110647", "25339070", "25339070",
                      "25451652", "25451652", "26357901", "26357901", "26357901", "30439101", "35726888", "35726888",
                      "35726888", "38120068", "3814632", "3828844", "41209827", "4167084", "423585", "423585", "423585",
                      "43316238", "48130397", "48130397", "50501121", "50501121", "50501121", "52645235", "52840267",
                      "52840267", "52840267", "5402805", "55289183", "55289183", "59900655", "69946549", "72892473",
                      "74335036", "74335036", "78868119", "78868119", "79933029", "82105704", "82105704", "82134632",
                      "82773292", "87112784", "87112784", "88120966", "89516305", "9486959"]

    darklord_2_cards = ["14517422", "14517422", "14517422", "18168997", "18168997", "22110647", "25339070", "25339070",
                        "25451652", "26357901", "26357901", "28427869", "28427869", "28427869", "30439101", "35726888",
                        "35726888", "35726888", "38120068", "3814632", "38904695", "41209827", "4167084", "43316238",
                        "45420955", "48130397", "48130397", "49565413", "50501121", "50501121", "50501121", "52119435",
                        "52645235", "52840267", "52840267", "52840267", "5402805", "55289183", "55289183", "59900655",
                        "69946549", "72892473", "74335036", "74335036", "78868119", "78868119", "79933029", "82105704",
                        "82105704", "82134632", "82773292", "83340560", "83764719", "87112784", "87112784", "88120966",
                        "9486959"]

    thin_cards = ["14517422"] * 1

    DECKS = [Deck(name="Spellcaster", cards=spellcaster_cards, main_card_id="1003840"),
             Deck(name="Darklord", cards=darklord_cards, main_card_id="14517422"),
             Deck(name="Darklord 2", cards=darklord_2_cards, main_card_id="14517422"),
             Deck(name="Thin Deck", cards=thin_cards, main_card_id="token")]
    deck_manager = DeckManager()
    pygame.init()
    pygame.display.set_caption("A tool for playtesting Yu-Gi-Oh!")

    game_engine.schedule_scene_change(create_main_menu, "main_menu")
    running = True
    while running:
        running = environment.handle_events()
        game_engine.start_tick()
        game_engine.get_scene_manager().get_current_scene().process()

        environment.draw_screen()

        game_engine.end_tick()

        environment.clock.tick(FPS)
    pygame.quit()

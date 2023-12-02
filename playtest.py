import os
import sys
import random
import math
import time
import assets
import constants
from environment import environment, Scene, scene_manager, placeholder, surface_manager
import utility_functions as utils
from constants import *
import pickle

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


# TODO: Change CardOverlay into a class that inherits from Overlay!
# TODO: Right now, the code repetition is high.
# TODO: Create a "help" button?
# TODO: Implement text fields, dice, etc? For randomness, life points etc.
# TODO: Perhaps implement a place to enter commands, such as shuffle deck etc.
# TODO: Fix comments, code, documentation.
# TODO: Find a way to highlight buttons even when they use images.
# could work with always highlighting a border around the button, or using a transparent white layer above the button.
# TODO: Fix classes, functions etc so that things work without knowing how everything works in detail.
# That is, fix the api, so that you can create a new scene easily.
# TODO: Overlay exit button only looks good on white overlays. Make buttons transparent?
# TODO: Increase loading speed, creating cards takes too long time. Does everything have to be done immediately?
# I think it's loading the images that takes time. Perhaps this should be done at start, or maybe the images are too
# big, and should be the "standard size".
# TODO: Make small_card_overlay into a sub-class of Overlay?
# TODO: Rename schedule_processing to something else? And make it prettier.
# TODO: Make button colors easier to use. Specify one main color, and then the highlighting is done either by
# opacity or increasing (or decreasing) the brightness by a certain amount.
# TODO: Some bug with create_overlay_card, FileNotFoundError. Can't seem to reproduce this reliably.
# TODO: Fix the deck selection scene
# TODO: Rotating a card on the edge of the field doesnt immediately clamp it, looks weird.
# TODO: Enable the possibility for checking a new button click.

# TODO: Remove possibility to add extra_deck_card to the hand
# TODO: Token flickers and teleports on creation.
# TODO: Add support for pendulum monsters.
# This include show if a card is face-up or face-down (only has to be in the extra deck, but could as well include
# this functionality for any card). Also add pendulum types for the get_card_type. Pendulum cards should be able
# to be sent to the extra_deck.



class Deck:
    def __init__(self, name="", cards=None, main_card_id=None):
        if cards is None:
            self.cards = []
        else:
            self.cards = cards
        if main_card_id is None:
            main_card_id = cards[0]

        self.name = name
        self.main_card_id = main_card_id
        self.image_id = surface_manager.create_image(card_image_location + self.main_card_id + ".jpg")

    def get_image(self):
        return surface_manager.fetch_image(self.image_id)


class CardOverlay(assets.GameObject):
    def __init__(self, x=0, y=0, width=1540, height=760, alpha=255, name=None, card_list_function=None):
        super().__init__(name)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.alpha = alpha
        self.name = name
        self.card_list_function = card_list_function

        self.cards_per_row = 7
        self.number_of_rows = 4
        self.start_index = 0
        self.stop_index = self.start_index + self.cards_per_row * self.number_of_rows - 1

        self.buttons = []
        self.box = assets.Box(x=self.x, y=self.y, width=self.width, height=self.height,
                              color=WHITE, alpha=self.alpha)

        self.card_list = self.card_list_function()
        self.cards = []
        for i, card in enumerate(self.card_list):
            self.set_overlay_card(self.create_overlay_card(card, i), i)

        close_btn_size = 30
        close_btn_offset = 5
        self.close_btn = assets.Button(x=self.x + self.width - close_btn_size - close_btn_offset,
                                       y=self.y + close_btn_offset, width=close_btn_size, height=close_btn_size,
                                       image=pygame.image.load("Images/close_button.png"), name="close_btn",
                                       left_click_function=self.destroy, left_trigger_keys=["escape"])

        self.buttons.append(self.close_btn)

    def create_overlay_card(self, card, i):
        card.parent = self
        x, y, card_width, card_height = self.get_card_info(i)
        card.set_pos(x, y)
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

    def get_card_info(self, i):
        max_cards_to_show = self.cards_per_row * self.number_of_rows
        min_x_offset = 10
        min_y_offset = 10
        card_space = 5
        aspect_ratio = card_aspect_ratio

        card_width = int(
            min((self.box.height - 2 * min_y_offset - (math.ceil(max_cards_to_show / self.cards_per_row) - 1)
                 * card_space) / (math.ceil(max_cards_to_show / self.cards_per_row) * aspect_ratio),
                (self.box.width - 2 * min_x_offset - (self.cards_per_row - 1) * card_space)
                / self.cards_per_row))

        card_height = int(aspect_ratio * card_width)

        x_offset = int(
            (self.box.width - (self.cards_per_row - 1) * card_space - self.cards_per_row * card_width) / 2)

        y_offset = int((self.box.height - math.ceil(max_cards_to_show / self.cards_per_row - 1) * card_space
                        - math.ceil(max_cards_to_show / self.cards_per_row) * card_height) / 2)

        x = self.box.x + x_offset + int(i % self.cards_per_row * (card_space + card_width))
        y = self.box.y + y_offset + int(i // self.cards_per_row * (card_space + card_height))
        return x, y, card_width, card_height

    def remove_overlay(self):
        scene = scene_manager.current_scene
        scene.overlays.remove(self)

    def schedule_processing(self):
        self.pre_process()
        items_to_be_processed = []
        items_to_be_processed.extend(self.box.schedule_processing())

        for btn in self.buttons:
            items_to_be_processed.extend(btn.schedule_processing())

        items_to_be_processed.append(self)

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
                scene_manager.current_scene.process_given_objects(items_to_be_processed)
                item_index = scene_manager.current_scene.display_order.index(self) + 1
                for item in items_to_be_processed:
                    scene_manager.current_scene.add_to_display_order(item, item_index)
                    item_index += 1

    def pre_process(self):
        self.card_list = self.card_list_function()

        if self.start_index + (self.number_of_rows - 1) * self.cards_per_row + 1 > len(self.card_list):
            self.start_index = utils.clamp(self.cards_per_row - self.cards_per_row, 0, self.cards_per_row)

        self.stop_index = self.start_index + self.cards_per_row * self.number_of_rows - 1

        for i, card in enumerate(self.cards):
            if card not in self.card_list:
                self.cards.remove(card)

        # This is what's causing the issues with shuffling the deck with overlay.
        for i, card in enumerate(self.card_list):
            if card not in self.cards:
                self.set_overlay_card(self.create_overlay_card(card, i), i)
            else:
                self.set_overlay_card(card, i)

        for i, card in enumerate(self.cards[self.start_index:self.stop_index + 1]):
            x, y, _, _ = self.get_card_info(i)
            card.set_pos(x=x, y=y)


class Board:
    def __init__(self, card_ids=None, name=""):
        if card_ids is None:
            card_ids = []

        self.deck = []
        self.extra_deck = []
        for card_id in card_ids:
            new_card = assets.Card(card_id=card_id)
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
        card_space = 10  # TODO: This is hard-coded.
        if scene_manager.current_scene.name == "play_testing":
            self.display_hand_number = utils.find_object_from_name(scene_manager.current_scene.boxes, "hand_box").width \
                                       // (constants.standard_card_width + card_space)
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

        scene = scene_manager.current_scene
        hand_box = utils.find_object_from_name(scene.boxes, "hand_box")

        y_offset = (hand_box.get_rect().height - card.get_rect().height) // 2
        card_space = 10

        visible_cards = self.hand[self.display_hand_start_index:self.display_hand_start_index + card_index]
        cards_in_hand_width = sum([hand_card.width + card_space for hand_card in visible_cards])

        all_cards_in_hand_width = self.display_hand_number * (self.hand[0].width + card_space)

        x_offset = (hand_box.width - all_cards_in_hand_width) // 2
        x = hand_box.x + x_offset + cards_in_hand_width
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
            default_x, default_y = scene_manager.current_scene.get_default_position()
            card.set_pos(default_x, default_y)
        card.new_location(location="field")
        self.field.append(card)
        self.begin_processing(card)
        if not card.moving:
            x, y = scene_manager.current_scene.get_default_position()
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
            is_visible_in_hand = self.display_hand_start_index <= self.hand.index(card) < display_stop_index
            x, y = self.get_card_in_hand_pos(card, self.hand.index(card) - self.display_hand_start_index)
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

    def save(self):
        pass


def generate_board(scene):
    existing_board = utils.find_object_from_name(scene.others, "board")
    if existing_board is not None:
        scene.others.remove(existing_board)

    board = Board(card_ids=environment.deck.cards, name="board")
    scene.others.append(board)
    return board


def cards_in_deck_string(scene=None):
    if scene is None:
        scene = scene_manager.current_scene
    board = utils.find_object_from_name(scene.others, "board")
    return "Cards: {}".format(len(board.deck))


def choose_deck(deck):
    environment.set_deck(deck)
    scene_manager.schedule_scene_change(create_play_testing)


def change_overlay_limits(overlay, change_in_limits):
    new_start_index = overlay.start_index + change_in_limits
    if new_start_index + (overlay.number_of_rows - 1) * overlay.cards_per_row + 1 > len(overlay.card_list):
        return

    elif new_start_index < 0:
        overlay.start_index = 0

    else:
        overlay.start_index += change_in_limits


def create_main_menu():
    scene = Scene(name="main_menu")
    # TODO: Perhaps ask scene_manager for a new scene here instead.
    scene_manager.change_scene(scene)
    scene.background_color = WHITE
    width = 200
    height = 100

    start_btn = assets.Button(y=environment.get_height() // 2, width=width,
                              height=height, text="Start", left_click_function=scene_manager.schedule_scene_change,
                              left_click_args=[create_deck_selection_scene])

    load_btn = assets.Button(y=environment.get_height() // 2, width=width,
                             height=height, text="Load Save", left_click_function=scene_manager.load)

    test_btn = assets.Button(y=environment.get_height() // 2, width=width, height=height,
                             text="Testing", font_size=35,
                             left_click_function=scene_manager.schedule_scene_change,
                             left_click_args=[create_test_scene])

    exit_btn = assets.Button(y=environment.get_height() // 2, width=width,
                             height=height, text="Exit", left_click_function=sys.exit)

    buttons = [start_btn, load_btn, test_btn, exit_btn]
    number_of_buttons = len(buttons)
    x_offset = (environment.get_width() - number_of_buttons * width) // (number_of_buttons + 1)
    for i, btn in enumerate(buttons):
        btn.static = False
        btn.set_pos((i + 1) * x_offset + i * width, btn.y)
        scene.buttons.append(btn)


def create_test_scene():
    scene = Scene(name="test_scene")
    scene_manager.change_scene(scene)
    scene.background_color = SIENNA
    exit_btn = assets.Button(text="Main Menu", alpha=255, left_click_function=scene_manager.schedule_scene_change,
                             left_click_args=[create_main_menu])
    scene.buttons.append(exit_btn)
    button = assets.Button(x=500, y=500, width=200, height=100, text="Create confirmation overlay",
                           left_click_function=create_confirmation_overlay,
                           left_click_args=[(700, 700), test_button, []],
                           colors={"normal": SIENNA, "hover": SADDLE_BROWN, "pressed": SADDLE_BROWN})
    button.hug_text(15)
    box = assets.Box(x=100, y=100, color=GREY, text="HEJSAN")
    scene.others.append(box)
    scene.buttons.append(button)


def create_play_testing():
    scene = Scene(name="play_testing")
    scene.persistent = True
    # TODO: Fix the scene change structure so that the below code doesn't have to be repeated for every scene
    # creation function. Perhaps using classes?
    if scene.name in scene_manager.scenes:
        scene_manager.change_scene_by_name(scene.name)
        return
    scene_manager.change_scene(scene)
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

    scene.boxes.extend([field_box, hand_box, left_side_box, right_side_box])
    scene.others.append(hand_border)
    board = generate_board(scene)

    draw_btn = assets.Button(x=environment.get_width() - button_width - offset,
                             y=environment.get_height() - deck_height - offset,
                             width=deck_width, height=deck_height, image=pygame.image.load("Images/card_back.png"),
                             name="draw_btn", left_click_function=board.draw)

    deck_text_box = assets.Box(text=cards_in_deck_string(scene), font_size=25, color=LIGHT_GREY,
                               update_text_func=cards_in_deck_string)
    deck_text_box.static = False
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
                                  left_click_function=scene_manager.schedule_scene_change,
                                  left_click_args=[create_main_menu])

    save_btn = assets.Button(x=main_menu_btn.x, y=main_menu_btn.y + main_menu_btn.height + offset,
                             text="SAVE", name="save_btn",
                             left_click_function=placeholder.schedule_end_of_tick_function,
                             left_click_args=[scene_manager.save, []])

    """assets.Button(x=main_menu_btn.x, y=main_menu_btn.y + main_menu_btn.height + offset,
                              text="Reset", name="reset_btn", left_click_function=scene_manager.schedule_scene_change,
                              left_click_args=[create_play_testing])"""

    token_btn = assets.Button(x=show_extra_deck_btn.x, y=show_extra_deck_btn.y - offset - button_height,
                              width=button_width,
                              height=button_height,
                              text="Token", name="token_btn", left_click_function=generate_token)

    # hand_overlay_button = assets.Button(text="Show hand", name="hand_overlay_btn",
    # left_click_function=create_hand_overlay)
    small_button_size = 50

    hand_index_button_offset = (hand_box.height - button_height / 2) // 2
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

    scene.buttons.extend([main_menu_btn, draw_btn, show_deck_btn, save_btn, shuffle_deck_btn, show_extra_deck_btn,
                          show_gy_btn, show_banished_btn, token_btn, hand_index_increment_btn,
                          hand_index_decrement_btn])

    scene.boxes.extend([deck_text_box])

    for _ in range(5):
        board.draw()


def create_deck_selection_scene():
    scene = Scene(name="deck_selection")
    scene_manager.change_scene(scene)

    deck_selection_overlay = assets.Overlay(width=environment.get_width(), height=environment.get_height(),
                                            background_color=WHITE)
    deck_selection_overlay.close_btn.destroy()
    for i, deck in enumerate(DECKS):
        deck_btn = assets.Button(text=deck.name, x=i * large_card_width, y=500, width=large_card_width,
                                 height=large_card_height,
                                 left_click_function=create_confirmation_overlay,
                                 left_click_args=[(i * large_card_width, 500), choose_deck, [deck]])
        deck_btn.set_image(deck.get_image())
        deck_selection_overlay.buttons.append(deck_btn)

    deck_selection_overlay.parent = scene
    scene.overlays.append(deck_selection_overlay)


def cards_in_deck():
    board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
    return board.deck


def cards_in_extra_deck():
    board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
    return board.extra_deck


def cards_in_gy():
    board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
    return board.gy


def cards_in_banished():
    board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
    return board.banished


def cards_in_hand():
    board = utils.find_object_from_name(scene_manager.current_scene.others, "board")
    return board.hand


def generate_token():
    scene = scene_manager.current_scene
    token = assets.Card(card_id="token")
    token.x, token.y = scene.get_default_position()
    board = utils.find_object_from_name(scene.others, "board")
    board.field.append(token)
    board.card_processing_order.append(token)  # TODO: Perhaps add a method in class Board for the adding of cards.


def create_deck_overlay():
    create_location_overlay("main_deck", cards_in_deck)


def create_extra_deck_overlay():
    create_location_overlay("extra_deck", cards_in_extra_deck)


def create_gy_overlay():
    create_location_overlay("gy", cards_in_gy)


def create_banished_overlay():
    create_location_overlay("banished", cards_in_banished)


def create_hand_overlay():
    create_location_overlay("hand", cards_in_hand)


def test_button():
    print("BUTTON TEST AT TIME:", time.time())


def value_from_card_type(card_type):
    type_value_dict = {
        "pendulum": 0,
        "fusion": 1,
        "synchro": 2,
        "xyz": 3,
        "link": 4
    }
    return type_value_dict[card_type]


def create_location_overlay(location_name, card_list_function):
    scene = scene_manager.current_scene
    if len(scene.overlays) > 0:
        overlay_to_remove = utils.find_object_from_name(scene.overlays, location_name)
        scene.overlays = []
        if overlay_to_remove is not None:
            return
    field_box = utils.find_object_from_name(scene.boxes, "field_box")
    x_offset = 10
    y_offset = 10
    overlay_width = field_box.width - 2 * x_offset
    overlay_height = field_box.height - 2 * y_offset
    overlay = CardOverlay(x=field_box.x + x_offset, y=field_box.y + y_offset, width=overlay_width,
                          height=overlay_height, alpha=180, name=location_name, card_list_function=card_list_function)
    small_button_width = 50
    small_button_height = small_button_width

    scroll_up_btn = assets.Button(x=overlay.x + overlay_width - small_button_width - x_offset,
                                  y=overlay.y + 2 * y_offset + overlay.close_btn.height,
                                  width=small_button_width, height=small_button_height,
                                  image=pygame.image.load("Images/up_arrow.png"), name="scroll_up_btn",
                                  left_trigger_keys=["up"],
                                  left_click_function=change_overlay_limits,
                                  left_click_args=[overlay, -overlay.cards_per_row])

    scroll_down_btn = assets.Button(x=overlay.x + overlay_width - small_button_width - x_offset,
                                    y=overlay.y + overlay_height - small_button_height - y_offset,
                                    width=small_button_width, height=small_button_height,
                                    image=pygame.image.load("Images/down_arrow.png"), name="scroll_down_btn",
                                    left_trigger_keys=["down"],
                                    left_click_function=change_overlay_limits,
                                    left_click_args=[overlay, overlay.cards_per_row])

    overlay.buttons.extend([scroll_up_btn, scroll_down_btn])
    scene.overlays.append(overlay)


def create_confirmation_overlay(position, func, args):
    # TODO: Add remove_on_external_clicks?
    # TODO: Make this into a sub-class of Overlay?
    scene_overlays = scene_manager.current_scene.overlays
    existing_confirmation_overlay = utils.find_object_from_name(scene_overlays, "confirmation_overlay")
    if existing_confirmation_overlay is not None:
        return
    x, y = position
    overlay = assets.Overlay(x=x, y=y, width=300, height=150, name="confirmation_overlay",
                             parent=scene_manager.current_scene)
    overlay.parent = scene_manager.current_scene
    overlay.close_btn.destroy()

    overlay_border = assets.Border(x=overlay.x, y=overlay.y, width=overlay.width, height=overlay.height, color=BLACK,
                                   parent=overlay)
    overlay.objects.append(overlay_border)
    button_size = 50
    offset = 7
    font_size = 30
    text_box = assets.Box(y=y + offset, text="Are you sure?")
    text_box.hug_text(offset)
    text_box.set_pos(x + (overlay.width - text_box.width) // 2, text_box.y)
    overlay.objects.append(text_box)
    yes_btn = assets.Button(x=x, y=y + overlay.height - offset - button_size, width=button_size, height=button_size,
                            text="Yes", font_size=font_size,
                            left_click_function=utils.execute_multiple_functions,
                            left_click_args=[[overlay.destroy, func], [[], args]])
    yes_btn.hug_text(offset)
    no_btn = assets.Button(x=x + 50, y=y + overlay.height - offset - button_size, width=button_size, height=button_size,
                           text="No", font_size=font_size,
                           left_click_function=overlay.destroy, left_trigger_keys=["escape"])
    no_btn.hug_text(offset)

    buttons = [yes_btn, no_btn]
    number_of_buttons = len(buttons)
    x_offset = (overlay.width - number_of_buttons * button_size) // (number_of_buttons + 1)
    for i, btn in enumerate(buttons):
        btn.static = False
        btn.set_pos(x + (i + 1) * x_offset + i * button_size, btn.y)
        overlay.buttons.append(btn)

    scene_manager.current_scene.overlays.append(overlay)

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

    thin_cards = ["14517422"] * 15

    DECKS = [Deck(name="Spellcaster", cards=spellcaster_cards, main_card_id="1003840"),
             Deck(name="Darklord", cards=darklord_cards, main_card_id="14517422"),
             Deck(name="Darklord 2", cards=darklord_2_cards, main_card_id="14517422"),
             Deck(name="Thin Deck", cards=thin_cards, main_card_id="token")]
    pygame.init()
    pygame.display.set_caption("A tool for playtesting Yu-Gi-Oh!")

    create_main_menu()
    running = True
    while running:
        running = environment.handle_events()
        placeholder.start_tick()
        scene_manager.current_scene.process()

        environment.draw_screen()

        placeholder.end_tick()

        environment.clock.tick(FPS)
        # scene_manager.save()
    pygame.quit()

import assets
from game_engine import environment, Scene
import game_engine
from constants import *
import utility_functions as utils
from Scenes import main_menu_scene
import random
import math
import glob


class PlaytestingScene(game_engine.Scene):
    """Creates a scene used for playtesting a Yu-Gi-Oh!.

    Inherits all attributes from the Scene class, and implements the create_scene method.
    """

    def __init__(self, deck):
        super().__init__(name="playtesting_scene")
        self.deck = deck

    def create_scene(self):
        """Creates a playtesting scene for playtesting a Yu-Gi-Oh! deck.

        Returns:
            Scene: The playtesting scene.
        """
        self.background_color = DARK_GREY

        button_width = 200
        button_height = 100
        deck_width = button_width
        deck_height = int(button_width * card_aspect_ratio)
        offset = 15
        side_width = max(button_width, deck_width) + 2 * offset
        card_height = standard_card_width * card_aspect_ratio

        left_side_box = assets.Box(x=0, y=0, width=large_card_width + 2 * offset,
                                   height=environment.get_height(), color=DARK_GREY, name="left_side_box")

        right_side_box = assets.Box(x=environment.get_width() - side_width, width=side_width,
                                    height=environment.get_height(),
                                    color=DARK_GREY,
                                    name="right_side_box")

        field_box = assets.Box(x=left_side_box.x + left_side_box.width,
                               width=environment.get_width() - left_side_box.width - right_side_box.width,
                               height=environment.get_height() - int(card_height) - offset, color=SADDLE_BROWN,
                               name="field_box")

        hand_box_width = environment.get_width() - left_side_box.width - right_side_box.width - 2 * button_width
        hand_box = assets.Box(x=left_side_box.width + button_width,
                              y=environment.get_height() - int(card_height) - offset,
                              width=hand_box_width,
                              height=int(card_height) + offset, color=DARK_GREY, name="hand_box")

        hand_border = assets.Border(x=hand_box.x, y=hand_box.y, width=hand_box.width,
                                    height=hand_box.height,
                                    parent=hand_box)

        self.add_multiple_objects([field_box, hand_box, left_side_box, right_side_box])
        self.add_object(hand_border)
        board = generate_board(self, self.deck)

        draw_btn = assets.Button(x=environment.get_width() - button_width - offset,
                                 y=environment.get_height() - deck_height - offset,
                                 width=deck_width, height=deck_height, image_id=game_engine.load_image(
                image_location + "card_back.png"),
                                 name="draw_btn", left_click_function=board.draw)

        deck_text_box = assets.Box(width=100, height=30, text=cards_in_deck_string(self), resize_to_fit_text=True,
                                   font_size=25, color=LIGHT_GREY,
                                   update_text_func=cards_in_deck_string)

        deck_text_box.set_pos(x=right_side_box.x + (right_side_box.width - deck_text_box.width) / 2,
                              y=draw_btn.y - deck_text_box.height - offset)

        show_deck_btn = assets.Button(x=draw_btn.x, y=deck_text_box.y - button_height - offset, width=button_width / 2,
                                      height=button_height,
                                      image_id=game_engine.load_image(image_location + "millennium_eye.png"),
                                      name="show_deck_btn", left_click_function=create_deck_overlay)

        show_extra_deck_btn = assets.Button(x=left_side_box.x + offset,
                                            y=environment.get_height() - deck_height - offset,
                                            width=deck_width, height=deck_height,
                                            image_id=game_engine.load_image(image_location + "card_back.png"),
                                            name="show_extra_deck_btn", left_click_function=create_extra_deck_overlay)

        shuffle_deck_btn = assets.Button(x=draw_btn.x + button_width / 2, y=deck_text_box.y - button_height - offset,
                                         width=button_width / 2, height=button_height,
                                         image_id=game_engine.load_image(image_location + "shuffle.png"),
                                         name="shuffle_deck_btn",
                                         left_click_function=board.shuffle_the_deck)

        show_gy_btn = assets.Button(x=draw_btn.x, y=deck_text_box.y - 2 * button_height - offset,
                                    width=button_width / 2,
                                    height=button_height,
                                    image_id=game_engine.load_image(image_location + "gy_icon.png"),
                                    name="show_gy_btn", left_click_function=create_gy_overlay)

        show_banished_btn = assets.Button(x=draw_btn.x + button_width / 2,
                                          y=deck_text_box.y - 2 * button_height - offset,
                                          width=button_width / 2,
                                          height=button_height,
                                          image_id=game_engine.load_image(image_location + "banished_icon.png"),
                                          name="show_banished_btn", left_click_function=create_banished_overlay)

        extra_options_button = assets.Button(x=show_gy_btn.x, y=show_gy_btn.y - button_height, width=button_width / 2,
                                             height=button_height,
                                             image_id=game_engine.load_image(image_location + "extra_options.png"),
                                             name="extra_options_button",
                                             left_click_function=create_extra_options_overlay)

        token_btn = assets.Button(x=show_gy_btn.x + button_width / 2, y=show_gy_btn.y - button_height,
                                  width=button_width / 2,
                                  height=button_height,
                                  text="Token", font_size=30, name="token_btn", left_click_function=generate_token)

        main_menu_btn = assets.Button(x=draw_btn.x, y=offset, width=button_width, height=button_height,
                                      text="Main Menu", name="main_menu_btn", font_size=35,
                                      left_click_function=game_engine.schedule_scene_change,
                                      left_click_args=[main_menu_scene.MainMenuScene()])

        save_btn = assets.Button(x=main_menu_btn.x, y=main_menu_btn.y + main_menu_btn.height + offset,
                                 text="SAVE", name="save_btn",
                                 left_click_function=game_engine.schedule_end_of_tick_function,
                                 left_click_args=[game_engine.save, []])

        """assets.Button(x=main_menu_btn.x, y=main_menu_btn.y + main_menu_btn.height + offset,
                                  text="Reset", name="reset_btn",
                                  left_click_function=game_engine.schedule_scene_change,
                                  left_click_args=[create_play_testing])"""

        input_field = assets.InputField(x=show_extra_deck_btn.x, y=show_extra_deck_btn.y - offset - button_height,
                                        width=button_width,
                                        height=button_height, text="Life points: ", initial_text_buffer="8000",
                                        allowed_input_types=assets.InputTypes.NUMBER)
        small_button_size = 50

        hand_index_button_offset = int((hand_box.height - button_height / 2) / 2)
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

        self.add_multiple_objects(
            [main_menu_btn, draw_btn, show_deck_btn, save_btn, shuffle_deck_btn, show_extra_deck_btn,
             show_gy_btn, show_banished_btn, extra_options_button, token_btn, input_field, hand_index_increment_btn,
             hand_index_decrement_btn])

        self.add_multiple_objects([deck_text_box])

        for _ in range(5):
            board.draw()

        return self


class Board(assets.GameObject):
    """A class representing a game board.

    Attributes:
        x (int): X-coordinate of the board.
        y (int): Y-coordinate of the board.
        z (float): Z-coordinate of the board.
        width (int): Width of the board.
        height (int): Height of the board.
        alpha (int): The alpha value, ranging from 0 (transparent) to 255 (opaque).
        name (str): Name of the board.
        destroyed (bool): Indicates whether the board has been destroyed.
        parent: Parent object to which this board is attached.
        static (bool): Indicates whether the board is static (does not move together with its parent).
        displayable (bool): Indicates whether the board is visible.
        opaque (bool): Indicates whether the board blocks objects earlier in the processing order from
            being clicked.
        children (list): List of child board.
        rect (pygame.Rect): Rectangular area occupied by the board.
        rotation_angle (int): Rotation angle of the board in degrees.
        relative_x (int): The x-coordinate of the board in relation to its parent, if applicable.
        relative_y (int): The y-coordinate of the board in relation to its parent, if applicable.
        name (str): The name of the board.
        scene: The scene to which the board belongs.
    """

    def __init__(self, card_ids=None, scene=None):
        """Initializes a Board instance.

        Args:
            card_ids (list): List of card IDs for the cards in the deck.
            scene (game_engine.Scene): The scene to which the board belongs.
        """
        super().__init__(name="board")
        self.z = 2
        if card_ids is None:
            card_ids = []

        self.deck = []
        self.extra_deck = []
        for card_id in card_ids:
            new_card = Card(card_id=card_id, board=self)
            card_start_location = new_card.card_starting_location()
            new_card.location = card_start_location
            if card_start_location == "main_deck":
                self.deck.append(new_card)
            else:
                self.extra_deck.append(new_card)

        card_sort_card_type(self.extra_deck)

        random.shuffle(self.deck)
        self.hand = []
        self.gy = []
        self.banished = []
        self.field = []
        self.card_processing_order = []
        self.scene = scene
        card_space = standard_space
        scene_objects = self.scene.get_objects()
        hand_box_width = utils.find_object_from_name(scene_objects, "hand_box").width
        self.display_hand_number = hand_box_width // (standard_card_width + card_space)
        self.display_hand_start_index = 0

    def set_display_hand_start_index(self, new_index):
        """Sets the starting index for displaying the hand.

       Args:
           new_index (int): The new starting index.
       """
        max_display_index = utils.clamp(len(self.hand) - self.display_hand_number, 0, len(self.hand))
        self.display_hand_start_index = utils.clamp(new_index, 0, max_display_index)

    def set_display_hand_start_index_relative(self, index_change):
        """Sets the starting index for displaying the hand relative to the current index.

        Args:
            index_change (int): The change in the starting index.
        """
        self.set_display_hand_start_index(self.display_hand_start_index + index_change)

    def get_location(self, card):
        """Gets the location of a card on the board.

        Args:
            card: The card for which to determine the location.

        Returns:
            list: The location of the card.
        """
        location_list = [self.hand, self.field, self.gy, self.banished, self.deck, self.extra_deck]
        for location in location_list:
            for comparison_card in location:
                if card == comparison_card:
                    return location

        return None

    def get_card_in_hand_pos(self, card, card_index=None):
        """Gets the position of a card in the hand.

        Args:
            card (Card): The card for which to determine the position.
            card_index (int or None): The index of the card in the hand.

        Returns:
            Tuple containing the x and y coordinates.
        """
        if card_index is None:
            card_index = self.hand.index(card)

        card_width = self.hand[0].width
        hand_box = utils.find_object_from_name(self.scene.get_objects(), "hand_box")
        y_offset = (hand_box.get_rect().height - card.get_rect().height) / 2
        card_space = 10

        cards_to_the_left_width = (card_width + card_space) * (card_index - self.display_hand_start_index)

        all_cards_in_hand_width = self.display_hand_number * (card_width + card_space)

        x_offset = (hand_box.width - all_cards_in_hand_width) / 2
        x = hand_box.x + x_offset + cards_to_the_left_width
        y = hand_box.y + y_offset

        return x, y

    def get_visible_hand(self):
        """Returns the list of cards that are visible in the hand."""
        return self.hand[self.display_hand_start_index:self.display_hand_start_index + self.display_hand_number]

    def shuffle_the_deck(self):
        """Shuffles the main deck."""
        random.shuffle(self.deck)

    def draw(self):
        """Draws a card from the main deck and adds it to the hand."""
        if len(self.deck) == 0:
            return
        drawn_card = self.deck[0]
        self.add_to_hand(drawn_card, self.deck)

    def send_to_gy(self, card, previous_location):
        """Sends a card to the graveyard and removes it from the previous location.

        Args:
            card: The card to send to the graveyard.
            previous_location: The previous location of the card.
        """
        if card not in previous_location:
            raise IndexError("Card not found in previous location")

        self.stop_processing(card)
        self.gy.insert(0, card)
        previous_location.remove(card)
        card.new_location(location="gy")

    def banish(self, card, previous_location):
        """Banishes a card and removes it from the previous location.

        Args:
            card: The card to banish.
            previous_location: The previous location of the card.
        """
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        self.stop_processing(card)
        self.banished.insert(0, card)
        previous_location.remove(card)
        card.new_location(location="banished")

    def add_to_the_deck(self, card, previous_location):
        """Adds a card to the main deck and removes it from the previous location.

        Args:
            card: The card to add to the main deck.
            previous_location: The previous location of the card.
        """
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        self.stop_processing(card)
        self.deck.insert(0, card)
        card.moving = False
        previous_location.remove(card)
        card.new_location(location="main_deck")

    def add_to_the_extra_deck(self, card, previous_location):
        """Adds a card to the extra deck and removes it from the previous location.

        Args:
            card: The card to add to the extra deck.
            previous_location: The previous location of the card.
        """
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        self.stop_processing(card)
        self.extra_deck.insert(0, card)

        card.moving = False
        previous_location.remove(card)
        card.new_location(location="extra_deck")

    def add_to_hand(self, card, previous_location):
        """Adds a card to the hand and removes it from the previous location.

        Args:
            card: The card to add to the hand.
            previous_location: The previous location of the card.
        """
        if card not in previous_location:
            raise IndexError("Card not found in previous location")

        if not card.moving:
            self.hand.append(card)
            x, y = self.get_card_in_hand_pos(card)
            card.set_pos(x, y)
        else:
            card_index = self.find_index_by_x_value(card)
            self.hand.insert(card_index, card)

        previous_location.remove(card)
        card.new_location(location="hand", visible_after=self.is_card_visible(card))

    def move_to_field(self, card, previous_location):
        """Moves a card to the field and removes it from the previous location.

        Args:
            card: The card to move to the field.
            previous_location: The previous location of the card.
        """
        if card not in previous_location:
            raise IndexError("Card not found in previous location")
        if card.location != "hand":
            default_x, default_y = game_engine.get_scene_manager().get_current_scene().get_default_position()
            card.set_pos(default_x, default_y)

        self.field.append(card)
        previous_location.remove(card)
        self.begin_processing(card)
        if not card.moving:
            x, y = game_engine.get_scene_manager().get_current_scene().get_default_position()
            card.set_pos(x, y)

        card.new_location(location="field", visible_after=True)

    def find_index_by_x_value(self, card):
        """Calculates the index a card should have in the hand, based on its x-coordinate.

        Args:
            card (Card): The card whose new index should be calculated.

        Returns:
            int: The index the card should have in the hand.
        """
        visible_hand = self.get_visible_hand()
        visible_hand.append(card)
        visible_hand.sort(key=lambda hand_card: hand_card.x)
        card_index = visible_hand.index(card)
        card_index = utils.clamp(card_index, 0, self.display_hand_number - 1) + self.display_hand_start_index
        return card_index

    def is_card_visible(self, card):
        """Determines if a card is visible on the board.
        Args:
            card (Card): The card for which the visibility should be determined.
        """
        return card in self.field or card in self.get_visible_hand()

    def bump(self, card):
        """Moves a card to the end of the processing order list, so that it will be processed first.

        Args:
            card: The card to move."""
        if card not in self.card_processing_order:
            return
        self.card_processing_order.remove(card)
        self.card_processing_order.append(card)

    def remove_card(self, card):
        """Removes a card from its location and removes it from the list of cards to be processed.

        Args:
            card: The card to remove.
        """
        card_location = self.get_location(card)
        if card_location is None:
            return
        card_location.remove(card)
        self.stop_processing(card)

    def begin_processing(self, card):
        """Adds the card to a list representing the cards that will be processed this tick.

        Args:
            card (Card): The card to be added to the list.
        """
        if card not in self.card_processing_order:
            self.card_processing_order.append(card)

    def stop_processing(self, card):
        """Removes the card from a list representing the cards that will be processed this tick.

        Args:
            card (Card): The card to be removed from the list.
        """
        if card in self.card_processing_order:
            self.card_processing_order.remove(card)

    def schedule_processing(self):
        """Schedules processing for all cards on the field, and the visible cards in the hand."""
        items_to_be_processed = []
        for i, card in enumerate(self.hand):
            if card.moving:
                continue
            x, y = self.get_card_in_hand_pos(card, i)
            card.set_pos(x, y)
            if card in self.get_visible_hand():
                self.begin_processing(card)
            else:
                self.stop_processing(card)

        moving_card = None
        for card in self.card_processing_order:
            if card.moving:
                moving_card = card
                continue
            items_to_be_processed.extend(card.schedule_processing())
        if moving_card is not None:
            items_to_be_processed.extend(moving_card.schedule_processing())
        items_to_be_processed.append(self)

        return items_to_be_processed

    def process(self):
        """Processes the board, sorting the hand based on the card's x-coordinate."""
        self.sort_visible_hand()

    def sort_visible_hand(self):
        """Sorts the visible cards in the hand based on their x-position."""
        start, stop = self.display_hand_start_index, self.display_hand_start_index + self.display_hand_number
        self.hand[start:stop] = sorted(self.hand[start:stop], key=lambda card: card.x)

    def get_displayable_objects(self):
        """Gets all displayable objects on the board, namely the cards on the field and
        the visible cards in the hand."""
        displayable_objects = []

        for i, card in enumerate(self.hand):
            if card.moving:
                continue
            x, y = self.get_card_in_hand_pos(card, i)
            card.set_pos(x, y)

        visible_hand = self.get_visible_hand()
        moving_card = None
        for card in reversed(visible_hand):
            if card.moving:
                moving_card = card
                continue
            displayable_objects.extend(card.get_displayable_objects())

        for card in self.card_processing_order:
            if card in self.field:
                if card.moving:
                    moving_card = card
                    continue
                displayable_objects.extend(card.get_displayable_objects())

        if moving_card is not None:
            displayable_objects.extend(moving_card.get_displayable_objects())
        return displayable_objects


def generate_board(scene, deck):
    """Generates a game board for the specified scene.

    Args:
        scene (Scene): The scene to which the board will be added.
        deck (Deck): The deck that the board should use.

    Returns:
        Board: The newly generated game board.
    """
    existing_board = utils.find_object_from_name(scene.get_objects(), "board")
    if existing_board is not None:
        scene.remove_object(existing_board)

    board = Board(card_ids=deck.cards, scene=scene)
    scene.add_object(board)
    return board


class Card(assets.MobileButton):
    """A class representing cards.

    Attributes:
        card_type (str): A string representing the type of card (e.g Fusion, Xyz, etc.).
        location (str): A string representing the current location of the card.
    """

    def __init__(self, x=0, y=0, card_id="423585", parent=None, board=None):
        """Initializes a Card instance.

        Args:
            x (float): The x-coordinate of the card.
            y (float): The y-coordinate of the card.
            card_id (str): The ID of the card.
            parent: The parent of the card.
        """
        matching_images = glob.glob(image_location + f"{card_id}.*")
        card_image_id = None
        for image_path in matching_images:
            card_image_id = game_engine.load_image(str(image_path))

        super().__init__(x=x, y=y, z=1, width=standard_card_width, height=standard_card_height, indicate_hover=False,
                         indicate_clicks=False,
                         image_id=card_image_id, include_border=False,
                         name=card_id, static=False, parent=parent,
                         right_click_function=self.create_card_location_overlay)

        self.opaque_to_sibling = True
        self.card_type = self.get_card_type()
        self.board = board
        self.location = None

    def get_card_type(self):
        """Determine the type of the card based on the color of its card frame.

        Returns:
            str: The type of the card.
        """
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
        x = round(width_fraction * image.get_width())
        y = round(height_fraction * image.get_height())
        pixel_value = image.get_at((x, y))
        best_match = closest_color(card_colors, pixel_value)
        return best_match

    def clamp_pos(self, rect):
        """Clamps the card's position within the specified rect.

        Args:
            rect: The rect to clamp the card's position to.
        """
        self.get_rect().clamp_ip(rect)
        x = utils.clamp(self.x, rect.x, rect.x + rect.width - self.width)
        y = utils.clamp(self.y, rect.y, rect.y + rect.height - self.height)
        self.set_pos(x, y)

    def set_rotation(self, angle):
        """Sets the rotation of the card. Only supports integer multiples of 90 degrees.

        Args:
            angle: The rotation angle.
        """
        if self.rotation_angle == angle:
            return

        super().set_rotation(angle)
        self.update_card_location_overlay_anchor()

    def rotate(self, angle=90):
        """Rotates the card.

        Args:
            angle: The rotation angle. Defaults to 90 degrees.
        """
        if self.location != "field":
            return

        if self.get_rotation() == 0:
            self.set_rotation(90)
        else:
            self.set_rotation(0)

        scene = game_engine.get_scene_manager().get_current_scene()
        hand_box = utils.find_object_from_name(scene.get_objects(), "hand_box")
        field_box = utils.find_object_from_name(scene.get_objects(), "field_box")
        if not self.moving and field_box is not None:
            self.clamp_pos(field_box)
        if self.get_rect().colliderect(hand_box.get_rect()):
            self.set_rotation(0)

    def card_starting_location(self):
        """Returns the starting location of the card based on its type.

        Returns:
            str: The starting location of the card (e.g., "main_deck" or "extra_deck").
        """
        if self.card_type in ["normal", "effect", "ritual", "spell", "trap"]:
            return "main_deck"
        elif self.card_type in ["fusion", "synchro", "xyz", "link"]:
            return "extra_deck"
        return None

    def update_in_hand(self):
        """Updates the card's state when in the hand."""
        scene = game_engine.get_scene_manager().get_current_scene()
        board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
        if board is None or self not in board.get_visible_hand():
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
        """Updates the card's state when on the field."""
        scene = game_engine.get_scene_manager().get_current_scene()
        board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
        if board is None or self not in board.field:
            return

        hand_box = utils.find_object_from_name(scene.get_objects(), "hand_box")
        field_box = utils.find_object_from_name(scene.get_objects(), "field_box")
        if hand_box is None or field_box is None:
            return

        in_hand = hand_box.get_rect().colliderect(self.get_rect())
        can_be_added_to_hand = self.card_starting_location() == "main_deck"
        if in_hand and can_be_added_to_hand:
            self.set_rotation(0)
            in_hand_again = hand_box.get_rect().colliderect(self.get_rect())
            if in_hand_again:
                board.add_to_hand(self, board.field)
                return

        if self.check_deck_collision(board, board.field):
            return
        if not self.moving:
            self.clamp_pos(field_box)

    def check_deck_collision(self, board, current_location):
        """Checks collision with the deck or extra deck buttons, and adds the card to the respective deck if true.

        Args:
            board: The board object.
            current_location: The current location of the card.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        scene = game_engine.get_scene_manager().get_current_scene()
        draw_btn = utils.find_object_from_name(scene.get_objects(), "draw_btn")
        extra_deck_btn = utils.find_object_from_name(scene.get_objects(), "show_extra_deck_btn")
        on_the_deck = draw_btn.get_rect().colliderect(self.get_rect())
        on_the_extra_deck = extra_deck_btn.get_rect().colliderect(self.get_rect())

        starting_location = self.card_starting_location()

        if on_the_deck and not self.moving and starting_location == "main_deck":
            board.add_to_the_deck(self, current_location)
            return True

        elif on_the_extra_deck and not self.moving and starting_location == "extra_deck":
            board.add_to_the_extra_deck(self, current_location)
            return True
        return False

    def process(self):
        """Processes the card, updating its state."""
        super().process()
        self.update_in_hand()
        self.update_on_field()

    def start_movement(self):
        """Starts the movement of the card. Removes the card overlay, creates a large_card_button, and places it at
        the top of the board processing order.
        """
        self.remove_card_location_overlay()
        board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
        if board is not None:
            board.bump(self)

        super().start_movement()

        self.create_large_card_button()

    def new_location(self, location=None, visible_after=False):
        """Updates the card's location, destroying the card overlay and/or large card button if necessary.

        Args:
            location (str): The new location of the card.
            visible_after (bool): Indicates if the card will be visible at its new location.
        """
        previous_location = self.location
        self.location = location
        self.set_rotation(0)
        self.remove_card_location_overlay()

        if not visible_after:
            self.remove_large_card_button()

        if self.location in ["hand", "field"] and previous_location not in ["hand", "field"]:
            self.change_to_movable_card()

    def change_to_movable_card(self):
        """Changes the card to a movable state."""
        self.set_left_click_function(self.start_movement)
        self.set_size(standard_card_width, standard_card_height)
        self.set_z(1)
        self.set_parent(self.board)

    def create_card_location_overlay(self):
        """Creates an overlay for the card. Includes buttons for sending the card to the gy, field, deck, hand, etc."""

        card_location_overlay = utils.find_object_from_name(self.children, "card_location_overlay")

        if card_location_overlay is not None:
            return

        if self.get_rotation() == 0:
            overlay_width = self.width
            overlay_height = self.height
        else:
            overlay_width = self.height
            overlay_height = self.width

        button_space = 5
        number_of_buttons = 4
        total_height = overlay_height - button_space * (2 + number_of_buttons)
        button_height = total_height / number_of_buttons
        button_width = overlay_width - 2 * button_space

        overlay = assets.Overlay(x=self.x + self.width, y=self.y, z=self.z, width=overlay_width, height=overlay_height,
                                 name="card_location_overlay", parent=self, static=False,
                                 external_process_function=utils.destroy_on_external_clicks)
        overlay.external_process_arguments = [overlay, [overlay.get_rect(), self.get_rect()]]
        overlay_close_button = utils.find_object_from_name(overlay.children, "close_btn")
        overlay_close_button.destroy()
        self.add_child(overlay)
        board = utils.find_object_from_name(game_engine.get_scene_manager().get_current_scene().get_objects(), "board")
        board.bump(self)
        starting_location = self.card_starting_location()
        card_location = board.get_location(self)

        large_card_btn = utils.find_object_from_name(self.children, "large_card_btn")
        if large_card_btn is None:
            large_card_btn = self.create_large_card_button()

        [large_card_btn_arg, large_card_btn_allowed_rect_list] = large_card_btn.get_external_process_arguments()
        large_card_btn_allowed_rect_list.append(overlay.get_rect())
        large_card_btn.set_external_process_arguments([large_card_btn_arg, large_card_btn_allowed_rect_list])

        remove_btn_height = round(overlay_height - button_space * 4)
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

        border = overlay.get_box().get_border()
        if border is not None:
            border_thickness = border.thickness
        else:
            border_thickness = 0
        y = button_space + border_thickness
        used_space = sum([button.height + button_space for button in location_buttons]) + button_space + 2 * border_thickness
        unused_height = (overlay.height - used_space)
        extra_button_space = unused_height / (len(location_buttons)+1)
        for btn in location_buttons:
            btn.set_pos_relative_to_parent(button_space, y + extra_button_space)
            btn.set_z(overlay.z)
            y += btn.height + button_space

        overlay.add_multiple_children(location_buttons)

    def update_card_location_overlay_anchor(self):
        """Updates the card overlay anchor."""
        card_location_overlay = utils.find_object_from_name(self.children, "card_location_overlay")
        if card_location_overlay is not None:
            card_location_overlay.set_pos_relative_to_parent(self.width, 0)

    def create_large_card_button(self):
        """Creates a large card button."""
        large_card_btn = utils.find_object_from_name(self.children, "large_card_btn")
        if large_card_btn is not None:
            return

        scene = game_engine.get_scene_manager().get_current_scene()
        left_side_box = utils.find_object_from_name(scene.get_objects(), "left_side_box")
        if left_side_box is None:
            return
        large_card_offset = (left_side_box.width - large_card_width) / 2

        large_card_btn = assets.Button(x=left_side_box.x + large_card_offset, y=left_side_box.y + large_card_offset,
                                       z=self.z - 0.1,
                                       width=large_card_width,
                                       height=round(large_card_width * card_aspect_ratio),
                                       image_id=self.source_image_id,
                                       name="large_card_btn",
                                       left_click_function=create_large_card_overlay, left_click_args=[self],
                                       key_functions={"r": [self.rotate, []]})

        large_card_btn.set_require_continuous_hovering(False)
        large_card_btn.set_external_process_function(utils.destroy_on_external_clicks)
        large_card_btn.static = True
        allowed_rect_list = [self.get_rect(), large_card_btn.get_rect()]
        card_overlay = utils.find_object_from_name(self.children, "card_location_overlay")
        if card_overlay is not None:
            allowed_rect_list.append(card_overlay.get_rect())
        large_card_btn.set_external_process_arguments([large_card_btn, allowed_rect_list])

        self.add_child(large_card_btn)
        return large_card_btn

    def remove_card_location_overlay(self):
        """Removes the card location overlay."""
        card_location_overlay = utils.find_object_from_name(self.children, "card_location_overlay")
        if card_location_overlay is None:
            return
        card_location_overlay.destroy()

    def remove_large_card_button(self):
        """Removes the large card button."""
        large_card_btn = utils.find_object_from_name(self.children, "large_card_btn")
        if large_card_btn is None:
            return
        large_card_btn.destroy()

    def destroy(self):
        """Destroys the card, extending the base class method."""
        super().destroy()
        self.board.remove_card(self)


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
    width = round((height - close_btn_size - close_btn_offset) / card_aspect_ratio)

    overlay = LargeCardOverlay(x=field_box.x, y=field_box.y, z=2, width=width, height=height, name="large_card_overlay",
                               card=card)
    close_btn = utils.find_object_from_name(overlay.get_buttons(), "close_btn")
    offset = 15

    card_height = overlay.height - 3 * offset - close_btn.height
    card_width = round(card_height / card_aspect_ratio)

    large_card_box = assets.Box(x=overlay.x + offset,
                                y=close_btn.y + offset + close_btn.height,
                                z=overlay.z,
                                width=card_width,
                                height=card_height,
                                source_image_id=card.source_image_id)
    large_card_box.set_parent(overlay)

    allowed_rect_list = [overlay.get_box().get_rect(), large_card_btn.get_rect()]
    overlay.external_process_function = utils.destroy_on_external_clicks
    overlay.external_process_arguments = [overlay, allowed_rect_list]

    large_card_btn.external_process_arguments[1].append(overlay.get_rect())

    overlay.add_child(large_card_box)

    scene.add_object(overlay)


class LargeCardOverlay(assets.Overlay):
    """Overlay for displaying the image of a card in an easily readable way.

    Attributes:
        card (assets.Card): The card the button Overlay should display.
    """

    def __init__(self, x=0, y=0, z=0, width=1540, height=760, alpha=255, name=None, background_color=WHITE,
                 close_btn_size=30, close_btn_offset=5, parent=None, card=None,
                 external_process_function=None, external_process_arguments=None):
        """Initializes a LargeCardOverlay instance.

        Args:
            x (float): The x-coordinate of the overlay.
            y (float): The y-coordinate of the overlay.
            z (int): The z-coordinate of the overlay.
            width (float): The width of the overlay.
            height (float): The height of the overlay.
            alpha (int): The alpha value of the overlay.
            name (str): The name of the overlay.
            background_color: The background color of the overlay.
            close_btn_size (float): The size of the close button.
            close_btn_offset (float): The offset of the close button.
            parent: The parent object.
            card: The card associated with the large overlay.
            external_process_function: The external process function for the overlay.
            external_process_arguments: The external process arguments for the overlay.
        """
        super().__init__(x=x, y=y, z=z, width=width, height=height, alpha=alpha, name=name,
                         background_color=background_color,
                         close_btn_size=close_btn_size, close_btn_offset=close_btn_offset, parent=parent,
                         external_process_function=external_process_function,
                         external_process_arguments=external_process_arguments)
        self.card = card

    def destroy(self):
        """Destroys the large card overlay. Overrides the base class method to remove the large card button from the
        allowed rects list used in the destroy_on_external_clicks function for the associated cards large card button.
        """
        large_card_btn = utils.find_object_from_name(self.card.children, "large_card_btn")
        allowed_rects = large_card_btn.get_external_process_arguments()
        allowed_rects[1].remove(self.get_rect())
        large_card_btn.set_external_process_arguments(allowed_rects)
        super().destroy()


class CardOverlay(assets.Overlay):
    """A class representing an overlay of cards.

        Attributes:
        card_list_function (callable): The function responsible for updating the card list of the overlay.
        cards_per_row (int): The number of cards to be displayed for each row.
        number_of_rows (int): The number of rows to be displayed.
        start_index (int): The index of the first displayed card.
        stop_index (int): The index of the last displayed cards.
        card_list (list): The list containing the cards to be displayed on the overlay.
        cards (list): The list currently in the overlay.
        """

    def __init__(self, x=0, y=0, z=2, width=1540, height=760, alpha=255, static=True, name=None, background_color=WHITE,
                 close_btn_size=30, close_btn_offset=5, parent=None, external_process_function=None,
                 external_process_arguments=None, card_list_function=None):
        """Initializes a CardOverlay instance.

        Args:
            x (float): The x-coordinate of the overlay.
            y (float): The y-coordinate of the overlay.
            z (float): The z-coordinate of the overlay.
            width (float): The width of the overlay.
            height (float): The height of the overlay.
            alpha (int): The alpha value of the overlay.
            static (bool): Indicates whether the overlay is static.
            name (str): The name of the overlay.
            background_color: The background color of the overlay.
            close_btn_size (float): The size of the close button.
            close_btn_offset (float): The offset of the close button.
            parent: The parent object.
            external_process_function: The external process function for the overlay.
            external_process_arguments: The external process arguments for the overlay.
            card_list_function: The function to retrieve the list of cards for the overlay.
        """
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
        """Turns a card into an overlay card.

        Args:
            card: The card to change.
            i (int): The index of the card in the card list.

        Returns:
            Card: The changed overlay card.
        """
        card.set_parent(self)
        x, y, card_width, card_height = self.get_card_info(i)
        card.set_pos(x, y)
        card.set_z(self.z)
        card.set_size(card_width, card_height)
        card.set_left_click_function(card.create_large_card_button)
        card.set_left_hold_function(None)
        return card

    def set_overlay_card(self, card, i):
        """Sets the card in 'cards' to the specified card.

        Args:
            card: The overlay card to set.
            i (int): The index to set the card at.
        """
        if i == len(self.cards):
            self.cards.append(card)
        elif i < len(self.cards):
            self.cards[i] = card
        else:
            raise IndexError("Cannot set self.cards[i] to card, to few cards in the list")

    def update_card_list(self):
        """Updates the list of overlay cards."""
        del self.cards[len(self.card_list):]
        for i, card in enumerate(self.card_list):
            if card not in self.cards:
                self.set_overlay_card(self.create_overlay_card(card, i), i)
            else:
                self.set_overlay_card(card, i)

    def update_card_positions(self):
        """Updates the positions of overlay cards."""
        for i, card in enumerate(self.get_visible_cards()):
            x, y, _, _ = self.get_card_info(i)
            card.set_pos(x=x, y=y)

    def get_card_info(self, i):
        """Gets position and size of the overlay card.

        Args:
            i (int): The index of the card.

        Returns:
            Tuple[int, int, int, int]: The x, y, width, and height of the overlay card.
        """
        max_cards_to_show = self.cards_per_row * self.number_of_rows
        min_x_offset = 10
        min_y_offset = 10
        card_space = 5
        aspect_ratio = card_aspect_ratio

        card_width = round(
            min((self.get_box().height - 2 * min_y_offset - (math.ceil(max_cards_to_show / self.cards_per_row) - 1)
                 * card_space) / (math.ceil(max_cards_to_show / self.cards_per_row) * aspect_ratio),
                (self.get_box().width - 2 * min_x_offset - (self.cards_per_row - 1) * card_space)
                / self.cards_per_row))

        card_height = round(aspect_ratio * card_width)

        x_offset = round(
            (self.get_box().width - (self.cards_per_row - 1) * card_space - self.cards_per_row * card_width) / 2)

        y_offset = round((self.get_box().height - math.ceil(max_cards_to_show / self.cards_per_row - 1) * card_space
                          - math.ceil(max_cards_to_show / self.cards_per_row) * card_height) / 2)
        x = self.get_box().x + x_offset + round(i % self.cards_per_row * (card_space + card_width))
        y = self.get_box().y + y_offset + round(i // self.cards_per_row * (card_space + card_height))
        return x, y, card_width, card_height

    def is_card_visible(self, card=None, i=None):
        """Determines if a card is visible in the overlay, either by using the card itself or its index.

        Args:
            card (Card): The card for which the visibility should be determined.
            i (int): The index of the card in the card list.

        Returns:
            bool: True if the card is visible in the overlay, False otherwise.
        """
        if i is None:
            return card in self.get_visible_cards()
        return self.start_index <= i <= self.stop_index

    def get_visible_cards(self):
        """Gets the visible cards in the overlay.

        Returns:
            list: The list of cards that are visible in the overlay.
        """
        return self.cards[self.start_index:self.stop_index + 1]

    def schedule_processing(self):
        """Schedules processing of the overlay and its cards.

        Returns:
            List: A list of items to be processed.
        """
        items_to_be_processed = []

        items_to_be_processed.extend(self.get_box().schedule_processing())
        for btn in self.get_buttons():
            items_to_be_processed.extend(btn.schedule_processing())

        for j, card in enumerate(reversed(self.cards.copy())):
            i = len(self.cards) - 1 - j
            if not self.is_card_visible(i=i):
                continue
            items_to_be_processed.extend(card.schedule_processing())
        items_to_be_processed.append(self)
        return items_to_be_processed

    def get_displayable_objects(self):
        """Gets the displayable objects within the overlay and updates the card list and their positions.

        Returns:
            List: A list of displayable objects.
        """
        displayable_objects = []

        if self.destroyed:
            return displayable_objects

        displayable_objects.extend(super().get_displayable_objects())

        self.update_card_list()

        self.update_card_positions()
        for j, card in enumerate(reversed(self.cards)):
            i = len(self.cards) - 1 - j
            if not self.is_card_visible(i=i):
                continue

            displayable_objects.extend(card.get_displayable_objects())

        return displayable_objects

    def change_overlay_limits(self, change_in_limits):
        """Changes the start index of the overlay within specified limits.

        Args:
            change_in_limits (int): The change in start index. A positive value moves down, and a negative value
            moves up.
        """
        new_start_index = self.start_index + change_in_limits
        new_stop_index = new_start_index + (self.number_of_rows - 1) * self.cards_per_row + 1
        new_index_out_of_bounds = new_stop_index > len(self.cards)
        if new_index_out_of_bounds and change_in_limits > 0:
            return

        elif new_start_index < 0:
            self.start_index = 0

        else:
            self.start_index += change_in_limits
            self.stop_index += change_in_limits

    def destroy(self):
        super().destroy()
        for card in self.cards:
            card.remove_card_location_overlay()
            card.remove_large_card_button()


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

    token = Card(card_id="token", board=board)
    token.static = True
    x, y = scene.get_default_position()  # TODO: Change this to something else? Perhaps use the board instead. Perhaps
    # use a counter so that all cards don't end up in the same location.
    token.set_pos(x, y)
    token.location = "field"
    board.field.append(token)
    board.card_processing_order.append(token)  # TODO: Perhaps add a method in class Board for the adding of cards.


def destroy_overlays(overlay_name):
    """Destroys all active overlays, and returns whether an overlay with the name same_overlay_name was found.

    Args:
        overlay_name (str): The overlay name to be queried.

    Returns:
        bool: Whether an overlay with the query name was found.
    """
    scene = game_engine.get_scene_manager().get_current_scene()
    same_location_overlay = utils.find_object_from_name(scene.get_objects(), overlay_name)
    overlays = [obj for obj in scene.get_objects() if isinstance(obj, assets.Overlay) and not obj.destroyed]
    number_of_overlays = len(overlays)
    if number_of_overlays == 0:
        return False

    for overlay_to_remove in overlays:
        overlay_to_remove.destroy()

    if same_location_overlay is not None:
        return True

    return False


def create_location_overlay(location_name, card_list_function):
    """Create an overlay displaying cards from a specific location in the game.

    Args:
        location_name (str): The name of the location to display.
        card_list_function (callable): A function returning the list of cards to be displayed.
    """
    scene = game_engine.get_scene_manager().get_current_scene()
    if destroy_overlays(location_name):
        return

    field_box = utils.find_object_from_name(scene.get_objects(), "field_box")
    x_offset = 10
    y_offset = 10
    overlay_width = field_box.width - 2 * x_offset
    overlay_height = field_box.height - 2 * y_offset
    overlay = CardOverlay(x=field_box.x + x_offset, y=field_box.y + y_offset, z=2, width=overlay_width,
                          height=overlay_height, alpha=180, name=location_name,
                          card_list_function=card_list_function)
    small_button_width = 50
    small_button_height = small_button_width

    close_btn = utils.find_object_from_name(overlay.get_buttons(), "close_btn")
    scroll_up_btn = assets.Button(x=overlay.x + overlay_width - small_button_width - x_offset,
                                  y=overlay.y + 2 * y_offset + close_btn.height,
                                  z=overlay.z,
                                  width=small_button_width, height=small_button_height,
                                  image_id=game_engine.load_image(image_location + "up_arrow.png"),
                                  name="scroll_up_btn",
                                  left_trigger_keys=["up"],
                                  left_click_function=overlay.change_overlay_limits,
                                  left_click_args=[-overlay.cards_per_row])

    scroll_down_btn = assets.Button(x=overlay.x + overlay_width - small_button_width - x_offset,
                                    y=overlay.y + overlay_height - small_button_height - y_offset,
                                    z=overlay.z,
                                    width=small_button_width, height=small_button_height,
                                    image_id=game_engine.load_image(image_location + "down_arrow.png"),
                                    name="scroll_down_btn",
                                    left_trigger_keys=["down"],
                                    left_click_function=overlay.change_overlay_limits,
                                    left_click_args=[overlay.cards_per_row])

    overlay.add_multiple_children([scroll_up_btn, scroll_down_btn])
    scene.add_object(overlay)


def create_extra_options_overlay():
    """Creates an overlay containing extra buttons for additional functionality."""
    scene = game_engine.get_scene_manager().get_current_scene()
    if destroy_overlays("extra_options_overlay"):
        return

    field_box = utils.find_object_from_name(scene.get_objects(), "field_box")
    overlay_width = field_box.width
    overlay_height = field_box.height

    options_overlay = assets.Overlay(x=field_box.x, y=field_box.y, z=2,
                                     width=overlay_width, height=overlay_height,
                                     name="extra_options_overlay")

    dice_result_box = assets.Box(x=options_overlay.x + 100 + standard_space, y=options_overlay.y + standard_space,
                                 z=options_overlay.z,
                                 width=100, height=100,
                                 text="?", name="dice_result_box", parent=options_overlay, color=SIENNA,
                                 include_border=False)

    dice_button = assets.Button(x=options_overlay.x + standard_space, y=options_overlay.y + standard_space,
                                z=options_overlay.z, width=100, height=100,
                                parent=options_overlay,
                                image_id=game_engine.load_image(image_location + "dice.png"),
                                name="dice_button")

    dice_button.set_left_click_function(roll_dice, [dice_result_box])

    options_overlay.add_child(dice_button)
    options_overlay.add_child(dice_result_box)
    game_engine.get_scene_manager().get_current_scene().add_object(options_overlay)


def roll_dice(text_box):
    """Rolls a six-sided dice, and modifies the text of the given text box.

    Args:
        text_box (assets.Box): The box which text should be modified.
    """
    result = random.randint(1, 6)
    text_box.set_text(str(result))


def closest_color(color_dict, reference_color):
    """Finds the closest color in a dictionary to a given color.

    Args:
        color_dict (dict): The dictionary mapping color names to RGB values.
        reference_color (tuple): The RGB values of the color to match.

    Returns:
        str: The name of the color with the closest match in the dictionary.

    Raises:
        ValueError: If no good match for the color is found.
    """
    min_distance = 3 * 255 ** 2
    saved_color_name = None
    for color_name, color in color_dict.items():
        color_distance = 0
        for i in range(3):
            color_distance += (color[i] - reference_color[i]) ** 2
        if color_distance <= min_distance:
            min_distance = color_distance
            saved_color_name = color_name

    if saved_color_name is None:
        raise ValueError("No good match for the color.")
    return saved_color_name


def card_sort_card_type(cards):
    """Sorts a list of cards in-place based on their card type using insertion sort.

    Args:
        cards (list): The list of cards to be sorted.
    """
    i = 1
    while i < len(cards):
        temp_card = cards[i]
        j = i - 1
        while j >= 0 and card_type_int(cards[j]) > card_type_int(temp_card):
            cards[j + 1] = cards[j]
            j = j - 1
        cards[j + 1] = temp_card
        i = i + 1


def card_type_int(card):
    """Converts a card type string to an integer for sorting purposes.

    Args:
        card: The card object.

    Returns:
        int: The integer value representing the card type.

    Raises:
        ValueError: If the card type is not valid.
    """
    card_type = card.get_card_type()
    card_type_order = ["normal", "effect", "spell", "trap", "ritual", "xyz", "synchro", "fusion", "link", "token"]
    for i, element in enumerate(card_type_order):
        if card_type == element:
            return i
    raise ValueError(f"{card_type} is not a valid card type")

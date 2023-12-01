import pygame
from environment import environment, scene_manager
from constants import *


def clamp(x, lower, upper):
    if x < lower:
        return lower
    elif x > upper:
        return upper
    return x


def card_sort_card_type(cards):
    """An in-place sorting algorithm that uses insertion sort to sort cards based on the card type."""
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
    card_type = card.get_card_type()
    card_type_order = ["normal", "effect", "spell",  "trap", "ritual", "xyz", "synchro", "fusion", "link", "token"]
    for i, element in enumerate(card_type_order):
        if card_type == element:
            return i
    raise ValueError("{} is not a valid card type".format(type))


def execute_multiple_functions(functions, argument_list):
    for i, function in enumerate(functions):
        if type(argument_list[i]) is dict:
            function(**argument_list[i])
        else:
            function(*argument_list[i])


def find_object_from_name(obj_list, name):
    for obj in obj_list:
        if hasattr(obj, "name") and obj.name == name:
            return obj
    return None


def closest_color(color_dict, color):
    min_distance = 3 * 255 ** 2
    card_type = None
    for key in color_dict.keys():
        color_distance = 0
        for i in range(3):
            color_distance += (color_dict[key][i] - color[i]) ** 2
        if color_distance <= min_distance:
            min_distance = color_distance
            card_type = key

    if card_type is None:
        raise ValueError("No good match for the card type")
    return card_type


def card_starting_location(card_type):
    if card_type in ["normal", "effect", "ritual", "spell", "trap"]:
        return "main_deck"
    elif card_type in ["fusion", "synchro", "xyz", "link"]:
        return "extra_deck"
    return None


def remove_on_external_clicks(obj, allowed_rect_list):
    # TODO: Make this into a method for the assets?
    left_mouse_click = pygame.mouse.get_pressed(num_buttons=3)[0]
    right_mouse_click = pygame.mouse.get_pressed(num_buttons=3)[2]
    mouse_click = left_mouse_click or right_mouse_click

    if not mouse_click:
        return

    mouse_position = environment.get_mouse_position()
    for rect in allowed_rect_list:
        if rect.collidepoint(mouse_position):
            return
    obj.destroy()

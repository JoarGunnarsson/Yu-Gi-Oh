from game_engine import environment


def clamp(x, lower, upper):
    """Clamps a value 'x' to the range ['lower', 'upper'].

     Args:
         x: The value to be clamped.
         lower: The lower bound of the range.
         upper: The upper bound of the range.

     Returns:
         The clamped value within the specified range.
     """
    if x < lower:
        return lower
    elif x > upper:
        return upper
    return x


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
    card_type_order = ["normal", "effect", "spell",  "trap", "ritual", "xyz", "synchro", "fusion", "link", "token"]
    for i, element in enumerate(card_type_order):
        if card_type == element:
            return i
    raise ValueError(f"{card_type} is not a valid card type")


def execute_multiple_functions(functions, argument_list):
    """Executes multiple functions with corresponding argument lists.

    Args:
        functions (list): List of functions to be executed.
        argument_list (list): List of argument lists corresponding to the functions.
    """
    for i, function in enumerate(functions):
        if isinstance(argument_list[i], dict):
            function(**argument_list[i])
        else:
            function(*argument_list[i])


def find_object_from_name(obj_list, name):
    """Finds an object with a specific name in a list.

    Args:
        obj_list (list): The list of objects to search.
        name (str): The name of the object to find.

    Returns:
        The first object with the specified name, or None if not found.
    """
    for obj in obj_list:
        if hasattr(obj, "name") and obj.name == name:
            return obj
    return None


def find_objects_from_type(obj_list, match_type):
    """Finds objects of a specific type in a list.

    Args:
        obj_list (list): The list of objects to search.
        match_type (type): The type of objects to find.

    Returns:
        list: List of objects with the specified type found in the list.
    """
    found_objects = []
    for obj in obj_list:
        if hasattr(obj, "name") and isinstance(obj, match_type):
            found_objects.append(obj)
    return found_objects


def closest_color(color_dict, color):
    """Finds the closest color in a dictionary to a given color.

    Args:
        color_dict (dict): The dictionary mapping color names to RGB values.
        color (tuple): The RGB values of the color to match.

    Returns:
        str: The name of the color with the closest match in the dictionary.

    Raises:
        ValueError: If no good match for the color is found.
    """
    min_distance = 3 * 255 ** 2
    card_type = None
    for key in color_dict:
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
    """Determines the starting location of a card based on its type.

    Args:
        card_type (str): The type of the card.

    Returns:
        str: The starting location of the card (e.g., "main_deck" or "extra_deck").
    """
    if card_type in ["normal", "effect", "ritual", "spell", "trap"]:
        return "main_deck"
    elif card_type in ["fusion", "synchro", "xyz", "link"]:
        return "extra_deck"
    return None


def destroy_on_external_clicks(obj, allowed_rect_list):
    """Destroys an object if a mouse click occurs outside a list of allowed rectangles.

    Args:
        obj: The object to be destroyed.
        allowed_rect_list (list): List of pygame.Rect objects representing allowed areas.
    """
    mouse_click_this_tick = environment.get_left_mouse_click_this_tick() or environment.get_right_mouse_click_this_tick()
    mouse_click_last_tick = environment.get_left_mouse_click_last_tick() or environment.get_right_mouse_click_last_tick()
    if not mouse_click_this_tick or (mouse_click_this_tick and mouse_click_last_tick):
        return

    mouse_position = environment.get_mouse_position()
    for rect in allowed_rect_list:
        if rect.collidepoint(mouse_position):
            return
    obj.destroy()

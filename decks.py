import glob
from constants import *
import requests
import time
import file_operations as file_op


class Deck:
    """Class representing a deck of cards.

       Attributes:
           name (str): The name of the deck.
           main_deck (list): List of card IDs in the main deck.
           extra_deck (list): List of card IDs in the extra deck.
           side_deck (list): List of card IDs in the side deck.
           image_id (int): The ID of the image representing the main card.
       """

    def __init__(self, file_path, main_card_id=None):
        """Initializes a Deck instance.

        Args:
            file_path (str): The file_path of the deck YDK file.
            main_card_id: The ID of the main card in the deck.
        """
        self.main_deck = []
        self.extra_deck = []
        self.side_deck = []

        self.load_deck_from_file(file_path)
        if main_card_id is None:
            if len(self.main_deck) != 0:
                main_card_id = self.main_deck[0]
            else:
                main_card_id = "card_back"

        self.download_necessary_images()

        self.name = file_path.split("/")[-1][:-4]

        image_path = file_op.find_image_path_from_name(main_card_id)
        self.image_id = file_op.load_image(image_path)

    def get_image_id(self):
        """Returns the ID of the image representing the main card.

        Returns:
            int: The image ID.
        """
        return self.image_id

    def load_deck_from_file(self, file_path):
        with open(file_path) as deck_file:
            deck_file_lines = deck_file.read().split("\n")
            deck_file_lines = [x for x in deck_file_lines if x != ""]

            main_deck_start = find_index_by_string(deck_file_lines, "main") + 1
            extra_deck_start = find_index_by_string(deck_file_lines, "extra") + 1
            side_deck_start = find_index_by_string(deck_file_lines, "side") + 1

            self.main_deck = deck_file_lines[main_deck_start:extra_deck_start - 1]
            self.extra_deck = deck_file_lines[extra_deck_start:side_deck_start - 1]
            self.side_deck = deck_file_lines[side_deck_start:]

    def download_necessary_images(self):
        self.download_card_list_images(self.main_deck)
        self.download_card_list_images(self.extra_deck)
        self.download_card_list_images(self.side_deck)

    @staticmethod
    def download_card_list_images(card_list):
        for card_id in card_list.copy():
            if not file_op.image_exists(card_id):
                try:
                    print(f"Requesting card image with id {card_id} from ygoprodeck.com.")
                    response = requests.get(f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg")
                    if response.status_code != 200:
                        print(f"Card id {card_id} is not a valid card id.")
                        card_list.remove(card_id)
                        continue
                    card_image = response.content
                    file_op.save_image(card_image, f"{image_location}{card_id}.jpg")
                    time.sleep(0.5)
                except requests.exceptions.RequestException:
                    print(f"Error with requesting card image with id {card_id} from YGOPRODECK.COM API. Card will be "
                          f"temporarily ignored. \nPlease try again later.")
                    card_list.remove(card_id)


def write_deck_to_file(deck):
    if deck.name + ".ydk" in glob.glob("./Decks/*.ydk"):
        while True:
            confirmation = input("Are you sure you want to overwrite the deck {}? y/n\n")
            if "y" in confirmation:
                break
            elif "n" in confirmation:
                return
            else:
                print("Not a valid answer.")

    file_contents = ["#main\n"]
    for card in deck.main_deck:
        file_contents.append(card + "\n")

    file_contents.append("#extra\n")

    for card in deck.extra_deck:
        file_contents.append(card + "\n")
    file_contents.append("!side\n")

    for card in deck.extra_deck:
        file_contents.append(card + "\n")

    with open("Decks/"+deck.name + ".ydk", "w") as file:
        file.write("".join(file_contents))


def find_index_by_string(array, string):
    """Finds the index of an element that contains a certain string in an array.

    Args:
        array (list): The array to be searched
        string (str): The string to match the elements against.

    Returns:
        int or None: The index of the element if it exists, None otherwise.
    """
    for i, element in enumerate(array):
        if string in element:
            return i
    return None


DECKS = []

for deck_path in glob.glob("./Decks/*.ydk"):
    DECKS.append(Deck(deck_path))

from constants import *
import game_engine


class Deck:
    """Class representing a deck of cards.

       Attributes:
           name (str): The name of the deck.
           cards (list): List of card IDs in the deck.
           image_id (int): The ID of the image representing the main card.
       """

    def __init__(self, name="", cards=None, main_card_id=None):
        """Initializes a Deck instance.

        Args:
            name (str): The name of the deck.
            cards (list): List of card IDs in the deck.
            main_card_id: The ID of the main card in the deck.
        """
        if cards is None:
            self.cards = []
        else:
            self.cards = cards
        if main_card_id is None:
            main_card_id = cards[0]

        self.name = name
        self.image_id = game_engine.load_image(image_location + main_card_id + ".jpg")

    def get_image_id(self):
        """Returns the ID of the image representing the main card.

        Returns:
            int: The image ID.
        """
        return self.image_id


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

beast_cards = ["10602628", "13382806", "13382806", "19882096", "19882096", "20129614", "20618850", "20618850",
               "30439101", "30439101", "34800281", "34800281", "34800281", "34976176", "37256135", "38745520",
               "38745520", "40975243", "40975243", "46877100", "46877100", "46877100", "52331012",
               "54191698", "55990317", "55990317", "56063182", "56401775", "57523313", "62709239", "63644830",
               "66712905", "67835547", "68957034", "73079836", "73304257", "76981308", "76981308",
               "76981308", "78868119", "78868119", "79606837", "81019803", "81439173", "82134632", "83488497",
               "84224627", "93229151", "94076521", "94076521", "9486959", "95245571", "95245571",
               "95245571", "97661969", "98416533", "98416533", "99726621"]

test_cards = ["14517422", "14517422", "14517422", "18168997", "18168997", "22110647", "25339070", "25339070",
              "25451652", "26357901", "26357901", "28427869", "28427869", "28427869", "30439101", "35726888",
              "35726888", "35726888", "38120068", "3814632", "38904695", "41209827", "4167084", "43316238",
              "45420955", "48130397", "48130397", "49565413", "50501121", "50501121", "50501121", "52119435",
              "52645235", "52840267", "52840267", "52840267", "5402805", "55289183", "55289183", "59900655",
              "69946549", "72892473", "74335036", "74335036", "78868119", "78868119", "79933029", "82105704",
              "82105704", "82134632", "82773292", "83340560", "83764719", "87112784", "87112784", "88120966",
              "9486959", "transparent_card", "transparent_card", "transparent_card", "transparent_card", "gy_icon"]

DECKS = [Deck(name="Spellcaster", cards=spellcaster_cards, main_card_id="1003840"),
         Deck(name="Darklord", cards=darklord_cards, main_card_id="14517422"),
         Deck(name="Darklord 2", cards=darklord_2_cards, main_card_id="14517422"),
         Deck(name="Beast", cards=beast_cards, main_card_id="98416533"),
         Deck(name="Test Deck", cards=test_cards, main_card_id="token")]

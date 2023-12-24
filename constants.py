import os
FPS = 30
BLACK = (0, 0, 0)
GREY = (50, 50, 50)
LIGHT_GREY = (169, 169, 169)
WHITE = (255, 255, 255)
SADDLE_BROWN = (139, 69, 19)
SIENNA = (160, 82, 45)
standard_font_size = 40
card_aspect_ratio = 1.45843230404
standard_card_width = 100
standard_card_height = int(standard_card_width * card_aspect_ratio)
standard_space = 10
large_card_width = 300
large_card_height = int(large_card_width * card_aspect_ratio)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
card_image_location = ROOT_DIR + "/Images/"

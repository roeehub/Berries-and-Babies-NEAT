
# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (220, 15, 243)
PURPLE = (190, 0, 190)
DARK_PURPLE = (65, 0, 65)
DARKER_PURPLE = (45, 0, 45)
BROWN = (138, 126, 46)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 102)
RED = (255, 0, 0)
YELLOW = (222, 225, 0)
GRAY = (66, 66, 66)
GREEN = (0, 255, 0)
LEAF_GREEN = (0, 160, 0)
TREE_TOP_GREEN = (0, 100, 0)
ORANGE = (255, 128, 0)
B_5 = (153, 0, 153)
B_4 = (203, 0, 203)
B_3 = (255, 0, 255)
B_2 = (255, 51, 255)
B_1 = (255, 102, 255)
B_0 = (255, 204, 255)
TEXTCOLOR = (255, 255, 255)

# playground params
BOARD_WIDTH = 720
BOARD_HEIGHT = 720
CELL_EDGE_SIZE = 18
NUM_OF_REAL_COLS = BOARD_WIDTH // CELL_EDGE_SIZE
NUM_OF_REAL_ROWS = BOARD_HEIGHT // CELL_EDGE_SIZE

# time
ROUND_TIME = 0.01
LOOP = False    # for time management

# main game
DEBUG = False
DRAW = True

# player params
DEFAULT_POP_SIZE = 20
STARVATION_DEATH = 20
BERRIE_FOOD_BONUS = 6

# berrie params
# CHANCE_BARRIE_FALLS = 0.05  # average 100 -- obsolete?
BERRIE_GROW_CHANCE = 0.75
REGROW_FREQUENCY = 25

# player params
VISIBLE_PLAYERS_NUM = 3
PLAYER_COLORS = [WHITE, BLACK, BLUE, YELLOW, ORANGE, GRAY, DARK_BLUE]
BOARD_OFFSET = 700
MAX_MOVES = 200
NUM_OF_GAMES = 5


def log(s):
    if DEBUG:
        print(s)



import pygame
from enum import Enum
from config import *


class Status(Enum):
    FREE = 0
    TRUNK = 1
    BERRIE = 2
    ENEMY = 3


class Cell:
    def __init__(self, surface, status=Status.FREE, color=BROWN):
        self.surface = surface
        self.color = color
        self.status = status
        self.player_ids_curr = set()
        self.player_ids_next = set()


class CellP2(Cell):  # new!
    def __init__(self, surface, status=Status.FREE, color=BROWN):
        super().__init__(surface, status, color)
        # self.berries_left = berries_num
        self.berrie_color = [B_0, B_1, B_2, B_3, B_4, B_5]
        self.ids_mark_on_cell = set()


class CellGridP2:
    def __init__(self, surface):
        self.surface = surface
        self.grid = [[CellP2(surface) for cell in range(NUM_OF_REAL_COLS)] for row in range(NUM_OF_REAL_ROWS)]
        self.eggs = set()
        for col in range(NUM_OF_REAL_COLS):
            self.set_tree(0, col)
            self.set_tree(NUM_OF_REAL_ROWS - 1, col)
        for row in range(1, NUM_OF_REAL_ROWS - 1):
            self.set_tree(row, 0)
            self.set_tree(row, NUM_OF_REAL_COLS - 1)

    def reset(self):
        for row in range(NUM_OF_REAL_ROWS):
            for col in range(NUM_OF_REAL_COLS):
                self.grid[row][col].status = Status.FREE
                self.grid[row][col].color = BROWN
                self.grid[row][col].player_ids_next.clear()
                self.grid[row][col].player_ids_curr.clear()
                self.grid[row][col].ids_mark_on_cell.clear()
        for col in range(NUM_OF_REAL_COLS):
            self.set_tree(0, col)
            self.set_tree(NUM_OF_REAL_ROWS - 1, col)
        for row in range(1, NUM_OF_REAL_ROWS - 1):
            self.set_tree(row, 0)
            self.set_tree(row, NUM_OF_REAL_COLS - 1)

    def set_tree(self, row, col, tree_top_color=TREE_TOP_GREEN, leaf_color=LEAF_GREEN):
        self.grid[row][col].status = Status.TRUNK
        self.grid[row][col].color = tree_top_color

        # LEAVES setup TODO - to keep!
        # if row + 1 < NUM_OF_REAL_ROWS and self.grid[row + 1][col].status in (Status.FREE, Status.BERRIE):
        #     self.grid[row + 1][col].status = Status.LEAVES
        #     self.grid[row + 1][col].color = leaf_color
        # if row - 1 >= 0 and self.grid[row - 1][col].status in (Status.FREE, Status.BERRIE):
        #     self.grid[row - 1][col].status = Status.LEAVES
        #     self.grid[row - 1][col].color = leaf_color
        # if col + 1 < NUM_OF_REAL_COLS and self.grid[row][col + 1].status in (Status.FREE, Status.BERRIE):
        #     self.grid[row][col + 1].status = Status.LEAVES
        #     self.grid[row][col + 1].color = leaf_color
        # if col - 1 >= 0 and self.grid[row][col - 1].status in (Status.FREE, Status.BERRIE):
        #     self.grid[row][col - 1].status = Status.LEAVES
        #     self.grid[row][col - 1].color = leaf_color

    def set_trees(self, arr, tree_top_color=TREE_TOP_GREEN, leaf_color=LEAF_GREEN):
        for row, col in arr:
            self.set_tree(row, col, tree_top_color, leaf_color)

    def set_flag(self, row, col, color=YELLOW):
        self.grid[row][col].status = Status.FLAG
        self.grid[row][col].color = color

    def set_enemy(self, row, col, color=RED):
        self.grid[row][col].status = Status.ENEMY
        self.grid[row][col].color = color

    def set_berrie_bush(self, row, col, color=PURPLE):
        if self.grid[row][col].status == Status.FREE:
            self.grid[row][col].status = Status.BERRIE
            self.grid[row][col].color = color

    def regrow_berries(self):
        for row in range(NUM_OF_REAL_ROWS):
            for col in range(NUM_OF_REAL_COLS):
                if self.grid[row][col].color == B_1:
                    self.grid[row][col].status = Status.BERRIE
                    # self.grid[row][col].color = B_5
                    self.grid[row][col].ids_mark_on_cell.clear()

    def add_player_to_cell(self, row, col, player_id):
        self.grid[row][col].player_ids_curr.add(player_id)
        self.grid[row][col].ids_mark_on_cell.add(player_id // 100)

    def remove_player_from_cell(self, row, col, player_id):
        self.grid[row][col].player_ids_curr.remove(player_id)

    def update_players_in_cells(self):
        for row in range(NUM_OF_REAL_ROWS):
            for col in range(NUM_OF_REAL_COLS):
                self.grid[row][col].player_ids_curr = self.grid[row][col].player_ids_next.copy()
                self.grid[row][col].player_ids_next.clear()

    def draw_grid(self, board_offset_x, board_offset_y, draw):
        left = board_offset_x
        top = board_offset_y
        if draw:
            for row in range(NUM_OF_REAL_ROWS):
                for col in range(NUM_OF_REAL_COLS):
                    cell = self.grid[row][col]
                    square = pygame.Rect(left, top, CELL_EDGE_SIZE, CELL_EDGE_SIZE)
                    pygame.draw.rect(cell.surface, cell.color, square)
                    left += CELL_EDGE_SIZE

                left = board_offset_x
                top += CELL_EDGE_SIZE


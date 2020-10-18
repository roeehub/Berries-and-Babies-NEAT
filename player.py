import pygame
import Cell
from config import *

DIRECTIONS = {'UP': 0, 'DOWN': 1, 'LEFT': 2, 'RIGHT': 3, 'UP_RIGHT': 4, 'UP_LEFT': 5, 'DOWN_RIGHT': 6, 'DOWN_LEFT': 7}


class Player:
    """
    A Player object. Each player is a member of a single colony (one square).
    It can Eat berries, bump into walls, reproduce and die.


    Important Attributes
    --------------------

    self.cell_grid:
        The cell grid the player lives on.

    self.row/col:
        Player location on grid




    Important Methods
    -----------------



    """
    def __init__(self, p_id, cell_grid, start_row, start_col, board_offset_x, board_offset_y,
                 color=WHITE, last_rep_time=-10):
        self.id = p_id
        self.cell_grid = cell_grid
        self.row = start_row
        self.col = start_col
        self.hunger = 0
        self.color = color
        self.is_alive = True
        self.draw = False
        self.board_offset_x = board_offset_x
        self.board_offset_y = board_offset_y
        self.last_time_reproduced = last_rep_time
        self.info_arr = self.set_antennae()  # bad name
        self.cell_grid.add_player_to_cell(self.row, self.col, self.id)

    def set_antennae(self):
        info_arr = []
        row = self.row
        col = self.col
        start_row = row - 2
        start_col = col - 2
        for i in range(5):
            if 0 <= start_row + i <= NUM_OF_REAL_ROWS - 1:
                for j in range(5):
                    if 0 <= start_col + j <= NUM_OF_REAL_COLS - 1:
                        cell = self.cell_grid.grid[start_row + i][start_col + j]
                        friend = False
                        for id in cell.player_ids_curr:
                            if id // 10 == self.id // 10:
                                friend = True
                                break
                        if friend:
                            info_arr.append(Cell.Status.ENEMY.value * 10)  # 30  TODO change to friend
                        else:   # berrie
                            info_arr.append(cell.status.value * 10)  # 20

                    else:
                        info_arr.append(-1)

            else:
                info_arr.extend([-1, -1, -1, -1, -1])

        assert(len(info_arr) == 25)
        return info_arr

    def die(self):
        self.is_alive = False
        if self.draw:
            self.leave_cell()

    def draw_player(self):
        if self.draw:
            player_left = self.col * CELL_EDGE_SIZE + self.board_offset_x
            player_top = self.row * CELL_EDGE_SIZE + self.board_offset_y
            player_square = pygame.Rect(player_left, player_top, CELL_EDGE_SIZE, CELL_EDGE_SIZE)
            # spike_left = self.spike_col * CELL_EDGE_SIZE + 3
            # spike_top = self.spike_row * CELL_EDGE_SIZE + 3
            # spike_square = pygame.Rect(spike_left, spike_top, 4, 4)
            pygame.draw.rect(self.cell_grid.surface, self.color, player_square)
            # pygame.draw.rect(self.cell_grid.surface, RED, spike_square)

    def leave_cell(self):
        if self.draw:
            cell = self.cell_grid.grid[self.row][self.col]
            left = self.col * CELL_EDGE_SIZE + self.board_offset_x
            top = self.row * CELL_EDGE_SIZE + self.board_offset_y
            square = pygame.Rect(left, top, CELL_EDGE_SIZE, CELL_EDGE_SIZE)
            pygame.draw.rect(self.cell_grid.surface, cell.color, square)
        # cell2 = self.cell_grid.grid[self.spike_row][self.spike_col]
        # spike_left = self.spike_col * CELL_EDGE_SIZE
        # spike_top = self.spike_row * CELL_EDGE_SIZE
        # spike_square = pygame.Rect(spike_left, spike_top, CELL_EDGE_SIZE, CELL_EDGE_SIZE)
        # pygame.draw.rect(self.cell_grid.surface, cell2.color, spike_square)

    def move(self, direction, round_num):
        found_berrie = False
        hit_a_wall = 0
        if direction == DIRECTIONS['UP']:
            row_delta = -1
            col_delta = 0
        elif direction == DIRECTIONS['DOWN']:
            row_delta = 1
            col_delta = 0
        elif direction == DIRECTIONS['LEFT']:
            row_delta = 0
            col_delta = -1
        elif direction == DIRECTIONS['RIGHT']:
            row_delta = 0
            col_delta = 1
        elif direction == DIRECTIONS['UP_RIGHT']:
            row_delta = -1
            col_delta = 1
        elif direction == DIRECTIONS['DOWN_RIGHT']:
            row_delta = 1
            col_delta = 1
        elif direction == DIRECTIONS['UP_LEFT']:
            row_delta = -1
            col_delta = -1
        elif direction == DIRECTIONS['DOWN_LEFT']:
            row_delta = 1
            col_delta = -1
        else:
            raise Exception

        next_cell = self.cell_grid.grid[self.row + row_delta][self.col + col_delta]

        player_group = self.id // 100
        if next_cell.status is Cell.Status.TRUNK:
            hit_a_wall = 1
        elif player_group in set(map(lambda x: x // 100, next_cell.player_ids_curr)):
            hit_a_wall = 0
        elif (player_group in next_cell.player_ids_curr or player_group in next_cell.player_ids_next) and \
                round_num - self.last_time_reproduced > 15:
            self.cell_grid.eggs.add((self.row + row_delta, self.col + col_delta, player_group, self.color))
            self.last_time_reproduced = round_num
        else:
            if next_cell.status == Cell.Status.BERRIE and player_group not in next_cell.ids_mark_on_cell:
                found_berrie = True
                next_cell.ids_mark_on_cell.add(player_group)
                # next_cell.color = B_1
                next_cell.status = Cell.Status.FREE

            if self.draw:
                self.leave_cell()
            self.row += row_delta
            self.col += col_delta
            next_cell.player_ids_next.add(self.id)
            if self.draw:
                self.draw_player()

        return hit_a_wall, found_berrie

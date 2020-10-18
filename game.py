from menus import *
import os
import pygame
import pickle
import Cell
from config import *
from threading import Timer
import neat
import random
from player import Player


class Game:
    """
    A Game object.


    Important Attributes & values
    -----------------------------

    gen_counter:
        A global variable for the number of generations in a run.

    self.display_viewed:  TODO - self.top_view
        The pygame.Surface object that is seen by the player.

    self.*_KEY:
        A recording of a key press.

    self.loop:
        Used in self.allow_another_loop to control round time.

    self.*_menu
        A *Menu object.

    self.cell_grid:
        The CellGrid object of the game.

    self.config:
        Configuration for neat.


    Important Methods
    -----------------

    game_loop(self):
        Wrapper function for self.run_neat.

    run_neat(self):
        Run the simulation. Set the reporters (for specs) and save the winner.

    eval_genomes(self, ...)
        The main function in which the genomes are evaluated.
        Functions that start with _ and __ are first and second order
        auxiliary functions for this one.

    _generation_loop(self, ...):
        The game loop of a single generation

    check_events(self):
        Record key presses.

    draw_text(self, ...):
        Draw text on the given surface.

    adjust_fitness(...):
        All fitness modifications of a genome is done here.

    show_specs(self):
        Show advance neat specs during simulation (when in NEAT specs mode).

    """
    gen_counter = -1

    def __init__(self, config_file):
        # pygame and windows
        pygame.init()
        self.base_window = pygame.display.set_mode(flags=pygame.FULLSCREEN | pygame.SCALED, size=(1920, 1080))
        self.DISPLAY_W, self.DISPLAY_H = pygame.display.get_surface().get_size()
        self.display_viewed = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        pygame.display.set_caption("B & B")
        icon = pygame.image.load('assets/blueberry.png')
        pygame.display.set_icon(icon)
        # gameplay and style
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.ENTER_KEY, self.BACK_KEY, self.LEFT_KEY, self.RIGHT_KEY = \
            False, False, False, False, False, False
        self.font_name = 'assets/XPAIDERP.TTF'
        self.background = DARKER_PURPLE
        self.loop = LOOP
        # menus
        self.main_menu = MainMenu(self)
        self.setup_menu = SetupMenu(self)
        self.quit_menu = QuitMenu(self)
        self.curr_menu = self.main_menu
        # board and setup
        self.cell_grid = Cell.CellGridP2(self.display_viewed)
        self.board_offset_x = self.DISPLAY_W - BOARD_WIDTH
        self.board_offset_y = self.DISPLAY_H - BOARD_HEIGHT
        self.draw = DRAW
        self.berrie_fitness_bonus = 1   # this value is changed in self._draw_sim_board
        self.starvation_death = STARVATION_DEATH
        self.visible = VISIBLE_PLAYERS_NUM
        self.regrow = REGROW_FREQUENCY
        self.neat_specs = 'NO'
        self.round_time = ROUND_TIME
        # Load configuration.
        local_dir = os.path.dirname(__file__)
        self.config_path = os.path.join(local_dir, 'config-feedforward.txt')
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                  neat.DefaultStagnation, config_file)

    def check_events(self):
        """ Record key presses. """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                # self.curr_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.ENTER_KEY = True
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True
                if event.key == pygame.K_RIGHT:
                    self.RIGHT_KEY = True
                if event.key == pygame.K_LEFT:
                    self.LEFT_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.ENTER_KEY, self.BACK_KEY, self.RIGHT_KEY, self.LEFT_KEY = \
            False, False, False, False, False, False

    def draw_text(self, text, size, x, y, color=WHITE, surface=None, easy_read=False):
        """
        Draw text on the given surface.
        easy_read is for using a different font.
        """
        if easy_read:
            font = pygame.font.Font('assets/Letters for Learners.ttf', size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (x, y)
        else:
            font = pygame.font.Font(self.font_name, size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
        if surface is not None:
            surface.blit(text_surface, text_rect)
        else:
            self.display_viewed.blit(text_surface, text_rect)

    def game_loop(self):
        if self.playing:
            self.run_neat()
            self.playing = False

    def run_neat(self):

        # Create the population, which is the top-level object for a NEAT run_neat.
        p = neat.Population(self.config)
        p.add_reporter(neat.FileReporter(True, 'specs.txt'))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(5))

        self.display_viewed.fill(self.background)
        self.draw_text("Loading", 35, self.DISPLAY_W / 2, self.DISPLAY_H / 2)
        self.base_window.blit(self.display_viewed, (0, 0))
        pygame.display.update()
        winner = p.run(self.eval_genomes, NUM_OF_GAMES)
        # save winner
        if self.gen_counter + 1 == NUM_OF_GAMES:
            with open("winner.pkl", "wb") as f:
                pickle.dump(winner, f)
                f.close()

    def eval_genomes(self, genomes, config):
        """
        The main function in which the genomes are evaluated .
        Parameter config is never used (must be passed for NEAT reasons).
        """
        # NEAT setup
        colonies = []
        nets = []
        genomes_copy = []

        self.gen_counter += 1
        self._draw_sim_text()
        self._draw_sim_board()
        self._create_nets_and_fill_colonies(genomes, genomes_copy, nets, colonies)
        res = self._generation_loop(self.draw, colonies, nets, self.berrie_fitness_bonus, genomes_copy, self.cell_grid)
        self.cell_grid.reset()
        return res

    def _draw_sim_text(self):
        self.display_viewed.fill(self.background)
        if self.neat_specs == 'YES':
            if self.gen_counter > 0:
                self.show_specs()
            self.board_offset_x = self.DISPLAY_W - BOARD_WIDTH
            self.board_offset_y = self.DISPLAY_H - BOARD_HEIGHT
            curr_x, curr_y = self.DISPLAY_W * (4 / 5) - 120, self.DISPLAY_H * (1 / 5) + 60
        else:
            self.board_offset_x = (self.DISPLAY_W - BOARD_WIDTH) / 2
            self.board_offset_y = (self.DISPLAY_H - BOARD_HEIGHT) / 2
            curr_x, curr_y = self.DISPLAY_W / 2 - 180, self.DISPLAY_H * (1/10)

        self.draw_text("Current Generation: {}".format(self.gen_counter), 50, curr_x, curr_y, WHITE,
                       self.display_viewed, True)

    def _draw_sim_board(self):
        self.plant_default_jungle(self.cell_grid)
        berrie_count = self.plant_berries(self.cell_grid, 1, B_5)
        self.berrie_fitness_bonus = round((NUM_OF_REAL_ROWS * NUM_OF_REAL_COLS * 5) / berrie_count)
        self.cell_grid.draw_grid(self.board_offset_x, self.board_offset_y, self.draw)

    def _create_nets_and_fill_colonies(self, genomes, genomes_copy, nets, colonies):
        colors = [WHITE, BLACK, BLUE, YELLOW, ORANGE, GRAY, DARK_BLUE]
        visible_players = random.choices(range(len(genomes)), k=self.visible)
        for i, (genome_id, genome) in enumerate(genomes):
            colony = []
            self.adjust_fitness(genome, 'START')
            genomes_copy.append(genome)
            net = neat.nn.FeedForwardNetwork.create(genome, self.config)
            nets.append(net)
            if len(visible_players) < 7 and i in visible_players:
                color = colors.pop()
            else:
                color = random.choice(colors)
            for j, coordinate in enumerate(self.__get_spawn_coordinates()):
                player = Player((i * 100) + j, self.cell_grid, coordinate[0], coordinate[1], self.board_offset_x,
                                self.board_offset_y, color)
                if self.draw and i in visible_players:
                    player.draw = True
                colony.append(player)
            colonies.append(colony)

    @staticmethod
    def __get_spawn_coordinates():
        spawn_coors = [(1, 3), (1, 10), (2, 15), (2, 22), (2, 31), (8, 1), (8, 8), (8, 17), (10, 24), (8, 31), (17, 1),
                       (16, 10), (15, 17), (16, 23), (15, 30), (24, 3), (23, 8), (22, 16), (24, 24), (24, 30), (29, 1),
                       (29, 10), (31, 15), (31, 23), (29, 29)]
        spawn_coors2 = [(1, 4), (1, 11), (2, 16), (2, 21), (2, 32), (8, 2), (8, 9), (8, 18), (10, 23), (8, 32), (17, 2),
                        (16, 11), (15, 16), (16, 24), (15, 31), (24, 4), (23, 9), (22, 17), (24, 25), (24, 29), (29, 2),
                        (29, 11), (31, 16), (31, 22), (29, 28)]
        spawn_coors.extend(spawn_coors2)
        return spawn_coors

    def _generation_loop(self, draw, colonies, nets, berrie_fitness_bonus, genomes_copy, cell_grid):
        """ The game loop of a single generation """
        running = True
        num_of_moves = 0  # TODO moves --> days
        while running:
            if draw:
                timer = Timer(self.round_time, self.allow_another_loop)
                timer.start()

            living_players = self.__move_players(colonies, nets, genomes_copy, berrie_fitness_bonus, num_of_moves)
            if living_players == 0:
                return 0

            # plan next move
            for colony in colonies:
                for player in colony:
                    player.info_arr = player.set_antennae()
            # update hunger
            for colony_index, colony in enumerate(colonies):
                for player in colony:
                    player.hunger += 1
                    if player.hunger >= self.starvation_death:
                        player.die()
            # not likely to happen
            num_of_moves += 1
            if num_of_moves > MAX_MOVES:
                return 0
            # berries grow back
            if num_of_moves % self.regrow == 0:
                cell_grid.regrow_berries()
                cell_grid.draw_grid(self.board_offset_x, self.board_offset_y, self.draw)
            # babies are born
            for egg in cell_grid.eggs:
                player = Player(egg[2] * 100, cell_grid, egg[0], egg[1], egg[3], num_of_moves)
                colonies[egg[2]].append(player)
                self.adjust_fitness(genomes_copy[egg[2]], 'EGG')
                # print("someone was born!")
            cell_grid.eggs.clear()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return -1
                    elif event.key == pygame.K_p:
                        running = self.pause()
            # time control
            if draw:
                while not self.loop:
                    pass
                self.loop = False
            self.base_window.blit(self.display_viewed, (0, 0))
            pygame.display.update()

    def __move_players(self, colonies, nets, genomes_copy, berrie_fitness_bonus, num_of_moves):
        """ moves all players on board and returns how many are still alive """
        living_players = 0
        for index, player_list in enumerate(colonies):
            for player in player_list:
                if player.is_alive:
                    if player.row == 1 or player.row == NUM_OF_REAL_ROWS - 2 or \
                            player.col == 1 or player.col == NUM_OF_REAL_COLS - 1:
                        player.die()
                        continue
                    living_players += 1
                    outputs = nets[index].activate(player.info_arr)
                    direction = outputs.index(max(outputs))
                    (hit_wall, found_berrie) = player.move(direction, num_of_moves)

                    if found_berrie:
                        self.adjust_fitness(genomes_copy[index], 'BERRIE', berrie_fitness_bonus)
                        player.hunger -= BERRIE_FOOD_BONUS
                        if player.hunger < 0:
                            player.hunger = 0
                    if hit_wall == 1:
                        self.adjust_fitness(genomes_copy[index], 'WALL')
        return living_players

    @staticmethod
    def adjust_fitness(genome, case, berrie_bonus=0):
        """ modify fitness of a given genome according to case"""
        if case == 'EGG':
            genome.fitness += 100
        elif case == 'WALL':
            genome.fitness -= 2
        elif case == 'BERRIE':
            genome.fitness += berrie_bonus * 2
        elif case == 'START':
            genome.fitness = 0
        else:
            print(case)
            raise Exception

    @staticmethod
    def plant_default_jungle(grid):
        """ draw the default jungle on the board """
        seeds = []
        cols = [1, 4, 4, 9, 9, 14, 24, 28, 30, 32, 37]
        col_roots = [37, 6, 10, 11, 22, 15, 20, 33, 1, 18, 8]
        col_lengths = [2, 13, 6, 4, 7, 2, 6, 6, 12, 11, 4]
        for index, l in enumerate(col_lengths):
            for row_delta in range(l):
                seeds.append((col_roots[index] + row_delta, cols[index]))

        rows = [3, 4, 7, 7, 13, 21, 24, 29, 33, 33, 38]
        row_roots = [6, 20, 7, 30, 22, 15, 20, 32, 1, 18, 8]
        row_lengths = [4, 8, 4, 4, 7, 2, 6, 7, 9, 4, 4]
        for index, l in enumerate(row_lengths):
            for col_delta in range(l):
                seeds.append((rows[index], row_roots[index] + col_delta))

        grid.set_trees(seeds)

    @staticmethod
    def random_jungle(grid, min_num_of_trees, max_num_of_trees, min_tree_size, max_tree_size):
        """ draw a random jungle on the board """
        for tree in range(min_num_of_trees, max_num_of_trees + 1):
            size = random.randint(min_tree_size, max_tree_size)
            row = random.randint(3, NUM_OF_REAL_ROWS - 3)
            col = random.randint(0, NUM_OF_REAL_COLS)
            if random.randint(0, 1) == 1:
                grid.set_trees([(row + s, col) for s in range(size)])  # index out of range !
            else:
                grid.set_trees([(row, col + s) for s in range(size)])  # index out of range !

    @staticmethod
    def plant_berries(grid, spread, color=B_5):
        """ plant berries. currently with only one berrie per bush """
        berrie_count = 0
        for row in range(0, NUM_OF_REAL_ROWS, spread):
            for col in range(0, NUM_OF_REAL_COLS, spread):
                if random.random() > BERRIE_GROW_CHANCE:
                    grid.set_berrie_bush(row, col, color)
                    berrie_count += 1

        return berrie_count

    def show_specs(self):
        """
        Show advance neat specs during simulation.
        Fine-tuned to fit well in the simulation window.
        """
        self.draw_text("Previous Generation results:", 50, 100, 50, WHITE, self.display_viewed, True)
        info_text_y_offset = 100
        ratios = [14, 13, 12, 20, 19, 20, 20]
        done = False
        with open('specs.txt', 'r+') as specs:
            for k, line in enumerate(specs):
                if k in {0, 1}:
                    self.draw_text(line[:-1], 50, 100, info_text_y_offset + k * 35, WHITE,
                                   self.display_viewed, True)
                    continue
                final_line = "       "
                word_list = line.split()
                if k == 2:
                    short_line = ""
                    for word in word_list:
                        if "Mean" in word:
                            short_line += word[:-4]
                            break
                        else:
                            short_line += word + " "
                    self.draw_text(short_line, 50, 100, info_text_y_offset + k * 35, WHITE,
                                   self.display_viewed, True)
                    continue
                if k == 3:
                    for x, word in enumerate(word_list):
                        if x == 4:
                            final_line += word + " "
                        else:
                            final_line += word + 8 * " "
                    self.draw_text(final_line, 50, 0, info_text_y_offset + 20 + k * 35, WHITE,
                                   self.display_viewed, True)
                    continue
                if k == 4:
                    for x, word in enumerate(word_list):
                        final_line += word + 8 * " "
                    self.draw_text(final_line, 50, 0, info_text_y_offset + 20 + k * 35, WHITE,
                                   self.display_viewed, True)
                    continue
                for x, word in enumerate(word_list):
                    if "Total" in word:
                        done = True
                        break
                    try:
                        num_of_spaces = ratios[x] - len(word) * 2
                        final_line += word + num_of_spaces * " "
                    except IndexError:
                        print("whoops")
                        pass
                if not done:
                    self.draw_text(final_line, 50, 0, info_text_y_offset + 20 + k * 34, WHITE,
                                   self.display_viewed, True)
                else:
                    break
            specs.truncate(0)

    def pause(self):
        """ pause the simulation with the p key """
        pause = True
        self.draw_text("P", 100, self.DISPLAY_W * (4/5), self.DISPLAY_H * (1/5), RED)
        self.base_window.blit(self.display_viewed, (0, 0))
        pygame.display.update()
        while pause:
            for event1 in pygame.event.get():
                if event1.type == pygame.QUIT:
                    return False
                elif event1.type == pygame.KEYDOWN:
                    if event1.key == pygame.K_p:
                        pause = False
        self.draw_text("P", 100, self.DISPLAY_W * (4/5), self.DISPLAY_H * (1/5), self.background)
        self.base_window.blit(self.display_viewed, (0, 0))
        pygame.display.update()
        return True

    def load_best(self):
        """ load the latest winner genome """
        with open("winner.pkl", "rb") as f:
            winner_genome = pickle.load(f)
        self.draw = True
        while self.eval_genomes([(0, winner_genome)], True) != -1:
            continue

    def allow_another_loop(self):
        """ Used with threading to control simulation speed """
        self.loop = True

    @staticmethod
    def quit():
        pygame.quit()

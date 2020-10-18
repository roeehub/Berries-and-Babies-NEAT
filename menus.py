import pygame
from config import *


class Menu:
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.cursor_offset_x = -130
        self.cursor_offset_y = 2
        self.background = game.background
        self.default_text_size = 35
        self.default_text_gap = 40
        self.default_cursor_size = 25

    def draw_cursor(self):
        self.game.draw_text('*',  self.default_cursor_size, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.game.base_window.blit(self.game.display_viewed, (0, 0))
        pygame.display.update()
        self.game.reset_keys()


class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Run"
        self.run_x, self.run_y = self.mid_w, self.mid_h + self.default_text_gap
        self.load_x, self.load_y = self.mid_w, self.mid_h + self.default_text_gap * 2
        self.setup_x, self.setup_y = self.mid_w, self.mid_h + self.default_text_gap * 3
        self.quit_x, self.quit_y = self.mid_w, self.mid_h + self.default_text_gap * 4
        self.cursor_rect.midtop = (self.run_x + self.cursor_offset_x, self.run_y + self.cursor_offset_y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            # collect input
            self.game.check_events()
            # react to input
            self.move_cursor()
            self.check_input()
            if self.game.BACK_KEY:
                return -1
            # display change
            self.game.display_viewed.fill(self.background)
            self.game.draw_text('BERRIES & BABIES', self.default_text_size + 10, self.mid_w, self.mid_h - 100)
            self.game.draw_text("Run", self.default_text_size, self.run_x, self.run_y)
            self.game.draw_text("Load Best", self.default_text_size, self.load_x, self.load_y)
            self.game.draw_text("Setup", self.default_text_size, self.setup_x, self.setup_y)
            self.game.draw_text("Quit", self.default_text_size, self.quit_x, self.quit_y)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == 'Run':
                self.cursor_rect.midtop = (self.load_x + self.cursor_offset_x, self.load_y + self.cursor_offset_y)
                self.state = 'Load'
            elif self.state == 'Load':
                self.cursor_rect.midtop = (self.setup_x + self.cursor_offset_x, self.setup_y + self.cursor_offset_y)
                self.state = 'Setup'
            elif self.state == 'Setup':
                self.cursor_rect.midtop = (self.quit_x + self.cursor_offset_x, self.quit_y + self.cursor_offset_y)
                self.state = 'Quit'
            elif self.state == 'Quit':
                self.cursor_rect.midtop = (self.run_x + self.cursor_offset_x, self.run_y + self.cursor_offset_y)
                self.state = 'Run'
        elif self.game.UP_KEY:
            if self.state == 'Run':
                self.cursor_rect.midtop = (self.quit_x + self.cursor_offset_x, self.quit_y + self.cursor_offset_y)
                self.state = 'Quit'
            elif self.state == 'Load':
                self.cursor_rect.midtop = (self.run_x + self.cursor_offset_x, self.run_y + self.cursor_offset_y)
                self.state = 'Run'
            elif self.state == 'Setup':
                self.cursor_rect.midtop = (self.load_x + self.cursor_offset_x, self.load_y + self.cursor_offset_y)
                self.state = 'Load'
            elif self.state == 'Quit':
                self.cursor_rect.midtop = (self.setup_x + self.cursor_offset_x, self.setup_y + self.cursor_offset_y)
                self.state = 'Setup'

    def check_input(self):
        if self.game.ENTER_KEY:
            if self.state == 'Run':
                self.game.playing = True
            elif self.state == 'Load':
                self.game.load_best()
            elif self.state == 'Setup':
                self.game.curr_menu = self.game.setup_menu
            elif self.state == 'Quit':
                self.game.curr_menu = self.game.quit_menu
            self.run_display = False
        elif self.game.BACK_KEY or not self.game.running:
            pygame.quit()


class SetupMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = [0, 0]
        self.cursor_offset_x = -175
        self.box_x, self.box_y = self.mid_w - 220, self.mid_h - 20
        self.input_box_x, self.input_box_y = self.mid_w - 220, self.mid_h + 25
        self.box_offset_x = 520
        self.box_offset_y = 120
        self.cursor_rect.midtop = (self.box_x + self.cursor_offset_x, self.box_y)
        self.changing_settings = [3, 3]    # out of range, better way?
        self.pop_size = DEFAULT_POP_SIZE
        self.starvation_at = STARVATION_DEATH
        self.visible = VISIBLE_PLAYERS_NUM
        self.regrow = REGROW_FREQUENCY
        self.neat_window = 'NO'
        self.game_pace_index = 3
        self.pace_list = ['very slow', 'slow', 'medium', 'fast']
        self.pop_size_color, self.starvation_color, self.visible_color, self.regrow_color, self.neat_window_color, \
            self.game_pace_color = WHITE, WHITE, WHITE, WHITE, WHITE, WHITE

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display_viewed.fill(self.background)
            self.game.draw_text('Setup', self.default_text_size + 15, self.mid_w, self.mid_h - 150)
            self.game.draw_text('Pop size: ', self.default_text_size, self.box_x, self.box_y, self.pop_size_color)
            self.game.draw_text("Starvation at:", self.default_text_size, self.box_x + self.box_offset_x, self.box_y, self.starvation_color)
            self.game.draw_text("Visible:", self.default_text_size, self.box_x, self.box_y + self.box_offset_y, self.visible_color)
            self.game.draw_text("Regrow:", self.default_text_size, self.box_x + self.box_offset_x, self.box_y + self.box_offset_y, self.regrow_color)
            self.game.draw_text("NEAT specs:", self.default_text_size, self.box_x, self.box_y + self.box_offset_y * 2, self.neat_window_color)
            self.game.draw_text("Game pace:", self.default_text_size, self.box_x + self.box_offset_x, self.box_y + self.box_offset_y * 2, self.game_pace_color)
            self.game.draw_text("{}".format(self.pop_size), self.default_text_size, self.input_box_x, self.input_box_y)
            self.game.draw_text("{}".format(self.starvation_at), self.default_text_size, self.input_box_x + self.box_offset_x, self.input_box_y)
            self.game.draw_text("{}".format(self.visible), self.default_text_size, self.input_box_x, self.input_box_y + self.box_offset_y)
            self.game.draw_text("{}".format(self.regrow), self.default_text_size, self.input_box_x + self.box_offset_x, self.input_box_y + self.box_offset_y)
            self.game.draw_text("{}".format(self.neat_window), self.default_text_size, self.input_box_x, self.input_box_y + self.box_offset_y * 2)
            self.game.draw_text("{}".format(self.pace_list[self.game_pace_index]), self.default_text_size, self.input_box_x + self.box_offset_x, self.input_box_y + self.box_offset_y * 2)

            self.draw_cursor()
            self.blit_screen()

        if self.game_pace_index == 0:
            self.game.round_time = 0.8
        if self.game_pace_index == 1:
            self.game.round_time = 0.3
        if self.game_pace_index == 2:
            self.game.round_time = 0.05
        if self.game_pace_index == 3:
            self.game.round_time = 0.01
        # apply change in config_feedforward file
        with open("config-feedforward.txt", 'r') as conf_file:
            lines = conf_file.readlines()
            pop_size_line = lines[5]
            lines[5] = pop_size_line[:-3] + "{}\n".format(self.pop_size)
        with open("config-feedforward.txt", 'w') as conf_file:
            conf_file.writelines(lines)

        self.game.visible = self.visible
        self.game.starvation_death = self.starvation_at
        self.game.regrow = self.regrow
        self.game.neat_specs = self.neat_window

    def check_input(self):
        if not self.game.running:
            self.game.quit()
        if self.changing_settings == [0, 0]:    # changing settings
            if self.game.ENTER_KEY or self.game.BACK_KEY:
                self.changing_settings = [3, 3]
                self.pop_size_color = WHITE
            elif self.game.UP_KEY and self.pop_size < 50:
                self.pop_size += 1
            elif self.game.DOWN_KEY and self.pop_size > 10:
                self.pop_size -= 1
                if self.pop_size < self.visible:
                    self.visible = self.pop_size
        elif self.changing_settings == [1, 0]:
            if self.game.ENTER_KEY or self.game.BACK_KEY:
                self.changing_settings = [3, 3]
                self.starvation_color = WHITE
            elif self.game.UP_KEY and self.starvation_at < 40:
                self.starvation_at += 1
            elif self.game.DOWN_KEY and self.starvation_at > 4:
                self.starvation_at -= 1
        elif self.changing_settings == [0, 1]:
            if self.game.ENTER_KEY or self.game.BACK_KEY:
                self.changing_settings = [3, 3]
                self.visible_color = WHITE
            elif self.game.UP_KEY and self.visible < self.pop_size:
                self.visible += 1
            elif self.game.DOWN_KEY and self.visible > 0:
                self.visible -= 1
        elif self.changing_settings == [1, 1]:
            if self.game.ENTER_KEY or self.game.BACK_KEY:
                self.changing_settings = [3, 3]
                self.regrow_color = WHITE
            elif self.game.UP_KEY and self.regrow < 100:
                self.regrow += 1
            elif self.game.DOWN_KEY and self.regrow > 5:
                self.regrow -= 1
        elif self.changing_settings == [0, 2]:
            if self.game.ENTER_KEY or self.game.BACK_KEY:
                self.changing_settings = [3, 3]
                self.neat_window_color = WHITE
            elif self.game.UP_KEY or self.game.DOWN_KEY:
                if self.neat_window == 'NO':
                    self.neat_window = 'YES'
                else:
                    self.neat_window = 'NO'
        elif self.changing_settings == [1, 2]:
            if self.game.ENTER_KEY or self.game.BACK_KEY:
                self.changing_settings = [3, 3]
                self.game_pace_color = WHITE
            elif self.game.UP_KEY and self.game_pace_index < 3:
                self.game_pace_index += 1
            elif self.game.DOWN_KEY and self.game_pace_index > 0:
                self.game_pace_index -= 1

        else:    # regular mode
            got_input = False
            if self.game.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            elif self.game.UP_KEY:
                self.state[0] += 0
                self.state[1] += -1
                got_input = True
            elif self.game.DOWN_KEY:
                self.state[0] += 0
                self.state[1] += 1
                got_input = True
            elif self.game.RIGHT_KEY:
                self.state[0] += 1
                self.state[1] += 0
                got_input = True
            elif self.game.LEFT_KEY:
                self.state[0] += -1
                self.state[1] += 0
                got_input = True
            elif self.game.ENTER_KEY:
                self.changing_settings = self.state
                if self.changing_settings == [0, 0]:
                    self.pop_size_color = BLUE
                elif self.changing_settings == [1, 0]:
                    self.starvation_color = BLUE
                elif self.changing_settings == [0, 1]:
                    self.visible_color = BLUE
                elif self.changing_settings == [1, 1]:
                    self.regrow_color = BLUE
                elif self.changing_settings == [0, 2]:
                    self.neat_window_color = BLUE
                elif self.changing_settings == [1, 2]:
                    self.game_pace_color = BLUE

            if got_input:
                self.state[0] = self.state[0] % 2
                self.state[1] = self.state[1] % 3
                self.cursor_rect.midtop = (self.box_x + self.cursor_offset_x + self.box_offset_x * self.state[0],
                                           self.box_y + self.box_offset_y * self.state[1])


class QuitMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.exit = False
        self.state = 'NO'
        self.no_x, self.no_y = self.mid_w, self.mid_h + 30
        self.yes_x, self.yes_y = self.mid_w, self.mid_h + 90
        self.cursor_offset_x = -52
        self.cursor_offset_y = 0
        self.lable_offset_y = 30
        self.cursor_rect.midtop = (self.no_x + self.cursor_offset_x, self.no_y + self.lable_offset_y + self.cursor_offset_y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            if self.exit:
                return -1
            if self.game.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            self.game.display_viewed.fill(self.background)
            self.game.draw_text('ARE YOU SURE?', self.default_text_size + 10, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 20)
            self.game.draw_text('NO', self.default_text_size, self.no_x, self.no_y + self.lable_offset_y)
            self.game.draw_text('YES', self.default_text_size, self.yes_x, self.yes_y + self.lable_offset_y)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if not self.game.running:
            self.game.quit()
        if self.game.BACK_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False
        if self.state == 'NO':
            if self.game.ENTER_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            if self.game.UP_KEY or self.game.DOWN_KEY:
                self.state = 'YES'
                self.cursor_rect.midtop = (self.yes_x + self.cursor_offset_x, self.yes_y + self.lable_offset_y + self.cursor_offset_y)
        elif self.state == 'YES':
            if self.game.ENTER_KEY:
                self.exit = True
            elif self.game.UP_KEY or self.game.DOWN_KEY:
                self.state = 'NO'
                self.cursor_rect.midtop = (self.no_x + self.cursor_offset_x, self.no_y + self.lable_offset_y + self.cursor_offset_y)


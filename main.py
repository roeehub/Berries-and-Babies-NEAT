from game import Game

game = Game('config-feedforward.txt')
while game.running:
    res = game.curr_menu.display_menu()
    if res == -1:
        game.quit()
        break
    game.game_loop()
    game.gen_counter = -1

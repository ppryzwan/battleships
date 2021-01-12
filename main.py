"""Game Client"""
import ctypes
import os
import pickle
import random
import time
import pygame
import pygame_menu
import settings

from board_classes import PlayerBoard, EnemyBoard, Display, AIBoard
from network_class import Network


def isend_game(game, player_board, net_game, player, enemy_board):
    """Printing end of game"""
    if game.wins[player] == 0:
        player_board.display.show_text(
            "You lost this game, no more ships!", True)
        player_board.display.flip()
        time.sleep(5)
        game = net_game.request_board(pickle.dumps([player, "Lost"]))
        print("Thanks for playing", game)
        player_board.display.close()
    else:
        player_board.display.show(enemy_board, player_board)
        player_board.display.show_text(
            "You won this game, no more ships for opponent!")
        player_board.display.flip()
        time.sleep(5)
        game = net_game.request_board(pickle.dumps([player, "Won"]))
        print("Thanks for playing", game)
        player_board.display.close()


def update_board(player_board, game, player):
    """Update player board"""
    player_board.ships_list = game.board[player][0].copy()
    player_board.hits_lists = game.board[player][1].copy()
    player_board.misses_lists = game.board[player][2].copy()


def player_shot(cord_x, cord_y, enemyboard):
    """Uses input to decide if a shot is valid or not"""
    if enemyboard.valid_target(cord_x, cord_y):
        enemyboard.shoot(cord_x, cord_y)
        return True
    return False


def is_gameover(ai_board, player_board):
    """Determines and prints the winner"""
    game_boolean = False
    if ai_board.gameover:
        player_board.display.show_text(
            "You won this game, no more ships for opponent!")
        player_board.display.flip()
        time.sleep(5)
        game_boolean = True
    elif player_board.gameover:
        player_board.display.show_text(
            "You lost this game, no more ships!")
        player_board.display.flip()
        time.sleep(5)
        game_boolean = True
    return game_boolean


def single_player():
    """
    Single player main function
    :return:
    """
    board_size = settings.BOARD_SIZE
    len_ships = settings.LEN_SHIPS

    list_cord = []
    for i in range(board_size):
        for j in range(board_size):
            list_cord.append((i, j))

    window = Display()
    player_board = PlayerBoard(window, board_size, len_ships)
    ai_board = AIBoard(board_size, len_ships)
    ctypes.windll.user32.MessageBoxW(0, "Your board is ready, prepare for game!",
                                     "Board ready!", 1)
    player_board.display.show(ai_board, player_board, include_top_ships=True)
    player_board.display.show_text(
        "Try to hit enemy ships on board above!", True)
    player_board.display.flip()
    game_over = False
    while not game_over:
        cord_x, cord_y = player_board.display.get_input(preparing=False)
        valid_target = ai_board.valid_target(cord_x, cord_y)
        while not valid_target:
            cord_x, cord_y = player_board.display.get_input(preparing=False)
            valid_target = ai_board.valid_target(cord_x, cord_y)
        ai_board.shoot(cord_x, cord_y)

        cord_ai = random.randint(0, len(list_cord) - 1)

        cordai_x, cordai_y = list_cord.pop(cord_ai)

        player_board.shoot(cordai_x, cordai_y)
        player_board.display.show(ai_board, player_board)
        player_board.display.show_text(
            "You need to hit AI ships!", True)
        player_board.display.flip()
        sink_ship = ai_board.sink(cord_x, cord_y)
        if sink_ship[0] == 1:
            ctypes.windll.user32.MessageBoxW(0,
                                             f"Ship {sink_ship[1]}-long for opponent has sunk!",
                                             "Ship has sunk!", 1)
        player_board.display.show(ai_board, player_board)
        player_board.display.show_text(
            "You need to hit AI ships!", True)
        player_board.display.flip()
        game_over = is_gameover(ai_board, player_board)
    ctypes.windll.user32.MessageBoxW(0, "Game Over - Redirecting to main menu!",
                                     "Game Over!", 1)
    game_menu()


def multi_player():
    """
    Main function of game - client side
    :return:
    """
    board_size = settings.BOARD_SIZE
    len_ships = settings.LEN_SHIPS
    run = True
    end_game = 0
    try:
        net_game = Network()
        player = int(net_game.get_p())
        helper_board = 0
        if player == 0:
            helper_board = 1
        print("You are player", player)
        enemy_board = None
        window = Display()
        player_board = PlayerBoard(window, board_size, len_ships)
        ctypes.windll.user32.MessageBoxW(0, "Your board is ready, wait for opponent!",
                                         "Board ready!", 1)
        board = [player, [player_board.ships_list, player_board.hits_lists,
                          player_board.misses_lists]]

        game = net_game.send(pickle.dumps(board))
        while not game.connected():
            player_board.display.show_text("Waiting for opponent to connect. . . ",
                                           True)
            player_board.display.flip()
            time.sleep(5)
            game = net_game.send(pickle.dumps("Game"))

        while game.recieved_board[helper_board] == 0:
            game = net_game.request_board(pickle.dumps("board"))
            run = True
        ctypes.windll.user32.MessageBoxW(0, "Opponent is found, prepare for game!",
                                         "Opponent Found!", 1)

        gametime = True
        while run:
            try:
                game = net_game.request_board(pickle.dumps("board"))
                update_board(player_board, game, player)

                if end_game != 0:
                    isend_game(game, player_board, net_game, player, enemy_board)

                if gametime:
                    net_game.request_board(pickle.dumps("Set"))
                    global is_hit
                    is_hit = False

                    if enemy_board is None:
                        enemy_board = EnemyBoard(board_size, len_ships,
                                                 [game.board[helper_board][0],
                                                  game.board[helper_board][1],
                                                  game.board[helper_board][2]])
                        player_board.display.show(enemy_board, player_board)
                    update_board(player_board, game, player)

                    if player_board.gameover:
                        player_board.display.show(enemy_board, player_board)
                        player_board.display.show_text(
                            "You lost this game, no more ships!", True)
                        player_board.display.flip()
                        time.sleep(5)
                        print("Thanks for playing")
                        player_board.display.close()
                        ctypes.windll.user32.MessageBoxW(0,
                                                         "Game Over - Redirecting to main menu!",
                                                         "Game Over!", 1)
                        game_menu()
                    elif enemy_board.gameover:
                        player_board.display.show(enemy_board, player_board)
                        player_board.display.show_text(
                            "You won this game, no more ships for opponent!")
                        player_board.display.flip()
                        time.sleep(5)
                        game = net_game.request_board(pickle.dumps([player, "Won"]))
                        print("Thanks for playing")
                        player_board.display.close()
                        ctypes.windll.user32.MessageBoxW(0,
                                                         "Game Over - Redirecting to main menu!",
                                                         "Game Over!", 1)
                        game_menu()
                    player_board.display.show(enemy_board, player_board)
                    player_board.display.show_text(
                        "Try to hit enemy ships on board above!", True)
                    player_board.display.flip()
                    cord_x, cord_y = None, None

                    if cord_x is None and cord_y is None and not is_hit:
                        cord_x, cord_y = player_board.display.get_input(
                            preparing=False)
                        valid = player_shot(cord_x, cord_y, enemy_board)
                        while not valid:
                            cord_x, cord_y = player_board.display.get_input(
                                preparing=False)
                            if cord_x is not None and cord_y is not None:
                                valid = player_shot(cord_x, cord_y, enemy_board)
                        sink_ship = enemy_board.sink(cord_x, cord_y)
                        if sink_ship[0] == 1:
                            ctypes.windll.user32.MessageBoxW(0,
                                                             f"Ship {sink_ship[1]}-long "
                                                             f"for opponent has sunk!",
                                                             "Ship has sunk!", 1)
                        player_board.display.show(enemy_board, player_board)
                        player_board.display.show_text(
                            "Waiting for other player to make a move!")
                        player_board.display.flip()
                        is_hit = True

                    update_board(player_board, game, player)
                    board = [helper_board,
                             [enemy_board.ships_list, enemy_board.hits_lists,
                              enemy_board.misses_lists]]
                    game = net_game.request_board(pickle.dumps(board))
                    end_game = game.wins[player] + game.wins[helper_board]
                    gametime = game.bothready()
                else:
                    while True:
                        game = net_game.request_board(pickle.dumps("turn"))
                        if game != "Waiting":
                            gametime = True
                            break

            except:
                print("Couldn't get game")
                break
    except:
        ctypes.windll.user32.MessageBoxW(0, "Server is not available!",
                                         "Server is offline!", 1)
        game_menu()


def game_menu():
    """
    Main menu
    :return:
    """
    global main_menu
    global surface

    background_image = pygame_menu.baseimage.BaseImage(
        image_path=os.getcwd() + "\\assets\\battleships.png")
    menu_fps = 60
    windows_size = (640, 480)

    surface = None
    main_menu = None
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    surface = pygame.display.set_mode(windows_size)
    pygame.display.set_caption("BattleShips")
    clock = pygame.time.Clock()
    main_menu_theme = pygame_menu.themes.THEME_DARK.copy()
    main_menu_theme.set_background_color_opacity(0.5)

    main_menu = pygame_menu.Menu(
        height=windows_size[1] * 0.7,
        width=windows_size[0] * 0.8,
        onclose=pygame_menu.events.EXIT,
        title='BattleShips',
        theme=main_menu_theme,
    )

    main_menu.add_button('Vs AI', single_player)
    main_menu.add_button('Vs Player via Network', multi_player)
    main_menu.add_button('Quit', pygame_menu.events.EXIT)

    while True:
        try:
            # Tick
            clock.tick(menu_fps)
            background_image.draw(surface)
            main_menu.mainloop(surface, lambda: background_image.draw(surface),
                               fps_limit=menu_fps)
            pygame.display.flip()
        except:
            break


if __name__ == "__main__":
    game_menu()

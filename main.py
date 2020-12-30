"""Game Client"""
import pickle
import time
import ctypes
from board_classes import PlayerBoard, EnemyBoard, Display
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
    player_board.ships_list = game.board[player][0]
    player_board.hits_lists = game.board[player][1]
    player_board.misses_lists = game.board[player][2]


def player_shot(cord_x, cord_y, enemyboard):
    """Uses input to decide if a shot is valid or not"""
    if enemyboard.valid_target(cord_x, cord_y):
        enemyboard.shoot(cord_x, cord_y)
        return True
    return False


def main():
    """
    Main function of game - client side
    :return:
    """
    board_size = 10
    len_ships = [1, 2]
    run = True
    end_game = 0
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
        player_board.display.show_text("Waiting for opponent to connect. . . ", True)
        player_board.display.flip()
        time.sleep(5)
        game = net_game.send(pickle.dumps("Game"))

    while game.recieved_board[helper_board] == 0:
        game = net_game.request_board(pickle.dumps("board"))
        run = True
    ctypes.windll.user32.MessageBoxW(0, "Opponend is found, prepare for game!",
                                     "Opponend Found!", 1)

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
                    game = net_game.request_board(pickle.dumps([player, "Lost"]))
                    print("Thanks for playing", game)
                    player_board.display.close()
                elif enemy_board.gameover:
                    player_board.display.show(enemy_board, player_board)
                    player_board.display.show_text(
                        "You won this game, no more ships for opponent!")
                    player_board.display.flip()
                    time.sleep(5)
                    game = net_game.request_board(pickle.dumps([player, "Won"]))
                    print("Thanks for playing", game)
                    player_board.display.close()

                player_board.display.show(enemy_board, player_board)
                player_board.display.show_text(
                    "Try to hit enemy ships on board above!", True)
                player_board.display.flip()
                cord_x, cord_y = None, None

                if cord_x is None and cord_y is None and not is_hit:
                    cord_x, cord_y = player_board.display.get_input(preparing=False)
                    valid = player_shot(cord_x, cord_y, enemy_board)
                    while not valid:
                        cord_x, cord_y = player_board.display.get_input(
                            preparing=False)
                        if cord_x is not None and cord_y is not None:
                            valid = player_shot(cord_x, cord_y, enemy_board)
                    sink_ship = enemy_board.sink(cord_x, cord_y)
                    if sink_ship[0] == 1:
                        ctypes.windll.user32.MessageBoxW(0,
                                                         f"Ship {sink_ship[1]}-long for opponent has sunk!",
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
            run = False
            print("Couldn't get game")
            break


if __name__ == "__main__":
    main()

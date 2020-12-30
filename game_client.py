"""Game Client"""
import pickle
import time

from board_classes import PlayerBoard, EnemyBoard, Display
from network_class import Network


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
    run = True
    net_game = Network()
    player = int(net_game.get_p())
    helper_board = 0
    if player == 0:
        helper_board = 1
    print("You are player", player)
    enemy_board = None
    window = Display()
    player_board = PlayerBoard(window, 10, [1, 2])
    board = [player, [player_board.ships_list, player_board.hits_lists,
                      player_board.misses_lists]]
    is_hit = False
    game = net_game.send(pickle.dumps(board))
    if not game.connected():
        player_board.display.show_text("Waiting for connection")
        player_board.display.flip()
    while game.recieved_board[helper_board] == 0:
        game = net_game.request_board(pickle.dumps("board"))

    gametime = True
    while run:
        try:
            game = net_game.request_board(pickle.dumps("board"))
            if gametime:

                net_game.request_board(pickle.dumps("Set"))
                is_hit = False
                if enemy_board is None:
                    enemy_board = EnemyBoard(10, [1, 2], [game.board[helper_board][0],
                                                          game.board[helper_board][1],
                                                          game.board[helper_board][2]])
                    player_board.display.show(enemy_board, player_board)
                player_board.ships_list = game.board[player][0]
                player_board.hits_lists = game.board[player][1]
                player_board.misses_lists = game.board[player][2]
                if player_board.gameover:
                    player_board.display.show(enemy_board, player_board)
                    player_board.display.show_text(
                        "You lost this game, no more ships!")
                    player_board.display.flip()
                    time.sleep(20)
                    game = net_game.request_board(pickle.dumps([player, "Lost"]))
                    print("Thanks for playing")
                    time.sleep(5)
                    player_board.display.close()
                elif enemy_board.gameover:
                    player_board.display.show(enemy_board, player_board)
                    player_board.display.show_text(
                        "You won this game, no more ships for opponent!")
                    player_board.display.flip()
                    time.sleep(5)
                    game = net_game.request_board(pickle.dumps([player, "Won"]))
                    print("Thanks for playing")
                    player_board.display.close()

                player_board.display.show(enemy_board, player_board)
                player_board.display.show_text(
                    "Try to hit enemy ships on board above!")
                player_board.display.flip()
                cord_x, cord_y = None, None

                while cord_x is None and cord_y is None:
                    cord_x, cord_y = player_board.display.get_input(preparing=False)
                    if cord_x is not None and cord_y is not None and not is_hit:
                        valid = player_shot(cord_x, cord_y, enemy_board)
                        while not valid:
                            cord_x, cord_y = player_board.display.get_input(
                                preparing=False)
                            if cord_x is not None and cord_y is not None:
                                valid = player_shot(cord_x, cord_y, enemy_board)
                                cord_x, cord_y = None, None
                        player_board.display.show(enemy_board, player_board)
                        player_board.display.show_text(
                            "Waiting for other player to make a move!")
                        player_board.display.flip()
                is_hit = True
                player_board.ships_list = game.board[player][0]
                player_board.hits_lists = game.board[player][1]
                player_board.misses_lists = game.board[player][2]
                board = [helper_board,
                         [enemy_board.ships_list, enemy_board.hits_lists,
                          enemy_board.misses_lists]]
                game = net_game.request_board(pickle.dumps(board))
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


import socket
from Game import Game
import _thread
from Game import Game
from Classes import *
from Network import Network
import pickle
import time

def player_shot(x, y, enemyboard):
    """Uses input to decide if a shot is valid or not"""
    if enemyboard.valid_target(x, y):
        enemyboard.shoot(x, y)
        return True
    else:
        return False


def main():
    run = True
    n = Network()
    player = int(n.getP())
    helper_board = 0
    if player == 0:
        helper_board = 1
    print("You are player", player)
    Enemy = None
    window = Display()
    d = PlayerBoard(window, 10, [1, 2])
    board = [player, [d.ships_list, d.hits_lists, d.misses_lists]]
    global hit
    n.send(pickle.dumps(board))
    while True:
        game = n.requestBoard(pickle.dumps("board"))
        if game.bothready():
            break
    while run:
        try:
            game = n.requestBoard(pickle.dumps("board"))
            if game.bothready():

                turns = n.requestBoard(pickle.dumps("Set"))
                hit = False
                if Enemy is None:
                    Enemy = EnemyBoard(10, [1, 2], game.board[helper_board][0], game.board[helper_board][1],
                                       game.board[helper_board][2])
                    d.display.show(Enemy, d)
                    if not game.connected():
                        d.display.show_text("Waiting for connection")
                        d.display.flip()
                    else:
                        d.display.show_text("Try to hit enemy ships on board above!")
                        d.display.flip()

                if d.gameover:
                    d.display.show_text("You lost this game, no more ships!")
                    d.display.flip()
                    game = n.requestBoard(pickle.dumps([player, "Lost"]))
                    print("Thanks for playing")
                    time.sleep(20)
                    d.display.close()
                    break
                elif Enemy.gameover:
                    d.display.show_text("You won this game, no more ships for opponent!")
                    d.display.flip()
                    game = n.requestBoard(pickle.dumps([player, "Won"]))
                    print("Thanks for playing")
                    time.sleep(20)
                    d.display.close()
                    break

                d.ships_list = game.board[player][0]
                d.hits_lists = game.board[player][1]
                d.misses_lists = game.board[player][2]
                d.display.show(Enemy, d)
                d.display.show_text("Try to hit enemy ships on board above!")
                d.display.flip()
                x, y = None, None

                while x is None and y is None:
                    x, y = d.display.get_input(preparing=False)
                    if x is not None and y is not None and not hit:
                        valid = player_shot(x, y, Enemy)
                        while not valid:
                            x, y = d.display.get_input(preparing=False)
                            if x is not None and y is not None:
                                valid = player_shot(x, y, Enemy)
                                x, y = None, None
                        d.display.show(Enemy, d, include_top_ships=False)
                        d.display.show_text("Waiting for other player to make a move!")
                        d.display.flip()
                hit = True
                d.ships_list = game.board[player][0]
                d.hits_lists = game.board[player][1]
                d.misses_lists = game.board[player][2]
                board = [helper_board, [Enemy.ships_list, Enemy.hits_lists, Enemy.misses_lists]]
                n.requestBoard(pickle.dumps(board))
            else:
                while True:
                    game = n.requestBoard(pickle.dumps("turn"))
                    if game != "Waiting":
                        break
        except Exception as e:
            run = False
            print("Couldn't get game", e)
            break


main()

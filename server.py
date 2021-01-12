""" Server of Game BattleShips"""
import pickle
import socket

from _thread import start_new_thread
from game_class import Game
import settings

SERVER = settings.SERVER
PORT = settings.PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.bind((SERVER, PORT))
except socket.error as sock_er:
    str(sock_er)

sock.listen(2)
print("Waiting for connection, Server Started")
connected = set()
games = {}
ID_COUNT = 0


def threaded_client(conn_server, player_n, game_id):
    """
    Function to handle requests
    :param conn_server:
    :param player_n:
    :param game_id:
    :return:
    """
    global ID_COUNT
    conn_server.send(str.encode(str(player_n), "utf-8"))

    while True:
        try:
            data = pickle.loads(conn_server.recv(2048 * 16))
            if game_id in games:
                game = games[game_id]
                if data == "board":
                    conn_server.send(pickle.dumps(game))
                elif data == "turn":
                    if game.bothready() or sum(game.wins) != 0:
                        conn_server.send(pickle.dumps(game))
                    else:
                        conn_server.send(pickle.dumps("Waiting"))
                elif data == "Set":
                    game.end_of_turn()
                    conn_server.send(pickle.dumps("Ok"))
                elif data == "Game":
                    conn_server.send(pickle.dumps(game))
                elif data[1] == "Won":
                    game.end_of_game(data[0], data[1])
                    conn_server.send(pickle.dumps(f"Player {data[0]} won!"))
                    print(f"Player {data[0]} won!")
                else:
                    game.player(data[0], data[1])
                    conn_server.send(pickle.dumps(game))

            else:
                break
            if sum(game.wins) > 0:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[game_id]
        print("Closing Game", game_id)
    except:
        pass
    ID_COUNT -= 2
    conn_server.close()


while True:
    conn_s, addr = sock.accept()
    print(f"Connected to {addr}")
    ID_COUNT += 1
    PLAYER_NUMBER = 0
    GAME_ID = (ID_COUNT - 1) // 2
    if ID_COUNT % 2 == 1:
        games[GAME_ID] = Game(GAME_ID)
        print("Creating a new game...")
    else:
        games[GAME_ID].allset = True
        PLAYER_NUMBER = 1

    start_new_thread(threaded_client, (conn_s, PLAYER_NUMBER, GAME_ID))

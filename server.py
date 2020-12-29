import socket
from _thread import *
from Game import Game
import Classes
import pickle

server = "127.0.0.1"
port = 5555

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.bind((server, port))
except socket.error as e:
    str(e)

sock.listen(2)
print("Waiting for connection, Server Started")
connected = set()
games = {}
idCount = 0


def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p), "utf-8"))

    while True:
        try:
            data = pickle.loads(conn.recv(2048 * 16))
            if gameId in games:
                game = games[gameId]
                if data == "board":
                    conn.send(pickle.dumps(game))
                elif data == "turn":
                    if game.bothready():
                        conn.send(pickle.dumps(game))
                    else:
                        conn.send(pickle.dumps("Waiting"))
                elif data == "Set":
                    game.end_of_turn()
                    conn.send(pickle.dumps("Ok"))
                elif data[1] == "Won":
                    game.end_of_game(data[0], data[1])
                    conn.send(pickle.dumps(f"Player {data[1]} won!"))
                    print(f"Player {data[0]} won!")
                    break
                elif data[1] == "Lost":
                    game.end_of_game(data[0],data[1])
                    conn.send(pickle.dumps(f"Player {data[1]} won!"))
                    print(f"Player {data[0]} won!")
                    break
                else:
                    game.player(data[0], data[1])
                    conn.send(pickle.dumps(game))

            else:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()


while True:
    conn, addr = sock.accept()
    print(f"Connected to {addr}")
    idCount += 1
    p = 0
    gameId = (idCount - 1) // 2
    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    else:
        games[gameId].allset = True
        p = 1

    start_new_thread(threaded_client, (conn, p, gameId))

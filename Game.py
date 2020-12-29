from Classes import *


class Game:
    """The overall class to control the game"""

    def __init__(self, iD):

        """Setup network"""
        self.ready2 = False
        self.ready1 = False
        self.allset = False
        self.iD = iD
        self.board = [[], [], [], [[], [], []]]
        self.wins = [0, 0]
        self.recieved_board = [0, 0]

    def recieved_data(self, player):
        self.recieved_board[player] = 1

    def get_player_board(self, p):
        return self.board[p]

    def end_of_game(self, player, result):
        if result == "Lost":
            self.wins[player] = 0
        elif result == "Won":
            self.wins[player] = 1

    def end_of_turn(self):
        self.ready1 = False
        self.ready2 = False

    def bothWent(self):
        return self.p1Went and self.p2Went

    def player(self, player, rest):
        self.board[player] = rest
        self.recieved_board[player] = 1
        if player == 0:
            self.ready1 = True
        else:
            self.ready2 = True

    def connected(self):
        return self.allset

    def bothready(self):
        return self.ready1 and self.ready2

    def winner(self):
        p1 = self.board[0]
        p2 = self.board[1]

        winner = -1
        if self.gameover(p1) == 1 and self.gameover(p2) == -1:
            winner = 1
        else:
            winner = 0

        return winner

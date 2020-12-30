"""
Game class
"""


class Game:
    """The overall class to control the game"""

    def __init__(self, game_id):

        """Setup network"""
        self.ready2 = False
        self.ready1 = False
        self.allset = False
        self.game_id = game_id
        self.board = [[], [], [], [[], [], []]]
        self.wins = [0, 0]
        self.recieved_board = [0, 0]

    def recieved_data(self, player):
        """
        Changing parametr that player gets board from server
        :param player:
        :return:
        """
        self.recieved_board[player] = 1

    def get_player_board(self, player_number):
        """
        Return board of player
        :param player_number:
        :return:
        """
        return self.board[player_number]

    def end_of_game(self, player, result):
        """
        Changing parametrs who won
        :param player:
        :param result:
        :return:
        """
        if result == "Lost":
            self.wins[player] = 0
        elif result == "Won":
            self.wins[player] = 1

    def end_of_turn(self):
        """
        Changing parameters to start new turn
        :return:
        """
        self.ready1 = False
        self.ready2 = False

    def player(self, player, rest):
        """
        Setting board of player
        :param player:
        :param rest:
        :return:
        """
        self.board[player] = rest
        self.recieved_board[player] = 1
        if player == 0:
            self.ready1 = True
        else:
            self.ready2 = True

    def connected(self):
        """
        Return parameter all set
        :return:
        """
        return self.allset

    def bothready(self):
        """
        Return if both players are ready
        :return:
        """
        return self.ready1 and self.ready2

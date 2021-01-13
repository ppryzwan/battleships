"""
Network Class
"""
import socket
import pickle
import settings


class Network:
    """
    Network class for games
    """

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = settings.SERVER
        self.port = settings.PORT
        self.addr = (self.server, self.port)
        self.play = self.connect()

    def get_p(self):
        """
        Method that returns connection
        :return:
        """
        return self.play

    def connect(self):
        """
        Send and recieved data
        :return:
        """
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except socket.error as socket_e:
            print(socket_e)

    def send(self, data):
        """
        Send and recieved data
        :param data: board
        :return:
        """
        try:
            self.client.send(data)
            return pickle.loads(self.client.recv(2048 * 16))
        except socket.error as socket_e:
            print(socket_e)

    def request_board(self, data):
        """
        Send data and recieved board
        :param data:
        :return:
        """
        try:
            self.client.send(data)
            return pickle.loads(self.client.recv(2048 * 16))
        except socket.error as socket_e:
            print(socket_e)

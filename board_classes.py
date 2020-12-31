""" Classes used to create user interface / boards """
from itertools import zip_longest
import random
import pygame


class Direction:
    """
    Directions of ships and rotating them
    """

    def __init__(self, value=0):
        self.value = value
        if self.value == 0:
            self.direction = "NORTH"
        elif self.value == 1:
            self.direction = "EAST"
        elif self.value == 2:
            self.direction = "SOUTH"
        elif self.value == 3:
            self.direction = "WEST"

    def next(self):
        """
        Changing value and direction clockwise
        :return:
        """

        if self.value == 0:
            self.value = 1
            self.direction = "EAST"
        elif self.value == 1:
            self.value = 2
            self.direction = "SOUTH"
        elif self.value == 2:
            self.value = 3
            self.direction = "WEST"
        elif self.value == 3:
            self.value = 0
            self.direction = "NORTH"

    def get_value(self):
        """
        Method that returns value
        :return:
        """
        return self.value


class Ship:
    """Ship class that contains coordinates"""

    def __init__(self, wsp_x, wsp_y, direction, length):
        self.wsp_poczatkowe = (wsp_x, wsp_y)
        self.direction = direction
        self.length = length

    def ship_coordinates(self):
        """
        Method that return coordinates of ships
        :return: List of coordinates
        """
        cord_x, cord_y = self.wsp_poczatkowe
        list_of_coordinates = []
        if self.direction == "NORTH":
            list_of_coordinates = [(cord_x, cord_y + i) for i in range(self.length)]
        elif self.direction == "EAST":
            list_of_coordinates = [(cord_x + i, cord_y) for i in range(self.length)]
        elif self.direction == "SOUTH":
            list_of_coordinates = [(cord_x, cord_y - i) for i in range(self.length)]
        elif self.direction == "WEST":
            list_of_coordinates = [(cord_x - i, cord_y) for i in range(self.length)]
        return list_of_coordinates

    def rotate(self, direction):
        """
        Function that changes direction to
        :param direction:
        :return:
        """
        self.direction = direction


class Boards:
    """
    Class that stores information about ships, hits and misses.
    Created to inheritance for player and enemy board
    """

    def __init__(self, size, ships):
        self.size = size
        self.ships_lengths = ships
        self.ships_list = []
        self.hits_lists = []
        self.misses_lists = []

    @staticmethod
    def ships_overlap(ship1, ship2):
        """
        Checks if two ships overlap
        :param ship1: Object of class ship
        :param ship2: Object of class ship
        :return: True if overlaping, flase if not
        """
        for ship1_coord in ship1.ship_coordinates():
            for ship2_coord in ship2.ship_coordinates():
                if ship1_coord == ship2_coord:
                    return True
        return False

    def is_valid(self, ship):
        """
        Checkf if coordinates of ship is valid
        :param ship: Object of class ship
        :return: True if valid, False if not
        """
        for cord_x, cord_y in ship.ship_coordinates():
            if cord_x < 0 or cord_y < 0 or cord_x >= self.size or cord_y >= self.size:
                return False
        for other_ship in self.ships_list:
            if self.ships_overlap(ship, other_ship):
                return False
        return True

    def add_ship(self, ship):
        """
        Adds a ship to the board
        :param ship: Object of class ship
        :return: Adds a ship if coordinates is valid
        """
        added = False
        if self.is_valid(ship):
            self.ships_list.append(ship)
            added = True
        return added

    def remove_ship(self, ship):
        """
        Removes a ship from the board
        :param ship:
        :return:
        """
        self.ships_list.remove(ship)

    def get_ship(self, cord_x, cord_y):
        """
        Checks if coordinates is ship
        :param cord_x: coordinate cord_x
        :param cord_y: coordinate cord_y
        :return:
        """
        for ship in self.ships_list:
            if (cord_x, cord_y) in ship.ship_coordinates():
                return ship
        return None

    def valid_target(self, cord_x, cord_y):
        """Checks whether a set of coordinates is a valid shot"""
        if cord_x not in range(self.size) or cord_y not in range(self.size):
            return False
        for previous_shot in self.misses_lists + self.hits_lists:
            if (cord_x, cord_y) == previous_shot:
                return False
        return True

    def shoot(self, cord_x, cord_y):
        """Registers a shot on the board, saving to appropriate list"""
        if not self.valid_target(cord_x, cord_y):
            return False

        for ship in self.ships_list:
            for ship_coordinate in ship.ship_coordinates():
                if (cord_x, cord_y) == ship_coordinate:
                    self.hits_lists.append((cord_x, cord_y))
                    return True

        self.misses_lists.append((cord_x, cord_y))
        return True

    def sink(self, cord_x, cord_y):
        """
        Checks if ship sunk
        :param cord_x:
        :param cord_y:
        :return: True of false
        """
        sink = 0
        for ship in self.ships_list:
            if (cord_x, cord_y) in ship.ship_coordinates():
                for coordinate in ship.ship_coordinates():
                    if coordinate in self.hits_lists:
                        sink += 1
                    if sink == ship.length:
                        return [1, ship.length]
            return [0, ship.length]

    def colour_grid(self, colours, include_ships=True):
        """Calculates a colour representation of the board for display"""
        grid = [[colours["board"] for _ in range(self.size)] for _ in range(self.size)]

        if include_ships:
            for ship in self.ships_list:
                for cord_y, cord_x in ship.ship_coordinates():
                    grid[cord_x][cord_y] = colours["ship"]

        for cord_y, cord_x in self.hits_lists:
            grid[cord_x][cord_y] = colours["hit"]

        for cord_y, cord_x in self.misses_lists:
            grid[cord_x][cord_y] = colours["miss"]

        return grid

    @property
    def gameover(self):
        """Checks to see if all the ships have been fully hit"""
        for ship in self.ships_list:
            for coordinate in ship.ship_coordinates():
                if coordinate not in self.hits_lists:
                    return False
        return True


class AIBoard(Boards):
    """A Board controlled by a AI"""

    def __init__(self, board_size, ship_sizes):
        """Initialises the board by randomly placing ships"""
        super().__init__(board_size, ship_sizes)
        for ship_length in self.ships_lengths:
            ship_added = False
            while not ship_added:
                cord_x = random.randint(0, board_size - 1)
                cord_y = random.randint(0, board_size - 1)
                ship_direction = Direction(random.randint(0, 3))
                ship = Ship(cord_x, cord_y, ship_direction.direction, ship_length)
                if self.is_valid(ship):
                    self.add_ship(ship)
                    ship_added = True


class EnemyBoard(Boards):
    """
    Class that will contain enemy board
    """

    def __init__(self, board_size, ship_sizes, board):
        """Initialises the board by randomly placing ships"""
        super().__init__(board_size, ship_sizes)
        self.ships_list = board[0]
        self.hits_lists = board[1]
        self.misses_lists = board[2]


class PlayerBoard(Boards):
    """A Board for user input"""

    def __init__(self, display, board_size, ship_sizes):
        """Initialises the board by placing ships."""
        super().__init__(board_size, ship_sizes)
        self.display = display
        direction = Direction()
        self.ready = False
        while True:
            self.display.show(None, self)

            if self.ship_to_place:
                text = f"Click where you want {self.ship_to_place}-long ship to be, " \
                       f"you can change direction of ship!"
            else:
                text = 'Click again to rotate a ship, or elsewhere if ready.'

            self.display.show_text(text)

            cord_x, cord_y = self.display.get_input()
            if cord_x is not None and cord_y is not None:
                ship = self.get_ship(cord_x, cord_y)
                if ship:
                    self.remove_ship(ship)
                    direction.next()
                    ship.rotate(direction.direction)
                    if self.is_valid(ship):
                        self.add_ship(ship)
                elif self.ship_to_place:
                    ship = Ship(cord_x, cord_y, direction.direction,
                                self.ship_to_place)
                    if self.is_valid(ship):
                        self.add_ship(ship)
                    else:
                        direction.next()
                else:
                    self.ready = True
                    break

                if self.is_valid(ship):
                    self.add_ship(ship)
            self.display.flip()

    @property
    def ship_to_place(self):
        """Returns a ship length that needs to be placed, if any"""
        placed_sizes = sorted(ship.length for ship in self.ships_list)
        sizes = sorted(self.ships_lengths)
        for placed, to_place in zip_longest(placed_sizes, sizes):
            if placed != to_place:
                return to_place
        return False


class Display:
    """Class to handle PyGame input and output"""
    colours = {
        "board": (0, 0, 0),
        "ship": (255, 255, 255),
        "hit": (139, 0, 0),
        "miss": (30, 144, 255),
        "background": (97, 97, 97)
    }
    colours_2 = {
        "board": (0, 0, 0),
        "ship": (255, 255, 255),
        "hit": (50, 205, 50),
        "miss": (30, 144, 255),
        "background": (97, 97, 97)
    }

    def __init__(self, board_size=10, cell_size=30, margin=15):
        self.board_size = board_size
        self.cell_size = cell_size
        self.margin = margin

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Helvetica", 12)
        self.font_text = pygame.font.SysFont("Helvetica", 12)

        screen_width = self.cell_size * (board_size + 1) + 2 * margin
        screen_height = 2 * self.cell_size * (board_size + 1) + 3 * margin
        self.screen = pygame.display.set_mode([screen_width, screen_height])
        pygame.display.set_caption("Project")

    def show(self, upper_board, lower_board, include_top_ships=False):
        """Functions that draw boards"""
        if upper_board is not None:
            upper_colours = upper_board.colour_grid(self.colours_2, include_top_ships)
        if lower_board is not None:
            lower_colours = lower_board.colour_grid(self.colours)
        alfabet = [chr(i) for i in range(65, 91)]
        self.screen.fill(Display.colours["background"])
        for cord_x in range(self.board_size):
            for cord_y in range(self.board_size):

                if upper_board is not None:
                    # Add symbols

                    if cord_x == 0:
                        white = (255, 255, 255)
                        text = self.font.render(str(cord_y + 1), True, white,
                                                (97, 97, 97))
                        self.screen.blit(text, (self.margin + int(self.cell_size / 4),
                                                self.cell_size + cord_y * self.cell_size +
                                                int(self.cell_size / 8)))

                    if cord_y == 0:
                        white = (255, 255, 255)
                        text = self.font.render(alfabet[cord_x], True, white,
                                                (97, 97, 97))
                        self.screen.blit(text,
                                         (self.margin + (cord_x + 1) * self.cell_size +
                                          int(self.cell_size / 4),
                                          int(self.cell_size / 4)))
                    # Draw board
                    pygame.draw.rect(self.screen, upper_colours[cord_x][cord_y],
                                     [self.cell_size + self.margin + (
                                             cord_y * self.cell_size),
                                      self.cell_size + cord_x * self.cell_size,
                                      self.cell_size - int(self.margin / 2),
                                      self.cell_size - int(self.margin / 2)])

                if lower_board is not None:
                    offset = self.margin * 2 + (self.board_size + 1) * self.cell_size
                    # Add symbols
                    if cord_x == 0:
                        white = (255, 255, 255)
                        text = self.font.render(str(cord_y + 1), True, white,
                                                (97, 97, 97))
                        self.screen.blit(text, (self.margin + int(self.cell_size / 4),
                                                self.cell_size + offset + cord_y * self.cell_size +
                                                int(self.cell_size / 8)))

                    if cord_y == 0:
                        white = (255, 255, 255)
                        text = self.font.render(alfabet[cord_x], True, white,
                                                (97, 97, 97))
                        self.screen.blit(text,
                                         (self.margin + (cord_x + 1) * self.cell_size +
                                          int(self.cell_size / 4),
                                          offset + int(self.cell_size / 4)))
                    # Draw board
                    pygame.draw.rect(self.screen, lower_colours[cord_x][cord_y],
                                     [self.cell_size + self.margin + (
                                             cord_y * self.cell_size),
                                      self.cell_size + offset + cord_x * self.cell_size,
                                      self.cell_size - int(self.margin / 2),
                                      self.cell_size - int(self.margin / 2)])

    def get_input(self, preparing=True):
        """Converts MouseEvents into board corrdinates, for input"""
        cell_margin = self.margin + self.cell_size
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cord_x, cord_y = pygame.mouse.get_pos()
                offset = self.margin * 2 + self.board_size * self.cell_size + self.cell_size
                if preparing:
                    if cord_y > offset and cord_x > cell_margin:
                        cord_y = int(
                            (cord_y - (self.cell_size + offset)) / self.cell_size)
                        cord_x = int((cord_x - cell_margin) / self.cell_size)
                        return cord_x, cord_y
                else:
                    if offset > cord_y > self.cell_size * 0.9 and cord_x > cell_margin:
                        cord_y = int((cord_y - self.cell_size) / self.cell_size)
                        cord_x = int((cord_x - cell_margin) / self.cell_size)
                        return cord_x, cord_y
        return None, None

    def show_text(self, text, prep=False):
        """Displays text on the screen"""
        if prep:
            self.font_text = pygame.font.SysFont("Helvetica", 18)
        white = (255, 255, 255)
        offset = self.margin * 2 + self.board_size * self.cell_size
        text = self.font_text.render(text, True, white, (97, 97, 97))
        self.screen.blit(text, (self.margin + int(self.cell_size / 4), offset))

    @classmethod
    def flip(cls):
        """
        Update window
        :return:
        """
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    @classmethod
    def close(cls):
        """
        Closing window
        :return:
        """
        pygame.display.quit()
        pygame.quit()

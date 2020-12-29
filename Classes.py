import pygame

from itertools import zip_longest


class Direction:
    def __init__(self):
        self.value = 0
        self.direction = "NORTH"

    def next(self):
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


class Ship:
    """Ship class that contains coordinates"""

    def __init__(self, wsp_x, wsp_y, direction, length):
        self.wsp_poczatkowe = (wsp_x, wsp_y)
        self.direction = direction
        self.length = length

    def ship_coordinates(self):
        x, y = self.wsp_poczatkowe
        if self.direction == "NORTH":
            return [(x, y + i) for i in range(self.length)]
        elif self.direction == "EAST":
            return [(x + i, y) for i in range(self.length)]
        elif self.direction == "SOUTH":
            return [(x, y - i) for i in range(self.length)]
        elif self.direction == "WEST":
            return [(x - i, y) for i in range(self.length)]

    def rotate(self, direction):
        self.direction = direction


class Boards:
    def __init__(self, size=10, ships=[1, 2, 3, 4, 5]):
        self.size = size
        self.ships_lengths = ships
        self.ships_list = []
        self.hits_lists = []
        self.misses_lists = []

    @staticmethod
    def ships_overlap(ship1, ship2):
        """Checks if two ships overlap"""
        for ship1_coord in ship1.ship_coordinates():
            for ship2_coord in ship2.ship_coordinates():
                if ship1_coord == ship2_coord:
                    return True
        return False

    def is_valid(self, ship):
        for x, y in ship.ship_coordinates():
            if x < 0 or y < 0 or x >= self.size or y >= self.size:
                return False
        for otherShip in self.ships_list:
            if self.ships_overlap(ship, otherShip):
                return False
        return True

    def add_ship(self, ship):
        """Adds a ship to the board"""
        if self.is_valid(ship):
            self.ships_list.append(ship)
            return True
        else:
            return False

    def remove_ship(self, ship):
        """Removes a ship from the board"""
        self.ships_list.remove(ship)

    def get_ship(self, x, y):
        """Checks if coordinates is ship"""
        for ship in self.ships_list:
            if (x, y) in ship.ship_coordinates():
                return ship
        return None

    def valid_target(self, x, y):
        """Checks whether a set of coordinates is a valid shot"""
        if x not in range(self.size) or y not in range(self.size):
            return False
        for previous_shot in self.misses_lists + self.hits_lists:
            if (x, y) == previous_shot:
                return False
        return True

    def shoot(self, x, y):
        """Registers a shot on the board, saving to appropriate list"""
        if not self.valid_target(x, y):
            return False

        for ship in self.ships_list:
            for ship_coordinate in ship.ship_coordinates():
                if (x, y) == ship_coordinate:
                    self.hits_lists.append((x, y))
                    return True

        self.misses_lists.append((x, y))
        return True

    def colour_grid(self, colours, include_ships=True):
        """Calculates a colour representation of the board for display"""
        grid = [[colours["board"] for _ in range(self.size)] for _ in range(self.size)]

        if include_ships:
            for ship in self.ships_list:
                for y, x in ship.ship_coordinates():
                    grid[x][y] = colours["ship"]

        for y, x in self.hits_lists:
            grid[x][y] = colours["hit"]

        for y, x in self.misses_lists:
            grid[x][y] = colours["miss"]

        return grid

    @property
    def gameover(self):
        """Checks to see if all the ships have been fully hit"""
        for ship in self.ships_list:
            for coordinate in ship.ship_coordinates():
                if coordinate not in self.hits_lists:
                    return False
        return True


class EnemyBoard(Boards):
    def __init__(self, board_size, ship_sizes, ships_list, hits_lists, misses_lists):
        """Initialises the board by randomly placing ships"""
        super().__init__(board_size, ship_sizes)
        self.ships_list = ships_list
        self.hits_lists = hits_lists
        self.misses_lists = misses_lists


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
                text = f"Click where you want your {self.ship_to_place}-long ship to be:"
            else:
                text = 'Click again to rotate a ship, or elsewhere if ready.'

            self.display.show_text(text)

            x, y = self.display.get_input()
            if x is not None and y is not None:
                ship = self.get_ship(x, y)
                if ship:
                    self.remove_ship(ship)
                    direction.next()
                    ship.rotate(direction.direction)
                    if self.is_valid(ship):
                        self.add_ship(ship)
                elif self.ship_to_place:
                    ship = Ship(x, y, direction.direction, self.ship_to_place)
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
        "board": pygame.color.Color("white"),
        "ship": pygame.color.Color("blue"),
        "hit": pygame.color.Color("red"),
        "miss": pygame.color.Color("green"),
        "background": pygame.color.Color("gray")
    }

    def __init__(self, board_size=10, cell_size=30, margin=15):
        self.board_size = board_size
        self.cell_size = cell_size
        self.margin = margin

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Helvetica", 14)

        screen_width = self.cell_size * (board_size + 1) + 2 * margin
        screen_height = 2 * self.cell_size * (board_size + 1) + 3 * margin
        self.screen = pygame.display.set_mode([screen_width, screen_height])
        pygame.display.set_caption("Project")

    def show(self, upper_board, lower_board, include_top_ships=False):
        """Functions that draw boards"""
        if upper_board is not None:
            upper_colours = upper_board.colour_grid(self.colours, include_top_ships)
        if lower_board is not None:
            lower_colours = lower_board.colour_grid(self.colours)
        alfabet = [chr(i) for i in range(65, 91)]
        self.screen.fill(Display.colours["background"])
        for x in range(self.board_size):
            for y in range(self.board_size):

                if upper_board is not None:
                    """Add symbols"""
                    if x == 0:
                        white = (255, 255, 255)
                        text = self.font.render(str(y + 1), True, white, pygame.color.Color("gray"))
                        self.screen.blit(text, (self.margin + int(self.cell_size / 4),
                                                self.cell_size + y * self.cell_size + int(self.cell_size / 8)))

                    if y == 0:
                        white = (255, 255, 255)
                        text = self.font.render(alfabet[x], True, white, pygame.color.Color("gray"))
                        self.screen.blit(text, (self.margin + (x + 1) * self.cell_size + int(self.cell_size / 4),
                                                int(self.cell_size / 4)))
                    """Draw board"""
                    pygame.draw.rect(self.screen, upper_colours[x][y],
                                     [self.cell_size + self.margin + (y * self.cell_size),
                                      self.cell_size + x * self.cell_size,
                                      self.cell_size - int(self.margin / 2), self.cell_size - int(self.margin / 2)])

                if lower_board is not None:
                    offset = self.margin * 2 + (self.board_size + 1) * self.cell_size
                    """Add symbols"""
                    if x == 0:
                        white = (255, 255, 255)
                        text = self.font.render(str(y + 1), True, white, pygame.color.Color("gray"))
                        self.screen.blit(text, (self.margin + int(self.cell_size / 4),
                                                self.cell_size + offset + y * self.cell_size + int(self.cell_size / 8)))

                    if y == 0:
                        white = (255, 255, 255)
                        text = self.font.render(alfabet[x], True, white, pygame.color.Color("gray"))
                        self.screen.blit(text, (self.margin + (x + 1) * self.cell_size + int(self.cell_size / 4),
                                                offset + int(self.cell_size / 4)))
                    """Draw board"""
                    pygame.draw.rect(self.screen, lower_colours[x][y],
                                     [self.cell_size + self.margin + (y * self.cell_size),
                                      self.cell_size + offset + x * self.cell_size,
                                      self.cell_size - int(self.margin / 2), self.cell_size - int(self.margin / 2)])

    def get_input(self, preparing=True):
        """Converts MouseEvents into board corrdinates, for input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                offset = self.margin * 2 + self.board_size * self.cell_size + self.cell_size
                if preparing:
                    if y > offset and x > self.margin + self.cell_size:
                        y = int((y - (self.cell_size + offset)) / self.cell_size)
                        x = int((x - (self.margin + self.cell_size)) / self.cell_size)
                        return x, y
                else:
                    if offset > y > self.cell_size * 0.9 and x > self.margin + self.cell_size:
                        y = int((y - self.cell_size) / self.cell_size)
                        x = int((x - (self.margin + self.cell_size)) / self.cell_size)
                        return x, y
        return None, None

    def show_text(self, text):
        """Displays text on the screen"""
        white = (255, 255, 255)
        offset = self.margin * 2 + self.board_size * self.cell_size
        text = self.font.render(text, True, white, pygame.color.Color("gray"))
        self.screen.blit(text, (self.margin + int(self.cell_size / 4), offset))

    @classmethod
    def flip(cls):
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    @classmethod
    def close(cls):
        pygame.display.quit()
        pygame.quit()

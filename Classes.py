class Gracz(object):
    def __init__(self, gracz):
        import numpy as np
        self.board = np.zeros((10, 10))
        self.statki = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
        self.name = gracz

    def alreadyShip(self, location):
        pass

    def addShips(self):
        # Dodanie okretów na boarda
        pass

    def isHit(self):
        pass

    def Hit(self):
        pass


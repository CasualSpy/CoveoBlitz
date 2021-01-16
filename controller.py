from enum import Enum
import math
from game_message import GameMessage, Crew


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class controller:
    def __init__(self, game_message: GameMessage):
        pass

    def turn(self, game_message: GameMessage, crew: Crew):
        pass

    def getdistancebetween(self, point1: Point, point2: Point):
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


class StateMachine(Enum):
    EARLYGAME = "EARLYGAME"
    MIDGAME = "MIDGAME"
    ENDGAME = "ENDGAME"
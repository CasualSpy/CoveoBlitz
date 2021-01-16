from enum import Enum
from game_message import GameMessage, Crew
class controller:
    def __init__(self, game_message: GameMessage):
        pass
    def turn(self, game_message: GameMessage, crew: Crew):
        pass

class StateMachine(Enum):
    EARLYGAME = "EARLYGAME"
    MIDGAME = "MIDGAME"
    ENDGAME = "ENDGAME"
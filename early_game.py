from game_message import GameMessage, Crew
from controller import controller, StateMachine


class EarlyGameController(controller):
    def __init__(self, game_message: GameMessage):
        self.NextState = None
        pass

    def turn(self, game_message: GameMessage, crew: Crew):
        ###


        ###
        #Set Next State
        #self.NextState = StateMachine.Early
        pass

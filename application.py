#!/usr/bin/env python

import asyncio
import os
from enum import Enum

import websockets
import json

from bot import Bot
from bot_message import BotMessage, MessageType
from controller import StateMachine
from early_game import EarlyGameController
from game_message import GameMessage, Crew
from game_command import UnitActionType

async def run():
    uri = "ws://127.0.0.1:8765"

    async with websockets.connect(uri) as websocket:
        bot = Bot()
        if "TOKEN" in os.environ:
            await websocket.send(json.dumps({"type": "REGISTER", "token": os.environ["TOKEN"]}))
        else:
            await websocket.send(json.dumps({"type": "REGISTER", "crewName": "MyBot"}))

        await game_loop(websocket=websocket, bot=bot)


async def game_loop(websocket: websockets.WebSocketServerProtocol, bot: Bot):
    nextState = None
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            # Connection is closed, the game is probably over
            break
        game_message: GameMessage = GameMessage.from_json(message)

        my_crew: Crew = game_message.get_crews_by_id()[game_message.crewId]
        print(f"\Tick {game_message.tick}")
        print(f"\nError? {' '.join(my_crew.errors)}")

        if nextState is None:
            earlyGame = EarlyGameController(game_message)
            nextState = earlyGame.NextState
        elif nextState == StateMachine.EARLYGAME:
            pass
            #Something
        elif nextState == StateMachine.MIDGAME:
            pass
            #Something
        elif nextState == StateMachine.ENDGAME:
            pass
            #Something

        next_move: UnitActionType.MOVE = bot.get_next_move(game_message)
        await websocket.send(BotMessage(type=MessageType.COMMAND, actions=next_move, tick=game_message.tick).to_json())


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
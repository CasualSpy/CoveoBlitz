from typing import List
from copy import copy
from functools import reduce
from game_message import GameMessage, Position, Crew, Unit, UnitType, Map
from game_command import Action, UnitAction, UnitActionType
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder



class Bot:
    def __init__(self):
        self.mines = []
        self.matrix = []

    def get_next_move(self, game_message: GameMessage) -> List[Action]:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        my_crew: Crew = game_message.get_crews_by_id()[game_message.crewId]
        if self.mines == []:
            transposed = []
            for x, col in enumerate(game_message.map.tiles):
                matrix_col = []
                for y, tile in enumerate(col):
                    matrix_col.append(1 if tile == "EMPTY" or tile == "MINE" else 0)
                    if tile == "MINE":
                        self.mines.append(Position(x,y))
                transposed.append(matrix_col)
            self.matrix = [[transposed[j][i] for j in range(len(transposed))] for i in range(len(transposed[0]))]
            print(self.matrix)
            self.finder = AStarFinder(diagonal_movement = DiagonalMovement.never)
            self.mine_neighbors = []
            for mine in self.mines:
                self.mine_neighbors += self.neighbors(mine)
            self.mine_neighbors = list(filter(lambda n : game_message.map.get_raw_tile_value_at(n) == "EMPTY", self.mine_neighbors))
            self.base_neighbors = self.neighbors(my_crew.homeBase)

        self.units = []
        for crew in game_message.crews:
            self.units += crew.units

        actions: List[UnitAction] = []
        for unit in my_crew.units:
            if unit.type == UnitType.MINER:
                if unit.blitzium == 5:
                    is_next_to_base = False
                    for neighbor in self.base_neighbors:
                        if neighbor.x == unit.position.x and neighbor.y == unit.position.y:
                            is_next_to_base = True
                            break
                    if is_next_to_base:
                        actions.append(UnitAction(UnitActionType.DROP, unit.id, my_crew.homeBase))
                    else:
                        base_neighbor = self.closest_to(unit.position, self.base_neighbors)
                        actions.append(UnitAction(UnitActionType.MOVE, unit.id, base_neighbor))
                else:
                    is_next_to_mine = False
                    for neighbor in self.mine_neighbors:
                        if neighbor.x == unit.position.x and neighbor.y == unit.position.y:
                            is_next_to_mine = True
                            break
                    if is_next_to_mine:
                        mine = self.closest_to(unit.position, self.mines)
                        actions.append(UnitAction(UnitActionType.MINE, unit.id, mine))
                    else:
                        mine_neighbor = self.closest_to(unit.position, self.mine_neighbors)
                        actions.append(UnitAction(UnitActionType.MOVE, unit.id, mine_neighbor))


        miners_position = []
        for unit in my_crew.units:
            if unit.type == "MINER":
                miners_position.append(unit.position)

        if unit.type == UnitType.CART:
            actions.append(UnitAction(UnitActionType.Move, unit.id, miners_position))
            if game_message.rules.MAX_CART_CARGO:
                actions.append(UnitAction(UnitActionType.MOVE, unit.id, my_crew.homeBase))
                actions.append(UnitAction(UnitActionType.DROP, unit.id))

        return actions

    def closest_to(self, position: Position, nodes: List[Position]):
        best_path = None
        distance = 0
        for node in nodes:
            path = self.get_path(position, node)
            if (best_path == None or len(path) < distance) and len(path) > 0:
                best_path = path
                distance = len(path)
        return Position(best_path[1][0], best_path[1][1])

    def get_path(self, start: Position, end: Position):
        grid = Grid(matrix=self.matrix)
        path_start = grid.node(start.x, start.y)
        path_end = grid.node(end.x, end.y)
        path, _ = self.finder.find_path(path_start, path_end, grid)
        return path
    def neighbors(self, position: Position):
        tiles = [(1,0),(-1,0),(0,1),(0,-1)]
        return [Position(t[0] + position.x, t[1] + position.y) for t in tiles]

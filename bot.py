from typing import List
from functools import reduce
from game_message import GameMessage, Position, Crew, Unit, UnitType
from game_command import Action, UnitAction, UnitActionType
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder



class Bot:
    def __init__(self):
        self.mines = []
        self.matrix = []
        self.finder = AStarFinder(diagonal_movement = DiagonalMovement.never)

    def get_next_move(self, game_message: GameMessage) -> List[Action]:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        if self.mines == []:
            for x, col in enumerate(game_message.map.tiles):
                matrix_col = []
                for y, tile in enumerate(col):
                    matrix_col.append(1 if tile == "EMPTY" else 0)
                    if tile == "MINE":
                        self.mines.append(Position(x,y))
                self.matrix.append(matrix_col)
            self.mine_neighbors = reduce(lambda x, y : x + y, list(map(self.neighbors, self.mines)))

        my_crew: Crew = game_message.get_crews_by_id()[game_message.crewId]
        self.units = reduce(lambda x, y : x + y, list(map(lambda x : x.units, game_message.crews)))

        actions: List[UnitAction] = []
        for unit in my_crew.units:
            if unit.type == UnitType.MINER:
                is_next_to_mine = reduce(lambda x, y : x or y, map(lambda m : m.x == unit.position.x and m.y == unit.position.y, self.mine_neighbors))
                if is_next_to_mine:
                    actions.append(UnitAction(UnitActionType.MINE, unit.id, self.closest_to(unit.position, self.mines)))
                else:
                    actions.append(UnitAction(UnitActionType.MOVE, unit.id, self.closest_to(unit.position, self.mines)))

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
        new_matrix = self.matrix[:]
        for unit in self.units:
            new_matrix[unit.position.x][unit.position.y] = 0
        grid = Grid(matrix = new_matrix)
        path_start = grid.node(start.x, start.y)
        path_end = grid.node(end.x, end.y)
        path, _ = self.finder.find_path(path_start, path_end, grid)
        return path
    def neighbors(self, position: Position):
        tiles = [(1,0),(-1,0),(0,1),(0,-1)]
        return list(map(lambda x : Position(x[0] + position.x, x[1] + position.y), tiles))

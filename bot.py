from typing import List
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

        #print(self.mines)
        my_crew: Crew = game_message.get_crews_by_id()[game_message.crewId]
        #print(my_crew.units)

        actions: List[UnitAction] = [UnitAction(UnitActionType.MOVE,
                                                unit.id,
                                                self.closest_to(unit.position, self.mines)) for unit in my_crew.units]
        return actions

    def closest_to(self, position: Position, nodes: List[Position]):
        #print(position, nodes)
        best_path = None
        distance = 0
        for node in nodes:
            path = self.get_path(position, node)
            if (best_path == None or len(path) < distance) and len(path) > 0:
                best_path = path
                distance = len(path)
        #print(best_path[0])
        return Position(best_path[1][0], best_path[1][1])

    def get_path(self, start: Position, end: Position):
        grid = Grid(matrix = self.matrix)
        path_start = grid.node(start.x, start.y)
        path_end = grid.node(end.x, end.y)
        path, _ = self.finder.find_path(path_start, path_end, grid)
        return path

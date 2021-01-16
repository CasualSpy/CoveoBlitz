from typing import List
from copy import copy
from functools import reduce
from game_message import GameMessage, Position, Crew, Unit, UnitType
from game_command import Action, UnitAction, UnitActionType, BuyAction
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder



class Bot:
    def __init__(self):
        self.mines = []
        self.matrix = []
        self.minors: List[Minor] = []
        self.carts: List[Cart] = []

    def get_next_move(self, game_message: GameMessage) -> List[Action]:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        my_crew: Crew = game_message.get_crews_by_id()[game_message.crewId]

        if self.mines == []:
            for x, col in enumerate(game_message.map.tiles):
                matrix_col = []
                for y, tile in enumerate(col):
                    pos = Position(x,y)
                    matrix_col.append(1 if tile == "EMPTY" or tile == "MINE" else 0)
                    if tile == "MINE":
                        self.mines.append(Position(x,y))
                self.matrix.append(matrix_col)
            self.mine_neighbors = reduce(lambda x, y : x + y, list(map(self.neighbors, self.mines)))
            self.base_neighbors = self.neighbors(my_crew.homeBase)
        self.units = reduce(lambda x, y : x + y, list(map(lambda x : x.units, game_message.crews)))

        for minor in self.minors:
            if minor.isDirty:
                unit = next((x for x in my_crew.units if x.id == minor.id), None)
                minor.position = unit.position

        actions: List[UnitAction] = []
        for unit in my_crew.units:
            print(unit.position)
            if unit.type == UnitType.CART:
                minor = next((x for x in self.minors if x.hasCart is False), None)
                if minor is not None:
                    minor.hasCart = True
                    cart = Cart(minor, unit.id)
                    self.carts.append(cart)

                cartObject = next((x for x in self.carts if x.id is unit.id), None)
                if unit.blitzium == 0:
                    minor = self.getClosestMinor(my_crew, unit, cartObject)
                    closest_path = self.closest_to(unit.position, [minor.position], my_crew)
                    minor_neighbors = self.neighbors(minor.position)

                    is_next_to_minor = reduce(lambda x, y: x or y,
                                              map(lambda m: m.x == unit.position.x and m.y == unit.position.y,
                                                  minor_neighbors))

                    if is_next_to_minor and unit.blitzium < 25:
                        actions.append(UnitAction(UnitActionType.PICKUP, unit.id, minor.position))
                    else:
                        actions.append(UnitAction(UnitActionType.MOVE, unit.id, closest_path))
                else:
                    closest_path_base = self.closest_to(unit.position, self.base_neighbors, my_crew)

                    is_next_to_base = reduce(lambda x, y: x or y,
                                             map(lambda m: m.x == unit.position.x and m.y == unit.position.y,
                                                 self.base_neighbors))
                    if is_next_to_base:
                        actions.append(UnitAction(UnitActionType.DROP, unit.id, my_crew.homeBase))
                    else:
                        actions.append(UnitAction(UnitActionType.MOVE, unit.id, closest_path_base))
            elif unit.type == UnitType.MINER:
                minor = next((x for x in self.minors if x.id is not unit.id), None)
                if minor is not None:
                    newMinor = Minor(unit.position, False, False, unit.id)
                    self.minors.append(newMinor)
                if game_message.tick == 0:
                    minor = Minor(unit.position, False, False, unit.id)
                    self.minors.append(minor)

                #if unit.blitzium == 5:
                ##    is_next_to_base = reduce(lambda x, y : x or y, map(lambda m : m.x == unit.position.x and m.y == unit.position.y, self.base_neighbors))
                #    if is_next_to_base:
                #        actions.append(UnitAction(UnitActionType.DROP, unit.id, my_crew.homeBase))
                #    else:
                #        base_neighbor = self.closest_to(unit.position, self.base_neighbors)
                 #       actions.append(UnitAction(UnitActionType.MOVE, unit.id, base_neighbor))
                #else:
                minor = next((x for x in self.minors if x.position == unit.position), None)
                is_next_to_mine = reduce(lambda x, y : x or y, map(lambda m : m.x == unit.position.x and m.y == unit.position.y, self.mine_neighbors))
                if is_next_to_mine:
                    mine = self.closest_to(unit.position, self.mines, my_crew)
                    actions.append(UnitAction(UnitActionType.MINE, unit.id, mine))
                    minor.isMining = True
                else:
                    mine_neighbor = self.closest_to(unit.position, self.mine_neighbors, my_crew)
                    actions.append(UnitAction(UnitActionType.MOVE, unit.id, mine_neighbor))
                    minor.isDirty = True

        #carts = self.getCarts(my_crew)

        if not self.hasSameAmountofMinorsAndCart(my_crew):
            actions.append(BuyAction(UnitType.CART))

        #for cart in carts:


        return actions


    def closest_to(self, position: Position, nodes: List[Position], my_crew):
        best_path = None
        distance = 0
        print(position)
        if position in nodes:
            return None

        crewPositions = []
        for unit in my_crew.units:
            if position != unit.position:
                crewPositions.append((unit.position.x, unit.position.y))
        for node in nodes:
            path = self.get_path(position, node)
            if my_crew.homeBase != position:
                for unit in crewPositions:
                    if unit in path:
                        self.matrix[unit[0]][unit[1]] = 0
                        path = self.get_path(position, node)
                        self.matrix[unit[0]][unit[1]] = 1
            if (best_path == None or len(path) < distance) and len(path) > 0:
                best_path = path
                distance = len(path)

        best_path_pos = Position(best_path[1][0], best_path[1][1])
        return best_path_pos

    def get_path(self, start: Position, end: Position):
        grid = Grid(matrix = self.matrix)
        path_start = grid.node(start.x, start.y)
        path_end = grid.node(end.x, end.y)
        finder = AStarFinder(diagonal_movement = DiagonalMovement.never)
        path, _ = finder.find_path(path_start, path_end, grid)
        return path

    def neighbors(self, position: Position):
        tiles = [(1,0),(-1,0),(0,1),(0,-1)]
        return list(map(lambda x : Position(x[0] + position.x, x[1] + position.y), tiles))

    def getMinorsPositions(self, my_crew):
        miners_position = []
        for unit in my_crew.units:
            if unit.type == UnitType.MINER:
                miners_position.append(unit.position)
        return miners_position

    def getCarts(self, my_crew):
        carts = []
        for unit in my_crew.units:
            if unit.type == UnitType.CART:
                carts.append(unit)
        return carts

    def getMinorFromPosition(self, my_crew, minor_pos):
        for unit in my_crew.units:
            if unit.type == UnitType.MINER:
                if unit.position == minor_pos:
                    return unit

    def getClosestMinor(self, my_crew, cart, cartUnit):
        distance = None
        minor = None
        for unit in my_crew.units:
            if unit.type == UnitType.MINER:
                if cartUnit.minor.id == unit.id:
                    return unit
                minor = next((x for x in self.minors if x.position == unit.position), None)
                if not minor.hasCart:
                    dist = abs(cart.position.x - unit.position.x) + abs(cart.position.y - unit.position.y)
                    if distance == None or dist < distance:
                        distance = dist
                        minor = unit
        return minor

    def hasSameAmountofMinorsAndCart(self, my_crew):
        minor_amount = 0
        cart_amount = 0
        for unit in my_crew.units:
            if unit.type == UnitType.MINER:
                minor_amount+=1
            elif unit.type == UnitType.CART:
                cart_amount +=1
        return minor_amount == cart_amount


class Minor():
    def __init__(self, position, hasCart, isMining, id):
        self.position = position
        self.hasCart = hasCart
        self.isMining = isMining
        self.isDirty = False
        self.id = id


class Cart():
    def __init__(self, minor: Minor, id):
        self.minor = minor
        self.id = id
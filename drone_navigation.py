from queuewrap import QueueWrap

import numpy as np

from enum import Enum

from node import Node
from nodetype import NodeType, NodeTypeStatics
from world import World



class State(Enum):
    IDLE = 0
    MOVING = 1



def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5  # euclidean
    # return max(abs(x2 - x1), abs(y2 - y1))  # octal
    # return abs(x2 - x1) + abs(y2 - y1)  # manhattan



class DroneNavigation:
    UNSEEN_NODE_VALUE = -1

    NEIGHBOUR_GRID_OFFSETS = [(dx, dy) for dx, dy in World.NEIGHBOUR_GRID_OFFSETS]
    NEIGHBOUR_GRID_OFFSETS_DISTANCED = [(dx, dy, calculate_distance(0, 0, dx, dy))
                                        for dx, dy in NEIGHBOUR_GRID_OFFSETS]

    PASSABLE_NODETYPES = NodeTypeStatics.PASSABLE_TYPES
    PASSABLE_VALUES = NodeTypeStatics.PASSABLE_VALUES

    def __init__(self, world_rows: int, world_columns: int, start_node: Node, end_node: Node):
        self.world_grid: np.array = initialize_world(
                world_rows, world_columns, start_node)
        self.visited: np.array = initialize_visited(
                world_rows, world_columns, start_node)

        self.end_x, self.end_y = end_node.coordinates

        self.world_rows = world_rows
        self.world_columns = world_columns

        self.state: State = State.IDLE
        self.path: [(int, int)] = []

        self.current_node: Node = start_node
        self.next_node: Node = self.current_node

    def get_next_grid_xy(self, current_node: Node, visible_nodes: [Node]) -> (int, int):
        self.current_node = current_node

        x, y = current_node.coordinates
        self.visited[y, x] = True

        found_new_nodes = self.remember_node(current_node)
        found_new_nodes = self.remember_nodes(visible_nodes) or found_new_nodes

        if found_new_nodes or self.state == State.IDLE:
            return self.handle_idle_state(current_node)
        elif self.state == State.MOVING:
            return self.handle_moving_state(current_node)

        return current_node.coordinates

    def handle_idle_state(self, current_node: Node) -> (int, int):
        self.path = self.a_star(current_node)

        if len(self.path) == 0:
            return current_node.coordinates

        self.state = State.MOVING
        return self.pop_next_loc_from_path()

    def handle_moving_state(self, current_node: Node) -> (int, int):
        return (self.pop_next_loc_from_path()
                if 0 < len(self.path)
                else self.handle_idle_state(current_node))

    def pop_next_loc_from_path(self):
        self.next_node = self.path.pop(0)

        if len(self.path) == 0:
            self.state = State.IDLE

        return self.next_node

    def remember_nodes(self, visible_nodes: [Node]) -> bool:
        return any([self.remember_node(node) for node in visible_nodes])

    def remember_node(self, visible_node: Node) -> bool:
        x, y = visible_node.coordinates
        if not self.is_in_bounds(x, y):
            return False

        self.reconsider_need_for_visit(x, y)

        if self.world_grid[y, x] != DroneNavigation.UNSEEN_NODE_VALUE:
            return False

        self.world_grid[y, x] = visible_node.node_type.value
        return True

    def reconsider_need_for_visit(self, x: int, y: int):
        if not self.is_in_bounds(x, y) or self.is_visited(x, y) or not self.is_seen(x, y):
            return

        neighbours = self.get_neighbours(x, y)

        if not all(self.is_seen(x2, y2) for x2, y2 in neighbours):
            return

        self.visited[y, x] = True

        for x2, y2 in neighbours:
            self.reconsider_need_for_visit(x2, y2)

    def is_seen(self, x: int, y: int) -> bool:
        return (self.is_in_bounds(x, y) and
                self.world_grid[y, x] != DroneNavigation.UNSEEN_NODE_VALUE)

    def a_star(self, current_node: Node) -> [(int, int)]:
        distances = initialize_distances(self.world_grid, current_node)
        previous = initialize_previous(self.world_grid)

        queue = QueueWrap([(0, current_node.coordinates)])

        while not queue.is_empty():
            x, y = queue.pop()
            x, y = (int(x), int(y))

            current_distance = distances[y, x]

            if self.is_end(x, y) or not self.is_visited(x, y):
                return get_path_from_start(x, y, previous)

            for x2, y2, distance_to in self.get_passable_neighbours_with_distances(x, y):
                distance_from_current = current_distance + distance_to

                if distances[y2, x2] <= distance_from_current:
                    continue

                distances[y2, x2] = distance_from_current
                previous[y2, x2] = np.array([x, y])

                queue.push(distance_from_current + self.distance_to_end(x2, y2), (x2, y2))

        return []  # means there is no way to get to end

    def is_end(self, x: int, y: int) -> bool:
        return (x, y) == (self.end_x, self.end_y)

    def get_neighbours(self, x: int, y: int) -> [(int, int)]:
        return list(filter(lambda pair: self.is_in_bounds(pair[0], pair[1]),
                           [(x + dx, y + dy)
                            for dx, dy in DroneNavigation.NEIGHBOUR_GRID_OFFSETS]))

    def get_passable_neighbours_with_distances(self, x: int, y: int) -> [(int, int, float)]:
        return list(filter(lambda triple: self.is_passable(triple[0], triple[1]),
                           [(x + dx, y + dy, distance)
                            for dx, dy, distance in
                            DroneNavigation.NEIGHBOUR_GRID_OFFSETS_DISTANCED]))

    def is_passable(self, x: int, y: int) -> bool:
        return self.is_in_bounds(x, y) and self.world_grid[y, x] in DroneNavigation.PASSABLE_VALUES

    def is_in_bounds(self, x2: int, y2: int) -> bool:
        return 0 <= x2 < self.world_columns and 0 <= y2 < self.world_rows

    def distance_to_end(self, x: int, y: int) -> float:
        return calculate_distance(x, y, self.end_x, self.end_y)

    def is_visited(self, x: int, y: int):
        return self.is_in_bounds(x, y) and self.visited[y, x]



def initialize_world(world_rows: int, world_columns: int, start_node: Node) -> np.array:
    output = np.repeat(DroneNavigation.UNSEEN_NODE_VALUE,
                       world_rows * world_columns).reshape([world_rows, world_columns])

    sx, sy = start_node.coordinates
    output[sy, sx] = NodeType.START.value

    return output



def initialize_visited(world_rows: int, world_columns: int, start_node: Node) -> np.array:
    output = np.repeat(False, world_rows * world_columns).reshape([world_rows, world_columns])

    sx, sy = start_node.coordinates
    output[sy, sx] = True

    return output



def initialize_distances(world: np.array, start_node: Node) -> np.array:
    n_rows, n_columns = world.shape
    output = np.repeat(float("inf"), n_rows * n_columns).reshape(world.shape)

    sx, sy = start_node.coordinates
    output[sy, sx] = 0

    return output



def initialize_previous(world: np.array) -> np.array:
    n_rows, n_columns = world.shape
    return np.repeat(-1, n_rows * n_columns * 2).reshape([n_rows, n_columns, 2])



def get_path_from_start(x: int, y: int, previous: np.array) -> [(int, int)]:
    output = []

    while 0 <= x and 0 <= y:
        output.append((x, y))
        x, y = previous[y, x]

    return output[::-1][1:]

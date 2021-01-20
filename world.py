import numpy as np

from node import *
from nodetype import *
from queuewrap import QueueWrap

EPSILON = 0.01
POINT_OFFSETS = [(0.5, 0.5), (0, 0), (1, 0), (0, 1), (1, 1)]


class World:
    # this is not the same as visibility
    NEIGHBOUR_GRID_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    #    def __init__(self, room_width: float, room_depth: float,
    #                 world_string: str, minimize_world: bool = True):

    def __init__(self, node_width: float, node_depth: float,
                 world_string: str, minimize_world: bool = True):

        self.grid: np.array = create_world(world_string, minimize_world)

        self.n_rows, self.n_columns = self.grid.shape
        self.room_width, self.room_depth = (
        self.n_columns * node_width, self.n_rows * node_depth)  # <- might as well forget it?
        # self.node_width: float = node_width / self.n_columns
        # self.node_height: float = node_depth / self.n_rows
        self.node_width: float = node_width
        self.node_height: float = node_depth

        self.start_node: Node = find_start_node(self)
        self.end_node: Node = find_end_node(self)

    def is_grid_loc_in_bounds(self, grid_x: int, grid_y: int) -> bool:
        return 0 <= grid_x < self.n_columns and 0 <= grid_y < self.n_rows

    def find_nodetype_value_at_grid_loc(self, grid_x: int, grid_y: int) -> int:
        return (self.grid[grid_y, grid_x]
                if self.is_grid_loc_in_bounds(grid_x, grid_y)
                else NodeType.VACANT.value)

    def find_nodetype_at_grid_loc(self, grid_x: int, grid_y: int) -> NodeType:
        return NodeTypeStatics.value_to_nodetype[self.find_nodetype_value_at_grid_loc(grid_x,
                                                                                      grid_y)]

    def grid_loc_to_node(self, grid_x: int, grid_y: int) -> Node:
        return Node(self.find_nodetype_at_grid_loc(grid_x, grid_y),
                    (grid_x + 0.5) * self.node_width,
                    (grid_y + 0.5) * self.node_height,
                    grid_x, grid_y)

    def is_grid_loc_passable(self, grid_x: int, grid_y: int) -> bool:
        return (self.is_grid_loc_in_bounds(grid_x, grid_y) and
                self.find_nodetype_value_at_grid_loc(grid_x, grid_y)
                in NodeTypeStatics.PASSABLE_VALUES)

    def get_in_bounds_neighbouring_nodes(self, node: Node) -> [Node]:
        return [self.grid_loc_to_node(i, j)
                for i, j in get_neighbour_grid_locs(node)
                if self.is_grid_loc_in_bounds(i, j)]

    def find_visible_nodes(self, source_node: Node) -> [Node]:
        n_rows, n_columns = (self.n_rows, self.n_columns)
        visibility_array = np.repeat(0, n_rows * n_columns).reshape([n_rows, n_columns])

        sx, sy = source_node.coordinates

        def get_visibility(node_to_check: Node):
            cx, cy = node_to_check.coordinates

            to_check = list(filter(lambda xy: self.is_grid_loc_in_bounds(xy[0], xy[1]),
                                   get_visibility_neighbours(cx, cy, sx, sy)))

            n = len(to_check)

            if n == 0:
                return 0

            if n == 1:
                nx, ny = to_check[0]
                return (2
                        if visibility_array[ny, nx] == 2 and self.is_grid_loc_passable(nx, ny)
                        else 0)

            return sum([visibility_array[oy, ox] == 2 and self.is_grid_loc_passable(ox, oy)
                        for ox, oy in to_check])

        output = []
        queue = QueueWrap([(0, (sx, sy))])

        while not queue.is_empty():
            x, y = queue.pop()

            if 0 < visibility_array[y, x]:
                continue

            node = self.grid_loc_to_node(x, y)
            visibility = 2 if sx == x and sy == y else get_visibility(node)

            if visibility == 0:
                continue

            visibility_array[y, x] = visibility
            output.append(node)

            if node.node_type == NodeType.OBSTACLE or visibility < 2:
                continue

            for neighbour in self.get_in_bounds_neighbouring_nodes(node):
                x2, y2 = neighbour.coordinates
                queue.push(calculate_distance(x, y, x2, y2), (x2, y2))

        return output

    def get_visible_nodes(self, node: Node) -> [Node]:
        return self.find_visible_nodes(node)

    def get_node_by_pos(self, x: float, y: float) -> Node:
        return self.grid_loc_to_node(int(x / self.node_width), int(y / self.node_height))


def get_neighbour_grid_locs(node: Node) -> [(int, int)]:
    grid_x, grid_y = node.coordinates

    return [(grid_x + offset_x, grid_y + offset_y)
            for offset_x, offset_y in World.NEIGHBOUR_GRID_OFFSETS]


def create_world(world_string: str, minimal: bool) -> np.array:
    array = world_string_to_array(fix_spaces(world_string))
    return clean_world_array(array) if minimal else array


def world_string_to_array(world_string: str) -> np.array:
    rows = world_string.strip().split("\n")

    n_rows = len(rows)
    n_columns = max([len(row) for row in rows])

    array = np.repeat(NodeType.VACANT.value, n_rows * n_columns).reshape([n_rows, n_columns])

    for i, row in enumerate(rows):
        for j, c in enumerate(row):
            array[i, j] = NodeTypeStatics.character_to_nodetype[c].value

    return array


def fix_spaces(world_string: str) -> str:
    space_replacer = NodeTypeStatics.nodetype_to_character[NodeType.VACANT]

    if " " in world_string and " " not in NodeTypeStatics.character_to_nodetype:
        world_string = world_string.replace(" ", space_replacer)

    return world_string


def clean_world_array(world_array: np.array) -> np.array:
    row_n, column_n = world_array.shape

    row_first, row_last = find_necessary_row_range(world_array, row_n)
    column_first, column_last = find_necessary_row_range(
        world_array.transpose(), column_n)

    return world_array[row_first:row_last, column_first:column_last]


def find_necessary_row_range(array: np.array, n: int) -> (int, int):
    def is_row_necessary(j: int) -> bool:
        return np.any(array[j, :] != NodeType.VACANT.value)

    first = 0
    last = n

    for i in range(n):
        if is_row_necessary(i):
            first = i
            break

    for i in range(n)[::-1]:
        if is_row_necessary(i):
            last = i + 1
            break

    return first, last


def find_node_of_type(world: World, nodetype: NodeType) -> Node or None:
    world_array = world.grid
    nodetype_value = nodetype.value

    n_i, n_j = world_array.shape

    for i in range(n_i):
        for j in range(n_j):
            if world_array[i, j] == nodetype_value:
                return world.grid_loc_to_node(j, i)

    return None


def find_end_node(world: World) -> Node or None:
    return find_node_of_type(world, NodeType.END)


def find_start_node(world: World) -> Node or None:
    return find_node_of_type(world, NodeType.START)


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5  # euclidean
    # return max(abs(x2 - x1), abs(y2 - y1))  # octal
    # return abs(x2 - x1) + abs(y2 - y1)  # manhattan


def get_overshoot_checker(x: float, y: float, sx: float, sy: float) -> callable:
    dx, dy = (sx - x, sy - y)

    def overshoot_checker(x2: float, y2: float) -> bool:
        dx2, dy2 = (sx - x2, sy - y2)

        if ((dx < 0) != (dx2 < 0)) or ((dy < 0) != (dy2 < 0)):
            return True

        return False

    return overshoot_checker


def get_visibility_neighbours(x: int, y: int, sx: int, sy: int) -> [(int, int)]:
    # assume (x, y) != (sx, sy)
    return ([] if sy == y else [(x, y - 1 if sy < y else y + 1)]) + \
           ([] if sx == x else [(x - 1 if sx < x else x + 1, y)])

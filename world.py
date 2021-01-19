import numpy as np

from node import *
from nodetype import *



class World:
    # this is not the same as visibility
    NEIGHBOUR_GRID_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, room_width: float, room_depth: float,
                 world_string: str, minimize_world: bool = True):
        self.grid: np.array = create_world(world_string, minimize_world)

        self.n_rows, self.n_columns = self.grid.shape
        self.room_width, self.room_depth = (room_width, room_depth)  # <- might as well forget it?
        self.node_width: float = room_width / self.n_columns
        self.node_height: float = room_depth / self.n_rows

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

    def get_neighbouring_nodes(self, node: Node) -> [Node]:
        return [self.grid_loc_to_node(i, j)
                for i, j in get_neighbour_grid_locs(node)
                if self.is_grid_loc_in_bounds(i, j)]

    def temp_visibility(self, current_node: Node, neighbours: [Node]) -> [Node]:
        output = list(neighbours)

        x, y = current_node.coordinates

        for dx, dy in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            if self.is_grid_loc_passable(x + dx, y) or self.is_grid_loc_passable(x, y + dy):
                output.append(self.grid_loc_to_node(x + dx, y + dy))

        return output

    def get_visible_nodes(self, node: Node) -> [Node]:
        return self.temp_visibility(node, self.get_neighbouring_nodes(node))

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

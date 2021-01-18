from nodetype import NodeType



class Node:
    def __init__(self, node_type: NodeType,
                 center_x: float, center_y: float,
                 coord_x: int, coord_y: int):
        self.node_type = node_type
        self.center_loc = (center_x, center_y)
        self.coordinates = (coord_x, coord_y)

    def __repr__(self):
        return f"Node<{self.node_type}>({self.center_loc}, {self.coordinates})"

    def __str__(self):
        return self.__repr__()

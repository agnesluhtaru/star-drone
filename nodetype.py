from enum import Enum



class NodeType(Enum):
    VACANT = 0
    OBSTACLE = 1
    START = 2
    END = 3



class NodeTypeStatics:
    value_to_nodetype = dict((int(node_type.value), node_type)
                             for node_type in [NodeType.VACANT, NodeType.OBSTACLE,
                                               NodeType.START, NodeType.END])

    character_to_nodetype = {
        ".": NodeType.VACANT,
        "#": NodeType.OBSTACLE,
        "s": NodeType.START,
        "e": NodeType.END,
    }

    nodetype_to_character = dict((nodetype, character)
                                 for character, nodetype in character_to_nodetype.items())

    passable_types = [NodeType.VACANT, NodeType.START, NodeType.END]
    passable_values = [type.value for type in passable_types]

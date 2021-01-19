from renderer import *



def small_world_test():
    world_str = """
            #
        # #.#
         #s#
        #e# #
         #
    """

    world = World(10, 10, world_str)

    print(world_str)
    print(world.array)
    print()
    print(world.array.shape)

    node = world.get_node_by_pos(4, 2.9)
    print(node)

    neighbours = world.get_neighbours(node)
    print("neighbours:")
    for neighbour in neighbours:
        print(f"\t{neighbour}")



def test_render():
    # world_str = "".join([((c * 30) + "\n") * 30 for c in "# s.e"])

    # world_str = \
    #     "#    #\n" +\
    #     "## #.#\n" +\
    #     "#.#s #\n" +\
    #     "##e# #\n" +\
    #     "#"

    world_str = """
           #    #
           ## #.#
           #.#s #
           ##e# #
           #
        """

    world = World(10, 10, world_str)
    print(world.array)

    drone_navigation = DroneNavigation(world.n_rows, world.n_columns,
                                       world.start_node, world.end_node)

    current_node = world.start_node

    print("Solving...")
    i = 1
    while current_node.coordinates != world.end_node.coordinates:
        print(f"Iteration {i}: ", end="")
        print(current_node, end=" -> ")

        visible_nodes = world.get_neighbours(current_node)
        print([node.coordinates for node in visible_nodes], end=" -> ")

        next_node = drone_navigation.get_next_node(current_node, visible_nodes)

        render_and_save(world, drone_navigation, f"test_output_{i}.png", upscale=50, show=True)
        current_node = world.index_to_node(next_node[0], next_node[1])
        print(current_node)

        input("<Press ENTER to continue!>")
        i += 1

    drone_navigation.get_next_node(current_node, [])
    render_and_save(world, drone_navigation, f"test_output_{i}.png", upscale=50, show=True)

    print("done")



def main():
    # small_world_test()
    test_render()



if __name__ == '__main__':
    main()

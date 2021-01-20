from renderer import *



def small_world_test():
    world_str = """
            #
        # #.#
         #s#
        #e# #
         #
    """

    world = World(world_str, 10, 10)

    print(world_str)
    print(world.grid)
    print()
    print(world.grid.shape)

    node = world.get_node_by_pos(4, 2.9)
    print(node)

    neighbours = world.get_in_bounds_neighbouring_nodes(node)
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

    # world_str = """
    #        #    #
    #        ## #.#
    #        #.#s #
    #        ##e# #
    #        #
    #     """

    # world_str = """
    #            ######
    #            #s...#
    #            #....#
    #            #...e#
    #            ######
    #         """

    # world_str = """
    #            ######
    #            #s...#
    #            #.##.#
    #            #.##e#
    #            ######
    #         """

    demo_run(world_str)



def test_visibility_visiting():
    world_str = """
               e
               #######.#
               #.......#.#
               #.#.#.#.
               #.....s.#
               #########
            """

    demo_run(world_str)



def demo_run(world_str: str, room_width: float = 10, room_depth: float = 10):
    world = World(world_str, room_width, room_depth)
    print(world.grid)

    drone_navigation = DroneNavigation(world.n_rows, world.n_columns,
                                       world.start_node, world.end_node)

    current_node = world.start_node

    print("Solving...")
    i = 1
    while current_node.coordinates != world.end_node.coordinates:
        print(f"Iteration {i}: ", end="")
        print(current_node, end=" -> ")

        visible_nodes = world.get_visible_nodes(current_node)
        print([node.coordinates for node in visible_nodes], end=" -> ")

        next_node = drone_navigation.get_next_grid_xy(current_node, visible_nodes)

        render_and_save(world, drone_navigation, f"test_output_{i}.png", upscale=50, show=True)
        current_node = world.grid_loc_to_node(next_node[0], next_node[1])
        print(current_node)

        input("<Press ENTER to continue!>")
        i += 1

    drone_navigation.get_next_grid_xy(current_node, [])
    render_and_save(world, drone_navigation, f"test_output_{i}.png", upscale=50, show=True)

    print("done")



def main():
    # small_world_test()
    # test_render()
    test_visibility_visiting()



if __name__ == '__main__':
    main()

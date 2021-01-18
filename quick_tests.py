from world import *



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

    node = world.get_node(4, 2.9)
    print(node)

    neighbours = world.get_neighbours(node)
    print("neighbours:")
    for neighbour in neighbours:
        print(f"\t{neighbour}")



def main():
    small_world_test()



if __name__ == '__main__':
    main()

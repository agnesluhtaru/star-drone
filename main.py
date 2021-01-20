import signal
import sys
import time

from drone_control import drone_init, move_to_location
from drone_navigation import DroneNavigation
from localization_module.localization import Localization
from renderer import render_and_save
from world import World


def run(world_str: str):
    world = World(61.5, 61.5, world_str)
    print(world.grid)

    drone_navigation = DroneNavigation(world.n_rows, world.n_columns,
                                       world.start_node, world.end_node)

    # take
    x, y = localization.get_xy()
    print(x, y)
    current_node = world.get_node_by_pos(x, y)
    # current_node = world.get_node_by_pos(pos.x, pos.y)

    print("Solving...")
    starting_time = time.time()
    i = 1

    running = False
    last_coordinates = current_node.coordinates
    while current_node.coordinates != world.end_node.coordinates:
        if running and last_coordinates == current_node.coordinates:
            move_to_location(drone, localization, next_pos[0], next_pos[1])
            continue
        running = True
        last_coordinates = current_node.coordinates

        print(f"Iteration {i}: ", end="")

        x, y = localization.get_xy()
        current_node = world.get_node_by_pos(x, y)
        print(current_node, end=" -> ")

        visible_nodes = world.get_visible_nodes(current_node)
        print([node.coordinates for node in visible_nodes], end=" -> ")

        next_grid_xy = drone_navigation.get_next_grid_xy(current_node, visible_nodes)

        x, y = next_grid_xy
        next_node = world.grid_loc_to_node(x, y)
        next_pos = next_node.center_loc

        # wait
        print(f"n={next_node}")

        render_and_save(world, drone_navigation, f"test_output_{i}.png", upscale=50, show=False)

        x, y = localization.get_xy()
        current_node = world.get_node_by_pos(x, y)


        # current_node = world.grid_loc_to_node(next_grid_xy[0], next_grid_xy[1])
        print(current_node)

        # input("<Press ENTER to continue!>")
        i += 1
        time.sleep(0.1)

        # if current_node.coordinates == next_node.coordinates:
        #    break

    drone_navigation.get_next_grid_xy(current_node, [])
    render_and_save(world, drone_navigation, f"test_output_{i}.png", upscale=50, show=False)

    print("done")


def signal_handler(sig):
    """
    This function will be called when CTRL+C is pressed, read_sensors specific
    """
    drone.land()
    localization.running = False
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    world_str = """
               ######
               #s...#
               #....#
               #...e#
               #....#
               ######
            """
    drone = drone_init()
    localization = Localization()
    while localization.get_xy() is None:
        continue
    try:
        run(world_str)
    except:
        drone.land()
    drone.land()

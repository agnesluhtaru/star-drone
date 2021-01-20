from PIL import Image, ImageDraw

from drone_navigation import DroneNavigation
from world import World, NodeType

import os


OUTPUT_DIRECTORY = os.path.join(".", "output")

COLOR_SEEN = (255, 255, 0, 50)
COLOR_UNSEEN = (0, 0, 0, 50)
COLOR_VISITED = (255, 255, 0, 150)
COLOR_CURRENT_NODE = (255, 0, 255, 255)
COLOR_CURRENT_PATH = (255, 150, 0, 255)
COLOR_GRID_OVERLAY = (0, 255, 255, 255)

ALPHA_WORLD = 0.5
ALPHA_NAVIGATION = 0.75
ALPHA_GRID = 0.9

WIDTH_GRID = 1

NODETYPE_TO_COLORS = {
    NodeType.VACANT: (255, 255, 255, 0),
    NodeType.OBSTACLE: (0, 0, 0, 255),
    NodeType.START: (0, 0, 255, 255),
    NodeType.END: (255, 0, 0, 255),
}

NODETYPE_VALUE_TO_COLORS = dict([(nodetype.value, color)
                                 for nodetype, color in NODETYPE_TO_COLORS.items()])



def render_and_save(world: World, drone_navigation: DroneNavigation,
                    filename: str, upscale: int = 1, show: bool = False):
    image = render(world, drone_navigation, upscale)

    image.save(os.path.join(OUTPUT_DIRECTORY, filename))

    if show:
        image.show()



def render(world: World, drone_navigation: DroneNavigation, upscale: int = 1) -> Image:
    n_rows, n_columns = (world.n_rows, world.n_columns)

    dimensions = (upscale * n_columns, upscale * n_rows)

    background = Image.new("RGBA", dimensions, (255, 255, 255))

    world_layer = render_world_image(world, dimensions, upscale, ALPHA_WORLD)
    navigation_layer = render_drone_navigation_to_drawing(drone_navigation, dimensions, upscale, ALPHA_NAVIGATION)
    grid_overlay = render_grid_overlay(world, dimensions, upscale, ALPHA_GRID)

    return Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(
            background, world_layer), navigation_layer), grid_overlay)

    # return Image.alpha_composite(Image.alpha_composite(background, world_layer), grid_overlay)
    # return Image.alpha_composite(background, world_layer)
    # return Image.alpha_composite(background, navigation_layer)



def render_grid_overlay(world: World, dimensions: (int, int),
                        upscale: int, alpha_scale: float = 1) -> Image:
    n_rows, n_columns = (world.n_rows, world.n_columns)

    image = Image.new("RGBA", dimensions)
    drawing = ImageDraw.Draw(image)
    color = scale_color_alpha(COLOR_GRID_OVERLAY, alpha_scale)

    for y in range(n_rows):
        y2 = upscale * y
        y2_end = upscale * (y + 1)

        for x in range(n_columns):
            x2 = upscale * x
            x2_end = upscale * (x + 1)

            drawing.rectangle([x2, y2, x2_end, y2 + WIDTH_GRID], fill=color)
            drawing.rectangle([x2, y2, x2 + WIDTH_GRID, y2_end], fill=color)

    x2_end = upscale * n_columns - 1
    y2_end = upscale * n_rows - 1
    drawing.rectangle([x2_end - WIDTH_GRID, 0, x2_end, y2_end], fill=color)
    drawing.rectangle([0, y2_end - WIDTH_GRID, x2_end, y2_end], fill=color)

    return image



def render_world_image(world: World, dimensions: (int, int),
                       upscale: int, alpha_scale: float = 1) -> Image:
    n_rows, n_columns = (world.n_rows, world.n_columns)

    image = Image.new("RGBA", dimensions)
    drawing = ImageDraw.Draw(image)

    for y in range(n_rows):
        y2 = upscale * y
        y2_end = upscale * (y + 1)

        for x in range(n_columns):
            x2 = upscale * x
            x2_end = upscale * (x + 1)

            nodetype_value = world.grid[y, x]
            color = scale_color_alpha(NODETYPE_VALUE_TO_COLORS[nodetype_value], alpha_scale)

            drawing.rectangle([x2, y2, x2_end, y2_end], fill=color)

    return image



def render_drone_navigation_to_drawing(drone_navigation: DroneNavigation, dimensions: (int, int),
                                       upscale: int, alpha_scale: float = 1):
    n_rows, n_columns = (drone_navigation.world_rows, drone_navigation.world_columns)

    image = Image.new("RGBA", dimensions)
    drawing = ImageDraw.Draw(image)

    for y in range(n_rows):
        y2 = upscale * y
        y2_end = upscale * (y + 1) - 1

        for x in range(n_columns):
            x2 = upscale * x
            x2_end = upscale * (x + 1) - 1

            nodetype_value = drone_navigation.world_grid[y, x]

            if nodetype_value == -1:
                continue

            color = NODETYPE_VALUE_TO_COLORS[nodetype_value]
            if nodetype_value == NodeType.VACANT.value:
                color = COLOR_SEEN

                if drone_navigation.is_visited(x, y):
                    color = COLOR_VISITED

            color = scale_color_alpha(color, alpha_scale)

            drawing.rectangle([x2, y2, x2_end, y2_end], fill=color)

    for x, y in [drone_navigation.next_node] + drone_navigation.path:
        drawing.rectangle(shrink_rectangle(x, y, upscale), fill=COLOR_CURRENT_PATH)

    x, y = drone_navigation.current_node.coordinates
    drawing.rectangle(shrink_rectangle(x, y, upscale), fill=COLOR_CURRENT_NODE)

    return image



def shrink_rectangle(x: int, y: int, upscale: int) -> [int, int, int, int]:
    x2 = upscale * x
    x2_end = upscale * (x + 1) - 1
    y2 = upscale * y
    y2_end = upscale * (y + 1) - 1

    if x2 < x2_end - 1 and y2 < y2_end - 1:
        shrink = upscale // 4
        x2 += shrink
        y2 += shrink
        x2_end -= shrink
        y2_end -= shrink

    return [x2, y2, x2_end, y2_end]



def scale_color_alpha(color: (int, int, int, int), alpha_scale: float) -> (int, int, int, int):
    color = list(color)
    return tuple(color[:3] + [int(alpha_scale * color[-1])])

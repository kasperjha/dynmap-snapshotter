import pathlib
import random
import argparse
import datetime
from PIL import Image, ImageColor
try:
    import discord
    is_discord_available = True
except ImportError:
    is_discord_available = False


def get_tile_paths(tiles_dir, worldname, mapname):
    # get filepaths of tile images
    print('getting tiles ...')
    map_dir = pathlib.Path(tiles_dir).joinpath(worldname, mapname)
    assert map_dir.exists()
    map_subdirs = [path for path in map_dir.iterdir() if path.is_dir()]

    tile_paths = []
    for subdir in map_subdirs:
        [tile_paths.append(path) for path in subdir.iterdir() if not path.name.startswith('z')]

    return tile_paths


class Tile:
    # tile object to store path coords and pixel coords
    def __init__(self, path):
        self.path = path
        self.coords = [int(x) for x in path.stem.split('_')]
        self.pixel_coords = None


def create_tile_objects(tile_paths):
    # create a object with variables: path, coords, pixel_coords
    return [Tile(path) for path in tile_paths]


def get_default_tile_size(tiles):
    # compare the sizes of two random tiles
    # if they are not the same or the size if snot somthing is seriously wrong
    print('getting tile size ...')
    tile_size_one, tile_size_two = [Image.open(tile.path).size for tile in random.sample(tiles, 2)]
    assert tile_size_one == tile_size_two and tile_size_one[0] == tile_size_one[1]
    return tile_size_one[0]


def calculate_new_tile_size(tile_size, scale, fixed_tile_size):
    # calculate new tile size
    if scale:
        assert isinstance(scale, float)
        return int(tile_size*scale)
    elif fixed_tile_size:
        assert isinstance(fixed_tile_size, int)
        return fixed_tile_size
    else:
        return tile_size


def calculate_image_positions(tiles, tile_size):
    # add properties with image positions for each tile object
    # image_size = ((x_range[1] - x_range[0] + 1), (y_range[1] - y_range[0] + 1))
    print('calculating image positions for tiles ...')
    all_x_coords = [tile.coords[0] for tile in tiles]
    all_y_coords = [tile.coords[1] for tile in tiles]
    x_range = (min(all_x_coords), max(all_x_coords))
    y_range = (min(all_y_coords), max(all_y_coords))

    for tile in tiles:
        pixel_x = (tile.coords[0] - x_range[0]) * tile_size
        pixel_y = -(tile.coords[1] - y_range[0] - (y_range[1] - y_range[0] + 1) + 1) * tile_size
        tile.pixel_coords = (pixel_x, pixel_y)

    return tiles


def calculate_image_size(tiles, tile_size):
    # use the properties of tiles objects to assemble output image
    print('calculating size of output image ...')
    all_x_coords = [tile.coords[0] for tile in tiles]
    all_y_coords = [tile.coords[1] for tile in tiles]
    x_range = (min(all_x_coords), max(all_x_coords))
    y_range = (min(all_y_coords), max(all_y_coords))
    image_size = ((x_range[1] - x_range[0] + 1)*tile_size, (y_range[1] - y_range[0] + 1)*tile_size)

    return image_size


def assemble_image(tiles, image_size, tile_size):
    # create empty image and load, resize and paste tile images onto it
    print('pasting tiles ...')
    output = Image.new('RGBA', image_size)

    for tile in tiles:
        # load image and resize
        tile_image = Image.open(tile.path)
        tile_image = tile_image.resize((tile_size, tile_size), Image.BICUBIC)
        output.paste(tile_image, (tile.pixel_coords))

    return output


def apply_background_color(snapshot, image_size, color_hex):
    print('applying background ...')
    rgb_color = ImageColor.getcolor(color_hex, 'RGB')
    background = Image.new('RGBA', image_size, rgb_color)
    snapshot_with_bg = Image.alpha_composite(background, snapshot)

    return snapshot_with_bg


def create_snapshot(tiles_dir, worldname, mapname, scale, fixed_tile_size, color_hex):
    # create a snapshot of dynmap
    # make sure we have required arguments
    assert (tiles_dir and worldname and mapname)

    # get tiles
    tile_paths = get_tile_paths(tiles_dir, worldname, mapname)
    tiles = create_tile_objects(tile_paths)

    # get sizes apply scale or fixed tile size
    default_tile_size = get_default_tile_size(tiles)
    new_tile_size = calculate_new_tile_size(default_tile_size, scale, fixed_tile_size)

    # calculate tile postitions and total size for output image
    tiles = calculate_image_positions(tiles, new_tile_size)
    image_size = calculate_image_size(tiles, new_tile_size)

    # assemble snapshot and apply background color
    snapshot = assemble_image(tiles, image_size, new_tile_size)
    if color_hex:
        snapshot = apply_background_color(snapshot, image_size, color_hex)

    return snapshot


def save_snapshot(snapshot, worldname, mapname):
    # get script dir and build save_dir path
    script_dir = pathlib.Path(__file__).resolve().parent
    save_dir = script_dir.joinpath('snapshots')

    # create folder if non existant
    if not save_dir.exists():
        print('creating folder ...')
        save_dir.mkdir()

    # create timestamped filename
    print('saving snapshot ...')
    now = datetime.datetime.now()
    timestamp = now.strftime("%d-%m-%Y--%H-%M")
    filename = f'{timestamp}--{worldname}-{mapname}.png'
    output_path = save_dir.joinpath(filename)
    snapshot.save(output_path, 'PNG')

    return output_path


def post_to_discord_webhook(snapshot_path, url, message):
    # post snapshot to discord channel via a webhook
    # get webhook object
    webhook_id, webhook_token = url.split("/")[-2:]
    webhook = discord.Webhook.partial(webhook_id, webhook_token, adapter=discord.RequestsWebhookAdapter())

    # take snapshot
    with open(file=snapshot_path, mode='rb') as f:
        print('posting to discord ...')
        webhook.send(message, username='dynmap-snapshots', file=discord.File(f))


def get_world_names(tiles_dir):
    # returns a list of dynmap world names
    excluded_names = ['_markers_', 'faces', '.vscode', '.git']
    world_names = [name.stem for name in pathlib.Path(tiles_dir).iterdir() if name.stem not in excluded_names]
    return world_names


def get_map_names(tiles_dir, worldname):
    # returns a list of dynmap map names of inut world
    world_dir = pathlib.Path.joinpath(tiles_dir, worldname)
    map_names = [name.stem for name in world_dir.iterdir() if name.exists() and name.is_dir()]
    return map_names


def user_choice(prompt, options, default=None):
    # let user select from a list of objects
    is_options_tuple = isinstance(options[0], tuple)
    is_default_tuple = isinstance(options[0], tuple)

    # promt the user
    if default is not None:
        default_string = default if not is_default_tuple else default[0]
        prompt += f' Default is {default_string}'
    print(prompt)

    # display menu and get user input
    for option in options:
        index = options.index(option)
        display_string = option if not is_options_tuple else option[0]
        print(f'    {index}: {display_string}')
    input_string = input(' > ')

    # parse input
    if input_string.isnumeric():
        option = options[int(input_string)]
        return option if not is_options_tuple else option[1]
    elif not input_string and default is not None:
        return default if not is_default_tuple else default[1]
    else:
        print('Invalid input')
        exit()


def user_input(prompt, input_type, default=None):
    # let user define a value with a nice interface
    # print promt and get input
    if default is not None:
        prompt += f' Press enter for default: {default}'
    print(prompt)
    input_string = input(' > ').strip()

    # set to defaul
    if not input_string and default is not None:
        return default

    try:
        # try to convert to input type
        return input_type(input_string)
    except ValueError:
        print('Invalid input')
        exit()


def interactive():
    # help pick variables and flags
    # let user specify the tiles directory
    path = user_input('\nSpecify the path to the dynmap tiles directory.', str, default='plugins/dynmap/web/tiles')
    tiles_dir = pathlib.Path(r"{}".format(path))  # convert to raw string literal
    if not tiles_dir.exists():
        print('Directory does not exist. Aborting ...')
        exit()

    # let user specify the world
    world_names = get_world_names(tiles_dir)
    world_name = user_choice('\nSpecify world name.', world_names, default=world_names[0])

    # let user specify the map name
    map_names = get_map_names(tiles_dir, world_name)
    map_name = user_choice("\nSpecify map name.", map_names, default=map_names[-1])

    # get tiles and default tile size
    print()
    tile_paths = get_tile_paths(tiles_dir, world_name, map_name)
    tiles = create_tile_objects(tile_paths)
    default_tile_size = get_default_tile_size(tiles)
    image_size = calculate_image_size(tiles, default_tile_size)

    # print resizing info
    print(f'\nCurrent tile size is {default_tile_size}.')
    print(f'Your output will be {image_size}.')
    print('Large images should be resized to reduce filesize.')

    # let user either scale or set a fixed tile size
    scale = None
    fixed_tile_size = None
    if user_choice('\nResize the output?', [('yes', True), ('no', False)], default=('no', False)):
        print('\nYou can resize the output by either scaling the output or by setting a new tile size.')
        if user_choice('How do you want to resize?', [('scale', True), ('tile size', False)]):
            scale = user_input('\nProvide a decimal number to scale with (eg. 0.5):', float)
        else:
            fixed_tile_size = user_input('\nSet a new tile size (eg. 64):', int)

    # calculate new tile_size, tile postitions and total size for output image
    print()
    new_tile_size = calculate_new_tile_size(default_tile_size, scale, fixed_tile_size)
    tiles = calculate_image_positions(tiles, new_tile_size)
    image_size = calculate_image_size(tiles, new_tile_size)

    # let user choose background color
    color_hex = None
    if user_choice('\nDo you want to apply a background color?', [('yes', True), ('no', False)], default=('no', False)):
        color_hex = user_input('\nProvide a hexadecimal color value (eg. #ff0000):', str)

    # assemble snapshot and apply background color
    print()
    snapshot = assemble_image(tiles, image_size, new_tile_size)
    if color_hex:
        snapshot = apply_background_color(snapshot, image_size, color_hex)

    # save snapshot
    snapshot_path = save_snapshot(snapshot, world_name, map_name)
    print('\nSnapshot saved to:')
    print(snapshot_path)


if __name__ == '__main__':
    # parse commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', action="store", type=str,
                        help="specify the absolute path for folder where dynmap tiles are stored. \
                        this is usually [server folder]/plugins/dynmap/web/tiles.")
    parser.add_argument('--world', action="store", type=str, help='world to take snapshot of')
    parser.add_argument('--map', action="store", type=str, help='map to take snapshot of')
    parser.add_argument('--interactive', action="store_true", help="helps user decide arguments trough prompts")
    parser.add_argument('--scale', action="store", default=None, type=float, help="resize the snapshot with a decimal point number")
    parser.add_argument('--fixed-tile-size', action="store", default=None, type=int, help="resize the snapshot with setting a new tile size")
    parser.add_argument('--color-hex', action="store", default=None, type=str, help="hex value of color to apply to background.")
    parser.add_argument('--discord-message', action='store', default=None, type=str, help="message to go along with discord post snapshot")
    parser.add_argument('--discord-webhook-url', action='store', default=None, type=str, help="discord webhook url to post snapshot to.")
    args = parser.parse_args()

    if args.interactive:
        interactive()
    else:
        # parser error if missing required args
        if not (args.folder and args.world and args.map):
            parser.error('--folder, --world and --map are required arguments when not using --interactive')

        # parser error if discord is not installed
        if args.discord_webhook_url and not is_discord_available:
            parser.error('"discord" python package is required to post to discord webhook. please do "pip install discord".')
            exit()

        # capture and save snapshot
        snapshot = create_snapshot(args.folder, args.world, args.map, args.scale, args.fixed_tile_size, args.color_hex)
        snapshot_path = save_snapshot(snapshot, args.world, args.map)
        print('snapshot created')

        # send to discord
        if args.discord_webhook_url:
            post_to_discord_webhook(snapshot_path, args.discord_webhook_url, args.discord_message)

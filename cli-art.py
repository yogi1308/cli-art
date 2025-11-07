import argparse
import shutil
from cli_art_image import to_ascii
from  cli_art_video import vid_to_ascii_legacy

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="converts an image to ascii. Recommended that you zoom out as much as you can before executing the script",
        epilog="""
            Examples: \n
            # Basic use with a local file: 
            %(prog)s my_image.jpg \n
            
            # From a URL (remember to use quotes!): 
            %(prog)s "https://i.pinimg.com/736x/f6/97/a8/f697a839e42edcb9a473809878b54420.jpg" \n
            
            # Full color, 100 pixels wide: 
            %(prog)s my_image.jpg --width 100 --img-color colored \n
            
            # Green text, inverted, and using 'average' brightness: 
            %(prog)s my_image.jpg --img-color green --invert --conversion-type average \n
            """
    )

    parser.add_argument(
        "filepath",
        help="The path to the input image file (e.g., image.png) or a URL."
    )

    parser.add_argument(
        '--img-color',
        default='colored',
        help="Set the output color. Options: 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', or an RGB string like \"255,100,20\" or \"b&w\" or colored"
    )

    parser.add_argument(
        '--invert',
        action='store_true',
        help="Invert the brightness (light <-> dark). Good for light terminal backgrounds."
    )

    parser.add_argument(
        '--width',
        type=int,
        help="Set a specific width in characters (e.g., 100). This will override the --fit setting."
    )

    parser.add_argument(
        '--fit',
        choices=['height', 'width'],
        default='height',
        help="Auto-fit to terminal 'height' or 'width'. (default: height)"
    )

    parser.add_argument(
        '--conversion-type',
        choices=['average', 'min-max', 'luminosity'],
        default='luminosity',
        help="How to calculate brightness: 'luminosity' (best), 'average', or 'min-max'. Determines how rgb values of each pixel are converted to ascii"
    )

    parser.add_argument(
        '--contrast',
        type=float,
        default=1.0,
        help="Enhance image contrast. >1.0 for more, <1.0 for less. (default: 1.0)"
    )

    parser.add_argument(
        '--brightness',
        type=float,
        default=1.0,
        help="Enhance image brightness. >1.0 for more, <1.0 for less. (default: 1.0)"
    )

    parser.add_argument(
        '--legacy',
        action='store_true',
        default=False,
        help="Uses the old legacy way of converting videos to ascii animations. Best suited for small widths and best viewed zoomed out after entering the command"
    )
    
    image_fit_input = ""
    user_inputs = parser.parse_args()
    user_input_image_width = 0
    terminal_size = int(shutil.get_terminal_size().columns/3)
    if user_inputs.width is not None:
        image_fit_input = "ignore"
        if 10 < user_inputs.width < terminal_size:
            user_input_image_width = user_inputs.width
        else:
            raise ValueError(f"Error: Width must be between 10 and {terminal_size}.")
    else:
        user_input_image_width = terminal_size

    if image_fit_input != "ignore":
        image_fit_input = user_inputs.fit
    
    input_image_color = []
    if "," in user_inputs.img_color.strip():
        input_image_color = user_inputs.img_color.strip().split(",")
        try:
            for i in range(0, len(input_image_color)):
                input_image_color[i] = int(input_image_color[i])
        except ValueError:
            raise ValueError(f"Error: RGB values should be integers between 0 and 255")
        for value in input_image_color:
            if value < 0 or value > 255:
                raise ValueError(f"Error: RGB values should be integers between 0 and 255")
        if len(input_image_color) != 3:
            raise ValueError(f"Error: your argument for rgb values doesn't contain 3 values")
    else:
        input_image_color = user_inputs.img_color
    
    if user_inputs.filepath.endswith(".mp4"):
        if user_inputs.legacy:
            vid_to_ascii_legacy(filepath=user_inputs.filepath, image_color=input_image_color, invert=user_inputs.invert, image_fit=image_fit_input, image_width=user_input_image_width, pixel_conversion_type=user_inputs.conversion_type, contrast=user_inputs.contrast, brightness=user_inputs.brightness) 
        else: 
            print(user_inputs.legacy)
    else: 
        to_ascii(filepath=user_inputs.filepath, image_color=input_image_color, invert=user_inputs.invert, image_fit=image_fit_input, image_width=user_input_image_width, pixel_conversion_type=user_inputs.conversion_type, contrast=user_inputs.contrast, brightness=user_inputs.brightness)
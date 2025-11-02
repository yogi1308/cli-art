# add max-height flag
from PIL import Image
from colorama import Fore
import sys
import argparse
import shutil
import requests  # For downloading the URL
from io import BytesIO # To let Pillow read the downloaded data from memory

def convert_brightness_to_ascii(value, invert):
    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    ascii_chars_reversed = ascii_chars[::-1]
    value = int((value/255)*100)
    if invert:
        return ascii_chars_reversed[int((value/100)*(len(ascii_chars)-1))]
    return ascii_chars[int((value/100)*(len(ascii_chars)-1))]

def get_resized_img(img, image_fit, image_width):
    image = img
    # print(image.size)
    if image_fit != "ignore":
        if image_fit == "height":
            new_image_height = int(shutil.get_terminal_size().lines/2)
            return img.resize((int(new_image_height / (img.height / img.width)), new_image_height))
        elif image_fit == "width":
            new_image_width = image_width
            return img.resize((new_image_width, int(new_image_width * (img.height / img.width))))
    else:
        new_image_width = image_width
        return img.resize((new_image_width, int(new_image_width * (img.height / img.width))))
    
def get_pixel_details(image):
    pixel_details = []
    for y in range(0, image.height): # gets pixel's rgb data
        row = []
        for x in range(0, image.width):
            image.getpixel((x, y))
            row.append(image.getpixel((x, y)))
        pixel_details.append(row)
    return pixel_details

def get_pixel_brightness_values(pixel_details, pixel_conversion_type):
    pixel_brightness_values = []
    for y in range(0, len(pixel_details)): # converts each pixel's rgb data to brightness
        row = []
        for x in range(0, len(pixel_details[y])):
            if pixel_conversion_type.lower() == "average":
                rgb_values = 0
                for value in pixel_details[y][x]:
                    rgb_values += value
                row.append(int(0.21*pixel_details[y][x][0] + 0.72*pixel_details[y][x][1] + 0.07*pixel_details[y][x][2])) # luminosity
            elif pixel_conversion_type.lower() == "min-max":
                row.append(int((max(pixel_details[y][x]) + (min(pixel_details[y][x])))/2)) # min-max
            elif pixel_conversion_type.lower() == "luminosity":
                row.append(int(0.21*pixel_details[y][x][0] + 0.72*pixel_details[y][x][1] + 0.07*pixel_details[y][x][2])) # luminosity
        pixel_brightness_values.append(row)
    return pixel_brightness_values

def get_pixel_ascii_char(pixel_brightness_values, invert):
    pixel_ascii_char = []
    for value in range(0, len(pixel_brightness_values)): # gets each pixel's ascii character based on the brightness data
        row = []
        for row_value in range(0, len(pixel_brightness_values[value])):
            row.append(convert_brightness_to_ascii(pixel_brightness_values[value][row_value], invert))
        pixel_ascii_char.append(row)
    # print(pixel_ascii_char[0])
    return pixel_ascii_char

    pixel_rgb_values = []
    for y in range(0, len(pixel_details)):
        row = []
        for x in range(0, len(pixel_details[y])):
            rgb_values = []
            for value in pixel_details[y][x]:
                rgb_values.append(value)
            row.append(rgb_values)
        pixel_rgb_values.append(row)
    # print(pixel_brightness_values[0], len(pixel_brightness_values))
    return pixel_rgb_values

def print_image(pixel_ascii_char, pixel_details, image_color):
    if isinstance(image_color, (list)):
        if 0 <= image_color[0] <= 255 and 0 <= image_color[1] <= 255 and 0 <= image_color[2] <= 255:
            for value in range(0, len(pixel_ascii_char)):
                for row_value in range(0, len(pixel_ascii_char[value])):
                    print(f"\033[38;2;{image_color[0]};{image_color[1]};{image_color[2]}m" + pixel_ascii_char[value][row_value] * 3, end = "")
                print()
                print()
        else:
            raise ValueError 
    elif image_color.lower().strip() == 'black' or image_color.lower().strip() == 'red' or image_color.lower().strip() == 'green' or image_color.lower().strip() == 'yellow' or image_color.lower().strip() == 'blue' or image_color.lower().strip() == 'magenta' or image_color.lower().strip() == 'cyan' or image_color.lower().strip() == 'white':
        image_color = image_color.upper().strip()
        for value in range(0, len(pixel_ascii_char)):
            for row_value in range(0, len(pixel_ascii_char[value])):
                print(getattr(Fore, image_color) + pixel_ascii_char[value][row_value] * 3, end = "")
            print()
            print()
    elif image_color.lower().strip() == "b&w":
        print(f"b&w")
        for value in range(0, len(pixel_ascii_char)):
            for row_value in range(0, len(pixel_ascii_char[value])):
                print(f"{pixel_ascii_char[value][row_value] * 3}", end="")
            print()
            print()
    else:
        for value in range(0, len(pixel_ascii_char)):
            for row_value in range(0, len(pixel_ascii_char[value])):
                print(f"\033[38;2;{pixel_details[value][row_value][0]};{pixel_details[value][row_value][1]};{pixel_details[value][row_value][2]}m" + pixel_ascii_char[value][row_value] * 3, end = "") # prints blue color with rgb(11, 219,247)
            print()
            print()

def to_ascii(filepath, image_color, invert, image_fit, image_width, pixel_conversion_type):
    image_source = None
    if filepath.startswith('http://') or filepath.startswith('https://'):
        try:
            # Download the image data
            response = requests.get(filepath)
            response.raise_for_status()  # Check for bad responses (404, 500)
            
            # Use BytesIO to treat the downloaded data (in memory) like a file
            image_source = BytesIO(response.content)
            
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to download image from URL. {e}", file=sys.stderr)
            sys.exit(1) # Exit if download fails
    
    else:
        image_source = filepath
    try:
        with Image.open(image_source) as image_file:
            # print("Successfully loaded image")
            # print(image_file.width, image_file.height, "og image size")
            image = get_resized_img(image_file, image_fit, image_width)

            pixel_details = get_pixel_details(image)

            pixel_brightness_values = get_pixel_brightness_values(pixel_details, pixel_conversion_type)
            # print(pixel_brightness_values[0], len(pixel_brightness_values))

            pixel_ascii_char = get_pixel_ascii_char(pixel_brightness_values, invert)

            print_image(pixel_ascii_char, pixel_details, image_color)
    except FileNotFoundError:
        print("Error: The specified file was not found. Please check the file path and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening or processing image: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="converts an image to ascii. Recommended that you zoom out as much as you can before executing the script"
    )

    parser.add_argument(
        "filepath",
        help="The path to the input image file (e.g., image.png) or a URL."
    )

    parser.add_argument(
        '--img-color',
        default='colored',
        help="image color options include color names (black, red, green, yellow, blue, magenta, cyan, white), rgb values(\"r, g, b\"), black and white(\"b&w\"), or colored(colored) which is the default value"
    )

    parser.add_argument(
        '--invert',
        action='store_true',
        help="Check this flag to invert the image."
    )

    parser.add_argument(
        '--width',
        type=int,
        help="an integer value greater than 10 and less than your terminal windows's max width. Default value is calculated using terminals height and image's aspect ratio. if you input a value which is less than 10 or greater than your terminal's width than it will use the defalut value. Height will be calculated using the width to preserve the original image's aspect ratio"
    )

    parser.add_argument(
        '--fit',
        choices=['height', 'width'],
        default='height',
        help="Fits to the terminal's height or width. default(height). will be ignored if provided with width"
    )

    parser.add_argument(
        '--conversion-type',
        choices=['average', 'min-max', 'luminosity'],
        default='luminosity',
        help="determines how the ascii value is calculated(average, min-max, luminosity(default)). Average calculates the ascii value by taking the average of the rgb values. Min-max takes the average of the minimum and maximum of rgb values. Luminosity takes a weighted average of the R(0.21), G(0.72) and B(0.07) values to account for human perception"
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


    to_ascii(filepath=user_inputs.filepath, image_color=input_image_color, invert=user_inputs.invert, image_fit=image_fit_input, image_width=user_input_image_width, pixel_conversion_type=user_inputs.conversion_type)

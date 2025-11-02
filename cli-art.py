# enable reading terminal height and width to get the ideal width and height for the image
from PIL import Image
from colorama import Fore
import sys
import argparse
import shutil

def convert_brightness_to_ascii(value, invert):
    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    ascii_chars_reversed = ascii_chars[::-1]
    value = int((value/255)*100)
    if invert:
        return ascii_chars_reversed[int((value/100)*(len(ascii_chars)-1))]
    return ascii_chars[int((value/100)*(len(ascii_chars)-1))]

def to_ascii(image_color, invert, image_width, pixel_conversion_type):
    with Image.open("95368ef6621659a09e8f2d1387c7fb8a.jpg") as image_file:
        print("Successfully loaded image")
        print(image_file.width, image_file.height, "og image size")


        image = image_file
        new_image_width = image_width
        image = image_file.resize((new_image_width, int(new_image_width * (image_file.height / image_file.width))))
        print(image.size)


        pixel_details = []
        for y in range(0, image.height): # gets pixel's rgb data
            row = []
            for x in range(0, image.width):
                image.getpixel((x, y))
                row.append(image.getpixel((x, y)))
            pixel_details.append(row)
        # print(pixel_details[0], len(pixel_details))

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
                
        # print(pixel_brightness_values[0], len(pixel_brightness_values))

        pixel_ascii_char = []
        for value in range(0, len(pixel_brightness_values)): # gets each pixel's ascii character based on the brightness data
            row = []
            for row_value in range(0, len(pixel_brightness_values[value])):
                row.append(convert_brightness_to_ascii(pixel_brightness_values[value][row_value], invert))
            pixel_ascii_char.append(row)
        # print(pixel_ascii_char[0])


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

        if image_color.lower == 'black' or image_color.lower == 'red' or image_color.lower == 'green' or image_color.lower == 'yellow' or image_color.lower == 'blue' or image_color.lower == 'magenta' or image_color.lower == 'cyan' or image_color.lower == 'white':
            image_color = image_color.upper()
            for value in range(0, len(pixel_ascii_char)):
                for row_value in range(0, len(pixel_ascii_char[value])):
                    print(Fore.image_color + pixel_ascii_char[value][row_value] * 3, end = "")
                print()
                print()
        elif isinstance(image_color, (list, tuple)):
            if 0 <= image_color[0] <= 255 and 0 <= image_color[1] <= 255 and 0 <= image_color[2] <= 255:
                for value in range(0, len(pixel_ascii_char)):
                    for row_value in range(0, len(pixel_ascii_char[value])):
                        print(Fore.image_color + pixel_ascii_char[value][row_value] * 3, end = "")
                    print()
                    print()
            else:
                raise ValueError 
        elif image_color.lower == "b&w":
            for value in range(0, len(pixel_ascii_char)):
                for row_value in range(0, len(pixel_ascii_char[value])):
                    print_this += f"{pixel_ascii_char[value][row_value] * 3}"
                print()
                print()
        else:
            for value in range(0, len(pixel_ascii_char)):
                for row_value in range(0, len(pixel_ascii_char[value])):
                    print(f"\033[38;2;{pixel_details[value][row_value][0]};{pixel_details[value][row_value][1]};{pixel_details[value][row_value][2]}m" + pixel_ascii_char[value][row_value] * 3, end = "") # prints blue color with rgb(11, 219,247)
                print()
                print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="converts an image to ascii"
    )

    parser.add_argument(
        '--img-color',
        type=str, 
        default='colored',
        help="image color options include color names (black, red, green, yellow, blue, magenta, cyan, white), rgb values in a list or tuple([r, g, b], (r, g, b)), black and white(b&w), or colored(colored) which is the default value"
    )

    parser.add_argument(
        '--invert',
        action='store_true',
        help="Check this flag to invert the image."
    )

    parser.add_argument(
        '--width',
        type=int,
        help="an integer value greater than 10 and less than your terminal windows's max width. Default value is the terminal windows's width. Height will be calculated using the width to preserve the original image's aspect ratio"
    )

    parser.add_argument(
        '--conversion-type',
        choices=['average', 'min-max', 'luminosity'],
        default='luminosity',
        help="determines how the ascii value is calculated(average, min-max, luminosity(default)). Average calculates the ascii value by taking the average of the rgb values. Min-max takes the average of the minimum and maximum of rgb values. Luminosity takes a weighted average of the R(0.21), G(0.72) and B(0.07) values to account for human perception"
    )

    user_inputs = parser.parse_args()
    user_input_image_width = user_inputs.width
    terminal_size = int(shutil.get_terminal_size().columns/3)
    if user_input_image_width is not None:
        if 10 < user_input_image_width < terminal_size:
            user_input_image_width = user_inputs.width
        else:
            user_input_image_width = terminal_size
    else:
        user_input_image_width = terminal_size


    to_ascii(image_color=user_inputs.img_color, invert=user_inputs.invert, image_width=user_input_image_width, pixel_conversion_type=user_inputs.conversion_type)

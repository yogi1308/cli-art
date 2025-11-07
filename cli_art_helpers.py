from colorama import Fore
import shutil
import cv2

VALID_COLORS = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

def convert_brightness_to_ascii(value, invert):
    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    ascii_chars_reversed = ascii_chars[::-1]
    value = int((value/255)*100)
    if invert:
        return ascii_chars_reversed[int((value/100)*(len(ascii_chars)-1))]
    return ascii_chars[int((value/100)*(len(ascii_chars)-1))]

def get_resized_img(img, image_fit, image_width, video):
    if not video:
        if image_fit != "ignore":
            if img.width > int(shutil.get_terminal_size().columns/3):
                new_image_width = image_width
                return img.resize((new_image_width, int(new_image_width * (img.height / img.width))))
            if image_fit == "height":
                new_image_height = int(shutil.get_terminal_size().lines/2)
                return img.resize((int(new_image_height / (img.height / img.width)), new_image_height))
            elif image_fit == "width":
                new_image_width = image_width
                return img.resize((new_image_width, int(new_image_width * (img.height / img.width))))
        else:
            new_image_width = image_width
            return img.resize((new_image_width, int(new_image_width * (img.height / img.width))))
    else:
        original_height, original_width = img.shape[:2]
        if image_fit != "ignore":
            if original_width > int(shutil.get_terminal_size().columns/3):
                new_image_width = image_width
                return cv2.resize(img, (new_image_width, int(new_image_width * (original_height / original_width))))
            if image_fit == "height":
                new_image_height = int(shutil.get_terminal_size().lines/2)
                return cv2.resize(img, (int(new_image_height / (original_height / original_width)), new_image_height))
            elif image_fit == "width":
                new_image_width = image_width
                return cv2.resize(img, (new_image_width, int(new_image_width * (original_height / original_width))))
        else:
            new_image_width = image_width
            return cv2.resize(img, (new_image_width, int(new_image_width * (original_height / original_width))))

    
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
                row.append(int(rgb_values/3)) # average
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

def print_image(pixel_ascii_char, pixel_details, image_color):
    img_str = ""
    if isinstance(image_color, (list)):
        if 0 <= image_color[0] <= 255 and 0 <= image_color[1] <= 255 and 0 <= image_color[2] <= 255:
            for value in range(0, len(pixel_ascii_char)):
                for row_value in range(0, len(pixel_ascii_char[value])):
                    img_str += f"\033[38;2;{image_color[0]};{image_color[1]};{image_color[2]}m" + pixel_ascii_char[value][row_value] * 3
                img_str += "\n\n"
        else:
            raise ValueError 
    elif image_color.lower().strip() in VALID_COLORS:
        image_color = image_color.upper().strip()
        for value in range(0, len(pixel_ascii_char)):
            for row_value in range(0, len(pixel_ascii_char[value])):
                img_str += getattr(Fore, image_color) + pixel_ascii_char[value][row_value] * 3
            img_str += "\n\n"
    elif image_color.lower().strip() == "b&w":
        for value in range(0, len(pixel_ascii_char)):
            for row_value in range(0, len(pixel_ascii_char[value])):
                img_str += f"{pixel_ascii_char[value][row_value] * 3}"
            img_str += "\n\n"
    else:
        for value in range(0, len(pixel_ascii_char)):
            for row_value in range(0, len(pixel_ascii_char[value])):
                img_str += f"\033[38;2;{pixel_details[value][row_value][0]};{pixel_details[value][row_value][1]};{pixel_details[value][row_value][2]}m" + pixel_ascii_char[value][row_value] * 3 # prints blue color with rgb(11, 219,247
            img_str += "\n\n"
    return img_str
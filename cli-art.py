# add option for brightness using lighness max(R, G, B) + min(R, G, B) / 2 and luminosity 0.21 R + 0.72 G + 0.07 B
from PIL import Image
from colorama import Fore

def convert_brightness_to_ascii(value):
    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    value = int((value/255)*100)
    return ascii_chars[int((value/100)*(len(ascii_chars)-1))]

with Image.open("image.png") as image_file:
    print("Successfully loaded image")
    print(image_file.width, image_file.height, "og image size")
    new_image_width = 622
    image = image_file.resize((new_image_width, int(new_image_width * (image_file.height / image_file.width))))
    print(image.size)
    pixel_details = []
    for y in range(0, image.height):
        row = []
        for x in range(0, image.width):
            rgb_values = image.getpixel((x, y))
            rgb_values_list = []
            for value in rgb_values:
                rgb_values_list.append(value)
            row.append(rgb_values_list)
        pixel_details.append(row)
    print(pixel_details[0], len(pixel_details))

    pixel_brightness_values = []
    for y in range(0, len(pixel_details)):
        row = []
        for x in range(0, len(pixel_details[y])):
            rgb_values = 0
            for value in pixel_details[y][x]:
                rgb_values += value
            row.append(int(rgb_values/3))
        pixel_brightness_values.append(row)
    print(pixel_brightness_values[0], len(pixel_brightness_values))

    pixel_ascii_char = []
    for value in range(0, len(pixel_brightness_values)):
        row = []
        for row_value in range(0, len(pixel_brightness_values[value])):
            row.append(convert_brightness_to_ascii(pixel_brightness_values[value][row_value]))
        pixel_ascii_char.append(row)
    print(pixel_ascii_char[0])

    for value in range(0, len(pixel_ascii_char)):
        for row_value in range(0, len(pixel_ascii_char[value])):
            print(pixel_ascii_char[value][row_value] * 3, end = "")
            # print("\033[38;2;11;219;247m" + pixel_ascii_char[value][row_value] * 3, end = "") # prints blue color with rgb(11, 219,247)
            # print(Fore.BLUE + pixel_ascii_char[value][row_value] * 3, end = "")
        print()
        print()
# enable reading terminal height and width to get the ideal width and height for the image
from PIL import Image
from colorama import Fore

def convert_brightness_to_ascii(value):
    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    ascii_chars_reversed = ascii_chars[::-1]
    value = int((value/255)*100)
    return ascii_chars_reversed[int((value/100)*(len(ascii_chars)-1))]

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
            image.getpixel((x, y))
            row.append(image.getpixel((x, y)))
        pixel_details.append(row)
    # print(pixel_details[0], len(pixel_details))

    pixel_brightness_values = []
    for y in range(0, len(pixel_details)):
        row = []
        for x in range(0, len(pixel_details[y])):
            rgb_values = 0
            for value in pixel_details[y][x]:
                rgb_values += value
            # row.append(int(rgb_values/3)) # average
            # row.append(int((max(pixel_details[y][x]) + (min(pixel_details[y][x])))/2)) # min-max
            row.append(int(0.21*pixel_details[y][x][0] + 0.72*pixel_details[y][x][1] + 0.07*pixel_details[y][x][2])) # luminosity
        pixel_brightness_values.append(row)
    # print(pixel_brightness_values[0], len(pixel_brightness_values))

    pixel_ascii_char = []
    for value in range(0, len(pixel_brightness_values)):
        row = []
        for row_value in range(0, len(pixel_brightness_values[value])):
            row.append(convert_brightness_to_ascii(pixel_brightness_values[value][row_value]))
        pixel_ascii_char.append(row)
    # print(pixel_ascii_char[0])

    print_this = ""

    for value in range(0, len(pixel_ascii_char)):
        for row_value in range(0, len(pixel_ascii_char[value])):
            print_this += f"{pixel_ascii_char[value][row_value] * 3}"
            # print("\033[38;2;11;219;247m" + pixel_ascii_char[value][row_value] * 3, end = "") # prints blue color with rgb(11, 219,247)
            # print(Fore.BLUE + pixel_ascii_char[value][row_value] * 3, end = "")
        print_this += "\n\n"
    print(print_this)
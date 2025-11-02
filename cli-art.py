# add option for brightness using lighness max(R, G, B) + min(R, G, B) / 2 and luminosity 0.21 R + 0.72 G + 0.07 B
from PIL import Image

def convert_brightness_to_ascii(value):
    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    value = int((value/255)*100)
    return ascii_chars[int((value/100)*65)]

with Image.open("image.png") as image_file:
    print("Successfully loaded image")
    print(image_file.size)
    pixel_details = []
    for y in range(0, image_file.height):
        for x in range(0, image_file.width):
            rgb_values = image_file.getpixel((x, y))
            rgb_values_list = []
            for value in rgb_values:
                rgb_values_list.append(value)
            pixel_details.append(rgb_values_list)
    print(pixel_details[0], len(pixel_details))

    pixel_brightness_values = []
    for y in range(0, len(pixel_details)):
        rgb_values = 0
        for x in pixel_details[y]:
            rgb_values += x
        pixel_brightness_values.append(rgb_values/3)
    print(pixel_brightness_values[0], len(pixel_brightness_values))

    pixel_ascii_char = []
    for value in pixel_brightness_values:
        pixel_ascii_char.append(convert_brightness_to_ascii(value))
    print(pixel_ascii_char[0], len(pixel_ascii_char))
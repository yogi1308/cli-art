import requests
import sys
from PIL import Image, ImageEnhance
from io import BytesIO
from cli_art_helpers import get_resized_img, get_pixel_details, get_pixel_brightness_values, get_pixel_ascii_char, print_image

def to_ascii(filepath, image_color, invert, image_fit, image_width, pixel_conversion_type, contrast, brightness):
    image_source = None
    if filepath.startswith('http://') or filepath.startswith('https://'):
        try:
            response = requests.get(filepath) # Download the image data
            response.raise_for_status()  # Check for bad responses (404, 500)
            image_source = BytesIO(response.content) # Use BytesIO to treat the downloaded data (in memory) like a file
            
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to download image from URL. {e}", file=sys.stderr)
            sys.exit(1) # Exit if download fails
    
    else:
        image_source = filepath
    try:
        with Image.open(image_source) as image_file:
            image = get_resized_img(image_file, image_fit, image_width)
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast)
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness)

            pixel_details = get_pixel_details(image)

            pixel_brightness_values = get_pixel_brightness_values(pixel_details, pixel_conversion_type)

            pixel_ascii_char = get_pixel_ascii_char(pixel_brightness_values, invert)

            print(print_image(pixel_ascii_char, pixel_details, image_color))
    except FileNotFoundError:
        print("Error: The specified file was not found. Please check the file path and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"Error opening or processing image: {e}", file=sys.stderr)
        sys.exit(1)
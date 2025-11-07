import requests
import sys
from PIL import Image
from io import BytesIO
from cli_art_helpers import get_resized_img, get_pixel_details, get_pixel_brightness_values, get_pixel_ascii_char, print_image
import cv2
from time import sleep
import shutil

def vid_to_ascii(filepath, image_color, invert, image_fit, image_width, pixel_conversion_type, contrast, brightness):
    if filepath.startswith('http://') or filepath.startswith('https://'):
        try:
            response = requests.get(filepath) # Download the image data
            response.raise_for_status()  # Check for bad responses (404, 500)
            video_source = BytesIO(response.content)  # Use BytesIO to treat the downloaded data (in memory) like a file
            
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to download image from URL. {e}", file=sys.stderr)
            sys.exit(1) # Exit if download fails
    
    else:
        video_source = filepath

    try:
        video_capture = cv2.VideoCapture(video_source)
        while True:
            success, frame = video_capture.read()
            if not success:
                break
            frame = get_resized_img(frame, image_fit, image_width, video=True)
            frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pillow_image = Image.fromarray(frame_rgb)
            pixel_details = get_pixel_details(pillow_image)

            pixel_brightness_values = get_pixel_brightness_values(pixel_details, pixel_conversion_type)

            pixel_ascii_char = get_pixel_ascii_char(pixel_brightness_values, invert)

            print("\033[H", end="")
            print(print_image(pixel_ascii_char, pixel_details, image_color), end ="")
            print("\033[H", end="")
            sleep(1/30)

        print(shutil.get_terminal_size().columns)

    except FileNotFoundError:
        print("Error: The specified file was not found. Please check the file path and try again.")
        sys.exit(1)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        line_number = exc_traceback.tb_next.tb_lineno if exc_traceback.tb_next else exc_traceback.tb_lineno
        print(f"Error opening or processing image on line {line_number}: {e}", file=sys.stderr)
        sys.exit(1)
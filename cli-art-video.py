# check invert
# fix image width in get resized image
# add ascii artwork fromascii art archive
# enable looping
from PIL import Image, ImageEnhance
from colorama import Fore
import sys
import argparse
import shutil
import requests  # For downloading the URL
from io import BytesIO # To let Pillow read the downloaded data from memory
import cv2
import numpy as np
import os
import time
from asciimatics.scene import Scene
from asciimatics.screen import Screen

class VideoPlayerEffect(Effect):
    def __init__(self, screen, **kwargs):
        super(VideoPlayerEffect, self).__init__(screen)
        self.args = kwargs
        video_source = self.args["filepath"] 
        self.video_capture = cv2.VideoCapture(video_source)
        if not self.video_capture.isOpened():
            raise Exception(f"Could not open video file.")

        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        if fps == 0: fps = 30 # A fallback for webcams/errors
            
        self._frame_delay = 1.0 / fps
        self._last_update_time = 0

    def _update(self, frame_no):
        if time.time() - self._last_update_time < self._frame_delay:
            return  # Not yet, do nothing

        self._last_update_time = time.time()
        success, frame = self.video_capture.read()
        if not success:
            raise StopApplication("Video has ended.")
        frame = get_resized_img(frame, self.args["image_fit"], self.args["image_width"], video=True)
        frame = cv2.convertScaleAbs(frame, alpha=self.args["contrast"], beta=self.args["brightness"])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        
        pixel_details = get_pixel_details(frame)
        pixel_brightness = get_pixel_brightness_values(pixel_details, self.args["pixel_conversion_type"])
        pixel_ascii = get_pixel_ascii_char(pixel_brightness, self.args["invert"])

        frame_string = print_image(pixel_ascii, pixel_details, self.args["image_color"])

        self.screen.clear_buffer(Screen.COLOUR_BLACK, 0, Screen.COLOUR_BLACK) # 2. Clear the screen
        
        for y, line in enumerate(frame_string.split('\n')):
            self.screen.paint(line, x=0, y=y)
            
        self.screen.refresh()

    def reset(self):
        self._last_update_time = time.time()

    def stop_frame(self):
        self.video_capture.release()
    

def animation(screen, settings):
    my_video_effect = VideoPlayerEffect(screen, **settings)
    video_capture = cv2.VideoCapture(video_source)
    delay_between_frames = 1.0 / video_capture.get(cv2.CAP_PROP_FPS)
    scenes = [
        Scene([my_video_effect], duration=delay_between_frames, name="Main")
    ]
    screen.play([scenes])


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
        delay_between_frames = 1.0 / video_capture.get(cv2.CAP_PROP_FPS)
        while True:
            success, frame = video_capture.read()
            if not success:
                break
            frame = get_resized_img(frame, image_fit, image_width, video=True)
            frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            pixel_details = get_pixel_details(frame)
            pixel_brightness_values = get_pixel_brightness_values(pixel_details, pixel_conversion_type)
            pixel_ascii_char = get_pixel_ascii_char(pixel_brightness_values, invert)
            print_ascii_for_vidframes(pixel_ascii_char, pixel_details, image_color, delay_between_frames)

        print("Success")

    except KeyboardInterrupt:
        print("\nStopping video.")
    except FileNotFoundError:
        print("Error: The specified file was not found. Please check the file path and try again.")
        sys.exit(1)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        line_number = exc_traceback.tb_next.tb_lineno if exc_traceback.tb_next else exc_traceback.tb_lineno
        print(f"Error opening or processing image on line {line_number}: {e}", file=sys.stderr)
        sys.exit(1)

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
        help="Enhance image contrast. >1.0 for more, <1.0 for less. (default: 1.0)"
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


    # img_to_ascii(filepath=user_inputs.filepath, image_color=input_image_color, invert=user_inputs.invert, image_fit=image_fit_input, image_width=user_input_image_width, pixel_conversion_type=user_inputs.conversion_type, contrast=user_inputs.contrast, brightness=user_inputs.brightness)

    vid_to_ascii(filepath=user_inputs.filepath, image_color=input_image_color, invert=user_inputs.invert, image_fit=image_fit_input, image_width=user_input_image_width, pixel_conversion_type=user_inputs.conversion_type, contrast=user_inputs.contrast, brightness=user_inputs.brightness)
    args_to_pass = {
        "filepath": user_inputs.filepath, 
        "image_color": input_image_color, 
        "invert": user_inputs.invert, 
        "image_fit": image_fit_input, 
        "image_width": user_input_image_width, 
        "pixel_conversion_type": user_inputs.conversion_type, 
        "contrast": user_inputs.contrast, 
        "brightness": user_inputs.brightness
    }
    Screen.wrapper(animation, arguments=args_to_pass)

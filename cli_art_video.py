import requests
import sys
from PIL import Image
from io import BytesIO
from cli_art_helpers import get_resized_img, get_pixel_details, get_pixel_brightness_values, get_pixel_ascii_char, print_image
import cv2
import time
from time import sleep
import shutil
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from asciimatics.exceptions import ResizeScreenError, StopApplication

def vid_to_ascii_legacy(filepath, image_color, invert, image_fit, image_width, pixel_conversion_type, contrast, brightness):
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
            sleep(1/24)

        print(shutil.get_terminal_size().columns)

    except FileNotFoundError:
        print("Error: The specified file was not found. Please check the file path and try again.")
        sys.exit(1)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        line_number = exc_traceback.tb_next.tb_lineno if exc_traceback.tb_next else exc_traceback.tb_lineno
        print(f"Error opening or processing image on line {line_number}: {e}", file=sys.stderr)
        sys.exit(1)

def animation(screen, settings_dict):
    """
    This is the "director" function that asciimatics calls.
    It sets up the scene and passes all the settings to the "actor".
    """
    try:
        # 1. Create your "actor" (the VideoPlayerEffect)
        effect = VideoPlayerEffect(screen, **settings_dict)
        
        # 2. Create the "scene"
        #    Duration=-1 means "run forever" (until the Effect stops itself)
        scenes = [Scene([effect], duration=-1, name="MainScene")]
        
        # 3. Start the "movie"
        screen.play(scenes, stop_on_resize=True)
        
    except StopApplication:
        pass # The video ended normally
    except KeyboardInterrupt:
        pass # User pressed Ctrl+C

class VideoPlayerEffect(Effect):
    def __init__(self, screen, **kwargs):
        super().__init__(screen)
        self.args = kwargs
        video_path = self.args["filepath"]
        self.video_capture = cv2.VideoCapture(video_path)
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self._frame_delay = 1.0 / fps
        self._last_update_time = 0
    def _update(self, frame_no):
        if time.time() - self._last_update_time < self._frame_delay:
            return
        self._last_update_time = time.time()
        success, frame = self.video_capture.read()
        if not success: 
            raise StopApplication("Video ended.")
        frame = get_resized_img(frame, self.args["image_fit"], self.args["image_width"], video=True)
        frame = cv2.convertScaleAbs(frame, alpha=self.args["contrast"], beta=self.args["brightness"])
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pillow_image = Image.fromarray(frame_rgb)
        pixel_details = get_pixel_details(pillow_image)

        pixel_brightness_values = get_pixel_brightness_values(pixel_details, self.args["pixel_conversion_type"])

        pixel_ascii_char = get_pixel_ascii_char(pixel_brightness_values, self.args["invert"])
        frame_string = print_image(pixel_ascii_char, pixel_details, self.args["image_color"])
        self.screen.clear_buffer(Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK)
        frame_string = frame_string.split('\n') 
        y = 0 
        for line in frame_string:
            self.screen.paint(line, 0, y)
            y += 1
        self.screen.refresh()

    def reset(self):
        self._last_update_time = time.time()

    def stop_frame(self):
        self.video_capture.release()
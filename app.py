# app.py

from flask import Flask, render_template, request, send_file, jsonify, url_for
from pathlib import Path
import os
import logging
import subprocess
from PIL import Image
import numpy as np  # Import NumPy
from io import BytesIO
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('VideoGenerator')
# Suppress DEBUG logs from PIL
logging.getLogger('PIL').setLevel(logging.WARNING)

# Create Flask app
app = Flask(__name__, 
            template_folder=Path(__file__).parent / 'templates',  # Explicit template path
            static_folder=Path(__file__).parent / 'static')       # Explicit static path

# Configure Upload Folder
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'static' / 'GeneratedVideos'

class VideoTextGenerator:
    def __init__(self):
        # Default character size used for scaling
        self.default_char_size = 300  # Default character size

        # Define vertical offsets for specific letters
        self.letter_offsets = {
            # Uppercase letters
            'A': -50, 'B': -50, 'C': -50, 'D': -50, 'E': -50, 'F': -50, 'G': -50,
            'H': -50, 'I': -50, 'J': -50, 'K': -50, 'L': -50, 'M': -50, 'N': -50,
            'O': -50, 'P': -50, 'Q': -50, 'R': -50, 'S': -50, 'T': -50, 'U': -50,
            'V': -50, 'W': -50, 'X': -50, 'Y': -50, 'Z': -50,
            # Lowercase letters
            'a': 0, 'b': 0, 'c': 0, 'd': -10, 'e': 0, 'f': -10, 'g': 10,
            'h': 0, 'i': -10, 'j': -8, 'k': -10, 'l': -8, 'm': 0, 'n': 0,
            'o': 0, 'p': 10, 'q': 10, 'r': 0, 's': 0, 't': -8, 'u': 0,
            'v': -8, 'w': -8, 'x': 0, 'y': 15, 'z': 10,
            # Numbers
            '0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0,
            '7': 0, '8': 0, '9': 0
        }

        # Define horizontal spacing offsets for specific letters (left_offset, right_offset)
        self.letter_spacing_offsets = {
            # Uppercase letters
            'A': (-4, -4), 'B': (-4, -4), 'C': (-4, -4), 'D': (-4, -4), 'E': (-4, -4), 'F': (-4, -4), 'G': (-4, -4),
            'H': (-4, -4), 'I': (-4, -4), 'J': (-4, -4), 'K': (-4, -4), 'L': (-4, -4), 'M': (4, 4), 'N': (-4, -4),
            'O': (-4, -4), 'P': (-4, -4), 'Q': (-4, -4), 'R': (-4, -4), 'S': (-4, -4), 'T': (-4, -4), 'U': (-4, -4),
            'V': (-4, -4), 'W': (-4, -4), 'X': (-4, -4), 'Y': (-4, -4), 'Z': (-4, -4),
            # Lowercase letters
            'a': (0, 0), 'b': (0, 0), 'c': (0, 0), 'd': (0, 0), 'e': (0, 0), 'f': (0, 0), 'g': (0, 0),
            'h': (0, 0), 'i': (-10, -10), 'j': (-10, -10), 'k': (0, 0), 'l': (-10, -10), 'm': (4, 4), 'n': (0, 0),
            'o': (0, 0), 'p': (0, 0), 'q': (0, 0), 'r': (0, 0), 's': (0, 0), 't': (-10, -10), 'u': (0, 0),
            'v': (0, 0), 'w': (16, 10), 'x': (0, 0), 'y': (0, 0), 'z': (0, 0),
            # Numbers
            '0': (0, 0), '1': (0, 0), '2': (0, 0), '3': (0, 0), '4': (0, 0), '5': (0, 0), '6': (0, 0),
            '7': (0, 0), '8': (0, 0), '9': (0, 0),
            # Space character
            ' ': (0, 0)
        }

        # Determine the script directory
        script_dir = Path(__file__).parent.resolve()

        # Paths to video folders
        self.lower_case_path = script_dir / "static" / "Source" / "LOWER_CASE"
        self.upper_case_path = script_dir / "static" / "Source" / "UPPER_CASE"

        # Path to preview images
        self.preview_images_path = script_dir / "static" / "PreviewImages"

        # Path to temporary previews
        self.preview_output_path = script_dir / "static" / "GeneratedPreviews"
        self.preview_output_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        # Video parameters
        self.VIDEO_DURATION = 10  # Duration in seconds
        self.VIDEO_WIDTH = 1920   # Width in pixels
        self.VIDEO_HEIGHT = 1080  # Height in pixels
        self.FPS = "25"           # Frames per second

        # Character width ratios for better spacing
        self.char_width_ratios = {
            'm': 1.2,  # m is wider
            'w': 1.2,  # w is wider
            'default': 1.0  # default ratio for all other characters
        }

        # Initialize parameters with default values
        self.base_char_size = self.default_char_size  # Start with default character size
        self.char_spacing_factor = -0.8  # default character spacing factor
        self.space_width = 20  # default space width

        # Load preview images
        self.preview_images = self.load_preview_images()

    def load_preview_images(self):
        """
        Loads all preview images into a dictionary for quick access.
        """
        images = {}
        logger.debug(f"Loading preview images from {self.preview_images_path}")
        for image_file in self.preview_images_path.glob("*.png"):
            key = image_file.stem  # e.g., 'upper_a' or 'lower_a'
            try:
                image = Image.open(image_file).convert('RGBA')  # Ensure RGBA mode
                images[key] = image
                logger.debug(f"Loaded image: {key}")
            except Exception as e:
                logger.error(f"Failed to load image {image_file}: {e}")
        logger.info(f"Total preview images loaded: {len(images)}")
        return images

    def screen_blend(self, img1, img2):
        """
        Blends two images using the 'screen' blend mode.
        """
        arr1 = np.array(img1).astype('float') / 255.0
        arr2 = np.array(img2).astype('float') / 255.0

        # Separate the RGB and alpha channels
        rgb1 = arr1[..., :3]
        alpha1 = arr1[..., 3]
        rgb2 = arr2[..., :3]
        alpha2 = arr2[..., 3]

        # Compute the screen blending for RGB channels
        rgb = 1 - (1 - rgb1) * (1 - rgb2)

        # Compute the combined alpha channel
        alpha = alpha1 + alpha2 * (1 - alpha1)

        # Handle invalid values
        alpha = np.clip(alpha, 0, 1)
        rgb = np.clip(rgb, 0, 1)

        # Multiply RGB by alpha
        rgb = rgb * alpha[..., np.newaxis]

        # Combine RGB and alpha channels
        result = np.dstack((rgb, alpha))

        # Convert back to uint8
        result = (result * 255).astype('uint8')

        # Create an image from the result
        return Image.fromarray(result, 'RGBA')

    def generate_preview_image(self, text_input, case_var, char_size_var, char_spacing_var):
        """
        Generates a preview image, saves it to the temporary directory, and returns the filename.
        """
        logger.debug("Starting preview image generation")
        text = text_input.strip()
        if not text:
            text = "Preview"
            logger.debug("No text provided. Using default 'Preview'")

        # Apply chosen case
        if case_var == "upper":
            text_display = text.upper()
        elif case_var == "lower":
            text_display = text.lower()
        else:
            text_display = text
        logger.debug(f"Processed text for display: '{text_display}'")

        base_char_size = char_size_var
        char_spacing_factor = char_spacing_var
        char_spacing = int(base_char_size * char_spacing_factor)
        space_width = self.space_width

        logger.debug(f"Base Character Size: {base_char_size}")
        logger.debug(f"Character Spacing Factor: {char_spacing_factor}")
        logger.debug(f"Calculated Character Spacing: {char_spacing}")
        logger.debug(f"Space Width: {space_width}")

        # Calculate vertical scaling factor
        vertical_scale = base_char_size / self.default_char_size
        logger.debug(f"Vertical Scale: {vertical_scale}")

        # Base character size and spacing
        # Calculate total width considering character sizes and spacing
        total_width = 0
        char_positions = []

        for i, char in enumerate(text_display):
            if char.isalpha() or char.isdigit():
                case = "upper" if char.isupper() else "lower"

                # Get left and right spacing offsets
                left_offset, right_offset = self.letter_spacing_offsets.get(char, (0, 0))
                logger.debug(f"Character '{char}' left_offset: {left_offset}, right_offset: {right_offset}")

                # Apply left offset
                total_width += left_offset

                # Add extra spacing before uppercase characters (except first character)
                if i > 0 and case == "upper":
                    extra_spacing = int(base_char_size * 0.2)
                    total_width += extra_spacing
                    logger.debug(f"Added extra spacing for uppercase character '{char}': {extra_spacing}")

                # Adjust size for uppercase characters
                current_char_size = int(base_char_size * 1.2) if case == "upper" else base_char_size
                logger.debug(f"Character '{char}' size: {current_char_size}")

                # Store position
                char_positions.append((total_width, current_char_size))
                total_width += current_char_size

                # Apply right offset
                total_width += right_offset

                # Add spacing between characters (except last character)
                if i < len(text_display) - 1:
                    total_width += char_spacing
                    logger.debug(f"Added character spacing after '{char}': {char_spacing}")

            elif char.isspace():
                # Get left and right spacing offsets for space
                left_offset, right_offset = self.letter_spacing_offsets.get(' ', (0, 0))
                logger.debug(f"Space character left_offset: {left_offset}, right_offset: {right_offset}")
                total_width += left_offset

                char_positions.append(None)
                total_width += space_width

                total_width += right_offset

        if not char_positions:
            logger.warning("No characters to process for preview")
            return None

        logger.debug(f"Total width after processing characters: {total_width}")

        # Create base image for blending
        canvas_width = 1920  # Updated to 1920
        canvas_height = 1080  # Updated to 1080
        base_image = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 255))
        logger.debug(f"Created base image with size: {base_image.size}")

        # Scaling factor from video size to canvas size
        scale_x = canvas_width / self.VIDEO_WIDTH
        scale_y = canvas_height / self.VIDEO_HEIGHT
        scale = min(scale_x, scale_y)  # Maintain aspect ratio
        logger.debug(f"Scaling factor: {scale}")

        # Scale positions and sizes
        scaled_char_positions = []
        for pos in char_positions:
            if pos is not None:
                x, size = pos
                scaled_x = int(x * scale)
                scaled_size = int(size * scale)
                scaled_char_positions.append((scaled_x, scaled_size))
            else:
                scaled_char_positions.append(None)
        scaled_total_width = int(total_width * scale)
        logger.debug(f"Scaled total width: {scaled_total_width}")

        # Calculate center offset
        y_offset = (canvas_height - (base_char_size * scale)) // 2
        x_offset = (canvas_width - scaled_total_width) // 2
        logger.debug(f"Y Offset: {y_offset}, X Offset: {x_offset}")

        # Blend images
        current_image = base_image.copy()
        char_index = 0

        for i, (position, char) in enumerate(zip(char_positions, text_display)):
            if position is not None:
                case = "upper" if char.isupper() else "lower"
                key = f"{case}_{char.lower()}"
                img = self.preview_images.get(key)

                if img:
                    x, char_size = position
                    # Adjust y position for uppercase characters and apply custom vertical offset
                    original_y_offset = self.letter_offsets.get(char, 0)
                    y_pos = y_offset + int(original_y_offset * vertical_scale * scale)
                    logger.debug(f"Character '{char}' position: ({x_offset + x}, {y_pos})")

                    resized_img = img.resize((char_size, char_size), Image.LANCZOS).convert('RGBA')
                    temp_image = Image.new('RGBA', current_image.size, (0, 0, 0, 0))
                    temp_image.paste(resized_img, (int(x_offset + x), int(y_pos)), mask=resized_img)
                    current_image = self.screen_blend(current_image, temp_image)
                    logger.debug(f"Blended character '{char}' at position ({x_offset + x}, {y_pos})")
                else:
                    logger.warning(f"No preview image found for key '{key}'")
        logger.debug("Finished blending characters into the final image")
        logger.debug(f"Final image size: {current_image.size}")
        
        # Convert final image to RGB and save to temporary directory
        final_image = current_image.convert('RGB')
        
        # Generate a unique filename
        unique_filename = f"preview_{uuid.uuid4().hex}.png"
        final_image.save(self.preview_output_path / unique_filename)
        logger.debug(f"Saved preview image as '{unique_filename}' in '{self.preview_output_path}'")
        
        # Delete previous preview images to keep only the latest
        self.cleanup_previews()
        
        return unique_filename

    def cleanup_previews(self):
        """
        Deletes all preview images in the temporary directory except the latest one.
        """
        preview_files = list(self.preview_output_path.glob("preview_*.png"))
        if len(preview_files) > 1:
            # Sort files by modification time (newest first)
            preview_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            # Keep only the first file, delete the rest
            for old_file in preview_files[1:]:
                try:
                    old_file.unlink()
                    logger.debug(f"Deleted old preview image '{old_file.name}'")
                except Exception as e:
                    logger.error(f"Failed to delete old preview image '{old_file.name}': {e}")

    def get_video_path(self, char, case="lower"):
        """
        Returns the full path to the video file corresponding to the character and specified case.
        """
        base_path = self.lower_case_path if case == "lower" else self.upper_case_path
        video_file = f"{char.upper()}.mp4" if case == "upper" else f"{char.lower()}.mp4"
        full_path = base_path / video_file
        logger.debug(f"Looking for video file: {full_path} (exists: {full_path.exists()})")
        return full_path

    def create_video(self, text_input, case_var, char_size_var, char_spacing_var):
        """
        Generates the video using FFmpeg by combining character videos with improved spacing
        and proper uppercase letter handling
        """
        logger.info("Starting video creation")
        text = text_input.strip()
        if not text:
            text = "SampleText"
            logger.debug("No text provided. Using default 'SampleText'")

        # Apply chosen case
        if case_var == "upper":
            text = text.upper()
        elif case_var == "lower":
            text = text.lower()

        logger.info(f"Generating video for text: '{text}' with case: {case_var}")

        try:
            # Collect valid videos for each character
            valid_chars = []
            for i, char in enumerate(text):
                if char.isalpha() or char.isdigit() or char.isspace():
                    case = "upper" if char.isupper() else "lower"
                    if char.isspace():
                        valid_chars.append((i, None))
                    else:
                        video_path = self.get_video_path(char, case)
                        if video_path.exists():
                            valid_chars.append((i, str(video_path)))
                        else:
                            raise FileNotFoundError(f"No video found for character '{char}'")
                else:
                    raise ValueError(f"Unsupported character '{char}' in text")

            if not valid_chars:
                raise ValueError("No valid characters to process")

            base_char_size = char_size_var
            char_spacing_factor = char_spacing_var
            char_spacing = int(base_char_size * char_spacing_factor)
            space_width = self.space_width

            # Calculate vertical scaling factor
            vertical_scale = base_char_size / self.default_char_size

            # Calculate total width considering individual character widths and spacing
            total_width = 0
            char_positions = []
            current_x = 0

            for i, (char_index, path) in enumerate(valid_chars):
                char = text[char_index]

                if path is None:  # Space character
                    # Get left and right spacing offsets for space
                    left_offset, right_offset = self.letter_spacing_offsets.get(' ', (0, 0))
                    current_x += left_offset

                    char_positions.append(None)
                    current_x += space_width

                    current_x += right_offset
                else:
                    case = "upper" if char.isupper() else "lower"

                    # Get left and right spacing offsets
                    left_offset, right_offset = self.letter_spacing_offsets.get(char, (0, 0))

                    # Apply left offset
                    current_x += left_offset

                    # Add extra spacing before uppercase characters (except first character)
                    if i > 0 and case == "upper":
                        current_x += int(base_char_size * 0.2)  # Add 20% of base size as extra spacing

                    # Adjust size for uppercase characters
                    char_width = int(base_char_size * 1.2) if case == "upper" else base_char_size

                    # Store position
                    char_positions.append((current_x, char_width))
                    current_x += char_width

                    # Apply right offset
                    current_x += right_offset

                    # Add spacing between characters (overlap), except for last character
                    if i < len(valid_chars) - 1:
                        current_x += char_spacing

            total_width = current_x

            # Scale everything if too wide
            scale_factor = 1.0
            if total_width > self.VIDEO_WIDTH * 0.9:
                scale_factor = (self.VIDEO_WIDTH * 0.9) / total_width
                base_char_size = int(base_char_size * scale_factor)
                char_spacing = int(char_spacing * scale_factor)
                space_width = int(space_width * scale_factor)
                total_width = int(total_width * scale_factor)
                char_positions = [
                    (int(pos[0] * scale_factor), int(pos[1] * scale_factor)) if pos is not None else None
                    for pos in char_positions
                ]
                # Recalculate vertical scaling factor after scaling
                vertical_scale = base_char_size / self.default_char_size

            # Center the text horizontally
            x_offset = (self.VIDEO_WIDTH - total_width) // 2
            y_base = (self.VIDEO_HEIGHT - base_char_size) // 2

            # Build FFmpeg command
            cmd = ["ffmpeg", "-y"]

            # Add input files for characters (excluding spaces)
            for _, path in valid_chars:
                if path is not None:
                    cmd.extend(["-i", path])

            # Construct the complex filter
            filter_parts = []
            # Corrected the size parameter by removing the '=' between x and 1080
            filter_parts.append(f"color=black:s={self.VIDEO_WIDTH}x{self.VIDEO_HEIGHT}:d={self.VIDEO_DURATION}:r={self.FPS}[bg];")

            # Initialize the overlay chain
            current = "bg"
            input_index = 0

            for i, (path, position) in enumerate(zip(valid_chars, char_positions)):
                char_index, path = path
                char = text[char_index]

                if path is not None and position is not None:
                    x_pos, char_width = position

                    # Adjust y position for characters and apply custom vertical offset
                    y_pos = y_base + int(self.letter_offsets.get(char, 0) * vertical_scale)

                    # Scale and position each character
                    filter_parts.append(
                        f"[{input_index}:v]scale={char_width}:{char_width},setsar=1,format=gbrp[s{char_index}];"
                    )
                    filter_parts.append(
                        f"color=black:s={self.VIDEO_WIDTH}x{self.VIDEO_HEIGHT}:d={self.VIDEO_DURATION}[tmp{char_index}];"
                    )
                    filter_parts.append(
                        f"[tmp{char_index}][s{char_index}]overlay=x={x_offset + x_pos}:y={y_pos}:format=auto[overlay{char_index}];"
                    )
                    filter_parts.append(
                        f"[{current}][overlay{char_index}]blend=all_mode='screen':shortest=1[blend{char_index}];"
                    )
                    current = f"blend{char_index}"
                    input_index += 1

            # Remove the trailing semicolon from the last filter part if necessary
            if filter_parts and filter_parts[-1].endswith(';'):
                filter_parts[-1] = filter_parts[-1][:-1]

            # Final assembly of the FFmpeg command
            filter_complex = "".join(filter_parts)
            output_filename = f"generated_{text}.mp4"
            output_filepath = self.get_output_filepath(output_filename)
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            cmd.extend([
                "-filter_complex", filter_complex,
                "-map", f"[{current}]",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-r", self.FPS,
                "-t", str(self.VIDEO_DURATION),
                "-pix_fmt", "yuv420p",
                output_filepath
            ])

            logger.debug("FFmpeg command: " + " ".join(cmd))

            # Execute the FFmpeg command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr}")
                raise RuntimeError(f"FFmpeg failed with error: {stderr}")

            logger.info("Video generation completed successfully")
            return output_filepath

        except Exception as e:
            logger.error(f"Error during video generation: {str(e)}", exc_info=True)
            raise e

    def get_output_filepath(self, output_filename):
        """
        Returns the full path to save the generated video.
        """
        return os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

video_generator = VideoTextGenerator()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text_input = request.form.get('text_input', '').strip()
        if not text_input:
            logger.warning("No text provided in video generation request.")
            return "Please enter some text.", 400

        case_var = request.form.get('case_var', 'mixed')
        try:
            char_size_var = int(request.form.get('char_size_var', 300))
            char_spacing_var = float(request.form.get('char_spacing_var', -0.8))
        except ValueError:
            logger.warning("Invalid character size or spacing provided in video generation request.")
            return "Invalid character size or spacing.", 400

        try:
            video_filepath = video_generator.create_video(text_input, case_var, char_size_var, char_spacing_var)
            return send_file(video_filepath, as_attachment=True)
        except Exception as e:
            logger.error(f"Error during video generation: {str(e)}", exc_info=True)
            return f"An error occurred: {str(e)}", 500
    else:
        return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    data = request.get_json()
    logger.debug(f"Received preview request with data: {data}")  # Debugging line

    text_input = data.get('text_input', '').strip()
    if not text_input:
        logger.warning("No text provided in preview request.")
        return jsonify({'error': 'No text provided'}), 400

    case_var = data.get('case_var', 'mixed')
    try:
        char_size_var = int(data.get('char_size_var', 300))
        char_spacing_var = float(data.get('char_spacing_var', -0.8))
    except ValueError:
        logger.warning("Invalid character size or spacing provided in preview request.")
        return jsonify({'error': 'Invalid character size or spacing'}), 400

    try:
        filename = video_generator.generate_preview_image(text_input, case_var, char_size_var, char_spacing_var)
        if not filename:
            logger.error("generate_preview_image returned None or empty filename.")
            return jsonify({'error': 'Unable to generate preview'}), 500

        # Generate the URL for the preview image
        preview_url = url_for('static', filename=f'GeneratedPreviews/{filename}', _external=True)
        logger.debug(f"Generated preview URL: {preview_url}")

        return jsonify({'preview_url': preview_url})
    except Exception as e:
        logger.error(f"Error during preview generation: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# Optional: Temporary Test Route
@app.route('/test_image')
def test_image():
    try:
        # Create a simple red square image for testing
        img = Image.new('RGBA', (200, 200), color=(255, 0, 0, 255))
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        logger.error(f"Error generating test image: {e}", exc_info=True)
        return "Error generating test image.", 500

if __name__ == '__main__':
    logger.info(f"Template folder: {app.template_folder}")
    logger.info(f"Static folder: {app.static_folder}")
    app.run(debug=True, port=5001)

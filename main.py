import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
import sys
import logging
import subprocess
import json  # For configuration file
from PIL import Image, ImageTk
import numpy as np  # Import NumPy

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('VideoGenerator')
# Suppress DEBUG logs from PIL
logging.getLogger('PIL').setLevel(logging.WARNING)

class VideoTextGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Text Generator")
        
        # Determine the script directory
        if getattr(sys, 'frozen', False):
            script_dir = Path(sys._MEIPASS)
        else:
            script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Paths to video folders
        self.lower_case_path = script_dir / "Source" / "LOWER_CASE"
        self.upper_case_path = script_dir / "Source" / "UPPER_CASE"
        
        # Path to preview images
        self.preview_images_path = script_dir / "PreviewImages"
        
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
        self.base_char_size = 150  # default character size
        self.char_spacing_factor = -0.7  # default character spacing factor
        self.word_spacing_factor = 0.5   # default word spacing factor
        self.uppercase_spacing_factor = 4.0  # Spacing factor for uppercase letters
        
        # Load preview images and compute vertical offsets
        self.preview_images = self.load_preview_images()
        
        # Custom vertical offsets for specific characters
        self.custom_offsets = {}  # Key: character key (e.g., 'lower_i'), Value: offset in pixels
        
        # Configuration file path
        self.config_file = script_dir / "config.json"
        
        # Load custom offsets from config file
        self.load_config()
        
        # Set up the GUI
        self.setup_gui()
    
    def load_config(self):
        """
        Loads custom offsets from the configuration file.
        """
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                try:
                    config = json.load(f)
                    self.custom_offsets = config.get('custom_offsets', {})
                    logger.info("Custom offsets loaded from config.")
                except json.JSONDecodeError:
                    logger.error("Error decoding config file. Starting with empty offsets.")
                    self.custom_offsets = {}
        else:
            self.custom_offsets = {}
    
    def save_config(self):
        """
        Saves custom offsets to the configuration file.
        """
        config = {
            'custom_offsets': self.custom_offsets
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info("Custom offsets saved to config.")
    
    def load_preview_images(self):
        """
        Loads all preview images into a dictionary for quick access.
        Also computes vertical alignment offsets for each character.
        """
        images = {}
        vertical_offsets = {}
        for image_file in self.preview_images_path.glob("*.png"):
            key = image_file.stem  # e.g., 'lower_a' or 'upper_A'
            image = Image.open(image_file).convert('RGBA')  # Ensure RGBA mode
            images[key] = image
            # Compute vertical offset ratio
            alpha = image.split()[-1]
            bbox = alpha.getbbox()
            if bbox is not None:
                bottom_padding = image.height - bbox[3]
                vertical_offset_ratio = bottom_padding / image.height
                vertical_offsets[key] = vertical_offset_ratio
            else:
                vertical_offsets[key] = 0
        self.vertical_offsets = vertical_offsets
        return images

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text input field
        ttk.Label(main_frame, text="Enter text:").grid(row=0, column=0, sticky=tk.W)
        self.text_input = ttk.Entry(main_frame, width=40)
        self.text_input.insert(0, "Ouais Ouais")  # Default text
        self.text_input.grid(row=0, column=1, padx=5, pady=5, columnspan=3)
        self.text_input.bind("<KeyRelease>", self.update_preview)
        
        # Radio buttons for case selection
        self.case_var = tk.StringVar(value="mixed")
        ttk.Radiobutton(main_frame, text="Uppercase", variable=self.case_var, 
                       value="upper", command=self.update_preview).grid(row=1, column=0)
        ttk.Radiobutton(main_frame, text="Lowercase", variable=self.case_var, 
                       value="lower", command=self.update_preview).grid(row=1, column=1)
        ttk.Radiobutton(main_frame, text="Mixed case", variable=self.case_var, 
                       value="mixed", command=self.update_preview).grid(row=1, column=2)
        
        # Spacing controls
        ttk.Label(main_frame, text="Character Size:").grid(row=2, column=0, sticky=tk.W)
        self.char_size_var = tk.IntVar(value=self.base_char_size)
        char_size_spin = ttk.Spinbox(main_frame, from_=50, to=300, increment=10, textvariable=self.char_size_var, command=self.update_preview)
        char_size_spin.grid(row=2, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Char Spacing:").grid(row=3, column=0, sticky=tk.W)
        self.char_spacing_var = tk.DoubleVar(value=self.char_spacing_factor)
        char_spacing_spin = ttk.Spinbox(main_frame, from_=-1.0, to=1.0, increment=0.1, textvariable=self.char_spacing_var, format="%.1f", command=self.update_preview)
        char_spacing_spin.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="Word Spacing:").grid(row=4, column=0, sticky=tk.W)
        self.word_spacing_var = tk.DoubleVar(value=self.word_spacing_factor)
        word_spacing_spin = ttk.Spinbox(main_frame, from_=0.0, to=2.0, increment=0.1, textvariable=self.word_spacing_var, format="%.1f", command=self.update_preview)
        word_spacing_spin.grid(row=4, column=1, sticky=tk.W)
        
        # Custom Offsets Controls
        ttk.Label(main_frame, text="Custom Character Offsets:").grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
        
        # Frame to hold custom offset entries
        self.offsets_frame = ttk.Frame(main_frame)
        self.offsets_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W)

        # Add Button
        ttk.Button(main_frame, text="+", command=self.add_offset_entry).grid(row=5, column=2, sticky=tk.E)

        # Load existing offsets
        self.offset_entries = []
        for key, offset in self.custom_offsets.items():
            self.create_offset_entry(key, offset)
        
        # Button to generate video
        ttk.Button(main_frame, text="Generate Video", 
                  command=self.generate_video).grid(row=7, column=1, pady=10)
        
        # Canvas for preview with 16:9 aspect ratio
        self.preview_canvas = tk.Canvas(main_frame, width=800, height=450, bg="black")
        self.preview_canvas.grid(row=8, column=0, columnspan=3, pady=10)
        
        # Update preview initially
        self.update_preview()
    
    def add_offset_entry(self):
        """
        Adds a new offset entry to the GUI.
        """
        self.create_offset_entry()
    
    def create_offset_entry(self, key=None, offset_value=0):
        """
        Creates a single offset entry in the GUI.
        """
        frame = ttk.Frame(self.offsets_frame)
        frame.pack(fill='x', pady=2)

        char_var = tk.StringVar(value=key.split('_')[1] if key else '')
        offset_var = tk.IntVar(value=offset_value)

        ttk.Label(frame, text="Character:").pack(side='left')
        char_entry = ttk.Entry(frame, width=5, textvariable=char_var)
        char_entry.pack(side='left', padx=5)

        ttk.Label(frame, text="Offset (px):").pack(side='left')
        offset_entry = ttk.Entry(frame, width=5, textvariable=offset_var)
        offset_entry.pack(side='left', padx=5)

        # Remove Button
        remove_button = ttk.Button(frame, text="Remove", command=lambda: self.remove_offset_entry(frame))
        remove_button.pack(side='left', padx=5)

        # Bind events to update preview and config when values change
        char_var.trace_add("write", self.offset_entry_changed)
        offset_var.trace_add("write", self.offset_entry_changed)

        # Store references
        self.offset_entries.append((frame, char_var, offset_var))

    def offset_entry_changed(self, *args):
        """
        Called when an offset entry changes to update the config and preview.
        """
        self.update_custom_offsets()
        self.save_config()
        self.update_preview()

    def remove_offset_entry(self, frame):
        """
        Removes an offset entry from the GUI and updates custom offsets.
        """
        # Find and remove the entry
        for i, (entry_frame, _, _) in enumerate(self.offset_entries):
            if entry_frame == frame:
                entry_frame.destroy()
                del self.offset_entries[i]
                break

        # Update custom offsets and preview
        self.update_custom_offsets()
        self.save_config()
        self.update_preview()
    
    def update_custom_offsets(self):
        """
        Updates the custom_offsets dictionary based on GUI entries.
        """
        self.custom_offsets = {}
        for _, char_var, offset_var in self.offset_entries:
            char = char_var.get().strip()
            offset = offset_var.get()
            if len(char) == 1 and char.isalpha():
                case = "upper" if char.isupper() else "lower"
                key = f"{case}_{char.lower()}"
                self.custom_offsets[key] = offset
            else:
                # If the character is invalid, remove it from custom_offsets
                key = char_var.get()
                if key in self.custom_offsets:
                    del self.custom_offsets[key]
        # Save config after updating offsets
        self.save_config()

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

    def update_preview(self, *args):
        """
        Updates the preview canvas to show the current text placement with the blending effect.
        """
        # Update custom offsets from GUI
        self.update_custom_offsets()

        # Clear the canvas
        self.preview_canvas.delete("all")
        
        # Get the text
        text = self.text_input.get().strip()
        if not text:
            return

        # Apply chosen case
        case_choice = self.case_var.get()
        if case_choice == "upper":
            text_display = text.upper()
        elif case_choice == "lower":
            text_display = text.lower()
        else:
            text_display = text

        # Get the parameters from the GUI variables
        self.base_char_size = self.char_size_var.get()
        self.char_spacing_factor = self.char_spacing_var.get()
        self.word_spacing_factor = self.word_spacing_var.get()

        # Base character size and spacing
        base_char_size = self.base_char_size
        char_spacing_base = int(base_char_size * self.char_spacing_factor)
        word_spacing = int(base_char_size * self.word_spacing_factor)

        # Collect valid characters and their images
        char_images = []
        char_keys = []
        char_cases = []
        for char in text_display:
            if char.isalpha():
                case = "upper" if char.isupper() else "lower"
                key = f"{case}_{char.lower()}"
                image = self.preview_images.get(key)
                if image:
                    char_images.append(image)
                    char_keys.append(key)
                    char_cases.append(case)
                else:
                    logger.warning(f"No preview image for character '{char}'")
            elif char.isspace():
                # Add a None to represent space
                char_images.append(None)
                char_keys.append(None)
                char_cases.append(None)
            else:
                logger.warning(f"Unsupported character '{char}' in text")

        if not char_images:
            return

        # Create base image for blending
        preview_width = int(self.preview_canvas['width'])
        preview_height = int(self.preview_canvas['height'])
        base_image = Image.new('RGBA', (preview_width, preview_height), (0, 0, 0, 255))

        # Calculate positions
        total_width = 0
        char_positions = []
        last_was_space = False
        for i, (img, case) in enumerate(zip(char_images, char_cases)):
            if img is None:
                total_width += word_spacing
                char_positions.append(None)
                last_was_space = True
            else:
                # Adjust spacing for uppercase letters
                if case == "upper":
                    char_spacing = int(char_spacing_base * self.uppercase_spacing_factor)
                else:
                    char_spacing = char_spacing_base

                if i > 0 and not last_was_space:
                    total_width += char_spacing
                char_positions.append(total_width)
                total_width += base_char_size
                last_was_space = False

        x_offset = (preview_width - total_width) // 2
        y_offset = (preview_height - base_char_size) // 2

        # Blend images using screen blending
        current_image = base_image.copy()
        for pos, img, key, case in zip(char_positions, char_images, char_keys, char_cases):
            if img is not None and pos is not None:
                vertical_offset_ratio = self.vertical_offsets.get(key, 0)
                vertical_offset = vertical_offset_ratio * base_char_size

                # Apply custom offset if any
                custom_offset = self.custom_offsets.get(key, 0)

                resized_img = img.resize((base_char_size, base_char_size), Image.LANCZOS).convert('RGBA')
                x = x_offset + pos
                y_adjusted = y_offset + vertical_offset + custom_offset
                temp_image = Image.new('RGBA', current_image.size, (0, 0, 0, 0))
                temp_image.paste(resized_img, (int(x), int(y_adjusted)), mask=resized_img)
                # Perform screen blending
                current_image = self.screen_blend(current_image, temp_image)

        # Convert to Tkinter image
        tk_image = ImageTk.PhotoImage(current_image.convert('RGB'))
        self.preview_canvas.image = tk_image  # Keep reference
        self.preview_canvas.create_image(0, 0, anchor='nw', image=tk_image)

    def get_video_path(self, char, case="lower"):
        """
        Returns the full path to the video file corresponding to the character and specified case.
        """
        base_path = self.lower_case_path if case == "lower" else self.upper_case_path
        video_file = f"{char.lower()}.mp4"
        full_path = base_path / video_file
        logger.debug(f"Looking for video file: {full_path} (exists: {full_path.exists()})")
        return full_path

    def generate_video(self):
        """
        Generates the video using FFmpeg by combining character videos with improved spacing.
        """
        # Update custom offsets from GUI
        self.update_custom_offsets()

        text = self.text_input.get().strip()
        if not text:
            text = "Ouais Ouais"

        # Apply chosen case
        case_choice = self.case_var.get()
        if case_choice == "upper":
            text_display = text.upper()
        elif case_choice == "lower":
            text_display = text.lower()
        else:
            text_display = text

        # Get the parameters from the GUI variables
        base_char_size = self.char_size_var.get()
        char_spacing_factor = self.char_spacing_var.get()
        word_spacing_factor = self.word_spacing_var.get()
        uppercase_spacing_factor = self.uppercase_spacing_factor

        char_spacing_base = int(base_char_size * char_spacing_factor)
        word_spacing = int(base_char_size * word_spacing_factor)

        logger.info(f"Generating video for text: '{text}' with case: {case_choice}")

        try:
            # Collect valid videos and vertical offsets for each character
            valid_chars = []
            char_cases = []
            for i, char in enumerate(text_display):
                if char.isalpha() or char.isdigit() or char.isspace():
                    case = "upper" if char.isupper() else "lower"
                    key = f"{case}_{char.lower()}"
                    if char.isspace():
                        valid_chars.append((i, None, 0, key, None))
                        char_cases.append(None)
                    else:
                        video_path = self.get_video_path(char.lower(), case)
                        vertical_offset_ratio = self.vertical_offsets.get(key, 0)
                        custom_offset = self.custom_offsets.get(key, 0)
                        if video_path.exists():
                            valid_chars.append((i, str(video_path), vertical_offset_ratio, custom_offset, case))
                            char_cases.append(case)
                        else:
                            raise FileNotFoundError(f"No video found for character '{char}'")
                else:
                    raise ValueError(f"Unsupported character '{char}' in text")

            if not valid_chars:
                raise ValueError("No valid characters to process")

            # Calculate total width considering individual character widths
            total_width = 0
            char_positions = []
            current_x = 0
            last_was_space = False

            for i, (char_index, path, _, _, case) in enumerate(valid_chars):
                if path is None:  # Space character
                    if i < len(valid_chars) - 1:
                        current_x += word_spacing
                        last_was_space = True
                    # Add a placeholder to keep indices aligned
                    char_positions.append(None)
                else:
                    # Adjust spacing for uppercase letters
                    if case == "upper":
                        char_spacing = int(char_spacing_base * uppercase_spacing_factor)
                    else:
                        char_spacing = char_spacing_base

                    if i > 0 and not last_was_space:
                        current_x += char_spacing
                    char_width = base_char_size
                    char_positions.append((current_x, char_width))
                    current_x += char_width
                    last_was_space = False

            total_width = current_x

            # Scale everything if too wide
            scale_factor = 1.0
            if total_width > self.VIDEO_WIDTH * 0.9:
                scale_factor = (self.VIDEO_WIDTH * 0.9) / total_width
                base_char_size = int(base_char_size * scale_factor)
                char_spacing_base = int(char_spacing_base * scale_factor)
                word_spacing = int(word_spacing * scale_factor)
                total_width = int(total_width * scale_factor)
                char_positions = [
                    (int(pos[0] * scale_factor), int(pos[1] * scale_factor)) if pos is not None else None
                    for pos in char_positions
                ]

            # Center the text horizontally
            x_offset = (self.VIDEO_WIDTH - total_width) // 2

            # Build FFmpeg command
            cmd = ["ffmpeg", "-y"]

            # Add input files for characters (excluding spaces)
            for _, path, _, _, _ in valid_chars:
                if path is not None:
                    cmd.extend(["-i", path])

            # Construct the complex filter
            filter_parts = []
            filter_parts.append(f"color=black:s={self.VIDEO_WIDTH}x{self.VIDEO_HEIGHT}:d={self.VIDEO_DURATION}:r={self.FPS}[bg];")

            # Initialize the overlay chain
            current = "bg"
            input_index = 0

            for i, ((char_index, path, vertical_offset_ratio, custom_offset, case), position) in enumerate(zip(valid_chars, char_positions)):
                if path is not None and position is not None:
                    rel_x, char_width = position
                    x_pos = x_offset + rel_x
                    # Adjust y_pos based on vertical offset
                    vertical_offset = vertical_offset_ratio * base_char_size + custom_offset
                    y_pos = (self.VIDEO_HEIGHT - base_char_size) // 2 + int(vertical_offset)

                    # Scale and position each character
                    filter_parts.append(
                        f"[{input_index}:v]scale={base_char_size}:{base_char_size},setsar=1,format=rgba[s{char_index}];"
                    )
                    filter_parts.append(
                        f"color=black@0:s={self.VIDEO_WIDTH}x{self.VIDEO_HEIGHT}:d={self.VIDEO_DURATION}[tmp{char_index}];"
                    )
                    filter_parts.append(
                        f"[tmp{char_index}][s{char_index}]overlay=x={x_pos}:y={y_pos}:format=auto[overlay{char_index}];"
                    )
                    filter_parts.append(
                        f"[{current}][overlay{char_index}]blend=all_mode='screen':shortest=1[blend{char_index}];"
                    )
                    current = f"blend{char_index}"
                    input_index += 1  # Increment input index only for non-space characters

            # Remove the trailing semicolon from the last filter part if necessary
            if filter_parts[-1].endswith(';'):
                filter_parts[-1] = filter_parts[-1][:-1]

            # Final assembly of the FFmpeg command
            filter_complex = "".join(filter_parts)
            cmd.extend([
                "-filter_complex", filter_complex,
                "-map", f"[{current}]",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-r", self.FPS,
                "-t", str(self.VIDEO_DURATION),
                "-pix_fmt", "yuv420p",
                f"generated_{text}.mp4"
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
            messagebox.showinfo("Success", f"Video generated successfully: generated_{text}.mp4")

        except Exception as e:
            logger.error(f"Error during video generation: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTextGenerator(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
import sys
import logging
import subprocess

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('VideoGenerator')

class VideoTextGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Text Generator")
        
        # Détermination du répertoire du script
        if getattr(sys, 'frozen', False):
            script_dir = Path(sys._MEIPASS)
        else:
            script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Chemins vers les dossiers de vidéos
        self.lower_case_path = script_dir / "Source" / "LOWER_CASE"
        self.upper_case_path = script_dir / "Source" / "UPPER_CASE"
        
        # Paramètres vidéo
        self.VIDEO_DURATION = 10  # Durée en secondes
        self.VIDEO_WIDTH = 1920   # Largeur en pixels
        self.VIDEO_HEIGHT = 1080  # Hauteur en pixels
        self.FPS = "25"           # Images par seconde
        
        # Character width ratios for better spacing
        self.char_width_ratios = {
            'm': 1.2,  # m is wider
            'w': 1.2,  # w is wider
            'default': 1.0  # default ratio for all other characters
        }
        
        # Configuration de l'interface graphique
        self.setup_gui()
    
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Champ de saisie du texte
        ttk.Label(main_frame, text="Enter text:").grid(row=0, column=0, sticky=tk.W)
        self.text_input = ttk.Entry(main_frame, width=40)
        self.text_input.insert(0, "Ouais Ouais")  # Texte par défaut
        self.text_input.grid(row=0, column=1, padx=5, pady=5)
        
        # Boutons radio pour choisir la casse
        self.case_var = tk.StringVar(value="mixed")
        ttk.Radiobutton(main_frame, text="Uppercase", variable=self.case_var, 
                       value="upper").grid(row=1, column=0)
        ttk.Radiobutton(main_frame, text="Lowercase", variable=self.case_var, 
                       value="lower").grid(row=1, column=1)
        ttk.Radiobutton(main_frame, text="Mixed case", variable=self.case_var, 
                       value="mixed").grid(row=1, column=2)
        
        # Bouton pour générer la vidéo
        ttk.Button(main_frame, text="Generate Video", 
                  command=self.generate_video).grid(row=2, column=1, pady=10)

    def get_video_path(self, char, case="lower"):
        """
        Retourne le chemin complet vers le fichier vidéo correspondant au caractère et à la casse spécifiée.
        """
        base_path = self.lower_case_path if case == "lower" else self.upper_case_path
        video_file = f"{char}.mp4"
        full_path = base_path / video_file
        logger.debug(f"Looking for video file: {full_path} (exists: {full_path.exists()})")
        return full_path

    def get_char_width(self, char, base_size):
        """
        Returns the adjusted width for a specific character based on predefined ratios
        """
        ratio = self.char_width_ratios.get(char.lower(), self.char_width_ratios['default'])
        return int(base_size * ratio)

    def generate_video(self):
        """
        Generates the video using FFmpeg by combining character videos with improved spacing
        """
        text = self.text_input.get().strip()
        if not text:
            text = "Ouais Ouais"

        # Apply chosen case
        case_choice = self.case_var.get()
        if case_choice == "upper":
            text = text.upper()
        elif case_choice == "lower":
            text = text.lower()

        logger.info(f"Generating video for text: '{text}' with case: {case_choice}")

        try:
            # Collect valid videos for each character
            valid_chars = []
            for i, char in enumerate(text):
                if char.isalpha() or char.isdigit() or char.isspace():
                    case = "upper" if char.isupper() else "lower"
                    if char.isspace():
                        valid_chars.append((i, None))
                    else:
                        video_path = self.get_video_path(char.lower(), case)
                        if video_path.exists():
                            valid_chars.append((i, str(video_path)))
                        else:
                            raise FileNotFoundError(f"No video found for character '{char}'")
                else:
                    raise ValueError(f"Unsupported character '{char}' in text")

            if not valid_chars:
                raise ValueError("No valid characters to process")

            # Base character size calculation
            base_char_size = 300
            char_spacing = int(base_char_size * -0.7)  # Increased overlap for closer letters
            word_spacing = int(base_char_size * 0.0)   # Reduced space between words

            # Calculate total width considering individual character widths
            total_width = 0
            char_positions = []
            current_x = 0
            last_was_space = False

            for i, (char_index, path) in enumerate(valid_chars):
                if path is None:  # Space character
                    if i < len(valid_chars) - 1:
                        current_x += word_spacing
                        last_was_space = True
                    # Add a placeholder to keep indices aligned
                    char_positions.append(None)
                else:
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
                char_spacing = int(char_spacing * scale_factor)
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
            for _, path in valid_chars:
                if path is not None:
                    cmd.extend(["-i", path])

            # Construct the complex filter
            filter_parts = []
            filter_parts.append(f"color=black:s={self.VIDEO_WIDTH}x{self.VIDEO_HEIGHT}:d={self.VIDEO_DURATION}:r={self.FPS}[bg];")

            # Initialize the overlay chain
            current = "bg"
            input_index = 0

            for i, ((char_index, path), position) in enumerate(zip(valid_chars, char_positions)):
                if path is not None and position is not None:
                    rel_x, char_width = position
                    x_pos = x_offset + rel_x
                    y_pos = (self.VIDEO_HEIGHT - base_char_size) // 2

                    # Scale and position each character
                    filter_parts.append(
                        f"[{input_index}:v]scale={base_char_size}:{base_char_size},setsar=1,format=gbrp[s{char_index}];"
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

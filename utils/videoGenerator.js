// utils/videoGenerator.js
import { createFFmpeg, fetchFile } from '@ffmpeg/ffmpeg';
import { v4 as uuidv4 } from 'uuid';

const ffmpeg = createFFmpeg({ log: true });

export async function loadFFmpeg() {
  if (!ffmpeg.isLoaded()) {
    await ffmpeg.load();
  }
}

export function getVideoPath(char, caseVar) {
  const caseFolder = caseVar === 'upper' ? 'UPPER_CASE' : 'LOWER_CASE';
  const charFile = caseVar === 'upper' ? `${char.toUpperCase()}.mp4` : `${char.toLowerCase()}.mp4`;
  return `public/Source/${caseFolder}/${charFile}`;
}

export async function createVideo({ textInput, caseVar, charSizeVar, charSpacingVar }) {
  await loadFFmpeg();

  const text = textInput.trim() || 'SampleText';
  let processedText = text;

  if (caseVar === 'upper') {
    processedText = text.toUpperCase();
  } else if (caseVar === 'lower') {
    processedText = text.toLowerCase();
  }

  try {
    // Create temporary files in FFmpeg's virtual filesystem
    const videoBlobs = [];
    const inputFiles = [];

    // Fetch and write video files to FFmpeg's filesystem
    for (let i = 0; i < processedText.length; i++) {
      const char = processedText[i];
      
      if (char === ' ') {
        const response = await fetch('/Source/blank.mp4');
        if (!response.ok) throw new Error('Silent video not found');
        const blob = await response.blob();
        const arrayBuffer = await blob.arrayBuffer();
        const inputFileName = `input_${i}.mp4`;
        ffmpeg.FS('writeFile', inputFileName, new Uint8Array(arrayBuffer));
        inputFiles.push(inputFileName);
      } else if (/[a-zA-Z0-9]/.test(char)) {
        const caseType = char === char.toUpperCase() ? 'UPPER_CASE' : 'LOWER_CASE';
        const videoPath = `/Source/${caseType}/${char.toLowerCase()}.mp4`;
        
        const response = await fetch(videoPath);
        if (!response.ok) throw new Error(`Video for character "${char}" not found`);
        const blob = await response.blob();
        const arrayBuffer = await blob.arrayBuffer();
        const inputFileName = `input_${i}.mp4`;
        ffmpeg.FS('writeFile', inputFileName, new Uint8Array(arrayBuffer));
        inputFiles.push(inputFileName);
      } else {
        throw new Error(`Invalid character: ${char}`);
      }
    }

    // Create filter complex command
    let filterComplex = `color=black:s=1920x1080:d=10:r=25[bg];`;
    let current = 'bg';

    // Add each character to the filter complex
    for (let i = 0; i < inputFiles.length; i++) {
      if (processedText[i] !== ' ') {
        const char = processedText[i];
        const verticalOffset = letterOffsets[char] || 0;
        const y = (1080 - charSizeVar) / 2 + verticalOffset * (charSizeVar / 300);
        const charSize = char === char.toUpperCase() ? charSizeVar * 1.2 : charSizeVar;

        filterComplex += `[${i}:v]scale=${charSize}:${charSize},setsar=1,format=gbrp[s${i}];`;
        filterComplex += `color=black@0:s=1920x1080:d=10[tmp${i}];`;
        filterComplex += `[tmp${i}][s${i}]overlay=x=${x_positions[i]}:y=${y}:format=auto[overlay${i}];`;
        filterComplex += `[${current}][overlay${i}]blend=all_mode='screen':shortest=1[blend${i}];`;
        current = `blend${i}`;
      }
    }

    // Write filter complex command
    await ffmpeg.exec([
      '-filter_complex', filterComplex,
      '-map', `[${current}]`,
      '-c:v', 'libx264',
      '-preset', 'medium',
      '-crf', '18',
      '-r', '25',
      '-t', '10',
      '-pix_fmt', 'yuv420p',
      'output.mp4'
    ]);

    // Read the output file
    const data = ffmpeg.FS('readFile', 'output.mp4');

    // Clean up temporary files
    inputFiles.forEach(file => {
      try {
        ffmpeg.FS('unlink', file);
      } catch (e) {
        console.warn(`Failed to clean up file ${file}:`, e);
      }
    });
    ffmpeg.FS('unlink', 'output.mp4');

    // Create blob and URL
    const blob = new Blob([data.buffer], { type: 'video/mp4' });
    const url = URL.createObjectURL(blob);
    const filename = `generated_${uuidv4()}.mp4`;

    return { url, filename };
  } catch (error) {
    console.error('Video generation error:', error);
    throw error;
  }
}

// Add letter offsets constant
const letterOffsets = {
  // Uppercase letters
  'A': -50, 'B': -50, 'C': -50, 'D': -50, 'E': -50, 'F': -50, 'G': -50,
  'H': -50, 'I': -50, 'J': -50, 'K': -50, 'L': -50, 'M': -50, 'N': -50,
  'O': -50, 'P': -50, 'Q': -50, 'R': -50, 'S': -50, 'T': -50, 'U': -50,
  'V': -50, 'W': -50, 'X': -50, 'Y': -50, 'Z': -50,
  // Lowercase letters
  'a': 0, 'b': 0, 'c': 0, 'd': -10, 'e': 0, 'f': -10, 'g': 10,
  'h': 0, 'i': -10, 'j': -8, 'k': -10, 'l': -8, 'm': 0, 'n': 0,
  'o': 0, 'p': 10, 'q': 10, 'r': 0, 's': 0, 't': -8, 'u': 0,
  'v': -8, 'w': -8, 'x': 0, 'y': 15, 'z': 10,
  // Numbers
  '0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0,
  '7': 0, '8': 0, '9': 0
};

function calculateXPositions(text, charSizeVar, charSpacingVar) {
  const positions = [];
  let totalWidth = 0;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === ' ') {
      positions.push(totalWidth);
      totalWidth += 20; // space width
    } else {
      const charSize = char === char.toUpperCase() ? charSizeVar * 1.2 : charSizeVar;
      positions.push(totalWidth);
      totalWidth += charSize + (charSizeVar * charSpacingVar);
    }
  }

  // Center the text
  const xOffset = (1920 - totalWidth) / 2;
  return positions.map(x => x + xOffset);
}

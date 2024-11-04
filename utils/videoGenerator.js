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

  const validChars = [];
  for (const char of processedText) {
    if (/[a-zA-Z0-9 ]/.test(char)) {
      if (char !== ' ') {
        const videoPath = getVideoPath(char, caseVar);
        validChars.push(videoPath);
      } else {
        validChars.push('space');
      }
    } else {
      throw new Error(`Unsupported character: ${char}`);
    }
  }

  // Write input videos to FFmpeg FS
  let inputIndex = 0;
  const inputFiles = [];

  for (const path of validChars) {
    if (path !== 'space') {
      const response = await fetch(path);
      const data = await response.arrayBuffer();
      ffmpeg.FS('writeFile', `char_${inputIndex}.mp4`, new Uint8Array(data));
      inputFiles.push(`char_${inputIndex}.mp4`);
      inputIndex++;
    } else {
      // Handle space by using a blank video or inserting a delay
      // For simplicity, using a blank video segment
      // You can create a blank.mp4 and use it here
      const response = await fetch('/Source/blank.mp4');
      const data = await response.arrayBuffer();
      ffmpeg.FS('writeFile', `blank_${inputIndex}.mp4`, new Uint8Array(data));
      inputFiles.push(`blank_${inputIndex}.mp4`);
      inputIndex++;
    }
  }

  // Concatenate videos
  let concatList = '';
  inputFiles.forEach((file, idx) => {
    concatList += `file '${file}'\n`;
  });

  ffmpeg.FS('writeFile', 'concat_list.txt', new TextEncoder().encode(concatList));

  await ffmpeg.run('-f', 'concat', '-safe', '0', '-i', 'concat_list.txt', '-c', 'copy', 'output.mp4');

  const data = ffmpeg.FS('readFile', 'output.mp4');

  const blob = new Blob([data.buffer], { type: 'video/mp4' });
  const url = URL.createObjectURL(blob);
  const filename = `generated_${uuidv4()}.mp4`;

  return { url, filename };
}

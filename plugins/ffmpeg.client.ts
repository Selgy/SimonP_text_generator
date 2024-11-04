// plugins/ffmpeg.client.ts
import { defineNuxtPlugin } from '#app';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { toBlobURL } from '@ffmpeg/util';

export default defineNuxtPlugin(async (nuxtApp) => {
  const ffmpeg = new FFmpeg();
  let loaded = false;

  const load = async () => {
    if (!loaded) {
      try {
        // Use the core-mt package for multi-threading support
        const baseURL = 'https://unpkg.com/@ffmpeg/core-mt@0.12.6/dist/esm';
        const [coreURL, wasmURL, workerURL] = await Promise.all([
          toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
          toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
          toBlobURL(`${baseURL}/ffmpeg-core.worker.js`, 'text/javascript'),
        ]);
        await ffmpeg.load({ coreURL, wasmURL, workerURL });
        loaded = true;
        console.log('FFmpeg loaded successfully from CDN');
      } catch (error) {
        console.error('Error loading FFmpeg:', error);
        throw error;
      }
    }
    return ffmpeg;
  };

  const fetchFile = async (file: string) => {
    const response = await fetch(file);
    const data = await response.arrayBuffer();
    return new Uint8Array(data);
  };

  return {
    provide: {
      ffmpeg: {
        instance: ffmpeg,
        load,
        loaded: () => loaded,
        fetchFile,
      },
    },
  };
});

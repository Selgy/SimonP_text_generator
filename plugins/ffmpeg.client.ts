// plugins/ffmpeg.client.ts
import { defineNuxtPlugin } from '#app';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { toBlobURL, fetchFile } from '@ffmpeg/util';

export default defineNuxtPlugin(async (nuxtApp) => {
  const ffmpeg = new FFmpeg();
  let loaded = false;

  const load = async () => {
    if (!loaded) {
      try {
        const baseURL = 'https://unpkg.com/@ffmpeg/core-mt@0.12.6/dist/esm';
        await ffmpeg.load({
          coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
          wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
          workerURL: await toBlobURL(`${baseURL}/ffmpeg-core.worker.js`, 'text/javascript'),
        });
        loaded = true;
        console.log('FFmpeg loaded successfully from CDN');
      } catch (error) {
        console.error('Error loading FFmpeg:', error);
        throw error;
      }
    }
    return ffmpeg;
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

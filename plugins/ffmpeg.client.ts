// plugins/ffmpeg.client.ts
import { defineNuxtPlugin } from '#app'
import { FFmpeg } from '@ffmpeg/ffmpeg'
import { toBlobURL } from '@ffmpeg/util'

export default defineNuxtPlugin(async (nuxtApp) => {
  const ffmpeg = new FFmpeg()
  let loaded = false

  const load = async () => {
    if (!loaded) {
      try {
        // Using ESM instead of UMD for Vite
        const baseURL = 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm'
        await ffmpeg.load({
          coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
          wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
          workerURL: await toBlobURL(`${baseURL}/ffmpeg-core.worker.js`, 'text/javascript'),
        })
        loaded = true
        console.log('FFmpeg loaded successfully from CDN')
      } catch (error) {
        console.error('Error loading FFmpeg:', error)
        throw error
      }
    }
    return ffmpeg
  }

  const fetchFile = async (file) => {
    const response = await fetch(file)
    const data = await response.arrayBuffer()
    return new Uint8Array(data)
  }

  return {
    provide: {
      ffmpeg: {
        instance: ffmpeg,
        load,
        loaded: () => loaded,
        fetchFile,
      },
    },
  }
})
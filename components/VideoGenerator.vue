<template>
  <div class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-2">Video Text Generator</h1>
        <p class="text-gray-600">Create stunning text animations with ease</p>
      </div>

      <!-- Main Content -->
      <div class="max-w-4xl mx-auto">
        <!-- Controls Card -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
          <form @submit.prevent="generateVideoHandler" class="space-y-6">
            <!-- Text Input -->
            <div>
              <label 
                for="text_input" 
                class="block text-sm font-medium text-gray-700 mb-2"
              >
                Enter Text
              </label>
              <input
                type="text"
                id="text_input"
                v-model="text"
                @input="updatePreview"
                class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your text here"
                required
              />
            </div>

            <!-- Case Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Text Case</label>
              <div class="flex space-x-4">
                <label class="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    v-model="caseVar"
                    value="upper"
                    @change="updatePreview"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span class="ml-2 text-gray-700">Uppercase</span>
                </label>
                <label class="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    v-model="caseVar"
                    value="lower"
                    @change="updatePreview"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span class="ml-2 text-gray-700">Lowercase</span>
                </label>
                <label class="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    v-model="caseVar"
                    value="mixed"
                    @change="updatePreview"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span class="ml-2 text-gray-700">Mixed Case</span>
                </label>
              </div>
            </div>

            <!-- Character Size -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Character Size: {{ charSizeVar }}
              </label>
              <input
                type="range"
                v-model.number="charSizeVar"
                @input="updatePreview"
                min="50"
                max="400"
                step="10"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <!-- Character Spacing -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Character Spacing: {{ charSpacingVar }}
              </label>
              <input
                type="range"
                v-model.number="charSpacingVar"
                @input="updatePreview"
                min="-1"
                max="0"
                step="0.05"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <!-- Space Width -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Space Width: {{ spaceWidthVar ? spaceWidthVar.toFixed(2) : '0.00' }}
              </label>
              <input
                type="range"
                v-model.number="spaceWidthVar"
                @input="updatePreview"
                min="-10"
                max="10"
                step="0.05"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <!-- Video Duration -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Video Duration: {{ videoDurationVar }} seconds
              </label>
              <input
                type="range"
                v-model.number="videoDurationVar"
                @input="updatePreview"
                min="1"
                max="15"
                step="1"
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <!-- Preview -->
            <div>
              <h3 class="text-lg font-medium text-gray-700 mb-2">Preview</h3>
              <div class="preview-container mb-8">
                <canvas 
                  ref="previewCanvas"
                  class="w-full h-full hidden"
                ></canvas>
                <img 
                  v-if="previewUrl" 
                  :src="previewUrl" 
                  alt="Preview" 
                  class="w-full h-full object-contain bg-black rounded-lg"
                />
                <div 
                  v-else 
                  class="w-full h-64 flex items-center justify-center bg-black text-white rounded-lg"
                >
                  {{ previewLoaded ? 'Enter text to see preview' : 'Loading preview...' }}
                </div>
              </div>
              
              <!-- Error Message Container -->
              <div 
                v-if="errorMessage" 
                class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md"
              >
                <p>{{ errorMessage }}</p>
              </div>
            </div>

            <!-- Progress Bar -->
            <div v-if="generating" class="space-y-2">
              <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-blue-600 transition-all duration-300" 
                  :style="{ width: `${progress}%` }"
                ></div>
              </div>
              <p class="text-sm text-gray-600">{{ progressMessage }}</p>
            </div>

            <!-- Generate Button -->
            <div class="flex justify-end mt-6">
              <button
                type="submit"
                class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                :disabled="loading || generating"
              >
                <span v-if="!generating">Generate Video</span>
                <span v-if="generating" class="flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    ></circle>
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Generating...
                </span>
              </button>
            </div>
          </form>
        </div>

        <!-- Video Container -->
        <div ref="videoContainer" class="video-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick, onUnmounted } from 'vue'
import { useNuxtApp } from '#app'
import { FFmpeg } from '@ffmpeg/ffmpeg';

// Constants for video parameters
const VIDEO_WIDTH = 1920
const VIDEO_HEIGHT = 1080
const DEFAULT_CHAR_SIZE = 300
const FPS = "25" // Frames per second

// Reactive variables
const text = ref('Sample text')
const caseVar = ref('mixed')
const charSizeVar = ref(300)
const charSpacingVar = ref(-0.8)
const spaceWidthVar = ref(0.1)
const previewUrl = ref('')
const previewCanvas = ref(null)
const previewCtx = ref(null)
const previewImages = ref({})
const previewLoaded = ref(false)
const loading = ref(false)
const generating = ref(false)
const errorMessage = ref('')
const progress = ref(0)
const progressMessage = ref('')
const videoUrl = ref(null) // Initialize as null
const isFFmpegLoaded = ref(false)
const ffmpeg = ref(null);

// Add ref for video container
const videoContainer = ref(null)
const error = ref(null)

// Letter offsets similar to Python implementation
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
}

// Letter spacing offsets
const letterSpacingOffsets = {
  // Uppercase letters
  'A': [-4, -4], 'B': [-4, -4], 'C': [-4, -4], 'D': [-4, -4], 'E': [-4, -4],
  'F': [-4, -4], 'G': [-4, -4], 'H': [-4, -4], 'I': [-4, -4], 'J': [-4, -4],
  'K': [-4, -4], 'L': [-4, -4], 'M': [4, 4], 'N': [-4, -4], 'O': [-4, -4],
  'P': [-4, -4], 'Q': [-4, -4], 'R': [-4, -4], 'S': [-9, -9], 'T': [-4, -4],
  'U': [-4, -4], 'V': [-4, -4], 'W': [-4, -4], 'X': [-4, -4], 'Y': [-4, -4],
  'Z': [-4, -4],
  // Lowercase letters
  'a': [0, 0], 'b': [0, 0], 'c': [0, 0], 'd': [0, 0], 'e': [0, 0],
  'f': [0, 0], 'g': [0, 0], 'h': [0, 0], 'i': [0, 0], 'j': [-10, -10],
  'k': [0, 0], 'l': [-10, -10], 'm': [4, 4], 'n': [0, 0], 'o': [0, 0],
  'p': [0, 0], 'q': [0, 0], 'r': [0, 0], 's': [0, 0], 't': [-4, -4],
  'u': [0, 0], 'v': [0, 0], 'w': [16, 10], 'x': [0, 0], 'y': [0, 0],
  'z': [0, 0],
  // Numbers and space
  '0': [0, 0], '1': [0, 0], '2': [0, 0], '3': [0, 0], '4': [0, 0],
  '5': [0, 0], '6': [0, 0], '7': [0, 0], '8': [0, 0], '9': [0, 0],
  ' ': [0, 0]
}

// Add new reactive variable (after other ref declarations)
const videoDurationVar = ref(5) // Default 7 seconds

// Add missing computed property for formattedText
const formattedText = computed(() => {
  if (caseVar.value === 'upper') return text.value.toUpperCase()
  if (caseVar.value === 'lower') return text.value.toLowerCase()
  return text.value
})

// Initialize FFmpeg and fetchFile from the plugin
const { $ffmpeg } = useNuxtApp()

// Initialize FFmpeg when component mounts
onMounted(async () => {
  if (process.client) {
    try {
      const { FFmpeg } = await import('@ffmpeg/ffmpeg');
      const { toBlobURL } = await import('@ffmpeg/util');
      
      ffmpeg.value = new FFmpeg();
      await ffmpeg.value.load({
        coreURL: await toBlobURL(
          'https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm/ffmpeg-core.js',
          'text/javascript'
        ),
        wasmURL: await toBlobURL(
          'https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm/ffmpeg-core.wasm',
          'application/wasm'
        )
      });
      
      isFFmpegLoaded.value = true;
      console.log('FFmpeg loaded successfully');
      
      // Load preview images
      await loadPreviewImages();
      await updatePreview();
    } catch (error) {
      console.error('Error loading FFmpeg:', error);
      errorMessage.value = 'Failed to load FFmpeg. Please check your setup and refresh.';
      isFFmpegLoaded.value = false;
    } finally {
      loading.value = false;
      progressMessage.value = '';
    }
  }
});

// Function to load preview images
const loadPreviewImages = async () => {
  const cases = ['upper', 'lower']
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
  
  for (const caseType of cases) {
    for (const char of chars) {
      const imgPath = `/PreviewImages/${caseType}_${char}.png`
      try {
        const response = await fetch(imgPath)
        if (response.ok) {
          const blob = await response.blob()
          const img = new Image()
          img.src = URL.createObjectURL(blob)
          await new Promise(resolve => { img.onload = resolve })
          previewImages.value[`${caseType}_${char}`] = img
        }
      } catch (error) {
        console.error(`Failed to load preview image for ${char}:`, error)
      }
    }
  }
  previewLoaded.value = true
}

// Function to update preview image
const updatePreview = async () => {
  if (!text.value.trim()) {
    // Clear previous preview
    previewUrl.value = ''
    return
  }

  try {
    loading.value = true
    errorMessage.value = ''

    // Clear any existing preview URL if using Blob URLs (not necessary for data URLs)
    // If you later switch to Blob URLs for preview, ensure to revoke the previous one
    // Example:
    // if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    //   URL.revokeObjectURL(previewUrl.value)
    // }

    // Initialize canvas if not already done
    if (!previewCtx.value && previewCanvas.value) {
      previewCanvas.value.width = VIDEO_WIDTH
      previewCanvas.value.height = VIDEO_HEIGHT
      previewCtx.value = previewCanvas.value.getContext('2d')
    }

    // Clear canvas
    previewCtx.value.clearRect(0, 0, VIDEO_WIDTH, VIDEO_HEIGHT)
    previewCtx.value.fillStyle = 'black'
    previewCtx.value.fillRect(0, 0, VIDEO_WIDTH, VIDEO_HEIGHT)

    // Format text based on case selection
    let formattedText = text.value
    if (caseVar.value === 'upper') formattedText = formattedText.toUpperCase()
    if (caseVar.value === 'lower') formattedText = formattedText.toLowerCase()

    // Calculate positions and sizes
    const charPositions = []
    let totalWidth = 0

    for (let i = 0; i < formattedText.length; i++) {
      const char = formattedText[i]
      if (char.match(/[a-zA-Z0-9]/)) {
        const case_type = char === char.toUpperCase() ? 'upper' : 'lower'
        const [leftOffset, rightOffset] = letterSpacingOffsets[char] || [0, 0]
        
        totalWidth += leftOffset * (charSizeVar.value / DEFAULT_CHAR_SIZE)
        
        if (i > 0 && case_type === 'upper') {
          totalWidth += charSizeVar.value * 0.2
        }
        
        const charSize = case_type === 'upper' ? charSizeVar.value * 1.2 : charSizeVar.value
        charPositions.push([totalWidth, charSize])
        
        totalWidth += charSize + (rightOffset * (charSizeVar.value / DEFAULT_CHAR_SIZE))
        
        if (i < formattedText.length - 1) {
          totalWidth += charSizeVar.value * charSpacingVar.value
        }
      } else if (char === ' ') {
        charPositions.push(null)
        // Use spaceWidthVar for space width control
        totalWidth += charSizeVar.value * spaceWidthVar.value
      }
    }

    // Center text
    const xOffset = (VIDEO_WIDTH - totalWidth) / 2
    const yOffset = (VIDEO_HEIGHT - charSizeVar.value) / 2

    // Draw characters
    for (let i = 0; i < formattedText.length; i++) {
      const char = formattedText[i]
      const position = charPositions[i]
      
      if (position) {
        const [x, size] = position
        const case_type = char === char.toUpperCase() ? 'upper' : 'lower'
        const img = previewImages.value[`${case_type}_${char.toLowerCase()}`]
        
        if (img) {
          const verticalOffset = letterOffsets[char] || 0
          const y = yOffset + verticalOffset * (charSizeVar.value / DEFAULT_CHAR_SIZE)
          
          previewCtx.value.globalCompositeOperation = 'screen'
          previewCtx.value.drawImage(img, xOffset + x, y, size, size)
        }
      }
    }

    // Update preview URL
    previewUrl.value = previewCanvas.value.toDataURL('image/png')
  } catch (error) {
    console.error('Preview error:', error)
    errorMessage.value = `Failed to load preview image. Please ensure "${text.value}" has a corresponding preview image.`
    previewUrl.value = '' // Clear preview on error
  } finally {
    loading.value = false
  }
}

// Add this helper function at the top of your component
const verifyVideoFile = async (buffer) => {
  // Check if buffer is valid
  if (!(buffer instanceof ArrayBuffer) || buffer.byteLength === 0) {
    throw new Error('Invalid video file buffer');
  }
  return new Uint8Array(buffer);
};

// Update the video generation part
const generateVideoHandler = async () => {
  if (!text.value.trim()) {
    errorMessage.value = 'Please enter some text'
    return
  }

  if (!isFFmpegLoaded.value || !ffmpeg.value) {
    errorMessage.value = 'FFmpeg is still loading. Please wait a moment.'
    return
  }

  generating.value = true
  progress.value = 0
  progressMessage.value = 'Preparing to generate video...'
  errorMessage.value = ''

  const videoData = []
  try {
    console.log('Starting video generation...')
    const characters = formattedText.value.split('')
    const inputFiles = []
    let currentIndex = 0

    // Fetch and verify all video files first
    for (let i = 0; i < characters.length; i++) {
      const char = characters[i]
      if (char === ' ') {
        // Skip spaces - don't try to load a video for them
        continue
      }

      try {
        const caseType = char === char.toUpperCase() ? 'UPPER_CASE' : 'LOWER_CASE'
        const videoPath = `/Source/${caseType}/${char.toLowerCase()}.mp4`
        const response = await fetch(videoPath)
        if (!response.ok) throw new Error(`Video not found at ${videoPath}`)

        const buffer = await response.arrayBuffer()
        const verifiedData = await verifyVideoFile(buffer)
        
        // Use the actual character and case in the filename
        const caseType2 = char === char.toUpperCase() ? 'upper' : 'lower'
        const fileName = `${caseType2}_${char.toLowerCase()}_${currentIndex}.mp4`
        
        inputFiles.push({
          name: fileName,
          data: verifiedData,
          char: char,
          index: currentIndex
        })
        videoData.push(fileName)
        currentIndex++

        console.log(`Processed ${videoPath} -> ${fileName}`)
        progress.value = Math.round(((i + 1) / characters.length) * 50)
        progressMessage.value = `Loading videos: ${i + 1}/${characters.length}`
      } catch (error) {
        throw new Error(`Error processing character "${char}" at position ${i}: ${error.message}`)
      }
    }

    // Write files to FFmpeg's virtual filesystem
    for (const file of inputFiles) {
      try {
        console.log(`Writing file ${file.name} for character "${file.char}"...`)
        await ffmpeg.value.writeFile(file.name, file.data)
      } catch (error) {
        throw new Error(`Error writing file ${file.name} for character "${file.char}": ${error.message}`)
      }
    }

    // Build FFmpeg command
    let filterComplex = `color=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:d=${videoDurationVar.value}:r=${FPS}[bg];`
    let current = 'bg'

    const positions = calculateCharacterPositions(formattedText.value)
    let videoIndex = 0
    
    for (let i = 0; i < characters.length; i++) {
      if (characters[i] !== ' ') {
        const pos = positions[i]
        if (pos) {
          const [x, width] = pos
          const char = characters[i]
          const verticalOffset = letterOffsets[char] || 0
          const y = (VIDEO_HEIGHT - charSizeVar.value) / 2 + 
                   verticalOffset * (charSizeVar.value / DEFAULT_CHAR_SIZE)

          // Create temporary black background for each character
          filterComplex += `[${videoIndex}:v]scale=${width}:${width},setsar=1,format=gbrp[s${videoIndex}];`
          filterComplex += `color=black@0:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:d=${videoDurationVar.value}[tmp${videoIndex}];`
          
          // Overlay character on black background
          filterComplex += `[tmp${videoIndex}][s${videoIndex}]overlay=x=${x}:y=${y}:format=auto[overlay${videoIndex}];`
          
          // Blend with screen mode (matching Python script)
          filterComplex += `[${current}][overlay${videoIndex}]blend=all_mode='screen':shortest=1[blend${videoIndex}];`
          
          current = `blend${videoIndex}`
          videoIndex++
        }
      }
    }

    // Remove trailing semicolon
    filterComplex = filterComplex.replace(/;$/, '')

    // Build FFmpeg command with updated parameters
    const command = [
      '-hwaccel', 'auto',     // Enable hardware acceleration if available
      ...videoData.flatMap(file => ['-i', file]),
      '-filter_complex', filterComplex,
      '-map', `[${current}]`,
      '-c:v', 'libx264',
      '-preset', 'ultrafast',
      '-tune', 'fastdecode',
      '-crf', '23',
      '-r', FPS,
      '-t', videoDurationVar.value.toString(),
      '-pix_fmt', 'yuv420p',
      '-threads', 'auto',
      'output.mp4'
    ]

    console.log('Executing FFmpeg command:', command)
    console.log('Filter complex:', filterComplex)
    await ffmpeg.value.exec(command)

    // Verify output file exists and has content
    const outputData = await ffmpeg.value.readFile('output.mp4')
    if (!outputData || outputData.length === 0) {
      throw new Error('Generated video file is empty or invalid')
    }

    try {
      const videoBlob = new Blob([outputData.buffer], { type: 'video/mp4' })
      const downloadUrl = URL.createObjectURL(videoBlob)

      // Create download link
      const downloadLink = document.createElement('a')
      downloadLink.href = downloadUrl
      downloadLink.download = 'generated-video.mp4'
      downloadLink.textContent = 'Download Video'
      downloadLink.className = 'download-button'

      // Create video element
      const videoElement = document.createElement('video')
      videoElement.src = downloadUrl
      videoElement.controls = true
      videoElement.autoplay = false
      videoElement.className = 'preview-video'

      // Clear previous content and append new elements
      if (videoContainer.value) {
        videoContainer.value.innerHTML = ''
        videoContainer.value.appendChild(videoElement)
        videoContainer.value.appendChild(downloadLink)

        // Clean up old URL if exists
        if (videoUrl.value) {
          URL.revokeObjectURL(videoUrl.value)
        }
        videoUrl.value = downloadUrl

        progress.value = 100
        progressMessage.value = 'Video generation complete!'
      } else {
        throw new Error('Video container not found')
      }
    } catch (error) {
      console.error('Error displaying video:', error)
      progress.value = 0
      progressMessage.value = `Error: ${error.message}`
      throw error
    }
  } catch (error) {
    console.error('Video generation error:', error)
    errorMessage.value = `Failed to generate video: ${error.message}`
  } finally {
    generating.value = false
    // Clean up files
    try {
      for (const file of videoData) {
        await ffmpeg.value.deleteFile(file).catch(console.warn)
      }
      await ffmpeg.value.deleteFile('output.mp4').catch(console.warn)
    } catch (e) {
      console.warn('Error during cleanup:', e)
    }
  }
}

// Add helper function for character position calculation
const calculateCharacterPositions = (text) => {
  const positions = []
  let totalWidth = 0

  for (let i = 0; i < text.length; i++) {
    const char = text[i]
    if (char.match(/[a-zA-Z0-9]/)) {
      const case_type = char === char.toUpperCase() ? 'upper' : 'lower'
      const [leftOffset, rightOffset] = letterSpacingOffsets[char] || [0, 0]
      
      totalWidth += leftOffset * (charSizeVar.value / DEFAULT_CHAR_SIZE)
      
      if (i > 0 && case_type === 'upper') {
        totalWidth += charSizeVar.value * 0.2
      }
      
      const charSize = case_type === 'upper' ? charSizeVar.value * 1.2 : charSizeVar.value
      positions.push([totalWidth, charSize])
      
      totalWidth += charSize + (rightOffset * (charSizeVar.value / DEFAULT_CHAR_SIZE))
      
      if (i < text.length - 1) {
        totalWidth += charSizeVar.value * charSpacingVar.value
      }
    } else if (char === ' ') {
      positions.push(null)
      // Use spaceWidthVar for space width control
      totalWidth += charSizeVar.value * spaceWidthVar.value
    }
  }

  const xOffset = (VIDEO_WIDTH - totalWidth) / 2
  return positions.map(pos => pos ? [pos[0] + xOffset, pos[1]] : null)
}

// Watch for changes to trigger preview update
watch([text, caseVar, charSizeVar, charSpacingVar, videoDurationVar, spaceWidthVar], () => {
  if (previewLoaded.value) {
    updatePreview()
  }
})

// Clean up URLs on unmount
onUnmounted(() => {
  if (videoContainer.value) {
    const video = videoContainer.value.querySelector('video')
    if (video && video.src) {
      URL.revokeObjectURL(video.src)
    }
    const link = videoContainer.value.querySelector('a')
    if (link && link.href) {
      URL.revokeObjectURL(link.href)
    }
  }
})
</script>

<style scoped>
.video-container {
  width: 100%;
  min-height: 200px;
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.preview-video {
  max-width: 100%;
  height: auto;
}

.download-button {
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  margin-top: 1rem;
}

.error-message {
  color: #ff4444;
  margin: 1rem 0;
  padding: 0.5rem;
  border: 1px solid #ff4444;
  border-radius: 4px;
  background: #fff5f5;
}
</style>

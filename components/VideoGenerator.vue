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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useNuxtApp } from '#app'
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { toBlobURL } from '@ffmpeg/util';

// Constants for video parameters
const VIDEO_WIDTH = 1920
const VIDEO_HEIGHT = 1080
const DEFAULT_CHAR_SIZE = 300

// Reactive variables
const text = ref('Sample Text')
const caseVar = ref('mixed')
const charSizeVar = ref(300)
const charSpacingVar = ref(-0.8)
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
const ffmpegInstance = ref(null)

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
  'P': [-4, -4], 'Q': [-4, -4], 'R': [-4, -4], 'S': [-4, -4], 'T': [-4, -4],
  'U': [-4, -4], 'V': [-4, -4], 'W': [-4, -4], 'X': [-4, -4], 'Y': [-4, -4],
  'Z': [-4, -4],
  // Lowercase letters
  'a': [0, 0], 'b': [0, 0], 'c': [0, 0], 'd': [0, 0], 'e': [0, 0],
  'f': [0, 0], 'g': [0, 0], 'h': [0, 0], 'i': [-10, -10], 'j': [-10, -10],
  'k': [0, 0], 'l': [-10, -10], 'm': [4, 4], 'n': [0, 0], 'o': [0, 0],
  'p': [0, 0], 'q': [0, 0], 'r': [0, 0], 's': [0, 0], 't': [-10, -10],
  'u': [0, 0], 'v': [0, 0], 'w': [16, 10], 'x': [0, 0], 'y': [0, 0],
  'z': [0, 0],
  // Numbers and space
  '0': [0, 0], '1': [0, 0], '2': [0, 0], '3': [0, 0], '4': [0, 0],
  '5': [0, 0], '6': [0, 0], '7': [0, 0], '8': [0, 0], '9': [0, 0],
  ' ': [0, 0]
}

// Initialize FFmpeg and fetchFile from the plugin
const { $ffmpeg } = useNuxtApp()

// Initialize FFmpeg when component mounts
onMounted(async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    if (!$ffmpeg.loaded()) {
      progressMessage.value = 'Loading FFmpeg...'
      await $ffmpeg.load()
    }
    isFFmpegLoaded.value = true
    ffmpegInstance.value = $ffmpeg.instance
    console.log('FFmpeg loaded successfully')
    
    // Load preview images
    await loadPreviewImages()

    // Generate initial preview
    await updatePreview()
  } catch (error) {
    console.error('Error loading FFmpeg:', error)
    errorMessage.value = 'Failed to load FFmpeg. Please check your internet connection and refresh.'
    isFFmpegLoaded.value = false
  } finally {
    loading.value = false
    progressMessage.value = ''
  }
})

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
        const [leftOffset, rightOffset] = letterSpacingOffsets[char.toLowerCase()] || [0, 0]
        
        totalWidth += leftOffset
        
        if (i > 0 && case_type === 'upper') {
          totalWidth += charSizeVar.value * 0.2
        }
        
        const charSize = case_type === 'upper' ? charSizeVar.value * 1.2 : charSizeVar.value
        charPositions.push([totalWidth, charSize])
        totalWidth += charSize + rightOffset
        
        if (i < formattedText.length - 1) {
          totalWidth += charSizeVar.value * charSpacingVar.value
        }
      } else if (char === ' ') {
        charPositions.push(null)
        totalWidth += 20 // space width
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

// Function to generate video
const generateVideoHandler = async () => {
  if (!text.value.trim()) {
    errorMessage.value = 'Please enter some text'
    return
  }

  if (!isFFmpegLoaded.value || !ffmpegInstance.value) {
    errorMessage.value = 'FFmpeg is still loading. Please wait a moment.'
    return
  }

  generating.value = true
  progress.value = 0
  progressMessage.value = 'Preparing to generate video...'
  errorMessage.value = ''

  try {
    const ffmpeg = ffmpegInstance.value;
    console.log('Starting video generation...');

    // Format text based on case selection
    const formattedText = caseVar.value === 'upper' 
      ? text.value.toUpperCase()
      : caseVar.value === 'lower' 
        ? text.value.toLowerCase()
        : text.value;

    // Split text into characters and fetch video files
    const characters = formattedText.split('')
    const videoBlobs = []

    // Fetch video files for each character
    for (let i = 0; i < characters.length; i++) {
      const char = characters[i]
      if (char === ' ') {
        // Handle space character
        const response = await fetch('/Source/blank.mp4')
        if (!response.ok) throw new Error('Silent video not found')
        const blob = await response.blob()
        videoBlobs.push(await $ffmpeg.fetchFile(blob))
      } else {
        // Handle regular characters
        const caseType = char === char.toUpperCase() ? 'UPPER_CASE' : 'LOWER_CASE'
        const videoPath = `/Source/${caseType}/${char.toLowerCase()}.mp4`
        
        const response = await fetch(videoPath)
        if (!response.ok) throw new Error(`Video for character "${char}" not found`)
        const blob = await response.blob()
        videoBlobs.push(await $ffmpeg.fetchFile(blob))
      }

      // Update progress
      progress.value = Math.round(((i + 1) / characters.length) * 50)
      progressMessage.value = `Loading videos: ${i + 1}/${characters.length}`
    }

    // Create directory
    await ffmpeg.FS('mkdir', '/tmp');
    console.log('Created /tmp directory');

    // Write video files
    console.log('Writing files to filesystem...');
    try {
      for (let i = 0; i < videoBlobs.length; i++) {
        const data = videoBlobs[i] instanceof Uint8Array 
          ? videoBlobs[i] 
          : new Uint8Array(videoBlobs[i]);
        
        await ffmpeg.FS('writeFile', `/tmp/char_${i}.mp4`, data);
        console.log(`Successfully wrote file /tmp/char_${i}.mp4`);
        
        // Update progress
        progress.value = Math.round(((i + 1) / characters.length) * 50);
        progressMessage.value = `Loading videos: ${i + 1}/${characters.length}`;
      }

      // Create concatenation file list
      console.log('Creating concat file list...');
      const fileList = videoBlobs.map((_, i) => `file '/tmp/char_${i}.mp4'`).join('\n');
      console.log('File list content:', fileList);

      // Write the file list
      await ffmpeg.FS('writeFile', '/tmp/filelist.txt', new TextEncoder().encode(fileList));
      console.log('Successfully wrote filelist.txt');

      // Execute FFmpeg command
      console.log('Executing FFmpeg command...');
      await ffmpeg.exec([
        '-f', 'concat',
        '-safe', '0',
        '-i', '/tmp/filelist.txt',
        '-c', 'copy',
        '-movflags', '+faststart',
        '-y',
        '/tmp/output.mp4'
      ]);
      console.log('FFmpeg command completed successfully');

      // Read the output file
      const outputData = await ffmpeg.FS('readFile', '/tmp/output.mp4');
      console.log('Successfully read output file, size:', outputData.length);

      // Revoke previous video URL if it exists
      if (videoUrl.value) {
        URL.revokeObjectURL(videoUrl.value)
        console.log('Revoked previous video URL')
      }

      // Create blob and URL
      const videoBlob = new Blob([outputData], { type: 'video/mp4' });
      videoUrl.value = URL.createObjectURL(videoBlob);
      console.log('Created new video URL')

    } catch (error) {
      console.error('Video generation error:', error)
      throw error
    } finally {
      // Cleanup temporary video files
      console.log('Cleaning up temporary video files...');
      try {
        const files = [
          '/tmp/filelist.txt',
          '/tmp/output.mp4',
          ...Array.from({length: videoBlobs.length}, (_, i) => `/tmp/char_${i}.mp4`)
        ];
        
        for (const file of files) {
          try {
            await ffmpeg.FS('unlink', file);
            console.log(`Deleted temporary file: ${file}`)
          } catch (e) {
            // Ignore errors if file doesn't exist
            console.warn(`Could not delete ${file}:`, e);
          }
        }
      } catch (e) {
        console.warn('Cleanup warning:', e);
      }
      console.log('Temporary video files cleanup completed')
    }

  } catch (error) {
    console.error('Video generation error:', error)
    errorMessage.value = 'Failed to generate video. Please try again.'
  } finally {
    // Final Cleanup
    try {
      console.log('Finalizing cleanup...');
      const ffmpeg = ffmpegInstance.value;
      
      // Revoke previous video URL if it exists (already handled above)
      // Ensure no residual Blob URLs are left

      console.log('Final cleanup completed')
    } catch (cleanupError) {
      console.error('Error during final cleanup:', cleanupError)
    }
    generating.value = false
  }
}

// Watch for changes to trigger preview update
watch([text, caseVar, charSizeVar, charSpacingVar], () => {
  if (previewLoaded.value) {
    updatePreview()
  }
})
</script>

<style scoped>
/* Add any component-specific styles here */
</style>

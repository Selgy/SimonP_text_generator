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
import { ref, onMounted, watch, computed } from 'vue'
import { useNuxtApp } from '#app'

// Constants for video parameters
const VIDEO_WIDTH = 1920
const VIDEO_HEIGHT = 1080
const DEFAULT_CHAR_SIZE = 300
const VIDEO_DURATION = 10 // Duration in seconds
const FPS = "25" // Frames per second

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
const ffmpeg = ref(null)

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
  loading.value = true
  errorMessage.value = ''

  try {
    // Use the plugin's FFmpeg instance instead of creating a new one
    const { instance, load } = $ffmpeg
    ffmpeg.value = instance
    
    progressMessage.value = 'Loading FFmpeg...'
    await load()
    
    isFFmpegLoaded.value = true
    console.log('FFmpeg loaded successfully')
    
    // Load preview images
    await loadPreviewImages()
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

// Update generateVideoHandler to handle FFmpeg commands correctly
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

  try {
    console.log('Starting video generation...')

    // Split text into characters
    const characters = formattedText.value.split('')
    const videoData = []

    // Fetch all video files first
    for (let i = 0; i < characters.length; i++) {
      const char = characters[i]
      try {
        let response
        if (char === ' ') {
          response = await fetch('/Source/blank.mp4')
          if (!response.ok) throw new Error('Silent video not found')
        } else {
          const caseType = char === char.toUpperCase() ? 'UPPER_CASE' : 'LOWER_CASE'
          const videoPath = `/Source/${caseType}/${char.toLowerCase()}.mp4`
          response = await fetch(videoPath)
          if (!response.ok) throw new Error(`Video for character "${char}" not found`)
        }

        const buffer = await response.arrayBuffer()
        const fileName = `input${i}.mp4`
        await ffmpeg.value.writeFile(fileName, new Uint8Array(buffer))
        videoData.push(fileName)

        progress.value = Math.round(((i + 1) / characters.length) * 50)
        progressMessage.value = `Loading videos: ${i + 1}/${characters.length}`
      } catch (error) {
        throw error
      }
    }

    // Build FFmpeg filter complex command
    let filterComplex = `color=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:d=${VIDEO_DURATION}:r=${FPS}[bg];`
    let current = 'bg'

    // Calculate positions
    const positions = calculateCharacterPositions(formattedText.value)
    
    // Add each character to the filter complex
    for (let i = 0; i < characters.length; i++) {
      if (characters[i] !== ' ') {
        const pos = positions[i]
        if (pos) {
          const [x, width] = pos
          const char = characters[i]
          const verticalOffset = letterOffsets[char] || 0
          const y = (VIDEO_HEIGHT - charSizeVar.value) / 2 + 
                   verticalOffset * (charSizeVar.value / DEFAULT_CHAR_SIZE)

          filterComplex += `[${i}:v]scale=${width}:${width},setsar=1[s${i}];`
          filterComplex += `[${current}][s${i}]overlay=x=${x}:y=${y}:format=auto[v${i}];`
          current = `v${i}`
        }
      }
    }

    // Prepare FFmpeg command
    const command = [
      ...videoData.flatMap(file => ['-i', file]),
      '-filter_complex', filterComplex,
      '-map', `[${current}]`,
      '-c:v', 'libx264',
      '-preset', 'medium',
      '-crf', '23',
      '-t', VIDEO_DURATION.toString(),
      '-pix_fmt', 'yuv420p',
      'output.mp4'
    ]

    // Execute FFmpeg command
    await ffmpeg.value.exec(command)

    // Read the output file
    const data = await ffmpeg.value.readFile('output.mp4')

    // Create video URL
    const videoBlob = new Blob([data.buffer], { type: 'video/mp4' })
    if (videoUrl.value) {
      URL.revokeObjectURL(videoUrl.value)
    }
    videoUrl.value = URL.createObjectURL(videoBlob)

    progress.value = 100
    progressMessage.value = 'Video generation complete!'

  } catch (error) {
    console.error('Video generation error:', error)
    errorMessage.value = `Failed to generate video: ${error.message}`
  } finally {
    generating.value = false
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
      const [leftOffset, rightOffset] = letterSpacingOffsets[char.toLowerCase()] || [0, 0]
      
      totalWidth += leftOffset
      
      if (i > 0 && case_type === 'upper') {
        totalWidth += charSizeVar.value * 0.2
      }
      
      const charSize = case_type === 'upper' ? charSizeVar.value * 1.2 : charSizeVar.value
      positions.push([totalWidth, charSize])
      totalWidth += charSize + rightOffset
      
      if (i < text.length - 1) {
        totalWidth += charSizeVar.value * charSpacingVar.value
      }
    } else if (char === ' ') {
      positions.push(null)
      totalWidth += 20 // space width
    }
  }

  // Center the text
  const xOffset = (VIDEO_WIDTH - totalWidth) / 2
  return positions.map(pos => pos ? [pos[0] + xOffset, pos[1]] : null)
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

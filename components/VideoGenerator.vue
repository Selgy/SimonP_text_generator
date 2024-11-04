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
                <div class="preview-container bg-black rounded-lg overflow-hidden relative">
                  <img 
                    :src="previewUrl" 
                    alt="Preview Image" 
                    class="w-full h-full object-contain"
                  />
                  <div 
                    v-if="loading" 
                    class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50"
                  >
                    <svg
                      class="animate-spin h-8 w-8 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
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
  import { ref, onMounted } from 'vue'
  import { useNuxtApp } from '#app'
  
  // Reactive variables
  const text = ref('Sample Text')
  const caseVar = ref('mixed')
  const charSizeVar = ref(300)
  const charSpacingVar = ref(-0.8)
  const previewUrl = ref('')
  const loading = ref(false)
  const generating = ref(false)
  const errorMessage = ref('')
  const progress = ref(0)
  const progressMessage = ref('')
  const videoUrl = ref('')
  const isFFmpegLoaded = ref(false)
  const ffmpegInstance = ref(null)
  
  // Get FFmpeg from Nuxt plugin
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
  
  // Function to update preview image
  const updatePreview = async () => {
    if (!text.value.trim()) {
      previewUrl.value = ''
      return
    }
  
    try {
      loading.value = true
      errorMessage.value = ''
  
      // Construct the preview image URL based on user input
      const formattedText = caseVar.value === 'upper' 
        ? text.value.toUpperCase()
        : caseVar.value === 'lower' 
          ? text.value.toLowerCase()
          : text.value
  
      // Use absolute path for preview images
      const imageName = formattedText.replace(/\s+/g, '_') + '.png'
      const imagePath = `/PreviewImages/${imageName}`
  
      // Attempt to load the image
      const response = await fetch(imagePath)
      if (!response.ok) {
        throw new Error(`Preview image not found: ${imagePath}`)
      }
  
      const blob = await response.blob()
      previewUrl.value = URL.createObjectURL(blob)
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
      const ffmpeg = ffmpegInstance.value
      const { fetchFile } = $ffmpeg
  
      // Format text based on case selection
      const formattedText = caseVar.value === 'upper' 
        ? text.value.toUpperCase()
        : caseVar.value === 'lower' 
          ? text.value.toLowerCase()
          : text.value
  
      // Split text into characters
      const characters = formattedText.split('')
      
      // Prepare array for video files
      const videoBlobs = []
  
      // Fetch video files for each character
      for (let i = 0; i < characters.length; i++) {
        const char = characters[i]
        
        if (char === ' ') {
          // Handle spaces with silent video
          const silentVideoPath = '/Source/LOWER_CASE/silent.mp4'
          const response = await fetch(silentVideoPath)
          if (!response.ok) throw new Error('Silent video not found')
          const blob = await response.blob()
          videoBlobs.push(await fetchFile(blob))
        } else {
          // Handle regular characters
          const caseType = char === char.toUpperCase() ? 'UPPER_CASE' : 'LOWER_CASE'
          const videoPath = `/Source/${caseType}/${char.toLowerCase()}.mp4`
          
          const response = await fetch(videoPath)
          if (!response.ok) throw new Error(`Video for character "${char}" not found`)
          const blob = await response.blob()
          videoBlobs.push(await fetchFile(blob))
        }
  
        // Update progress
        progress.value = Math.round(((i + 1) / characters.length) * 50)
        progressMessage.value = `Loading videos: ${i + 1}/${characters.length}`
      }
  
      // Write files to FFmpeg virtual filesystem
      for (let i = 0; i < videoBlobs.length; i++) {
        await ffmpeg.FS('writeFile', `char_${i}.mp4`, videoBlobs[i])
      }
  
      // Create concatenation file list
      const fileList = videoBlobs.map((_, i) => `file 'char_${i}.mp4'`).join('\n')
      await ffmpeg.FS('writeFile', 'filelist.txt', fileList)
  
      // Progress update
      progress.value = 70
      progressMessage.value = 'Generating video...'
  
      // Run FFmpeg command to concatenate videos
      await ffmpeg.run(
        '-f', 'concat',
        '-safe', '0',
        '-i', 'filelist.txt',
        '-c', 'copy',
        'output.mp4'
      )
  
      // Read the output file
      progress.value = 90
      progressMessage.value = 'Processing final video...'
      
      const data = await ffmpeg.FS('readFile', 'output.mp4')
      const videoBlob = new Blob([data.buffer], { type: 'video/mp4' })
      videoUrl.value = URL.createObjectURL(videoBlob)
  
      // Trigger download
      const link = document.createElement('a')
      link.href = videoUrl.value
      link.download = `${formattedText.replace(/\s+/g, '_')}.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
  
      progress.value = 100
      progressMessage.value = 'Video generated successfully!'
  
      // Cleanup FFmpeg filesystem
      await ffmpeg.FS('unlink', 'filelist.txt')
      await ffmpeg.FS('unlink', 'output.mp4')
      for (let i = 0; i < videoBlobs.length; i++) {
        await ffmpeg.FS('unlink', `char_${i}.mp4`)
      }
  
    } catch (error) {
      console.error('Video generation error:', error)
      errorMessage.value = `Failed to generate video: ${error.message}`
    } finally {
      generating.value = false
      setTimeout(() => {
        progress.value = 0
        progressMessage.value = ''
      }, 3000)
    }
  }
  </script>
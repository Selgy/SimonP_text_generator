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
                <label for="text_input" class="block text-sm font-medium text-gray-700 mb-2">Enter Text</label>
                <input
                  type="text"
                  id="text_input"
                  v-model="text"
                  @input="updatePreview"
                  class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your text here"
                />
              </div>
  
              <!-- Case Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Text Case</label>
                <div class="flex space-x-4">
                  <label class="flex items-center">
                    <input
                      type="radio"
                      v-model="caseVar"
                      value="upper"
                      @change="updatePreview"
                      class="h-4 w-4 text-blue-600"
                    />
                    <span class="ml-2">Uppercase</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      type="radio"
                      v-model="caseVar"
                      value="lower"
                      @change="updatePreview"
                      class="h-4 w-4 text-blue-600"
                    />
                    <span class="ml-2">Lowercase</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      type="radio"
                      v-model="caseVar"
                      value="mixed"
                      @change="updatePreview"
                      class="h-4 w-4 text-blue-600"
                    />
                    <span class="ml-2">Mixed Case</span>
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
                  <img :src="previewUrl" class="w-full h-full object-contain" alt="Preview" />
                  <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
                    <!-- Loading spinner SVG -->
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
                <div v-if="errorMessage" class="text-red-500 mt-4">
                  <p>{{ errorMessage }}</p>
                </div>
              </div>
  
              <!-- Generate Button -->
              <div class="flex justify-end">
                <button
                  type="submit"
                  class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  :disabled="loading || generating"
                  :class="{ 'opacity-50 cursor-not-allowed': loading || generating }"
                >
                  <span v-if="!generating">Generate Video</span>
                  <span v-else>Generating...</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useNuxtApp } from '#app'; // Import useNuxtApp to access FFmpeg
  
  const text = ref('Sample Text');
  const caseVar = ref('mixed');
  const charSizeVar = ref(300);
  const charSpacingVar = ref(-0.8);
  const previewUrl = ref('');
  const loading = ref(false);
  const generating = ref(false);
  const errorMessage = ref('');
  
  const { $ffmpeg, $fetchFile } = useNuxtApp(); // Access FFmpeg and fetchFile from the plugin
  
  // Function to load FFmpeg
  const loadFFmpeg = async () => {
    if (!$ffmpeg.isLoaded()) {
      loading.value = true;
      try {
        await $ffmpeg.load();
        console.log('FFmpeg loaded successfully');
      } catch (error) {
        console.error('Error loading FFmpeg:', error);
        errorMessage.value = 'Failed to load FFmpeg. Check the console for details.';
      } finally {
        loading.value = false;
      }
    }
  };
  
  // Example function to use FFmpeg (replace with your actual FFmpeg logic)
  const generateVideoHandler = async () => {
    generating.value = true;
    try {
      if (!$ffmpeg.isLoaded()) {
        await loadFFmpeg();
      }
  
      // Add your FFmpeg commands here
      console.log('Ready to process video with FFmpeg');
  
      // Example: Log FFmpeg is ready
      // Note: Replace this with actual video processing logic
    } catch (error) {
      console.error('Error processing video:', error);
      alert('Error processing video. Check the console for details.');
    } finally {
      generating.value = false;
    }
  };
  
  // Load FFmpeg when the component is mounted
  onMounted(() => {
    loadFFmpeg();
  });
  </script>
  
  <style scoped>
  .preview-container {
    aspect-ratio: 16 / 9;
    background-color: black;
    position: relative;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  
  .animate-spin {
    animation: spin 1s linear infinite;
  }
  </style>
  
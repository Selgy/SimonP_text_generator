self.onmessage = async function(e) {
  const { videoData, command } = e.data
  try {
    // Process video data
    const result = await processVideo(videoData, command)
    self.postMessage({ success: true, result })
  } catch (error) {
    self.postMessage({ success: false, error: error.message })
  }
} 
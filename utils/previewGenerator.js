// utils/previewGenerator.js
export function generatePreviewImage({ textInput, caseVar, charSizeVar, charSpacingVar }) {
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      canvas.width = 1920;
      canvas.height = 1080;
      const ctx = canvas.getContext('2d');
  
      if (!ctx) {
        reject(new Error('Canvas not supported'));
        return;
      }
  
      // Fill background
      ctx.fillStyle = 'black';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
  
      const text = textInput.trim() || 'Preview';
      let processedText = text;
  
      if (caseVar === 'upper') {
        processedText = text.toUpperCase();
      } else if (caseVar === 'lower') {
        processedText = text.toLowerCase();
      }
  
      // Positioning variables
      let x = 100; // Starting x position
      const y = canvas.height / 2; // Center y position
  
      // Load and draw each character
      const loadImages = async () => {
        for (const char of processedText) {
          if (char === ' ') {
            x += charSizeVar * 0.5; // Adjust space width as needed
            continue;
          }
  
          const caseType = char === char.toUpperCase() ? 'UPPER_CASE' : 'LOWER_CASE';
          const charLower = char.toLowerCase();
          const imgSrc = `/Source/${caseType}/${charLower}.png`;
  
          const img = new Image();
          img.src = imgSrc;
          img.crossOrigin = 'anonymous';
  
          await new Promise((res, rej) => {
            img.onload = () => {
              ctx.drawImage(img, x, y - charSizeVar / 2, charSizeVar, charSizeVar);
              x += charSizeVar + charSpacingVar * charSizeVar;
              res();
            };
            img.onerror = (err) => rej(err);
          });
        }
  
        resolve(canvas.toDataURL('image/png'));
      };
  
      loadImages().catch((error) => reject(error));
    });
  }
  
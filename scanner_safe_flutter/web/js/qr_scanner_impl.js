// Custom JS implementation for QR code scanning in web
window.jsQRScanner = {
  setupCamera: function(videoElement) {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment' 
        },
        audio: false 
      })
      .then(function(stream) {
        videoElement.srcObject = stream;
        videoElement.play();
        console.log('Camera initialized successfully');
      })
      .catch(function(error) {
        console.error('Error accessing camera:', error);
      });
    } else {
      console.error('MediaDevices API not supported in this browser');
    }
  },
  
  processFrame: function(videoElement, canvasElement, callback) {
    const canvas = canvasElement;
    const context = canvas.getContext('2d');
    
    // Set canvas dimensions to match video
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    
    if (videoElement.videoWidth === 0) {
      // Video not ready yet
      return null;
    }
    
    // Draw video frame to canvas
    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    
    // Get image data from canvas
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    
    // Process with jsQR
    if (window.jsQR) {
      const code = window.jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: 'dontInvert',
      });
      
      if (code) {
        callback(code.data);
        return code.data;
      }
    } else {
      console.error('jsQR library not loaded');
    }
    
    return null;
  }
}; 
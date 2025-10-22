/**
 * Resize image to max dimensions while maintaining aspect ratio
 * @param {File} file - Image file to resize
 * @param {number} maxWidth - Maximum width (default 1600px)
 * @param {number} maxHeight - Maximum height (default 1600px)
 * @returns {Promise<Blob>} - Resized image blob
 */
export const resizeImage = (file, maxWidth = 1600, maxHeight = 1600) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const img = new Image();
      
      img.onload = () => {
        let width = img.width;
        let height = img.height;
        
        // Calculate new dimensions
        if (width > height) {
          if (width > maxWidth) {
            height = height * (maxWidth / width);
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = width * (maxHeight / height);
            height = maxHeight;
          }
        }
        
        // Create canvas and resize
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        // Convert to blob
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Canvas to Blob conversion failed'));
            }
          },
          'image/jpeg',
          0.92 // Quality
        );
      };
      
      img.onerror = () => reject(new Error('Image load failed'));
      img.src = e.target.result;
    };
    
    reader.onerror = () => reject(new Error('FileReader failed'));
    reader.readAsDataURL(file);
  });
};

/**
 * Resize multiple images
 * @param {File[]} files - Array of image files
 * @returns {Promise<Blob[]>} - Array of resized image blobs
 */
export const resizeMultipleImages = async (files) => {
  const resizePromises = Array.from(files).map(file => resizeImage(file));
  return Promise.all(resizePromises);
};

/**
 * Validate image file
 * @param {File} file - File to validate
 * @returns {boolean} - True if valid image
 */
export const isValidImage = (file) => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  const maxSize = 10 * 1024 * 1024; // 10MB
  
  return validTypes.includes(file.type) && file.size <= maxSize;
};
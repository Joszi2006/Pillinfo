/**
 * Image utility functions for resizing and validation
 */

// Constants
const MAX_IMAGES = 5;
const MAX_WIDTH = 1600;
const MAX_HEIGHT = 1600;
const VALID_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
const MAX_SIZE = 10 * 1024 * 1024; // 10MB
const JPEG_QUALITY = 0.92;

/**
 * Resize image to max dimensions while maintaining aspect ratio
 * @param {File} file - Image file to resize
 * @param {number} maxWidth - Maximum width (default 1600px)
 * @param {number} maxHeight - Maximum height (default 1600px)
 * @returns {Promise<Blob>} - Resized image blob
 */
export const resizeImage = (file, maxWidth = MAX_WIDTH, maxHeight = MAX_HEIGHT) => {
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
          JPEG_QUALITY
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
  return VALID_TYPES.includes(file.type) && file.size <= MAX_SIZE;
};

/**
 * Validate and limit number of images
 * @param {FileList|File[]} files - Files to validate
 * @returns {Object} - {valid: File[], errors: string[]}
 */
export const validateImages = (files) => {
  const fileArray = Array.from(files);
  const errors = [];
  
  // Check image count limit
  if (fileArray.length > MAX_IMAGES) {
    errors.push(`Maximum ${MAX_IMAGES} images allowed. Only the first ${MAX_IMAGES} will be processed.`);
  }
  
  // Limit to max images
  const limitedFiles = fileArray.slice(0, MAX_IMAGES);
  
  // Validate each file
  const validFiles = limitedFiles.filter(file => {
    if (!isValidImage(file)) {
      errors.push(`${file.name}: Invalid file type or size (max 10MB)`);
      return false;
    }
    return true;
  });
  
  return {
    valid: validFiles,
    errors: errors
  };
};

/**
 * Get image validation constants (for UI display)
 */
export const getImageLimits = () => ({
  maxImages: MAX_IMAGES,
  maxSize: MAX_SIZE,
  maxSizeMB: MAX_SIZE / (1024 * 1024),
  validTypes: VALID_TYPES,
  validExtensions: ['.jpg', '.jpeg', '.png', '.webp']
});
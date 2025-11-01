import { useState, useRef, useEffect } from 'react';
import ImagePreviewGrid from '../ui/ImagePreviewGrid';
import UploadOptionsDialog from '../ui/UploadOptionsDialog';
import { resizeMultipleImages, isValidImage } from '../../utils/imageUtils';

const InputArea = ({ onSendMessage, onUploadImages, prefillText = '', onPrefillClear }) => {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [selectedImages, setSelectedImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (prefillText) {
      setInput(prefillText);
      if (inputRef.current) {
        inputRef.current.focus();
        inputRef.current.setSelectionRange(prefillText.length, prefillText.length);
      }
      onPrefillClear();
    }
  }, [prefillText, onPrefillClear]);

  const handleSend = async () => {
  // Images selected = use image endpoint with optional text
  if (selectedImages.length > 0) {
    try {
      setIsProcessing(true);

      const resizedBlobs = await resizeMultipleImages(selectedImages);
      const resizedFiles = resizedBlobs.map((blob, idx) => 
        new File([blob], selectedImages[idx].name, { type: 'image/jpeg' })
      );

      // Pass images + text (backend extracts weight/age from text)
      await onUploadImages(resizedFiles, input.trim() || undefined);

      clearImages();
      setInput('');

    } catch (error) {
      console.error('Image upload error:', error);
      alert('Failed to upload images');
    } finally {
      setIsProcessing(false);
    }
  } 
  // No images = text endpoint
  else if (input.trim()) {
    onSendMessage(input);
    setInput('');
  }
};

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    addImages(files);
    e.target.value = '';
  };

  const handleCameraCapture = async (e) => {
    const files = Array.from(e.target.files);
    addImages(files);
    e.target.value = '';
  };

  const addImages = (files) => {
    const validFiles = files.filter(isValidImage);

    if (validFiles.length === 0) {
      alert('Please select valid image files');
      return;
    }

    if (selectedImages.length + validFiles.length > 5) {
      alert('Maximum 5 images allowed');
      return;
    }

    setSelectedImages(prev => [...prev, ...validFiles]);
    const newPreviews = validFiles.map(file => URL.createObjectURL(file));
    setImagePreviews(prev => [...prev, ...newPreviews]);
  };

  const removeImage = (index) => {
    URL.revokeObjectURL(imagePreviews[index]);
    setSelectedImages(prev => prev.filter((_, idx) => idx !== index));
    setImagePreviews(prev => prev.filter((_, idx) => idx !== index));
  };

  const clearImages = () => {
    imagePreviews.forEach(url => URL.revokeObjectURL(url));
    setSelectedImages([]);
    setImagePreviews([]);
  };

  return (
    <>
      <div className="border-t border-slate-200 bg-white">
        {/* Image Preview */}
        <ImagePreviewGrid images={imagePreviews} onRemove={removeImage} />

        <div className="p-3 md:p-5">
          <div className="flex items-center gap-1 bg-linear-to-r from-slate-50 to-slate-100 rounded-2xl p-1 border-2 border-transparent focus-within:border-blue-500 transition-all">
            {/* Upload Button (Desktop) */}
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={isProcessing || selectedImages.length >= 5}
              className="hidden md:flex shrink-0 w-11 h-11 rounded-full bg-black shadow-lg items-center justify-center hover:scale-105 active:scale-95 transition-transform disabled:opacity-50"
            >
              {isProcessing ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              )}
            </button>

            {/* Plus Button (Mobile) */}
            <button 
              onClick={() => setIsUploadDialogOpen(true)}
              disabled={isProcessing || selectedImages.length >= 5}
              className="md:hidden shrink-0 w-10 h-10 rounded-full bg-black shadow-lg flex items-center justify-center hover:scale-105 active:scale-95 transition-transform disabled:opacity-50"
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
              </svg>
            </button>

            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                    selectedImages.length > 0 
                      ? "Add weight/age (e.g., 52kg, 14 years) or ask..." 
                      : "Ask about a medication..."
                  }
              disabled={isProcessing}
              className="flex-1 bg-transparent border-none outline-none px-3 md:px-4 py-2 md:py-3 text-sm md:text-[15px] text-slate-700 placeholder-slate-400 disabled:opacity-50"
            />

            <button
              onClick={handleSend}
              disabled={(!input.trim() && selectedImages.length === 0) || isProcessing}
              className="shrink-0 w-10 h-10 md:w-11 md:h-11 rounded-full bg-black shadow-lg flex items-center justify-center hover:scale-105 active:scale-95 transition-transform disabled:opacity-50"
            >
              <svg className="w-4 h-4 md:w-5 md:h-5 text-white transform rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>

        <p className="text-center text-[11px] md:text-xs text-slate-400 pb-2 md:pb-3 px-4">
          Pillinfo can make mistakes. Verify important information with healthcare professionals.
        </p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileSelect}
        className="hidden"
      />

      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleCameraCapture}
        className="hidden"
      />

      <UploadOptionsDialog
        isOpen={isUploadDialogOpen}
        onClose={() => setIsUploadDialogOpen(false)}
        onCamera={() => {
          setIsUploadDialogOpen(false);
          cameraInputRef.current?.click();
        }}
        onGallery={() => {
          setIsUploadDialogOpen(false);
          fileInputRef.current?.click();
        }}
      />
    </>
  );
};

export default InputArea;
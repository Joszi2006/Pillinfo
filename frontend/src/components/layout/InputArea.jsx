import { useState, useRef, useEffect } from 'react';
import CameraModal from '../ui/CameraModal';
import { resizeMultipleImages, isValidImage } from '../../utils/imageUtils';

const InputArea = ({ onSendMessage, onUploadImages, prefillText = '', onPrefillClear }) => {
  const [input, setInput] = useState('');
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);

  // Handle prefill text
  useEffect(() => {
    if (prefillText) {
      setInput(prefillText);
      // Focus input and move cursor to end
      if (inputRef.current) {
        inputRef.current.focus();
        inputRef.current.setSelectionRange(prefillText.length, prefillText.length);
      }
      // Clear prefill
      onPrefillClear();
    }
  }, [prefillText, onPrefillClear]);

  const handleSend = () => {
    if (input.trim()) {
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
    const files = e.target.files;
    if (!files || files.length === 0) return;

    // Validate all files
    const validFiles = Array.from(files).filter(isValidImage);
    
    if (validFiles.length === 0) {
      alert('Please select valid image files (JPEG, PNG, WebP) under 10MB');
      return;
    }

    if (validFiles.length > 5) {
      alert('Maximum 5 images allowed');
      return;
    }

    try {
      setIsProcessing(true);
      
      // Resize all images
      const resizedBlobs = await resizeMultipleImages(validFiles);
      
      // Convert blobs to files with original names
      const resizedFiles = resizedBlobs.map((blob, idx) => 
        new File([blob], validFiles[idx].name, { type: 'image/jpeg' })
      );
      
      onUploadImages(resizedFiles);
      
      // Reset input
      e.target.value = '';
    } catch (error) {
      console.error('Image processing error:', error);
      alert('Failed to process images. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCameraCapture = async (blob) => {
    try {
      setIsProcessing(true);
      
      // Resize camera capture
      const resizedBlob = await resizeMultipleImages([
        new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
      ]);
      
      const file = new File(resizedBlob, 'camera-capture.jpg', { type: 'image/jpeg' });
      onUploadImages([file]);
    } catch (error) {
      console.error('Camera capture processing error:', error);
      alert('Failed to process photo. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const openCamera = () => {
    setIsCameraOpen(true);
  };

  const openFileUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <>
      <div className="border-t border-slate-200 bg-white">
        <div className="p-3 md:p-5">
          <div className="flex items-center gap-1 bg-linear-to-r from-slate-50 to-slate-100 rounded-2xl p-1 border-2 border-transparent focus-within:border-blue-500 focus-within:shadow-[0_0_0_3px_rgba(59,130,246,0.1)] transition-all">
            {/* Upload Button (Desktop only) */}
            <button 
              onClick={openFileUpload}
              disabled={isProcessing}
              className="hidden md:flex shrink-0 w-11 h-11 rounded-full bg-black shadow-lg items-center justify-center hover:scale-105 active:scale-95 transition-transform disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden"
              title="Upload from gallery"
            >
              <div className="absolute inset-0 bg-linear-to-br from-white/20 to-transparent" />
              {isProcessing ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin z-10" />
              ) : (
                <svg className="w-5 h-5 text-white z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              )}
            </button>

            {/* Plus Button (Mobile only) - Opens dialog */}
            <button 
              onClick={() => setIsUploadDialogOpen(true)}
              disabled={isProcessing}
              className="md:hidden shrink-0 w-10 h-10 rounded-full bg-black shadow-lg flex items-center justify-center hover:scale-105 active:scale-95 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
              title="Add image"
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
              placeholder="Ask about a medication..."
              disabled={isProcessing}
              className="flex-1 bg-transparent border-none outline-none px-3 md:px-4 py-2 md:py-3 text-sm md:text-[15px] text-slate-700 placeholder-slate-400 disabled:opacity-50"
            />

            <button
              onClick={handleSend}
              disabled={!input.trim() || isProcessing}
              className="shrink-0 w-10 h-10 md:w-11 md:h-11 rounded-full bg-black shadow-lg flex items-center justify-center hover:scale-105 active:scale-95 transition-transform disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-linear-to-br from-white/20 to-transparent" />
              <svg className="w-4 h-4 md:w-5 md:h-5 text-white z-10 transform rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>

        <p className="text-center text-[11px] md:text-xs text-slate-400 pb-2 md:pb-3 px-4 md:px-5 flex items-center justify-center gap-2">
          <svg className="w-3 h-3 md:w-3.5 md:h-3.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Pillinfo can make mistakes. Verify important information with healthcare professionals.
        </p>
      </div>

      {/* Hidden file input - multiple files allowed */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Camera Modal */}
      <CameraModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onCapture={handleCameraCapture}
      />

      {/* Upload Options Dialog (Mobile) */}
      {isUploadDialogOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-100 flex items-end md:hidden animate-fadeIn" onClick={() => setIsUploadDialogOpen(false)}>
          <div className="bg-white w-full rounded-t-3xl p-6 animate-slideIn" onClick={(e) => e.stopPropagation()}>
            <div className="w-12 h-1 bg-slate-300 rounded-full mx-auto mb-6"></div>
            
            <button
              onClick={() => {
                setIsUploadDialogOpen(false);
                openCamera();
              }}
              className="w-full flex items-center gap-4 p-4 hover:bg-slate-50 rounded-xl transition-colors"
            >
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div className="text-left">
                <p className="font-semibold text-slate-900">Take Photo</p>
                <p className="text-sm text-slate-500">Use camera to capture pill</p>
              </div>
            </button>

            <button
              onClick={() => {
                setIsUploadDialogOpen(false);
                openFileUpload();
              }}
              className="w-full flex items-center gap-4 p-4 hover:bg-slate-50 rounded-xl transition-colors"
            >
              <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="text-left">
                <p className="font-semibold text-slate-900">Upload Image</p>
                <p className="text-sm text-slate-500">Choose from gallery</p>
              </div>
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default InputArea;
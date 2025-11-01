const UploadOptionsDialog = ({ isOpen, onClose, onCamera, onGallery }) => {
  if (!isOpen) return null;

  return (
  <div 
    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-100 flex items-end md:hidden animate-fadeIn" 
    onClick={onClose}
  >
      <div 
        className="bg-white w-full rounded-t-3xl p-6 animate-slideIn" 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="w-12 h-1 bg-slate-300 rounded-full mx-auto mb-6"></div>
        
        <button
          onClick={onCamera}
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
          onClick={onGallery}
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
  );
};

export default UploadOptionsDialog;
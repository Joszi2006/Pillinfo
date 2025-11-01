const ImagePreviewGrid = ({ images, onRemove }) => {
  if (images.length === 0) return null;

  return (
    <div className="p-3 border-b border-slate-200">
      <div className="flex gap-2 overflow-x-auto">
        {images.map((preview, idx) => (
          <div key={idx} className="relative shrink-0">
            <img 
              src={preview} 
              alt={`Preview ${idx + 1}`}
              className="w-15 h-15 object-cover rounded-lg border-2 border-blue-500"
            />
            {onRemove && (
              <button
                onClick={() => onRemove(idx)}
                className="absolute -top-0.5 -right-1 w-3 h-3 bg-black rounded-full flex items-center justify-center shadow-lg transition-colors"
              >
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ImagePreviewGrid;
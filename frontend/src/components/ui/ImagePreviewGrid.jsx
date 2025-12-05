const ImagePreviewGrid = ({ images, onRemove }) => {
  if (images.length === 0) return null;

  return (
    <div className="p-3 border-b border-slate-200">

      <div className="flex gap-3 overflow-x-auto pt-3 pb-1">
        {images.map((preview, idx) => (
          <div key={idx} className="relative shrink-0">
            <img 
              src={preview} 
              alt={`Preview ${idx + 1}`}
              className="w-16 h-16 object-cover rounded-lg border-2 border-blue-500"
            />
            {onRemove && (
              <button
                onClick={() => onRemove(idx)}
                className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center shadow-lg transition-colors z-10"
              >
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
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
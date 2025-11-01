import { createPortal } from 'react-dom';

const InfoModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[200] flex items-center justify-center p-4 animate-fadeIn" onClick={onClose}>
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl animate-slideIn" onClick={(e) => e.stopPropagation()}>
        {/* ... rest of your modal content stays exactly the same ... */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900">About Pillinfo</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-full transition-colors"
          >
            <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="text-slate-700 space-y-4">
          <p className="leading-relaxed">
            Pillinfo is your AI-powered medication information assistant. Upload pill images or search by name to get instant, accurate drug information including dosages, side effects, and safety warnings.
          </p>
          
          <div className="pt-4 border-t border-slate-200">
            <p className="text-sm font-semibold text-slate-900 mb-2">Data Sources:</p>
            <ul className="text-sm space-y-1">
              <li>• <span className="font-medium">RxNorm</span> - National Library of Medicine</li>
              <li>• <span className="font-medium">OpenFDA</span> - U.S. Food and Drug Administration</li>
            </ul>
          </div>

          <p className="text-xs text-slate-500 pt-2">
            Version 1.0.0 • Always verify critical information with healthcare professionals
          </p>
        </div>

        <button
          onClick={onClose}
          className="w-full mt-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl transition-colors"
        >
          Got it
        </button>
      </div>
    </div>,
    document.body
  );
};

export default InfoModal;
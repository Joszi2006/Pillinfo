import { useState } from 'react';

const DrugInfoMessage = ({ drugName, dosageInfo }) => {
  const [isFlipped, setIsFlipped] = useState(false);
  
  const { 
    purpose,
    dose_ml,
    dose_text,
    instructions,
    warning,
    warnings,
    contraindications,
    adverse_reactions
  } = dosageInfo || {};

  return (
    <div className="perspective-1000 mb-6 md:mb-8">
      <div 
        className="relative transition-transform duration-500"
        style={{ 
          transformStyle: 'preserve-3d',
          transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
        }}
      >
        {/* FRONT SIDE */}
        <div 
          className="absolute inset-0 bg-white border border-slate-200 rounded-[20px_20px_20px_4px] shadow-[0_4px_20px_rgba(0,0,0,0.06)] flex flex-col h-[450px] md:h-[432px]"
          style={{ 
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
            transform: 'rotateY(0deg)'
          }}
        >
          {/* Drug Header */}
          <div className="bg-gradient-to-b from-slate-50 to-white border-b border-slate-200 px-4 md:px-6 py-3 md:py-4 flex-shrink-0">
            <h3 className="text-[17px] md:text-[20px] font-bold text-slate-900">{drugName}</h3>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 px-4 md:px-6 py-4 md:py-5 space-y-3 md:space-y-4 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-slate-100">
            {/* Purpose */}
            {purpose && (
              <div>
                <h4 className="text-[13px] md:text-[15px] text-slate-500 font-semibold mb-1.5 md:mb-2">Purpose</h4>
                <p className="text-[13px] md:text-[15px] text-slate-800 leading-relaxed">
                  {purpose}
                </p>
              </div>
            )}

            {/* Dosage Instructions */}
            {instructions && (
              <div>
                <h4 className="text-[13px] md:text-[15px] text-slate-500 font-semibold mb-1.5 md:mb-2">Dosage</h4>
                <p className="text-[13px] md:text-[15px] text-slate-800 leading-relaxed">
                  {instructions}
                  
                  {/* Recommended numeric dose */}
                  {dose_ml && (
                    <> The recommended dose is <strong className="font-bold text-slate-900">{dose_ml}</strong>.</>
                  )}
                  
                  {/* Ask a doctor instruction */}
                  {dose_text && (
                    <> For this weight/age range, <strong className="font-bold text-amber-700">{dose_text}</strong>.</>
                  )}

                  {/* If neither dose_ml nor dose_text, suggest providing more info */}
                  {!dose_ml && !dose_text && (
                    <> To get a specific dosage recommendation, please provide your child's <strong className="font-bold text-blue-600">weight or age</strong>.</>
                  )}
                </p>
              </div>
            )}

            {/* Warning from dosage calculation */}
            {warning && (
              <div className="bg-amber-50 border-l-4 border-amber-500 rounded-r-lg px-3 md:px-4 py-2 md:py-3">
                <p className="text-[12px] md:text-[14px] text-amber-900">
                  <strong>Note:</strong> {warning}
                </p>
              </div>
            )}
          </div>

          {/* Button - Fixed at bottom */}
          <div className="px-4 md:px-6 pb-4 md:pb-5 pt-2 md:pt-3 flex-shrink-0 border-t border-slate-100">
            <button 
              onClick={() => setIsFlipped(true)}
              className="w-full px-4 md:px-6 py-2.5 md:py-3 bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 text-white text-[13px] md:text-[14px] font-semibold rounded-lg shadow-[0_4px_12px_rgba(37,99,235,0.3)] hover:scale-[1.02] active:scale-95 transition-transform relative overflow-hidden"
            >
              <div 
                className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent pointer-events-none" 
                style={{ transform: 'rotate(45deg)' }} 
              />
              <span className="relative z-10">Important Safety Information</span>
            </button>
          </div>
        </div>

        {/* BACK SIDE */}
        <div 
          className="absolute inset-0 bg-white border border-slate-200 rounded-[20px_20px_20px_4px] shadow-[0_4px_20px_rgba(0,0,0,0.06)] flex flex-col h-[450px] md:h-[432px]"
          style={{ 
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)'
          }}
        >
          {/* Header */}
          <div className="bg-gradient-to-b from-amber-50 to-white border-b border-amber-200 px-4 md:px-6 py-3 md:py-4 flex-shrink-0">
            <h3 className="text-[16px] md:text-[18px] font-bold text-amber-900">
              Safety Information
            </h3>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 px-4 md:px-6 py-4 md:py-5 space-y-3 md:space-y-4 overflow-y-auto scrollbar-thin scrollbar-thumb-amber-300 scrollbar-track-amber-100">
            {/* Warnings */}
            {warnings && (
              <div>
                <h4 className="text-[12px] md:text-[14px] text-red-700 font-semibold mb-1.5 md:mb-2 uppercase tracking-wide">
                  Warnings
                </h4>
                <p className="text-[12px] md:text-[13px] text-slate-700 leading-relaxed">
                  {warnings}
                </p>
              </div>
            )}

            {/* Contraindications */}
            {contraindications && (
              <div>
                <h4 className="text-[12px] md:text-[14px] text-red-700 font-semibold mb-1.5 md:mb-2 uppercase tracking-wide">
                  Contraindications
                </h4>
                <p className="text-[12px] md:text-[13px] text-slate-700 leading-relaxed">
                  {contraindications}
                </p>
              </div>
            )}

            {/* Adverse Reactions */}
            {adverse_reactions && (
              <div>
                <h4 className="text-[12px] md:text-[14px] text-orange-700 font-semibold mb-1.5 md:mb-2 uppercase tracking-wide">
                  Possible Side Effects
                </h4>
                <p className="text-[12px] md:text-[13px] text-slate-700 leading-relaxed">
                  {adverse_reactions}
                </p>
              </div>
            )}
          </div>

          {/* Button - Fixed at bottom */}
          <div className="px-4 md:px-6 pb-4 md:pb-5 pt-2 md:pt-3 flex-shrink-0 border-t border-amber-100">
            <button 
              onClick={() => setIsFlipped(false)}
              className="w-full px-4 md:px-6 py-2.5 md:py-3 bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 text-white text-[13px] md:text-[14px] font-semibold rounded-lg shadow-[0_4px_12px_rgba(37,99,235,0.3)] hover:scale-[1.02] active:scale-95 transition-transform relative overflow-hidden"
            >
              <div 
                className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent pointer-events-none" 
                style={{ transform: 'rotate(45deg)' }} 
              />
              <span className="relative z-10">Back to Dosage</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DrugInfoMessage;
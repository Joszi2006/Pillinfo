import Badge from '../ui/Badge';
import WarningBox from '../ui/WarningBox';

const DrugInfoMessage = ({ drugName, rxcui, dosageInfo }) => {
  const { 
    generic_name, 
    brand_names, 
    form, 
    route, 
    dosing_info, 
    warnings 
  } = dosageInfo || {};

  // Helper to highlight numeric dosage
  const highlightDosage = (text) => {
    if (!text) return text;
    
    const dosageMatch = text.match(/(\d+[\d\s]*(?:mg|mcg|ml|g|tablets?))/gi);
    if (!dosageMatch) return text;

    const parts = text.split(new RegExp(`(${dosageMatch.join('|')})`, 'gi'));
    
    return parts.map((part, idx) => {
      const isDosage = dosageMatch.some(d => d.toLowerCase() === part.toLowerCase());
      return isDosage ? (
        <strong key={idx} className="text-blue-500 font-semibold">{part}</strong>
      ) : (
        <span key={idx}>{part}</span>
      );
    });
  };

  return (
    <div className="bg-white border border-slate-200 rounded-[20px_20px_20px_4px] shadow-[0_4px_20px_rgba(0,0,0,0.06)] overflow-hidden">
      
      {/* Drug Header */}
      <div className="bg-gradient-to-b from-slate-50 to-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
        <h3 className="text-[20px] font-bold text-slate-900">{drugName}</h3>
        {rxcui && <Badge>RxCUI: {rxcui}</Badge>}
      </div>

      {/* Content */}
      <div className="px-6 py-5 space-y-3">
        
        {/* Key-Value Pairs */}
        {generic_name && (
          <div className="text-[15px]">
            <span className="text-[14px] text-slate-500 font-semibold">Generic Name: </span>
            <span className="text-slate-800">{generic_name}</span>
          </div>
        )}

        {brand_names && (
          <div className="text-[15px]">
            <span className="text-[14px] text-slate-500 font-semibold">Brand Names: </span>
            <span className="text-slate-800">{brand_names}</span>
          </div>
        )}

        {form && (
          <div className="text-[15px]">
            <span className="text-[14px] text-slate-500 font-semibold">Form: </span>
            <span className="text-slate-800">{form}</span>
          </div>
        )}

        {route && (
          <div className="text-[15px]">
            <span className="text-[14px] text-slate-500 font-semibold">Route: </span>
            <span className="text-slate-800">{route}</span>
          </div>
        )}

        {/* Dosage Section */}
        {dosing_info?.dosage_instructions && (
          <div className="mt-4">
            <h4 className="text-[15px] text-slate-500 font-semibold mb-2">Dosage</h4>
            <p className="text-[15px] text-slate-800 leading-relaxed">
              {highlightDosage(dosing_info.dosage_instructions)}
            </p>
          </div>
        )}

        {/* Indications */}
        {dosing_info?.pediatric_use && (
          <div className="mt-4">
            <h4 className="text-[15px] text-slate-500 font-semibold mb-2">Indications</h4>
            <p className="text-[15px] text-slate-800 leading-relaxed">
              {dosing_info.pediatric_use}
            </p>
          </div>
        )}

        {/* Warnings */}
        {warnings && warnings.length > 0 && (
          <WarningBox>
            {warnings.map((warning, idx) => (
              <p key={idx} className={idx > 0 ? 'mt-2' : ''}>
                {warning.message}
              </p>
            ))}
          </WarningBox>
        )}

        {/* Additional Warnings from dosing_info */}
        {dosing_info?.warnings && !warnings && (
          <WarningBox>
            {dosing_info.warnings.length > 200 
              ? `${dosing_info.warnings.substring(0, 200)}...` 
              : dosing_info.warnings
            }
          </WarningBox>
        )}

        {/* View Full Label Button */}
        <button className="mt-5 px-5 py-2.5 bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 text-white text-[14px] font-semibold rounded-lg shadow-[0_4px_12px_rgba(37,99,235,0.3)] hover:scale-[1.02] active:scale-95 transition-transform relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent" 
               style={{ transform: 'rotate(45deg)' }} />
          <span className="relative z-10">View Full FDA Label</span>
        </button>
      </div>
    </div>
  );
};

export default DrugInfoMessage;
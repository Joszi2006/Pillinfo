import Avatar from '../ui/Avatar';
import QuickActionButton from '../ui/QuickActionButton';

const WelcomeMessage = ({ onQuickAction }) => {
  return (
    <div className="mb-8 animate-[slideIn_0.3s_ease-out]">
      <div className="flex gap-2 md:gap-3">
        <div className="md:hidden">
          <Avatar size="sm" />
        </div>
        <div className="max-w-[90%] md:max-w-[85%]">
          <div className="bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200/50 rounded-[18px_18px_18px_4px] md:rounded-[20px_20px_20px_4px] p-4 md:p-5 shadow-[0_4px_16px_rgba(37,99,235,0.08)]">
            <h3 className="text-base md:text-[17px] font-semibold text-slate-900 mb-1 md:mb-2">
              Hi! I'm your Drug Information Assistant.
            </h3>
            <p className="text-sm md:text-[15px] text-slate-600 leading-relaxed">
              Ask me about any medication or upload a pill image to identify it!
            </p>
          </div>

          {/* Quick Action Buttons - Separated with margin */}
          <div className="flex flex-wrap gap-2 md:gap-3 mt-4 md:mt-4">
            <QuickActionButton
              icon={
                <svg className="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              }
              label="Search Drug"
              onClick={() => onQuickAction({ type: 'prefill', text: 'I want to search for ' })}
            />
            <QuickActionButton
              icon={
                <svg className="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              }
              label="Dosage"
              onClick={() => onQuickAction({ type: 'prefill', text: 'Calculate dosage for ' })}
            />
            <QuickActionButton
              icon={
                <svg className="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              }
              label="Upload Image"
              onClick={() => onQuickAction({ type: 'upload' })}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeMessage;
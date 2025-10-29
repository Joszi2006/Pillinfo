import { useState } from 'react';
import Avatar from '../ui/Avatar';
import InfoModal from '../ui/InfoModal';
import HelpModal from '../ui/HelpModal';

const Header = () => {
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  return (
    <>
      <header className="fixed top-[60px] left-1/2 -translate-x-1/2 w-[calc(100%-120px)] max-w-[1030px] h-[89px] md:h-[105px] bg-white backdrop-blur-lg rounded-t-[20px] shadow-[0_4px_12px_rgba(0,0,0,0.08)] border-b border-blue-100 flex items-center justify-between px-8 z-50">
        <div className="flex items-center gap-2 md:gap-3">
          {/* NEW pill logo */}
          <Avatar size="lg" />
          <div>
            <h1 className="text-xl md:text-[28px] font-bold text-slate-900 -tracking-[0.5px]">Pillinfo</h1>
            <p className="text-[11px] md:text-[13px] text-slate-500 font-medium hidden sm:block">No.1 Drug Informant</p>
          </div>
        </div>

        <div className="flex items-center gap-3 md:gap-5">
          {/* Info Button */}
          <button 
            onClick={() => setIsInfoOpen(true)}
            className="text-slate-500 hover:text-blue-500 transition-colors"
            title="About Pillinfo"
          >
            <svg className="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          
          {/* Help Button */}
          <button 
            onClick={() => setIsHelpOpen(true)}
            className="text-slate-500 hover:text-blue-500 transition-colors"
            title="Get Help"
          >
            <svg className="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>
      </header>

      {/* Modals */}
      <InfoModal isOpen={isInfoOpen} onClose={() => setIsInfoOpen(false)} />
      <HelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </>
  );
};

export default Header;
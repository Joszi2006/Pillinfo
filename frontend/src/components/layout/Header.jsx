const Header = () => {
  return (
    <header className="fixed top-0 left-1/2 -translate-x-1/2 w-full md:w-[62.5%] md:max-w-[900px] h-16 md:h-20 bg-white backdrop-blur-lg md:rounded-t-[20px] shadow-[0_4px_20px_rgba(37,99,235,0.08)] border-b border-blue-100 flex items-center justify-between px-4 md:px-6 z-50">
      <div className="flex items-center gap-2 md:gap-3">
        <div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 shadow-[0_4px_12px_rgba(37,99,235,0.25)] flex items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/40 via-white/10 to-transparent opacity-100" 
               style={{ transform: 'rotate(45deg)' }} />
          <svg className="w-5 h-5 md:w-6 md:h-6 text-white z-10" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <div>
          <h1 className="text-xl md:text-[28px] font-bold text-slate-900 -tracking-[0.5px]">Pillinfo</h1>
          <p className="text-[11px] md:text-[13px] text-slate-500 font-medium hidden sm:block">No.1 Drug Informant</p>
        </div>
      </div>
      
      <div className="flex items-center gap-3 md:gap-5">
        <button className="text-slate-500 hover:text-blue-500 transition-colors">
          <svg className="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
        <button className="relative text-slate-500 hover:text-blue-500 transition-colors">
          <svg className="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span className="absolute top-0 right-0 w-2 h-2 bg-blue-500 rounded-full"></span>
        </button>
      </div>
    </header>
  );
};

export default Header;
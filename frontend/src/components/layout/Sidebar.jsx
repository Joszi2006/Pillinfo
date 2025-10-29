const Sidebar = ({ recentMatches = [], onMatchClick, isOpen = false, onClose }) => {
  return (
    <>
      {/* Mobile Overlay Backdrop */}
      {isOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-150 animate-fadeIn"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed md:relative
        top-0 md:top-0
        left-0 md:left-0
        w-[280px]
        h-full
        bg-linear-to-br from-blue-400 via-blue-500 to-blue-700
         md:rounded-bl-[20px]
        shadow-lg md:shadow-none
        overflow-y-auto hide-scrollbar
        z-160 md:z-auto
        transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Glossy overlay effect */}
        <div className="absolute inset-0 bg-linear-to-br from-white/20 to-transparent pointer-events-none" />

        {/* Content */}
        <div className="relative p-6 pt-14">
          {/* Close button (Mobile only) */}
          <button
            onClick={onClose}
            className="md:hidden absolute top-4 right-4 p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
          >
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Recent Matches Section */}
          <div className="mb-8 mt-8 md:mt-0">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wide mb-4">
              Recent Matches
            </h3>
            
            {recentMatches.length === 0 ? (
              <p className="text-sm text-white/70 italic">No recent searches yet</p>
            ) : (
              <div className="space-y-3">
                {recentMatches.map((match, idx) => (
                  <button
                    key={idx}
                    onClick={() => onMatchClick(match)}
                    className="w-full text-left p-3 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-lg border-2 border-transparent hover:border-white/50 transition-all text-sm text-white animate-fadeIn"
                    style={{
                      animation: idx === 0 ? 'fadeIn 0.3s ease-out, borderDraw 1.5s ease-out' : 'fadeIn 0.3s ease-out'
                    }}
                  >
                    {match.drugName}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Bottom Links */}
          {/* <div className="mt-auto space-y-2 border-t border-white/20 pt-4">
            <a href="#" className="block text-sm text-white/90 hover:text-white transition-colors">
              About Pillinfo
            </a>
            <a href="#" className="block text-sm text-white/90 hover:text-white transition-colors">
              Help
            </a>
          </div> */}
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
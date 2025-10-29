const Avatar = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-11 h-11',
    lg: 'w-12 h-12'
  };

  return (
    <div className={`${sizeClasses[size]} shrink-0 rounded-full bg-linear-to-br from-blue-400 via-blue-500 to-blue-700 shadow-lg flex items-center justify-center relative overflow-hidden`}>
      {/* Glossy overlay */}
      <div className="absolute inset-0 bg-linear-to-br from-white/30 to-transparent" />
      
      {/* Pill capsule logo */}
      <svg className="w-9 h-9 relative z-10" viewBox="0 0 24 24" fill="none">
        {/* Rounded rectangle - taller than wide, tilted LEFT */}
        <rect 
          x="8.5" 
          y="4" 
          width="7" 
          height="16" 
          rx="3" 
          stroke="white" 
          strokeWidth="2.0" 
          fill="none"
          transform="rotate(45 12 12)"
        />
        {/* Line splitting ACROSS the width (horizontal line through middle) */}
        <line 
          x1="9.5" 
          y1="12" 
          x2="14.5" 
          y2="12" 
          stroke="white" 
          strokeWidth="2.5" 
          strokeLinecap="round"
          transform="rotate(45 12 12)"
        />
      </svg>
    </div>
  );
};

export default Avatar;
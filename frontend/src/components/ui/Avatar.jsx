const Avatar = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-11 h-11',
    lg: 'w-12 h-12'
  };

  return (
    <div className={`${sizeClasses[size]} flex-shrink-0 rounded-full bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 shadow-[0_4px_12px_rgba(37,99,235,0.25)] flex items-center justify-center relative overflow-hidden`}>
      <div className="absolute inset-0 bg-gradient-to-br from-white/40 via-white/10 to-transparent" 
           style={{ transform: 'rotate(45deg)' }} />
      <svg className="w-6 h-6 text-white z-10" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>
    </div>
  );
};

export default Avatar;
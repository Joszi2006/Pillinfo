const Badge = ({ children, variant = 'blue' }) => {
  const variants = {
    blue: 'bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 text-white shadow-[0_2px_8px_rgba(37,99,235,0.25)]',
    gray: 'bg-slate-200 text-slate-700'
  };

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-[11px] font-semibold ${variants[variant]} relative overflow-hidden`}>
      {variant === 'blue' && (
        <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent" 
             style={{ transform: 'rotate(45deg)' }} />
      )}
      <span className="relative z-10">{children}</span>
    </span>
  );
};

export default Badge;
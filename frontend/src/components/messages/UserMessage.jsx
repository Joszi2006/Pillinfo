const UserMessage = ({ text }) => {
  return (
    <div className="flex justify-end mb-3 md:mb-4 animate-[slideInRight_0.3s_ease-out]">
      <div className="max-w-[85%] md:max-w-[70%] bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 text-white rounded-[18px_18px_4px_18px] md:rounded-[20px_20px_4px_20px] px-4 md:px-5 py-2.5 md:py-3.5 shadow-[0_6px_20px_rgba(37,99,235,0.25)] relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-white/20 via-white/10 to-transparent opacity-100" 
             style={{ transform: 'rotate(45deg)' }} />
        <p className="text-sm md:text-[15px] leading-relaxed relative z-10">{text}</p>
      </div>
    </div>
  );
};

export default UserMessage;
const QuickActionButton = ({ icon, label, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-5 py-2.5 bg-white border-[1.5px] border-blue-200 rounded-xl text-sm font-medium text-blue-500 hover:bg-linear-to-br hover:from-blue-400 hover:via-blue-500 hover:to-blue-700 hover:text-white hover:scale-[1.02] transition-all duration-300 shadow-sm hover:shadow-md"
    >
      {icon}
      <span>{label}</span>
    </button>
  );
};

export default QuickActionButton;
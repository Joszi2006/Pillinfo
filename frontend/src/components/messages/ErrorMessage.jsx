const ErrorMessage = ({ message }) => {
  return (
    <div className="bg-white border border-slate-200 rounded-[20px_20px_20px_4px] p-5 shadow-[0_4px_20px_rgba(0,0,0,0.06)]">
      <p className="text-[15px] text-slate-600 leading-relaxed">{message}</p>
    </div>
  );
};

export default ErrorMessage;
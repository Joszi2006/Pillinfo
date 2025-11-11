const ErrorMessage = ({ message }) => {
  const isLoading = message === 'Searching drug database...';

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-[18px_18px_18px_4px] md:rounded-[20px_20px_20px_4px] p-3 md:p-4">
      {isLoading ? (
        // bounding dot animaton
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      ) : (
        // Error message
        <p className="text-sm md:text-[15px] text-slate-600 leading-relaxed">
          {message}
        </p>
      )}
    </div>
  );
};

export default ErrorMessage;
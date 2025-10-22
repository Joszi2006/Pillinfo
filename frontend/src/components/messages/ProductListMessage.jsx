const ProductListMessage = ({ message, products }) => {
  return (
    <div className="bg-white border border-slate-200 rounded-[20px_20px_20px_4px] p-5 shadow-[0_4px_20px_rgba(0,0,0,0.06)]">
      <p className="text-[15px] text-slate-800 mb-4 leading-relaxed">{message}</p>
      
      <ul className="space-y-2">
        {products.map((product, idx) => (
          <li key={idx} className="flex items-start gap-3">
            <span className="w-2 h-2 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 mt-2 flex-shrink-0 shadow-sm" />
            <span className="text-[15px] text-slate-800">{product.name}</span>
          </li>
        ))}
      </ul>

      <p className="text-[14px] text-slate-500 italic mt-4 leading-relaxed">
        Please specify dosage and form for detailed information.
      </p>
    </div>
  );
};

export default ProductListMessage;
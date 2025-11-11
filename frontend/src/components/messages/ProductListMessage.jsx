const ProductListMessage = ({ message, products }) => {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-[18px_18px_18px_4px] md:rounded-[20px_20px_20px_4px] p-4 md:p-5">
      {/* Message from backend */}
      {message && (
        <p className="text-sm md:text-[15px] text-slate-700 mb-4 leading-relaxed">
          {message}
        </p>
      )}

      {/* Suggest products when dosage, form and route are not provided */}
      {products && products.length > 0 && (
        <div className="text-sm md:text-[15px] text-slate-700 leading-relaxed">
          {products.length === 1 ? (
            <p>
              Found: <strong className="text-slate-900">{products[0].name}</strong>
            </p>
          ) : (
            <p>
              For example: {products.map((product, idx) => (
                <span key={idx}>
                  <strong className="text-slate-900">{product.name}</strong>
                  {idx < products.length - 1 && ', '}
                </span>
              ))}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default ProductListMessage;
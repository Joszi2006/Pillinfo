const ProductListMessage = ({ products }) => {
  return (
    <div className="bg-white border border-slate-200 rounded-[18px_18px_18px_4px] md:rounded-[20px_20px_20px_4px] p-4 md:p-5 shadow-sm">
      {products && products.length > 1 && (
        <div className="text-sm md:text-[15px] text-slate-700 leading-relaxed space-y-2">
          <p>
            I found <strong className="text-slate-900">{products.length} products</strong> matching your search.
          </p>
          
          <p>
            For example:{' '}
            {products.slice(0, 3).map((product, idx) => (
              <span key={product.rxcui || `product-${idx}`}>
                <strong className="text-slate-900">{product.name || product.product_name}</strong>
                {idx < Math.min(2, products.length - 1) && ', '}
              </span>
            ))}
            {products.length > 3 && ', and more'}
          </p>
          
          <p className="text-slate-600">
            Please specify the dosage, form (tablet/suspension), or concentration to narrow it down.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProductListMessage;
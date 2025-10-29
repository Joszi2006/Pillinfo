import Avatar from '../ui/Avatar';
import DrugInfoMessage from './DrugInfoMessage';
import ProductListMessage from './ProductListMessage';
import ErrorMessage from './ErrorMessage';

const BotMessage = ({ response }) => {
  const { success, brand_name, best_match, matched_products, message, dosage_info } = response;

  return (
    <div className="flex gap-3 m-5 animate-[slideIn_0.3s_ease-out]">
      <Avatar size="md" />
      
      <div className="flex-1 max-w-[80%]">
        {/* Scenario 1: Error or Failure */}
        {!success && (
          <ErrorMessage message={response.error || message} />
        )}

        {/* Scenario 2: Exact Match with Detailed Info */}
        {success && dosage_info && (
          <DrugInfoMessage
            drugName={best_match?.name || brand_name}
            rxcui={best_match?.rxcui}
            dosageInfo={dosage_info}
          />
        )}

        {/* Scenario 3: Multiple Matches (No Exact Match) */}
        {success && !dosage_info && matched_products && matched_products.length > 0 && (
          <ProductListMessage
            message={message}
            products={matched_products}
          />
        )}

        {/* Scenario 4: Success but No Products Found */}
        {success && !dosage_info && (!matched_products || matched_products.length === 0) && (
          <ErrorMessage message={message || "No products found."} />
        )}
      </div>
    </div>
  );
};

export default BotMessage;
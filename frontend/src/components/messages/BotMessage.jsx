import Avatar from '../ui/Avatar';
import DrugInfoMessage from './DrugInfoMessage';
import ProductListMessage from './ProductListMessage';
import ErrorMessage from './ErrorMessage';

const BotMessage = ({ response, id }) => {  
  const { success, brand_name, best_match, matched_products, dosage_info } = response;

  return (
    <div id={id} className="flex gap-2 md:gap-3 mb-6 md:mb-8 animate-[slideIn_0.3s_ease-out]">
      {/* ADD id attribute to div above */}
      <Avatar size="md" />
      <div className="flex-1 max-w-[80%]">
        {/* Scenario 1: Error or Failure */}
        {!success && (
          <ErrorMessage message={response.error} />
        )}

        {/* Scenario 2: Best Match with Detailed Info */}
        {success && dosage_info && (
          <DrugInfoMessage
            drugName={best_match?.name || best_match?.product_name || brand_name}
            dosageInfo={dosage_info}
          />
        )}

        {/* Scenario 3: Multiple Matches */}
        {success && !dosage_info && matched_products && matched_products.length > 0 && (
          <ProductListMessage
            products={matched_products}
          />
        )}

        {/* Scenario 4: Success but No Products Found */}
        {success && !dosage_info && (!matched_products || matched_products.length === 0) && (
          <ErrorMessage message="No products found." />
        )}
      </div>
    </div>
  );
};

export default BotMessage;
import { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export const useDrugLookup = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Lookup drug by text query
   */
  const lookupByText = async (text, useNer = true, lookupAllDrugs = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/lookup/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          use_ner: useNer,
          lookup_all_drugs: lookupAllDrugs,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to lookup drug information';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Lookup drug by image(s)
   */
  const lookupByImage = async (images, additionalText) => {
  setIsLoading(true);
  setError(null);

  try {
    const formData = new FormData();
    
    images.forEach(image => {
      formData.append('files', image);
    });

    // Add text for weight/age extraction
    if (additionalText) {
      formData.append('additional_text', additionalText);
    }

    const response = await fetch(`${API_BASE_URL}/lookup/image`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;

  } catch (err) {
    setError(err.message);
    return { success: false, error: err.message };
  } finally {
    setIsLoading(false);
  }
};

  return {
    lookupByText,
    lookupByImage,
    isLoading,
    error,
  };
};
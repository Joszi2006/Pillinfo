import { useState, useEffect } from 'react';

const HelpModal = ({ isOpen, onClose }) => {
  const [userLocation, setUserLocation] = useState(null);

  useEffect(() => {
    if (isOpen && !userLocation) {
      // Get user's general location
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setUserLocation({
              lat: position.coords.latitude,
              lng: position.coords.longitude
            });
          },
          (error) => {
            console.log('Location access denied or unavailable');
          }
        );
      }
    }
  }, [isOpen, userLocation]);

  const openPharmacySearch = () => {
    if (userLocation) {
      window.open(`https://www.google.com/maps/search/pharmacies/@${userLocation.lat},${userLocation.lng},13z`, '_blank');
    } else {
      window.open('https://www.google.com/maps/search/pharmacies+near+me', '_blank');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-200 flex items-center justify-center p-4 animate-fadeIn" onClick={onClose}>
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl animate-slideIn" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-900">Need Help?</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-full transition-colors"
          >
            <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Emergency Section */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center shrink-0">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">Medical Emergency</h3>
              <p className="text-sm text-slate-600">Severe reactions or life-threatening</p>
            </div>
          </div>
          
          <a
            href="tel:911"
            className="flex items-center justify-center gap-2 w-full py-3 bg-red-500 hover:bg-red-600 text-white font-bold rounded-xl transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            Call 911
          </a>
        </div>

        {/* Pharmacy Locator */}
        <div>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">Medication Questions</h3>
              <p className="text-sm text-slate-600">Find pharmacies near you</p>
            </div>
          </div>
          
          <button
            onClick={openPharmacySearch}
            className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl transition-colors"
          >
            Find Pharmacies
          </button>
        </div>
      </div>
    </div>
  );
};

export default HelpModal;
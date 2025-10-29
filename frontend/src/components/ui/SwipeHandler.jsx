import { useEffect } from 'react';

const SwipeHandler = ({ onSwipeRight, isEnabled = true }) => {
  useEffect(() => {
    if (!isEnabled) return;

    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    const handleTouchStart = (e) => {
      // Only detect swipes from left edge (first 30px)
      if (e.touches[0].clientX > 30) return;
      
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
    };

    const handleTouchMove = (e) => {
      touchEndX = e.touches[0].clientX;
      touchEndY = e.touches[0].clientY;
    };

    const handleTouchEnd = () => {
      if (touchStartX === 0) return;

      const deltaX = touchEndX - touchStartX;
      const deltaY = Math.abs(touchEndY - touchStartY);

      // Check if it's a horizontal swipe (more horizontal than vertical)
      // and if it's a right swipe (deltaX > 0) with significant distance (> 50px)
      if (deltaX > 50 && deltaY < 100) {
        onSwipeRight();
      }

      // Reset
      touchStartX = 0;
      touchStartY = 0;
      touchEndX = 0;
      touchEndY = 0;
    };

    document.addEventListener('touchstart', handleTouchStart, { passive: true });
    document.addEventListener('touchmove', handleTouchMove, { passive: true });
    document.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, [onSwipeRight, isEnabled]);

  return null; // This component doesn't render anything
};

export default SwipeHandler;
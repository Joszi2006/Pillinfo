import { useRef, useEffect } from 'react';

const ChatContainer = ({ children }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [children]);

  return (
    <div 
      ref={scrollRef}
      className="fixed top-16 md:top-20 left-0 md:left-1/2 md:-translate-x-1/2 w-full md:w-[62.5%] md:max-w-[900px] bg-white md:shadow-[0_8px_32px_rgba(37,99,235,0.12)] overflow-y-auto hide-scrollbar"
      style={{ height: 'calc(100vh - 136px)' }} // Adjusted for mobile header
    >
      <div className="p-4 md:p-10">
        {children}
      </div>
    </div>
  );
};

export default ChatContainer;
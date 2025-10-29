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
      className="flex-1 overflow-y-auto hide-scrollbar p-4 md:p-6"
    >
      {children}
    </div>
  );
};

export default ChatContainer;
import { useState, useRef } from 'react';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import ChatContainer from './components/layout/ChatContainer';
import InputArea from './components/layout/InputArea';
import WelcomeMessage from './components/messages/WelcomeMessage';
import UserMessage from './components/messages/UserMessage';
import BotMessage from './components/messages/BotMessage';
import { useDrugLookup } from './hooks/useDrugLookup';

function App() {
  const [messages, setMessages] = useState([
    { id: 1, type: 'welcome' }
  ]);
  const messageIdCounter = useRef(2);
  const [recentMatches, setRecentMatches] = useState([]);
  const [inputPrefill, setInputPrefill] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const { lookupByText, lookupByImage, isLoading } = useDrugLookup();

  const addUserMessage = (text) => {
    const newMessage = {
      id: messageIdCounter.current,  
      type: 'user',
      text,
    };
    messageIdCounter.current += 1;  
    setMessages((prev) => [...prev, newMessage]);
    return newMessage.id;
  };

  const addLoadingMessage = () => {
    const loadingMessage = {
      id: messageIdCounter.current,  
      type: 'bot',
      response: {
        success: false,
        error: 'Searching drug database...',
      },
    };
    const currentId = messageIdCounter.current;
    messageIdCounter.current += 1;  
    setMessages((prev) => [...prev, loadingMessage]);
    return currentId;
  };

  const replaceMessage = (messageId, response) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, response } : msg
      )
    );
  };

  const addToRecentMatches = (response, messageId) => {
  console.log('=== ADD TO RECENT MATCHES ===');
  console.log('Full response:', JSON.stringify(response, null, 2));
  console.log('response.success:', response.success);
  console.log('response.status:', response.status);
  console.log('response.best_match:', response.best_match);
  console.log('============================');
  
  if (response.success && response.status === 'best_match' && response.best_match) {
    const drugName = response.best_match.name || response.best_match.product_name || 'Unknown Drug';
    console.log('Adding drug to recent:', drugName);
    
    const exists = recentMatches.some(match => match.drugName === drugName);
    
    if (!exists) {
      setRecentMatches(prev => [
        { drugName, messageId },
        ...prev.slice(0, 9)
      ]);
    }
  }
};

  const handleMatchClick = (match) => {
    setIsSidebarOpen(false);
    
 
    const messageElement = document.getElementById(`message-${match.messageId}`);
    
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const handleSendMessage = async (text) => {
    addUserMessage(text);
    const loadingId = addLoadingMessage();
    const response = await lookupByText(text);
    replaceMessage(loadingId, response);
    addToRecentMatches(response, loadingId);
  };

  const handleUploadImages = async (images, additionalText) => {
    const imageText = images.length > 1 
      ? `Uploaded ${images.length} images` 
      : 'Uploaded 1 image';
    addUserMessage(imageText);
    const loadingId = addLoadingMessage();
    const response = await lookupByImage(images, additionalText);
    replaceMessage(loadingId, response);
    addToRecentMatches(response, loadingId);
  };

  const handleQuickAction = (action) => {
    if (typeof action === 'object') {
      if (action.type === 'upload') {
        // Trigger file upload dialog
        document.querySelector('input[type="file"][accept="image/*"][multiple]')?.click();
        return;
      }
      if (action.type === 'prefill') {
        setInputPrefill(action.text);
        return;
      }
    }
    handleSendMessage(action);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Floating Sidebar Toggle Button (Mobile Only) */}
      {!isSidebarOpen && (
  <button
    onClick={() => setIsSidebarOpen(true)}
    className="md:hidden fixed left-0 top-1/2 -translate-y-1/2 z-[100] w-9 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-r-full shadow-lg flex items-center justify-end pr-2 hover:w-14 active:scale-95 transition-all"
  >
    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  </button>
)}

      {/* Desktop view: Header spans full width above everything */}
      <div className="hidden md:block fixed top-[60px] left-1/2 -translate-x-1/2 w-[calc(100%-120px)] max-w-[1030px] z-50">
        <Header />
      </div>

      {/* Main Container */}
      <div className="fixed top-0 md:top-[165px] left-0 md:left-1/2 md:-translate-x-1/2 w-full md:w-[calc(100%-120px)] md:max-w-[1030px] h-screen md:h-[calc(80vh-105px)] flex flex-col md:flex-row">
        {/* Mobile: Header at top */}
        <div className="md:hidden w-full">
          <Header />
        </div>

        {/* Sidebar */}
        <Sidebar 
          recentMatches={recentMatches} 
          onMatchClick={handleMatchClick}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col bg-white shadow-md md:rounded-br-[20px] overflow-hidden">
          {/* Chat Container */}
          <ChatContainer>
            {messages.map((message) => {
              switch (message.type) {
                case 'welcome':
                  return (
                    <WelcomeMessage
                      key={message.id}
                      onQuickAction={handleQuickAction}
                    />
                  );
                case 'user':
                  return (
                    <UserMessage
                      key={message.id}
                      text={message.text}
                    />
                  );
                case 'bot':
                  return (
                    <BotMessage
                      key={message.id}
                      id={`message-${message.id}`}
                      response={message.response}
                    />
                  );
                default:
                  return null;
              }
            })}
          </ChatContainer>

          {/* Input Area */}
          <InputArea
            onSendMessage={handleSendMessage}
            onUploadImages={handleUploadImages}
            prefillText={inputPrefill}
            onPrefillClear={() => setInputPrefill('')}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
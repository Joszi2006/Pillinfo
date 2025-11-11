import { useState } from 'react';
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
  const [messageIdCounter, setMessageIdCounter] = useState(2);
  const [recentMatches, setRecentMatches] = useState([]);
  const [inputPrefill, setInputPrefill] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const { lookupByText, lookupByImage, isLoading } = useDrugLookup();

  const addUserMessage = (text) => {
    const newMessage = {
      id: messageIdCounter,
      type: 'user',
      text,
    };
    setMessages((prev) => [...prev, newMessage]);
    setMessageIdCounter((prev) => prev + 1);
    return newMessage.id;
  };

  const addLoadingMessage = () => {
    const loadingMessage = {
      id: messageIdCounter,
      type: 'bot',
      response: {
        success: false,
        error: 'Searching drug database...',
      },
    };
    setMessages((prev) => [...prev, loadingMessage]);
    const currentId = messageIdCounter;
    setMessageIdCounter((prev) => prev + 1);
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
    if (response.success && response.match_type === 'exact' && response.drug_info) {
      const drugName = response.drug_info.drug_name || 'Unknown Drug';
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
    <div className="min-h-screen bg-linear-to-b from-blue-50 to-white">
      {/* Floating Sidebar Toggle Button (Mobile Only) */}
          {!isSidebarOpen && (
      <button
        onClick={() => setIsSidebarOpen(true)}
        className="md:hidden absolute left-4 bottom-24 z-90 w-14 h-14 bg-linear-to-br from-blue-500 to-blue-600 rounded-full shadow-lg flex items-center justify-center hover:scale-110 active:scale-95 transition-transform"
      >
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    )}


      {/* Desktop view : Header spans full width above everything */}
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

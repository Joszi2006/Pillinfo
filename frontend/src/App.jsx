import { useState } from 'react';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import ChatContainer from './components/layout/ChatContainer';
import InputArea from './components/layout/InputArea';
import SwipeHandler from './components/ui/SwipeHandler';
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

  // Add user message to chat
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

  // Add loading message
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

  // Replace loading message with actual response
  const replaceMessage = (messageId, response) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId
          ? { ...msg, response }
          : msg
      )
    );
  };

  // Add to recent matches if exact match
  const addToRecentMatches = (response, messageId) => {
    if (response.success && response.match_type === 'exact' && response.drug_info) {
      const drugName = response.drug_info.drug_name || 'Unknown Drug';
      
      // Check if already exists
      const exists = recentMatches.some(match => match.drugName === drugName);
      if (!exists) {
        setRecentMatches(prev => [
          { drugName, messageId },
          ...prev.slice(0, 9) // Keep max 10
        ]);
      }
    }
  };

  // Handle clicking on recent match
  const handleMatchClick = (match) => {
    // Close sidebar on mobile
    setIsSidebarOpen(false);
    
    // Scroll to that message in chat
    const messageElement = document.getElementById(`message-${match.messageId}`);
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  // Handle text message send
  const handleSendMessage = async (text) => {
    addUserMessage(text);
    const loadingId = addLoadingMessage();
    const response = await lookupByText(text);
    replaceMessage(loadingId, response);
    addToRecentMatches(response, loadingId);
  };

  // Handle image upload
  const handleUploadImages = async (images) => {
    const imageText = images.length > 1 
      ? `Uploaded ${images.length} images` 
      : 'Uploaded 1 image';
    addUserMessage(imageText);

    const loadingId = addLoadingMessage();
    const response = await lookupByImage(images);
    replaceMessage(loadingId, response);
    addToRecentMatches(response, loadingId);
  };

  // Handle quick action clicks
  const handleQuickAction = (action) => {
    if (typeof action === 'object') {
      if (action.type === 'upload') {
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
      {/* Swipe handler for mobile sidebar */}
      <SwipeHandler 
        onSwipeRight={() => setIsSidebarOpen(true)} 
        isEnabled={!isSidebarOpen}
      />

      {/* Header - Separate and fixed at top */}
      <Header />

      {/* Unified Container - Below header */}
      <div className="fixed top-[150px] left-1/2 -translate-x-1/2 w-[calc(100%-120px)] max-w-[1030px] h-[80vh] flex ">
        
        {/* Sidebar - Desktop always visible, Mobile overlay */}
        <Sidebar 
          recentMatches={recentMatches} 
          onMatchClick={handleMatchClick}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col bg-white shadow-md md:rounded-r-[20px] rounded-r-[20px] md:rounded-l-none overflow-hidden">
          
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

            {isLoading && (
              <div className="flex items-center gap-3 mb-5">
                <div className="w-11 h-11 rounded-full bg-linear-to-br from-blue-400 via-blue-500 to-blue-700 shadow-[0_4px_12px_rgba(37,99,235,0.25)] flex items-center justify-center animate-pulse">
                  <div className="w-3 h-3 bg-white rounded-full" />
                </div>
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
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
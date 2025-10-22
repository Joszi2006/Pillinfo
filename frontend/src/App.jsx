import { useState } from 'react';
import Header from './components/layout/Header';
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

  // Add bot response to chat
  const addBotMessage = (response) => {
    const newMessage = {
      id: messageIdCounter,
      type: 'bot',
      response,
    };
    setMessages((prev) => [...prev, newMessage]);
    setMessageIdCounter((prev) => prev + 1);
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
    setMessageIdCounter((prev) => prev + 1);
    return loadingMessage.id;
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

  // Handle text message send
  const handleSendMessage = async (text) => {
    // Add user message
    addUserMessage(text);

    // Add loading indicator
    const loadingId = addLoadingMessage();

    // Lookup drug
    const response = await lookupByText(text);

    // Replace loading with actual response
    replaceMessage(loadingId, response);
  };

  // Handle image upload
  const handleUploadImages = async (images) => {
    // Add user message indicating image upload
    const imageText = images.length > 1 
      ? `Uploaded ${images.length} images` 
      : 'Uploaded 1 image';
    addUserMessage(imageText);

    // Add loading indicator
    const loadingId = addLoadingMessage();

    // Lookup drug from images
    const response = await lookupByImage(images);

    // Replace loading with actual response
    replaceMessage(loadingId, response);
  };

  // Handle quick action clicks
  const handleQuickAction = (action) => {
    if (action === 'upload') {
      // Trigger file upload (handled by InputArea)
      return;
    }
    
    if (action === 'calculator') {
      // For now, just search for common calculation query
      handleSendMessage('Calculate dosage for Advil');
      return;
    }

    // Default: treat as drug search
    handleSendMessage(action);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <Header />
      
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
                  response={message.response}
                />
              );
            
            default:
              return null;
          }
        })}

        {/* Loading indicator (optional, if you want a separate one) */}
        {isLoading && (
          <div className="flex items-center gap-3 mb-5">
            <div className="w-11 h-11 rounded-full bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 shadow-[0_4px_12px_rgba(37,99,235,0.25)] flex items-center justify-center animate-pulse">
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

      <InputArea
        onSendMessage={handleSendMessage}
        onUploadImages={handleUploadImages}
      />
    </div>
  );
}

export default App;
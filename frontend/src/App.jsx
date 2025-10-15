import React, { useState, useRef, useEffect } from 'react';
import { Send, Pill, Upload, Camera, Loader2, AlertCircle, X, FileImage } from 'lucide-react';

// API Configuration
const API_BASE_URL = 'http://localhost:8001';

// API call to backend for text lookup
const searchDrugByText = async (query) => {
  const response = await fetch(`${API_BASE_URL}/lookup/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      text: query,
      use_ner: true
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to search drug');
  }
  
  const data = await response.json();
  
  // Transform backend response to frontend format
  if (data.success && data.best_match) {
    return {
      drug_name: data.brand_name,
      generic_name: data.best_match.generic_name || data.best_match.substance_name || 'N/A',
      purpose: data.best_match.indications_and_usage || 'Information not available',
      dosage: data.processed?.dosage || data.best_match.dosage || 'Consult healthcare provider',
      side_effects: data.best_match.adverse_reactions 
        ? [data.best_match.adverse_reactions] 
        : ['Information not available'],
      warnings: data.best_match.warnings || 'Consult healthcare provider for warnings',
      route: data.processed?.route || data.best_match.route || 'N/A',
      form: data.processed?.form || data.best_match.dosage_form || 'N/A'
    };
  }
  
  throw new Error(data.error || 'Drug not found');
};

// API call to backend for image lookup
const searchDrugByImage = async (imageFile, description = '') => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch(`${API_BASE_URL}/lookup/image`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('Failed to process image');
  }
  
  const data = await response.json();
  
  // Transform backend response to frontend format
  if (data.success && data.best_match) {
    return {
      drug_name: data.brand_name,
      generic_name: data.best_match.generic_name || data.best_match.substance_name || 'N/A',
      purpose: data.best_match.indications_and_usage || 'Information not available',
      dosage: data.processed?.dosage || data.best_match.dosage || 'Consult healthcare provider',
      side_effects: data.best_match.adverse_reactions 
        ? [data.best_match.adverse_reactions] 
        : ['Information not available'],
      warnings: data.best_match.warnings || 'Consult healthcare provider for warnings',
      route: data.processed?.route || data.best_match.route || 'N/A',
      form: data.processed?.form || data.best_match.dosage_form || 'N/A',
      ocr_text: data.ocr_result?.corrected_text || ''
    };
  }
  
  throw new Error(data.error || 'Drug not found in image');
};

function ChatMessage({ message, isBot }) {
  return (
    <div className={`flex gap-3 ${isBot ? 'justify-start' : 'justify-end'} mb-4`}>
      {isBot && (
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
          <Pill className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div className={`max-w-[75%] ${isBot ? 'bg-gray-50 border border-gray-200' : 'bg-blue-500'} rounded-2xl px-5 py-3 shadow-sm`}>
        {message.type === 'text' ? (
          <p className={`${isBot ? 'text-gray-800' : 'text-white'} leading-relaxed`}>{message.content}</p>
        ) : message.type === 'image_preview' ? (
          <div className="space-y-2">
            <img src={message.imageUrl} alt="Uploaded pill" className="rounded-lg max-w-full h-auto" />
            {message.caption && <p className="text-sm text-white">{message.caption}</p>}
          </div>
        ) : message.type === 'drug_info' ? (
          <div className="space-y-3">
            <div className="pb-3 border-b border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-1">{message.drug_name}</h3>
              <p className="text-blue-600 text-sm font-medium">{message.generic_name}</p>
            </div>
            
            <div>
              <p className="text-xs text-gray-500 font-semibold mb-1 uppercase tracking-wide">Purpose</p>
              <p className="text-gray-800 text-sm">{message.purpose}</p>
            </div>
            
            <div>
              <p className="text-xs text-gray-500 font-semibold mb-1 uppercase tracking-wide">Dosage</p>
              <p className="text-gray-800 text-sm">{message.dosage}</p>
            </div>
            
            {message.side_effects && (
              <div>
                <p className="text-xs text-gray-500 font-semibold mb-2 uppercase tracking-wide">Common Side Effects</p>
                <ul className="space-y-1">
                  {message.side_effects.map((effect, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                      {effect}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {message.warnings && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-3">
                <div className="flex gap-2 items-start">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-xs text-red-600 font-semibold mb-1">Important Warning</p>
                    <p className="text-sm text-red-700">{message.warnings}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : null}
      </div>
      
      {!isBot && (
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center shadow-lg">
          <span className="text-white font-semibold text-sm">You</span>
        </div>
      )}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3 justify-start mb-4">
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
        <Pill className="w-5 h-5 text-white" />
      </div>
      <div className="bg-gray-50 border border-gray-200 rounded-2xl px-5 py-4 shadow-sm">
        <div className="flex gap-1.5">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
}

function ImageOptionsModal({ onClose, onCamera, onUpload }) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-sm w-full shadow-2xl overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Add Image</h3>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="p-4 space-y-3">
          <button
            onClick={() => {
              onCamera();
              onClose();
            }}
            className="w-full flex items-center gap-4 p-4 bg-blue-50 hover:bg-blue-100 rounded-xl transition-all border-2 border-blue-200 hover:border-blue-300"
          >
            <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center">
              <Camera className="w-6 h-6 text-white" />
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-900">Take Photo</p>
              <p className="text-sm text-gray-600">Use your camera</p>
            </div>
          </button>

          <button
            onClick={() => {
              onUpload();
              onClose();
            }}
            className="w-full flex items-center gap-4 p-4 bg-gray-50 hover:bg-gray-100 rounded-xl transition-all border-2 border-gray-200 hover:border-gray-300"
          >
            <div className="w-12 h-12 rounded-full bg-gray-500 flex items-center justify-center">
              <FileImage className="w-6 h-6 text-white" />
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-900">Upload Photo</p>
              <p className="text-sm text-gray-600">Choose from gallery</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}

function ImagePreviewModal({ imageUrl, onClose, onSend, caption, setCaption }) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Review Image</h3>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="p-4">
          <img src={imageUrl} alt="Preview" className="w-full rounded-lg" />
          
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add description (optional)
            </label>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              placeholder="Describe the pill (color, shape, imprint)..."
              className="w-full border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={3}
            />
          </div>
        </div>
        
        <div className="p-4 bg-gray-50 border-t border-gray-200 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onSend}
            className="flex-1 px-4 py-3 bg-blue-500 rounded-lg font-medium text-white hover:bg-blue-600 transition-colors shadow-sm"
          >
            Identify Pill
          </button>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'text',
      content: '👋 Hi! I\'m your Drug Information Assistant. Ask me about any medication or upload a pill image to identify it!',
      isBot: true
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageCaption, setImageCaption] = useState('');
  const [showImageOptions, setShowImageOptions] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'text',
      content: input,
      isBot: false
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await searchDrugByText(input);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'drug_info',
        isBot: true,
        ...response
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'text',
        content: '❌ Sorry, I encountered an error. Please try again.',
        isBot: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      setImagePreview({
        url: event.target.result,
        file: file
      });
    };
    reader.readAsDataURL(file);
  };

  const handleImageSend = async () => {
    if (!imagePreview) return;

    const userMessage = {
      id: Date.now(),
      type: 'image_preview',
      imageUrl: imagePreview.url,
      caption: imageCaption || '📷 Uploaded pill image',
      isBot: false
    };

    setMessages(prev => [...prev, userMessage]);
    setImagePreview(null);
    setImageCaption('');
    setIsTyping(true);

    try {
      const response = await searchDrugByImage(imagePreview.file, imageCaption);
      const botMessage = {
        id: Date.now() + 1,
        type: 'drug_info',
        isBot: true,
        ...response
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'text',
        content: '❌ Failed to process image. Please try again.',
        isBot: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
            <Pill className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Pillinfo</h1>
            <p className="text-sm text-gray-500">No.1 Drug Informant</p>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-5xl mx-auto">
          {messages.map(message => (
            <ChatMessage key={message.id} message={message} isBot={message.isBot} />
          ))}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="bg-white border-t border-gray-200 px-6 py-4 shadow-lg">
        <div className="max-w-5xl mx-auto">
          <div className="flex gap-3 items-end">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="image/*"
              className="hidden"
            />
            
            <input
              type="file"
              ref={cameraInputRef}
              onChange={handleFileSelect}
              accept="image/*"
              capture="environment"
              className="hidden"
            />
            
            <button
              onClick={() => setShowImageOptions(true)}
              className="flex-shrink-0 w-12 h-12 rounded-xl bg-slate-900 hover:bg-slate-800 flex items-center justify-center transition-all active:scale-95 shadow-md border border-slate-700"
              title="Add image"
            >
              <Upload className="w-5 h-5 text-white" />
            </button>

            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about a medication..."
                rows={1}
                className="w-full bg-gray-50 border border-gray-300 rounded-xl px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none max-h-32"
                style={{ minHeight: '48px' }}
              />
            </div>

            <button
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className="flex-shrink-0 w-12 h-12 rounded-xl bg-slate-900 hover:bg-slate-800 flex items-center justify-center transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-slate-900 shadow-md border border-slate-700"
            >
              {isTyping ? (
                <Loader2 className="w-5 h-5 text-white animate-spin" />
              ) : (
                <Send className="w-5 h-5 text-white" />
              )}
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-3 text-center">
            Pillinfo can make mistakes. Verify important information with healthcare professionals.
          </p>
        </div>
      </div>

      {imagePreview && (
        <ImagePreviewModal
          imageUrl={imagePreview.url}
          onClose={() => {
            setImagePreview(null);
            setImageCaption('');
          }}
          onSend={handleImageSend}
          caption={imageCaption}
          setCaption={setImageCaption}
        />
      )}

      {showImageOptions && (
        <ImageOptionsModal
          onClose={() => setShowImageOptions(false)}
          onCamera={() => cameraInputRef.current?.click()}
          onUpload={() => fileInputRef.current?.click()}
        />
      )}
    </div>
  );
}
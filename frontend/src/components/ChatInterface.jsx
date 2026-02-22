import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';
import MessageBubble from './MessageBubble';
import LaptopCard from './LaptopCard';
import InputBox from './InputBox';
import { Loader2 } from 'lucide-react';

const ChatInterface = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, recommendations]);

  useEffect(() => {
    initializeChat();
  }, []);

  const initializeChat = async () => {
    try {
      setLoading(true);
      const response = await chatAPI.createSession();
      setSessionId(response.session_id);
      setMessages([
        { role: 'assistant', content: response.message }
      ]);
    } catch (error) {
      console.error('Error initializing chat:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (message) => {
    if (!sessionId) return;

    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(sessionId, message);
      
      // Add assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);

      // Check if we have recommendations
      if (response.intent_confirmed && response.recommendations && response.recommendations.length > 0) {
        setRecommendations(response.recommendations);
        setUserProfile(response.user_profile);
        
        console.log("✅ Recommendations received:", response.recommendations);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, there was an error processing your message. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 shadow-lg">
        <h1 className="text-2xl font-bold">💻 Laptop Recommendation Assistant</h1>
        <p className="text-sm text-blue-100">Find your perfect laptop with AI assistance</p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <MessageBubble
            key={index}
            message={msg.content}
            isUser={msg.role === 'user'}
          />
        ))}

        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-lg p-4 flex items-center space-x-2">
              <Loader2 className="animate-spin" size={20} />
              <span>Thinking...</span>
            </div>
          </div>
        )}

        {/* Recommendations Section */}
        {recommendations && recommendations.length > 0 && (
          <div className="mt-8">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-lg mb-6">
              <h2 className="text-2xl font-bold mb-2">🎉 Perfect Matches Found!</h2>
              <p className="text-blue-100">Based on your requirements, here are our top {recommendations.length} recommendations:</p>
              
              {userProfile && (
                <div className="mt-4 bg-white/10 backdrop-blur rounded-lg p-4">
                  <h3 className="font-semibold mb-2">Your Profile:</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                    {Object.entries(userProfile).map(([key, value]) => (
                      <div key={key} className="bg-white/10 rounded px-3 py-1">
                        <span className="font-medium capitalize">{key}:</span> {value}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((laptop, index) => (
                <LaptopCard key={index} laptop={laptop} rank={index + 1} />
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <InputBox onSendMessage={handleSendMessage} disabled={loading} />
    </div>
  );
};

export default ChatInterface;
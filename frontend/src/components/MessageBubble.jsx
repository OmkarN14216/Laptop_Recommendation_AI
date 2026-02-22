import React from 'react';
import { User, Bot } from 'lucide-react';

const MessageBubble = ({ message, isUser }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-start max-w-[70%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500' : 'bg-gray-700'
          }`}>
            {isUser ? <User size={20} color="white" /> : <Bot size={20} color="white" />}
          </div>
        </div>
        <div className={`rounded-lg p-4 ${
          isUser 
            ? 'bg-blue-500 text-white' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          <p className="whitespace-pre-wrap">{message}</p>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
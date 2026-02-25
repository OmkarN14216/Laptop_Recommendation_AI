import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import MessageBubble from './MessageBubble'
import LaptopCard from './LaptopCard'
import { chatAPI } from '../services/api'
import './ChatInterface.css'

const QUICK_PROMPTS = [
  'Gaming under ₹1500',
  'Lightweight for travel',
  'Software Development',
]

export default function ChatInterface() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [recommendations, setRecommendations] = useState([])
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => { initializeChat() }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, recommendations])

  const initializeChat = async () => {
    setMessages([])
    setRecommendations([])
    setError(null)
    try {
      const data = await chatAPI.createSession()
      setSessionId(data.session_id)
      setMessages([{
        role: 'assistant',
        content: "Hello! I'm your AI Laptop Assistant. I can help you find the perfect machine for your needs. What's your budget and typical usage?",
        timestamp: Date.now(),
      }])
    } catch (err) {
      setError('Failed to connect to backend. Please ensure the server is running on port 8000.')
    }
  }

  const handleSend = async (text) => {
    const msgText = (text || input).trim()
    if (!msgText || loading) return

    setMessages(prev => [...prev, { role: 'user', content: msgText, timestamp: Date.now() }])
    setInput('')
    setLoading(true)
    setRecommendations([])

    try {
      const data = await chatAPI.sendMessage(sessionId, msgText)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.message || data.response,
        timestamp: Date.now(),
      }])
      if (data.recommendations?.length > 0) {
        setRecommendations(data.recommendations)
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: Date.now(),
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-root">

      {/* Sidebar */}
      <aside className="sidebar">
        <button className="sidebar-back-btn" onClick={() => navigate('/')}>← Back to Home</button>
        <button className="sidebar-new-btn" onClick={initializeChat}>+ New Search</button>

        <div className="sidebar-section">
          <p className="sidebar-label">QUICK PROMPTS</p>
          {QUICK_PROMPTS.map(p => (
            <button key={p} className="sidebar-item" onClick={() => handleSend(p)}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4F8EF7" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
              {p}
            </button>
          ))}
        </div>

        <div className="upgrade-box">
          <div className="upgrade-title">Unlock Advanced Specs</div>
          <button className="upgrade-btn">Upgrade to Pro</button>
        </div>
      </aside>

      {/* Main */}
      <main className="chat-main">

        {/* Top bar */}
        <div className="top-bar">
          <div className="top-bar-left">
            <div className="top-bar-logo-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <rect x="2" y="3" width="20" height="14" rx="2" stroke="#4F8EF7" strokeWidth="2"/>
                <path d="M8 21h8M12 17v4" stroke="#4F8EF7" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <span className="top-bar-title">Laptop Assistant <span>AI</span></span>
          </div>
          <div className="top-bar-right">
            <a href="#" className="top-bar-link">Compare</a>
            <a href="#" className="top-bar-link">Top Picks 2024</a>
            <a href="#" className="top-bar-link">Deals</a>
            <div className="settings-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
              </svg>
            </div>
            <div className="user-badge">JD</div>
          </div>
        </div>

        {/* Messages */}
        <div className="messages-area">
          {error && <div className="error-banner">{error}</div>}

          {messages.map((msg, i) => <MessageBubble key={i} message={msg} />)}

          {recommendations.length > 0 && (
            <div className="recommendations-section">
              <p className="reco-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#4F8EF7">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                Top recommendations for you
              </p>
              {recommendations.map((laptop, i) => (
                <LaptopCard key={i} laptop={laptop} rank={i} score={laptop.score || 7} />
              ))}
            </div>
          )}

          {loading && (
            <div className="typing-row">
              <div className="bot-avatar">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="7" width="20" height="12" rx="3" fill="#4F8EF7"/>
                  <circle cx="9" cy="13" r="1.5" fill="white"/>
                  <circle cx="15" cy="13" r="1.5" fill="white"/>
                </svg>
              </div>
              <div className="typing-bubble">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              className="chat-textarea"
              placeholder="Tell me your budget and usage..."
              value={input}
              onChange={e => {
                setInput(e.target.value);
                const el = inputRef.current;
                el.style.height = 'auto';
                el.style.height = el.scrollHeight + 'px';
              }
              }
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <div className="input-actions">
              <button className="icon-btn" title="Attach">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                  <path d="m21.44 11.05-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/>
                </svg>
              </button>
              <button className="icon-btn" title="Voice">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                  <path d="M12 2a3 3 0 013 3v7a3 3 0 01-6 0V5a3 3 0 013-3z"/>
                  <path d="M19 10v2a7 7 0 01-14 0v-2M12 19v3M8 22h8"/>
                </svg>
              </button>
              <button
                className="send-btn"
                onClick={() => handleSend()}
                disabled={!input.trim() || loading}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                  <path d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z"/>
                </svg>
              </button>
            </div>
          </div>
          <p className="chat-footer">LAPTOP ASSISTANT AI VERSION 2.4 | POWERED BY Grok</p>
        </div>

      </main>
    </div>
  )
}
import './MessageBubble.css'

export default function MessageBubble({ message }) {
  const isUser   = message.role === 'user'
  const isSystem = message.role === 'system'

  if (isSystem) {
    return (
      <div className="system-msg">
        <span className="system-dot" />
        {message.content}
      </div>
    )
  }

  const time = new Date(message.timestamp || Date.now())
    .toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  return (
    <div className={`msg-row ${isUser ? 'user' : 'bot'}`}>
      {!isUser && (
        <div className="bot-avatar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <rect x="2" y="7" width="20" height="12" rx="3" fill="#4F8EF7"/>
            <path d="M8 7V5a4 4 0 018 0v2" stroke="#4F8EF7" strokeWidth="2"/>
            <circle cx="9" cy="13" r="1.5" fill="white"/>
            <circle cx="15" cy="13" r="1.5" fill="white"/>
          </svg>
        </div>
      )}

      <div className={`msg-bubble ${isUser ? 'user' : 'bot'}`}>
        <p className="msg-text">{message.content}</p>
        <span className="msg-time">{time}</span>
      </div>

      {isUser && (
        <div className="user-avatar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="8" r="4" fill="white"/>
            <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" fill="white"/>
          </svg>
        </div>
      )}
    </div>
  )
}
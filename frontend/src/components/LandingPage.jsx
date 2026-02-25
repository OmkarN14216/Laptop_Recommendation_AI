import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './LandingPage.css'

const BRANDS = ['ASUS', 'DELL', 'APPLE', 'LENOVO', 'HP', 'RAZER']

const FEATURES = [
  { icon: '🤖', title: 'AI-Powered Matching',  desc: 'Our model understands your workflow, not just specs' },
  { icon: '⚡', title: 'Instant Results',       desc: 'Get top 3 recommendations in under 10 seconds' },
  { icon: '🎯', title: 'Precision Scoring',     desc: '9-feature scoring system tailored to your needs' },
  { icon: '💰', title: 'Budget Aware',          desc: 'Always respects your INR budget ceiling' },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const [loaded, setLoaded] = useState(false)
  const [mouseOffset, setMouseOffset] = useState({ x: 0, y: 0 })
  const heroRef = useRef(null)

  useEffect(() => {
    const t = setTimeout(() => setLoaded(true), 100)
    return () => clearTimeout(t)
  }, [])

  const handleMouseMove = (e) => {
    if (!heroRef.current) return
    const rect = heroRef.current.getBoundingClientRect()
    setMouseOffset({
      x: ((e.clientX - rect.left) / rect.width - 0.5) * 20,
      y: ((e.clientY - rect.top)  / rect.height - 0.5) * 20,
    })
  }

  return (
    <div className="landing-root">

      <nav className="nav">
        <div className="nav-logo">
          <div className="nav-logo-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <rect x="2" y="3" width="20" height="14" rx="2" stroke="#4F8EF7" strokeWidth="2"/>
              <path d="M8 21h8M12 17v4" stroke="#4F8EF7" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <span className="nav-logo-text">Laptops<span>AI</span></span>
        </div>
        <div className="nav-links">
          {['Features', 'How It Works', 'Compare', 'Reviews'].map(item => (
            <a key={item} href="#">{item}</a>
          ))}
        </div>
        <button className="nav-cta" onClick={() => navigate('/chat')}>Launch App</button>
      </nav>

      <section className="hero" ref={heroRef} onMouseMove={handleMouseMove}>
        <div className="hero-grid-bg" />
        <div className="hero-glow-1" />
        <div className="hero-glow-2" />

        <div className={`hero-content ${loaded ? 'loaded' : ''}`}>
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            NOW POWERED BY Grok
          </div>
          <h1 className="hero-title">
            <span className="dim">Find Your</span><br />
            <span className="white">Perfect</span><br />
            <span className="white">Laptop </span>
            <span className="blue">with AI</span>
          </h1>
          <p className="hero-subtitle">
            Skip the endless spec sheets and confusing benchmarks.<br />
            Tell our AI how you work, play, and create, and get a tailored<br />
            recommendation in seconds.
          </p>
          <div className="hero-ctas">
            <button className="btn-primary" onClick={() => navigate('/chat')}>Start Chat Now →</button>
            
          </div>
          <div className="social-proof">
            <div className="avatar-stack">
              <div className="avatar" style={{ background: '#4F8EF7' }} />
              <div className="avatar" style={{ background: '#7C3AED' }} />
              <div className="avatar" style={{ background: '#059669' }} />
            </div>
            <span className="social-text">Joined by <strong>12,000+</strong> users this month</span>
          </div>
        </div>

        <div
          className={`laptop-mockup ${loaded ? 'loaded' : ''}`}
          style={{
            transform: `perspective(1000px) rotateY(${-mouseOffset.x * 0.5}deg) rotateX(${mouseOffset.y * 0.3}deg)`,
          }}
        >
          <div className="mockup-screen">
            <div className="mockup-glow" />
            <div className="mockup-nebula" />
            <div className="mockup-bar">
              <div className="mockup-bar-label">LIVE ANALYSIS</div>
              <div className="mockup-progress-bg">
                <div className="mockup-progress-fill" />
              </div>
              <div className="mockup-bar-sub">Scanning RTX 4080 performance benchmarks...</div>
            </div>
          </div>
          <div className="mockup-base" />
        </div>
      </section>

      <div className="brand-strip">
        <p className="brand-label">ANALYZING HARDWARE FROM TOP MANUFACTURERS</p>
        <div className="brand-logos">
          {BRANDS.map(b => <span key={b} className="brand-name">{b}</span>)}
        </div>
      </div>

      <section className="features-grid">
        {FEATURES.map((f, i) => (
          <div key={i} className="feature-card">
            <div className="feature-icon">{f.icon}</div>
            <h3 className="feature-title">{f.title}</h3>
            <p className="feature-desc">{f.desc}</p>
          </div>
        ))}
      </section>

    </div>
  )
}
import { useState } from 'react'
import './LaptopCard.css'
import { chatAPI } from '../services/api'

export default function LaptopCard({ laptop, rank, score }) {
  const [expanded, setExpanded]       = useState(false)
  const [prices, setPrices]           = useState(null)
  const [priceLoading, setPriceLoading] = useState(false)
  const [priceError, setPriceError]   = useState(null)

  const isBestMatch = rank === 0

  const name  = laptop.brand + ' ' + laptop.model_name ||laptop.Name  || laptop.name  || laptop.laptop_name|| laptop.laptopName || 'Laptop' 
  const price = (laptop.Price || laptop.price)
    ? `₹${Number(laptop.Price || laptop.price).toLocaleString('en-IN')}`
    : 'N/A'

  const specs = [
    laptop.Processor || laptop.processor,
    laptop.RAM       || laptop.ram,
    laptop.Storage   || laptop.storage,
    laptop.Display   || laptop.display,
  ].filter(Boolean)

  const handleComparePrices = async () => {
    if (prices) { setPrices(null); return }
    setPriceLoading(true)
    setPriceError(null)
    try {
      const data = await chatAPI.scrapePrices(name)
      setPrices(data.prices)
    } catch (err) {
      setPriceError('Failed to fetch prices. Please try again.')
    } finally {
      setPriceLoading(false)
    }
  }

  const SITE_META = {
    flipkart: { label: 'Flipkart', color: '#2874f0', icon: '🛒' },
   
    croma:    { label: 'Croma',    color: '#6f2da8', icon: '🏪' },
  }

  return (
    <div className={`laptop-card ${isBestMatch ? 'best-match' : ''}`}>
      {isBestMatch && <div className="best-badge">BEST MATCH</div>}

      <div className="card-top">
        <div className={`card-image ${isBestMatch ? 'best' : ''}`}>
          <svg width="60" height="45" viewBox="0 0 60 45" fill="none">
            <rect x="5" y="2" width="50" height="32" rx="3" fill="#1e293b"
              stroke={isBestMatch ? '#4F8EF7' : '#334155'} strokeWidth="1.5"/>
            <rect x="8" y="5" width="44" height="26" rx="1"
              fill={isBestMatch ? 'rgba(79,142,247,0.1)' : '#0f172a'}/>
            <rect x="0" y="34" width="60" height="8" rx="2" fill="#1e293b" stroke="#334155" strokeWidth="1"/>
            <rect x="22" y="36" width="16" height="3" rx="1" fill="#334155"/>
          </svg>
        </div>

        <div className="card-info">
          <div className="card-header">
            <h3 className="laptop-name">{name}</h3>
            <span className="laptop-price">{price}</span>
          </div>

          <div className="score-row">
            <span className="score-label">Match Score</span>
            <div className="score-bar-bg">
              <div className="score-bar-fill" style={{ width: `${(score / 9) * 100}%` }} />
            </div>
            <span className="score-value">{score}/9</span>
          </div>

          <div className="specs-grid">
            {specs.slice(0, 4).map((spec, i) => (
              <div key={i} className="spec-pill">
                <span className="spec-dot" />
                <span className="spec-text">{spec}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="card-actions">
        <button
          className={`view-btn ${isBestMatch ? 'primary' : ''}`}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Hide Details' : 'View Detailed Specs'}
        </button>

        <button
          className={`compare-btn ${prices ? 'active' : ''}`}
          onClick={handleComparePrices}
          disabled={priceLoading}
        >
          {priceLoading ? (
            <span className="compare-loading">
              <span className="spinner" /> Scraping...
            </span>
          ) : prices ? '✕ Hide Prices' : '🔍 Compare Prices'}
        </button>

        <button className="bookmark-btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/>
          </svg>
        </button>
      </div>

      {/* Specs expanded */}
      {expanded && (
        <div className="expanded-section">
          {Object.entries(laptop)
            .filter(([k]) => !['_id', 'laptop_feature'].includes(k))
            .slice(0, 8)
            .map(([key, val]) => (
              <div key={key} className="expanded-row">
                <span className="expanded-key">{key.replace(/_/g, ' ')}</span>
                <span className="expanded-val">{String(val)}</span>
              </div>
            ))}
        </div>
      )}

      {/* Price comparison */}
      {priceError && (
        <div className="price-error">{priceError}</div>
      )}

      {prices && !priceError && (
        <div className="price-comparison">
          <p className="price-comparison-title">Live Price Comparison</p>
          {Object.entries(SITE_META).map(([site, meta]) => {
            const siteResults = prices[site] || []
            return (
              <div key={site} className="price-site-block">
                <div className="price-site-header" style={{ borderColor: meta.color }}>
                  <span className="price-site-icon">{meta.icon}</span>
                  <span className="price-site-name" style={{ color: meta.color }}>{meta.label}</span>
                  <span className="price-site-count">{siteResults.length} result{siteResults.length !== 1 ? 's' : ''}</span>
                </div>

                {siteResults.length === 0 ? (
                  <div className="price-no-results">No results found</div>
                ) : (
                  siteResults.map((item, i) => (
                    <div key={i} className="price-item">
                      <div className="price-item-left">
                        {i === 0 && <span className="price-rank-badge">Lowest</span>}
                        <span className="price-item-name">{item.name}</span>
                      </div>
                      <div className="price-item-right">
                        <span className="price-item-price">{item.price}</span>
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="price-buy-btn"
                          style={{ background: meta.color }}
                        >
                          Buy →
                        </a>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
import React from 'react';

export default function Navbar({ activeTab, onTabChange }) {
  return (
    <header>
      <div className="header-inner">
        <div className="brand">
          <div className="brick-icon">🧱</div>
          <div className="brand-text">
            <h1>LEGO Radar</h1>
          </div>
          <span className="brand-badge">India</span>
        </div>

        {/* Primary Tabs */}
        <nav className="main-tabs" aria-label="Main Navigation">
          <button
            className={`tab-btn ${activeTab === 'deals' ? 'active' : ''}`}
            onClick={() => onTabChange('deals')}
          >
            <span>🔥</span>
            <span>40%–50% Deals</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'cars' ? 'active active-cars' : ''}`}
            onClick={() => onTabChange('cars')}
          >
            <span>🏎️</span>
            <span>LEGO Cars & F1</span>
          </button>
        </nav>

        {/* Direct Store Links */}
        <div className="header-links">
          <a
            href="https://www.amazon.in/s?k=lego&rh=p_89%3ALEGO%2Cp_n_pct-off-with-tax%3A2665402031"
            target="_blank"
            rel="noopener noreferrer"
            className="direct-btn direct-amazon"
          >
            <span>🛒 Amazon Deals</span> ↗
          </a>
          <a
            href="https://www.flipkart.com/search?q=lego&p%5B%5D=facets.discount_range_v1%255B%255D%3D40%2525%2Bor%2Bmore"
            target="_blank"
            rel="noopener noreferrer"
            className="direct-btn direct-flipkart"
          >
            <span>🛍️ Flipkart Deals</span> ↗
          </a>
        </div>
      </div>
    </header>
  );
}

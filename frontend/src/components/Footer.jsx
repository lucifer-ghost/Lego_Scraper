import React from 'react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-inner">
        {/* Left / Main Section: Brand & Description */}
        <div className="footer-col-main">
          <div className="footer-brand">
            <span className="footer-logo">🧱</span>
            <span className="footer-title">LEGO Deal Radar</span>
            <span className="footer-country-badge">India</span>
          </div>
          <p className="footer-desc">
            Autonomous multi-store intelligence tracking authentic LEGO® sets, Speed Champions, and Formula 1 racers across India's top retailers.
          </p>
          
          {/* Live Store Chips */}
          <div className="footer-stores">
            <span className="footer-store-chip amazon">
              <span className="dot" /> Amazon.in
            </span>
            <span className="footer-store-chip flipkart">
              <span className="dot" /> Flipkart
            </span>
            <span className="footer-store-chip hamleys">
              <span className="dot" /> Hamleys India
            </span>
            <span className="footer-store-chip mybrickhouse">
              <span className="dot" /> MyBrickHouse
            </span>
          </div>
        </div>

        {/* Center / Feature Highlights */}
        <div className="footer-col-features">
          <h4 className="footer-col-title">Radar Capabilities</h4>
          <ul className="footer-features-list">
            <li>⚡ Real-time price tracking & verification</li>
            <li>🏎️ Dedicated F1 & Speed Champions catalog</li>
            <li>🛡️ 100% Genuine LEGO filtering</li>
            <li>💰 Savings & discount calculator</li>
            <li>📥 1-Click CSV data export</li>
          </ul>
        </div>

        {/* Right End: Created by GHOST & Details */}
        <div className="footer-col-right">
          <div className="creator-card">
            <div className="creator-badge-wrap">
              <span className="creator-ghost-icon">👻</span>
              <div className="creator-text-block">
                <span className="creator-sub">PROJECT ARCHITECT</span>
                <span className="creator-name">Created by <strong className="ghost-highlight">GHOST</strong></span>
              </div>
            </div>
            <p className="creator-status">
              <span className="pulse-indicator" /> System Online & Tracking
            </p>
          </div>

          <div className="footer-copyright">
            © {currentYear} LEGO Deal Radar India.
          </div>
        </div>
      </div>

      {/* Bottom Legal Disclaimer */}
      <div className="footer-bottom-bar">
        <p className="footer-disclaimer">
          <strong>Disclaimer:</strong> LEGO® is a trademark of the LEGO Group of companies, which does not sponsor, authorize, or endorse this application. 
          All product names, logos, and brands are property of their respective owners. Prices and availability are subject to real-time retailer updates.
        </p>
      </div>
    </footer>
  );
}

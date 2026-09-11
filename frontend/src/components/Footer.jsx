import React from 'react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer app-footer-fixed" aria-label="Application Footer">
      <div className="footer-bar-inner">
        {/* Left: Compact Brand & Retailers */}
        <div className="footer-bar-left">
          <span className="footer-bar-logo">🧱</span>
          <span className="footer-bar-title">LEGO Radar</span>
          <span className="footer-bar-badge">India</span>
          <span className="footer-bar-sep">•</span>
          <span className="footer-bar-stores">Amazon • Flipkart • Hamleys • MyBrickHouse</span>
        </div>

        {/* Right: Created by GHOST & System Pulse */}
        <div className="footer-bar-right">
          <div className="creator-bar-pill">
            <span className="creator-ghost-icon">👻</span>
            <span className="creator-bar-text">
              Created by <strong className="ghost-highlight">GHOST</strong>
            </span>
            <span className="pulse-indicator" title="System Online &amp; Tracking" />
          </div>
          <span className="footer-bar-copy">© {currentYear}</span>
        </div>
      </div>
    </footer>
  );
}



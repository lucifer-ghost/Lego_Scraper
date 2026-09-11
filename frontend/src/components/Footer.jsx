import React from 'react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-compact-inner">
        {/* Left: Brand Identity & Concise Info */}
        <div className="footer-compact-left">
          <div className="footer-brand-row">
            <span className="footer-logo">🧱</span>
            <span className="footer-title">LEGO Deal Radar</span>
            <span className="footer-country-badge">India</span>
          </div>
          <p className="footer-compact-desc">
            Autonomous multi-store intelligence across Amazon, Flipkart, Hamleys &amp; MyBrickHouse. Enthusiast tracker, not affiliated with the LEGO Group.
          </p>
        </div>

        {/* Right: Created by GHOST & Status */}
        <div className="footer-compact-right">
          <div className="creator-compact-badge">
            <span className="creator-ghost-icon">👻</span>
            <div className="creator-compact-text">
              <span className="creator-sub">PROJECT ARCHITECT</span>
              <span className="creator-name">
                Created by <strong className="ghost-highlight">GHOST</strong>
              </span>
            </div>
            <span className="pulse-indicator" title="System Online &amp; Tracking" />
          </div>
          <span className="footer-compact-copyright">© {currentYear} LEGO Radar</span>
        </div>
      </div>
    </footer>
  );
}


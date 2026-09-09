"""
LEGO Deal Finder Web Dashboard
Serves an interactive web interface on http://localhost:5000.
Requires only standard Python library + scraper.py.
"""

import sys
import os
import json
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading
from scraper import get_lego_deals, get_lego_cars

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LEGO Deal Radar - 40% to 50% Off Deals Finder</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: rgba(22, 27, 39, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --card-hover-border: rgba(255, 193, 7, 0.4);
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --lego-yellow: #ffc107;
      --lego-red: #ef4444;
      --amazon-orange: #ff9900;
      --flipkart-blue: #2874f0;
      --discount-green: #10b981;
      --accent: #6366f1;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      background-image: 
        radial-gradient(circle at 10% 20%, rgba(255, 193, 7, 0.05) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.06) 0%, transparent 40%),
        linear-gradient(to bottom, #090d16, #0b0f19);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
    }

    header {
      border-bottom: 1px solid var(--card-border);
      background: rgba(11, 15, 25, 0.85);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 16px 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brick-icon {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #ffc107, #f59e0b);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
    }

    .brand h1 {
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      background: linear-gradient(to right, #ffffff, #cbd5e1);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand span {
      font-size: 0.8rem;
      background: rgba(255, 193, 7, 0.15);
      color: var(--lego-yellow);
      padding: 3px 8px;
      border-radius: 999px;
      font-weight: 600;
      border: 1px solid rgba(255, 193, 7, 0.3);
    }

    .header-links {
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .direct-btn {
      text-decoration: none;
      font-size: 0.82rem;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .direct-amazon {
      background: rgba(255, 153, 0, 0.12);
      color: #ffaa22;
      border: 1px solid rgba(255, 153, 0, 0.3);
    }
    .direct-amazon:hover {
      background: rgba(255, 153, 0, 0.25);
      transform: translateY(-1px);
    }

    .direct-flipkart {
      background: rgba(40, 116, 240, 0.12);
      color: #60a5fa;
      border: 1px solid rgba(40, 116, 240, 0.3);
    }
    .direct-flipkart:hover {
      background: rgba(40, 116, 240, 0.25);
      transform: translateY(-1px);
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 32px 24px 64px;
    }

    /* Control Panel */
    .controls-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 32px;
      backdrop-filter: blur(16px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .controls-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 20px;
      align-items: end;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .form-group label {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
    }

    .form-group label span.value-badge {
      color: var(--lego-yellow);
      font-family: 'JetBrains Mono', monospace;
    }

    input[type="range"] {
      accent-color: var(--lego-yellow);
      height: 6px;
      background: #1e293b;
      border-radius: 4px;
      cursor: pointer;
    }

    select, input[type="text"] {
      background: #0f172a;
      border: 1px solid #334155;
      color: #fff;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.2s;
    }
    select:focus, input[type="text"]:focus {
      border-color: var(--lego-yellow);
    }

    /* Modern Accessible Toggle Switch */
    .toggle-wrapper {
      display: flex;
      align-items: center;
      gap: 12px;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 0 14px;
      cursor: pointer;
      transition: all 0.2s ease;
      user-select: none;
      height: 44px;
    }
    .toggle-wrapper:hover {
      border-color: rgba(255, 193, 7, 0.4);
      background: rgba(15, 23, 42, 0.9);
    }
    .toggle-wrapper input[type="checkbox"] {
      appearance: none;
      -webkit-appearance: none;
      width: 40px;
      height: 22px;
      background: #334155;
      border-radius: 20px;
      position: relative;
      outline: none;
      cursor: pointer;
      transition: background 0.25s ease;
      flex-shrink: 0;
      margin: 0;
    }
    .toggle-wrapper input[type="checkbox"]::before {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      top: 3px;
      left: 3px;
      background: #cbd5e1;
      transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), background 0.25s;
    }
    .toggle-wrapper input[type="checkbox"]:checked {
      background: linear-gradient(135deg, #ffc107, #f59e0b);
    }
    .toggle-wrapper input[type="checkbox"]:checked::before {
      transform: translateX(18px);
      background: #0b0f19;
    }
    .toggle-text {
      font-size: 0.88rem;
      font-weight: 600;
      color: #f1f5f9;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .toggle-status {
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      margin-left: auto;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .status-active {
      color: var(--lego-yellow);
      background: rgba(255, 193, 7, 0.12);
      border: 1px solid rgba(255, 193, 7, 0.25);
    }
    .status-inactive {
      color: #64748b;
      background: rgba(100, 116, 139, 0.12);
      border: 1px solid rgba(100, 116, 139, 0.2);
    }

    .btn-scan {
      background: linear-gradient(135deg, #ffc107, #f59e0b);
      color: #0b0f19;
      border: none;
      padding: 12px 24px;
      border-radius: 10px;
      font-weight: 800;
      font-size: 0.95rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 18px rgba(245, 158, 11, 0.4);
      transition: all 0.2s ease;
      height: 44px;
    }
    .btn-scan:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 22px rgba(245, 158, 11, 0.55);
    }
    .btn-scan:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    /* Stats bar */
    .stats-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 24px;
      padding: 16px 20px;
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--card-border);
      border-radius: 12px;
    }

    .stats-chips {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
      align-items: center;
    }

    .stat-chip {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.88rem;
    }
    .stat-chip .stat-label { color: var(--text-muted); }
    .stat-chip .stat-val { font-weight: 700; color: #fff; font-family: 'JetBrains Mono', monospace; }
    .stat-chip.savings .stat-val { color: var(--discount-green); }

    .brand-filter-indicator {
      font-size: 0.78rem;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(255, 193, 7, 0.15);
      color: var(--lego-yellow);
      border: 1px solid rgba(255, 193, 7, 0.3);
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .action-tools {
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .btn-outline {
      background: transparent;
      border: 1px solid #334155;
      color: #cbd5e1;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .btn-outline:hover {
      background: #1e293b;
      border-color: #475569;
      color: #fff;
    }

    /* Deals Grid */
    .deals-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 24px;
    }

    .deal-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: all 0.25s ease;
      position: relative;
      backdrop-filter: blur(10px);
    }
    .deal-card:hover {
      transform: translateY(-4px);
      border-color: var(--card-hover-border);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
    }

    .card-thumb {
      width: 100%;
      height: 220px;
      background: #ffffff;
      padding: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
    }
    .card-thumb img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      transition: transform 0.3s ease;
    }
    .deal-card:hover .card-thumb img {
      transform: scale(1.05);
    }

    .badge-discount {
      position: absolute;
      top: 12px;
      left: 12px;
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      font-weight: 800;
      font-size: 0.8rem;
      padding: 5px 10px;
      border-radius: 6px;
      box-shadow: 0 4px 10px rgba(16, 185, 129, 0.4);
      letter-spacing: -0.01em;
    }

    .badge-platform {
      position: absolute;
      top: 12px;
      right: 12px;
      font-weight: 700;
      font-size: 0.72rem;
      padding: 4px 8px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .badge-amazon {
      background: rgba(255, 153, 0, 0.9);
      color: #0b0f19;
    }
    .badge-flipkart {
      background: rgba(40, 116, 240, 0.9);
      color: #fff;
    }

    .card-body {
      padding: 18px;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
      gap: 12px;
    }

    .product-title {
      font-size: 0.92rem;
      font-weight: 600;
      color: #f1f5f9;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      min-height: 2.8em;
    }

    .price-row {
      display: flex;
      align-items: baseline;
      gap: 8px;
      flex-wrap: wrap;
    }

    .current-price {
      font-size: 1.35rem;
      font-weight: 800;
      color: #fff;
      font-family: 'JetBrains Mono', monospace;
    }

    .mrp {
      font-size: 0.88rem;
      color: #64748b;
      text-decoration: line-through;
      font-family: 'JetBrains Mono', monospace;
    }

    .savings-pill {
      font-size: 0.78rem;
      color: var(--discount-green);
      font-weight: 700;
      background: rgba(16, 185, 129, 0.12);
      padding: 2px 8px;
      border-radius: 4px;
      border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .card-footer {
      margin-top: auto;
      padding-top: 12px;
      border-top: 1px solid var(--card-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .rating-text {
      font-size: 0.78rem;
      color: #f59e0b;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .btn-buy {
      background: #1e293b;
      color: #fff;
      text-decoration: none;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .btn-buy:hover {
      background: var(--lego-yellow);
      color: #0b0f19;
      border-color: var(--lego-yellow);
    }

    /* Empty state */
    .empty-state {
      grid-column: 1 / -1;
      text-align: center;
      padding: 64px 24px;
      background: var(--card-bg);
      border: 1px dashed #334155;
      border-radius: 16px;
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 12px; }
    .empty-state h3 { font-size: 1.2rem; margin-bottom: 8px; }
    .empty-state p { color: var(--text-muted); font-size: 0.9rem; max-width: 480px; margin: 0 auto; }

    /* Spinner */
    .spinner {
      display: inline-block;
      width: 18px;
      height: 18px;
      border: 2px solid rgba(11, 15, 25, 0.3);
      border-radius: 50%;
      border-top-color: #0b0f19;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brick-icon">🧱</div>
      <div>
        <h1>LEGO Deal Radar</h1>
      </div>
      <span>India Edition</span>
    </div>
    <div class="header-links">
      <a href="https://www.amazon.in/s?k=lego&rh=p_89%3ALEGO%2Cp_n_pct-off-with-tax%3A2665402031" target="_blank" class="direct-btn direct-amazon">
        <span>🛒 Amazon.in (35%+ Deals)</span> ↗
      </a>
      <a href="https://www.flipkart.com/search?q=lego&p%5B%5D=facets.discount_range_v1%255B%255D%3D40%2525%2Bor%2Bmore" target="_blank" class="direct-btn direct-flipkart">
        <span>🛍️ Flipkart (40%+ Deals)</span> ↗
      </a>
    </div>
  </header>

  <div class="container">

    <!-- Filter & Control Panel -->
    <div class="controls-card">
      <div class="controls-grid">
        
        <div class="form-group">
          <label>
            <span>Min Discount</span>
            <span class="value-badge" id="minDiscVal">40%</span>
          </label>
          <input type="range" id="minDisc" min="10" max="80" value="40" oninput="updateRangeValues()">
        </div>

        <div class="form-group">
          <label>
            <span>Max Discount</span>
            <span class="value-badge" id="maxDiscVal">50%</span>
          </label>
          <input type="range" id="maxDisc" min="20" max="90" value="50" oninput="updateRangeValues()">
        </div>

        <div class="form-group">
          <label>Platform</label>
          <select id="platformSelect">
            <option value="both" selected>Both (Amazon & Flipkart)</option>
            <option value="amazon">Amazon.in Only</option>
            <option value="flipkart">Flipkart Only</option>
          </select>
        </div>

        <div class="form-group">
          <label>Scan Depth</label>
          <select id="pagesSelect">
            <option value="7" selected>All Pages (~7 Pages - Full Catalog)</option>
            <option value="3">3 Pages (Fast Scan ~8s)</option>
            <option value="1">1 Page (Quick Preview ~3s)</option>
          </select>
        </div>

        <!-- Official LEGO Brand Toggle (Checked by default) -->
        <div class="form-group">
          <label>Brand Authenticity</label>
          <label class="toggle-wrapper" for="officialCheckbox">
            <input type="checkbox" id="officialCheckbox" checked onchange="updateToggleState()">
            <span class="toggle-text">🛡️ Official LEGO Only</span>
            <span class="toggle-status status-active" id="toggleStatus">ACTIVE</span>
          </label>
        </div>

        <div class="form-group">
          <button id="scanBtn" class="btn-scan" onclick="startScan()">
            <span id="btnIcon">🔍</span>
            <span id="btnText">Find LEGO Deals</span>
          </button>
        </div>

      </div>
    </div>

    <!-- Stats & Toolbar -->
    <div class="stats-bar" id="statsBar" style="display: none;">
      <div class="stats-chips">
        <div class="stat-chip">
          <span class="stat-label">Deals Found:</span>
          <span class="stat-val" id="totalDeals">0</span>
        </div>
        <div class="stat-chip">
          <span class="stat-label">Average Discount:</span>
          <span class="stat-val" id="avgDiscount">0%</span>
        </div>
        <div class="stat-chip savings">
          <span class="stat-label">Max Savings:</span>
          <span class="stat-val" id="maxSavings">₹0</span>
        </div>
        <div class="brand-filter-indicator" id="brandIndicator">
          🛡️ Official LEGO Only: ON
        </div>
      </div>
      <div class="action-tools">
        <select id="sortSelect" onchange="sortDeals()" style="padding: 6px 12px; font-size: 0.82rem;">
          <option value="discount_desc">Sort: Highest Discount</option>
          <option value="price_asc">Sort: Lowest Price</option>
          <option value="price_desc">Sort: Highest Price</option>
          <option value="savings_desc">Sort: Highest Savings (₹)</option>
        </select>
        <button class="btn-outline" onclick="downloadCSV()">
          <span>📥</span> Export CSV
        </button>
      </div>
    </div>

    <!-- Results Cards Grid -->
    <div class="deals-grid" id="dealsGrid">
      <div class="empty-state">
        <div class="icon">🧱</div>
        <h3>Ready to scan for discounts!</h3>
        <p>Set your desired discount range above (default: 40% to 50%) and click <strong>"Find LEGO Deals"</strong> to scan Amazon India and Flipkart in real time.</p>
      </div>
    </div>

  </div>

  <script>
    let currentDeals = [];

    function updateRangeValues() {
      const min = document.getElementById('minDisc').value;
      const max = document.getElementById('maxDisc').value;
      document.getElementById('minDiscVal').textContent = min + '%';
      document.getElementById('maxDiscVal').textContent = max + '%';
      if (parseInt(min) > parseInt(max)) {
        document.getElementById('maxDisc').value = min;
        document.getElementById('maxDiscVal').textContent = min + '%';
      }
    }

    function updateToggleState() {
      const cb = document.getElementById('officialCheckbox');
      const statusEl = document.getElementById('toggleStatus');
      if (cb.checked) {
        statusEl.textContent = 'ACTIVE';
        statusEl.className = 'toggle-status status-active';
      } else {
        statusEl.textContent = 'ALL BRANDS';
        statusEl.className = 'toggle-status status-inactive';
      }
    }

    async function startScan() {
      const minDisc = document.getElementById('minDisc').value;
      const maxDisc = document.getElementById('maxDisc').value;
      const platform = document.getElementById('platformSelect').value;
      const pages = document.getElementById('pagesSelect').value;
      const official = document.getElementById('officialCheckbox').checked;

      const scanBtn = document.getElementById('scanBtn');
      const btnIcon = document.getElementById('btnIcon');
      const btnText = document.getElementById('btnText');
      const grid = document.getElementById('dealsGrid');

      scanBtn.disabled = true;
      btnIcon.innerHTML = '<span class="spinner"></span>';
      btnText.textContent = 'Scanning Amazon & Flipkart...';

      grid.innerHTML = `
        <div class="empty-state">
          <div class="spinner" style="width: 40px; height: 40px; border-width: 3px; border-color: rgba(255,193,7,0.2); border-top-color: #ffc107; margin-bottom: 16px;"></div>
          <h3>Scanning stores for ${minDisc}% - ${maxDisc}% discounts...</h3>
          <p>Filtering: <strong>${official ? 'Official LEGO Brand Only' : 'All Building Sets'}</strong> on ${platform.toUpperCase()}</p>
        </div>
      `;

      try {
        const queryParams = new URLSearchParams({
          min_discount: minDisc,
          max_discount: maxDisc,
          platform: platform,
          pages: pages,
          official_only: official ? 'true' : 'false'
        });

        const res = await fetch('/api/scan?' + queryParams.toString());
        const data = await res.json();
        currentDeals = data.deals || [];
        renderDeals();
      } catch (err) {
        grid.innerHTML = `
          <div class="empty-state">
            <div class="icon">⚠️</div>
            <h3>Error Fetching Deals</h3>
            <p>${err.message || 'Could not connect to the scraper backend.'}</p>
          </div>
        `;
      } finally {
        scanBtn.disabled = false;
        btnIcon.textContent = '🔍';
        btnText.textContent = 'Find LEGO Deals';
      }
    }

    function renderDeals() {
      const grid = document.getElementById('dealsGrid');
      const statsBar = document.getElementById('statsBar');
      const brandIndicator = document.getElementById('brandIndicator');
      const official = document.getElementById('officialCheckbox').checked;

      if (brandIndicator) {
        brandIndicator.textContent = official ? '🛡️ Official LEGO Only: ON' : '🧱 All Brands: ON';
        brandIndicator.style.color = official ? 'var(--lego-yellow)' : '#94a3b8';
      }

      if (!currentDeals || currentDeals.length === 0) {
        statsBar.style.display = 'none';
        grid.innerHTML = `
          <div class="empty-state">
            <div class="icon">🔍</div>
            <h3>No Deals Found in this Range</h3>
            <p>No sets currently match this exact range. Try widening the discount slider (e.g., 35% - 60%) or unchecking "Official LEGO Only".</p>
          </div>
        `;
        return;
      }

      // Update stats
      statsBar.style.display = 'flex';
      document.getElementById('totalDeals').textContent = currentDeals.length;
      
      const totalDisc = currentDeals.reduce((sum, d) => sum + (d.discount || 0), 0);
      const avgDisc = Math.round(totalDisc / currentDeals.length);
      document.getElementById('avgDiscount').textContent = avgDisc + '%';

      const maxSav = Math.max(...currentDeals.map(d => d.savings || 0));
      document.getElementById('maxSavings').textContent = '₹' + maxSav.toLocaleString('en-IN');

      grid.innerHTML = currentDeals.map(d => {
        const platformClass = d.platform === 'Amazon.in' ? 'badge-amazon' : 'badge-flipkart';
        const formattedPrice = d.price ? '₹' + d.price.toLocaleString('en-IN') : 'Check Site';
        const formattedMrp = d.mrp ? '₹' + d.mrp.toLocaleString('en-IN') : '';
        const formattedSavings = d.savings ? `Save ₹${d.savings.toLocaleString('en-IN')}` : '';
        const fallbackImg = 'https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=500&auto=format&fit=crop&q=60';
        const imgSrc = d.image || fallbackImg;

        return `
          <div class="deal-card">
            <div class="card-thumb">
              <span class="badge-discount">${d.discount}% OFF</span>
              <span class="badge-platform ${platformClass}">${d.platform}</span>
              <img src="${imgSrc}" alt="${d.title}" loading="lazy" onerror="this.src='${fallbackImg}'">
            </div>
            <div class="card-body">
              <h4 class="product-title" title="${d.title}">${d.title}</h4>
              <div class="price-row">
                <span class="current-price">${formattedPrice}</span>
                ${formattedMrp ? `<span class="mrp">${formattedMrp}</span>` : ''}
                ${formattedSavings ? `<span class="savings-pill">${formattedSavings}</span>` : ''}
              </div>
              <div class="card-footer">
                <span class="rating-text">${d.rating ? '★ ' + d.rating : '⚡ High Discount'}</span>
                <a href="${d.url}" target="_blank" class="btn-buy">
                  View Deal ↗
                </a>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function sortDeals() {
      const mode = document.getElementById('sortSelect').value;
      if (mode === 'discount_desc') {
        currentDeals.sort((a, b) => (b.discount || 0) - (a.discount || 0));
      } else if (mode === 'price_asc') {
        currentDeals.sort((a, b) => (a.price || 999999) - (b.price || 999999));
      } else if (mode === 'price_desc') {
        currentDeals.sort((a, b) => (b.price || 0) - (a.price || 0));
      } else if (mode === 'savings_desc') {
        currentDeals.sort((a, b) => (b.savings || 0) - (a.savings || 0));
      }
      renderDeals();
    }

    function downloadCSV() {
      if (!currentDeals || currentDeals.length === 0) return;
      const headers = ['Platform', 'Discount %', 'Price (INR)', 'MRP (INR)', 'Savings (INR)', 'Title', 'Rating', 'URL'];
      const rows = currentDeals.map(d => [
        `"${d.platform}"`,
        d.discount,
        d.price || '',
        d.mrp || '',
        d.savings || '',
        `"${(d.title || '').replace(/"/g, '""')}"`,
        `"${d.rating || ''}"`,
        `"${d.url}"`
      ]);
      const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(r => r.join(','))].join('\\n');
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', 'lego_deals_40_50_discount.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    // Run scan automatically on initial page load
    window.addEventListener('DOMContentLoaded', () => {
      startScan();
    });
  </script>
</body>
</html>
"""

class DealsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/scan":
            params = urllib.parse.parse_qs(parsed.query)
            min_disc = int(params.get("min_discount", ["40"])[0])
            max_disc = int(params.get("max_discount", ["50"])[0])
            platform = params.get("platform", ["both"])[0]
            pages_raw = params.get("pages", ["all"])[0]
            if str(pages_raw).lower() in ("all", "0", "auto"):
                pages = 0  # 0 indicates auto-detect complete catalog
            else:
                try:
                    pages = int(pages_raw)
                except ValueError:
                    pages = 0
            official_param = params.get("official_only", ["true"])[0].lower()
            official = official_param not in ("false", "0", "no")

            print(f"[Web API] Scan request: min={min_disc}%, max={max_disc}%, platform={platform}, official={official}, pages={'Auto-detect (All)' if pages == 0 else pages}")
            deals = get_lego_deals(
                min_discount=min_disc,
                max_discount=max_disc,
                platform=platform,
                official_only=official,
                pages=pages,
                verbose=True
            )

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            payload = json.dumps({"count": len(deals), "deals": deals})
            self.wfile.write(payload.encode("utf-8"))
            return

        if path == "/api/cars":
            params = urllib.parse.parse_qs(parsed.query)
            platform = params.get("platform", ["both"])[0]
            category = params.get("category", ["all"])[0]
            refresh = params.get("refresh", ["false"])[0].lower() in ("true", "1")
            pages = int(params.get("pages", ["2"])[0])

            print(f"[Web API] Cars request: platform={platform}, category={category}, refresh={refresh}")
            sys.stdout.flush()
            cars = get_lego_cars(
                platform=platform,
                category=category,
                pages=pages,
                force_refresh=refresh,
                verbose=True
            )
            print(f"[Web API] Returning {len(cars)} cars for {platform}/{category}")
            sys.stdout.flush()

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            payload = json.dumps({"count": len(cars), "cars": cars})
            self.wfile.write(payload.encode("utf-8"))
            return

        # Check if React dist build exists
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dist_dir = os.path.join(base_dir, "frontend", "dist")
        if os.path.exists(dist_dir):
            clean_path = path.lstrip("/")
            file_path = os.path.join(dist_dir, clean_path)
            if not clean_path or not os.path.exists(file_path) or os.path.isdir(file_path):
                file_path = os.path.join(dist_dir, "index.html")

            if os.path.exists(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                mime_types = {
                    '.html': 'text/html; charset=utf-8',
                    '.js': 'application/javascript; charset=utf-8',
                    '.mjs': 'application/javascript; charset=utf-8',
                    '.css': 'text/css; charset=utf-8',
                    '.json': 'application/json; charset=utf-8',
                    '.svg': 'image/svg+xml',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.ico': 'image/x-icon',
                    '.woff': 'font/woff',
                    '.woff2': 'font/woff2',
                }
                ctype = mime_types.get(ext, 'application/octet-stream')
                self.send_response(200)
                self.send_header("Content-type", ctype)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        # Fallback to embedded HTML
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # Clean server logging
        sys.stderr.write(f"[Server] {format % args}\n")

def run_server(port=5000, auto_open=True):
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, DealsHandler)
    url = f"http://localhost:{port}"
    print(f"\n=======================================================")
    print(f"🚀 LEGO Deal Radar Dashboard running at: {url}")
    print(f"Press Ctrl+C in terminal to stop.")
    print(f"=======================================================\n")
    sys.stdout.flush()
    # Preload car catalog in background thread for instant response
    threading.Thread(target=lambda: get_lego_cars(platform='both', verbose=False), daemon=True).start()
    if auto_open:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
        httpd.server_close()

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port=port)

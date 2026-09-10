import React, { useState, useEffect, useMemo } from 'react';

export default function DealsRadarView() {
  const [minDisc, setMinDisc] = useState(40);
  const [maxDisc, setMaxDisc] = useState(50);
  const [platform, setPlatform] = useState('both');
  const [pages, setPages] = useState('all');
  const [officialOnly, setOfficialOnly] = useState(true);
  const [dealSearchQuery, setDealSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [deals, setDeals] = useState([]);
  const [sortBy, setSortBy] = useState('discount_desc');
  const [error, setError] = useState(null);

  const fetchDeals = async (overrides = {}) => {
    setLoading(true);
    setError(null);
    const mMin = overrides.minDisc !== undefined ? overrides.minDisc : minDisc;
    const mMax = overrides.maxDisc !== undefined ? overrides.maxDisc : maxDisc;
    const mPlat = overrides.platform !== undefined ? overrides.platform : platform;
    const mPages = overrides.pages !== undefined ? overrides.pages : pages;
    const mOfficial = overrides.officialOnly !== undefined ? overrides.officialOnly : officialOnly;

    try {
      const query = new URLSearchParams({
        min_discount: mMin,
        max_discount: mMax,
        platform: mPlat,
        pages: mPages,
        official_only: mOfficial ? 'true' : 'false',
      });
      const res = await fetch(`/api/scan?${query.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setDeals(data.deals || []);
    } catch (err) {
      setError(err.message || 'Failed to scan deals.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeals();
  }, []);

  const applyPreset = (min, max) => {
    setMinDisc(min);
    setMaxDisc(max);
    fetchDeals({ minDisc: min, maxDisc: max });
  };

  const handlePlatformChange = (newPlatform) => {
    setPlatform(newPlatform);
    fetchDeals({ platform: newPlatform });
  };

  const filteredDeals = useMemo(() => {
    if (!dealSearchQuery.trim()) return deals;
    const q = dealSearchQuery.toLowerCase().trim();
    return deals.filter((d) => {
      const title = (d.title || '').toLowerCase();
      const plat = (d.platform || '').toLowerCase();
      return title.includes(q) || plat.includes(q);
    });
  }, [deals, dealSearchQuery]);

  const sortedDeals = useMemo(() => {
    return [...filteredDeals].sort((a, b) => {
      if (sortBy === 'discount_desc') return (b.discount || 0) - (a.discount || 0);
      if (sortBy === 'price_asc') return (a.price || 999999) - (b.price || 999999);
      if (sortBy === 'price_desc') return (b.price || 0) - (a.price || 0);
      if (sortBy === 'savings_desc') return (b.savings || 0) - (a.savings || 0);
      return 0;
    });
  }, [filteredDeals, sortBy]);

  const downloadCSV = () => {
    if (!filteredDeals.length) return;
    const headers = ['Platform', 'Discount %', 'Price (INR)', 'MRP (INR)', 'Savings (INR)', 'Title', 'Rating', 'URL'];
    const rows = filteredDeals.map((d) => [
      `"${d.platform}"`,
      d.discount,
      d.price || '',
      d.mrp || '',
      d.savings || '',
      `"${(d.title || '').replace(/"/g, '""')}"`,
      `"${d.rating || ''}"`,
      `"${d.url}"`,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const encoded = encodeURI(csvContent);
    const link = document.createElement('a');
    link.href = encoded;
    link.download = `lego_deals_${minDisc}_${maxDisc}_percent.csv`;
    link.click();
  };

  const avgDiscount = deals.length
    ? Math.round(deals.reduce((s, d) => s + (d.discount || 0), 0) / deals.length)
    : 0;
  const maxSavings = deals.length ? Math.max(...deals.map((d) => d.savings || 0)) : 0;
  const fallbackImg = 'https://m.media-amazon.com/images/I/81A19lSMmcL._AC_UL320_.jpg';

  return (
    <div className="deals-radar-container">
      {/* Compact, Small Filter Section */}
      <div className="compact-filter-bar">
        {/* Row 1: Presets & Controls */}
        <div className="filter-row-top">
          {/* Presets */}
          <div className="compact-presets">
            <span className="compact-label">PRESETS:</span>
            <button
              type="button"
              className={`compact-preset-btn ${minDisc === 10 && maxDisc === 90 ? 'active' : ''}`}
              onClick={() => applyPreset(10, 90)}
              title="View all discounted sets (including 10%-21% F1 & cars)"
            >
              🚀 10%–90% (All Deals)
            </button>
            <button
              type="button"
              className={`compact-preset-btn ${minDisc === 40 && maxDisc === 50 ? 'active' : ''}`}
              onClick={() => applyPreset(40, 50)}
            >
              🔥 40%–50%
            </button>
            <button
              type="button"
              className={`compact-preset-btn ${minDisc === 50 && maxDisc === 80 ? 'active' : ''}`}
              onClick={() => applyPreset(50, 80)}
            >
              ⚡ 50%+
            </button>
          </div>

          {/* Platform Segment */}
          <div className="compact-segment">
            <button
              type="button"
              className={`compact-seg-btn ${platform === 'both' ? 'active' : ''}`}
              onClick={() => handlePlatformChange('both')}
            >
              Both
            </button>
            <button
              type="button"
              className={`compact-seg-btn ${platform === 'amazon' ? 'active-amazon' : ''}`}
              onClick={() => handlePlatformChange('amazon')}
            >
              🛒 Amazon
            </button>
            <button
              type="button"
              className={`compact-seg-btn ${platform === 'flipkart' ? 'active-flipkart' : ''}`}
              onClick={() => handlePlatformChange('flipkart')}
            >
              🛍️ Flipkart
            </button>
          </div>

          {/* Sliders in a Compact Pill */}
          <div className="compact-range-pill">
            <div className="range-pill-label">
              <span>Discount</span>
              <strong>{minDisc}% – {maxDisc}%</strong>
            </div>
            <div className="compact-slider-inputs">
              <input
                type="range"
                min="5"
                max="90"
                value={minDisc}
                className="compact-slider"
                title={`Min Discount: ${minDisc}%`}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setMinDisc(val);
                  if (val > maxDisc) setMaxDisc(val);
                }}
              />
              <input
                type="range"
                min="10"
                max="95"
                value={maxDisc}
                className="compact-slider"
                title={`Max Discount: ${maxDisc}%`}
                onChange={(e) => {
                  const val = Number(e.target.value);
                  setMaxDisc(val);
                  if (val < minDisc) setMinDisc(val);
                }}
              />
            </div>
          </div>

          {/* Scan Depth Dropdown - Auto Detect All Pages */}
          <div className="compact-dropdown-group">
            <span className="compact-label">PAGES:</span>
            <select
              className="custom-dropdown"
              value={pages}
              onChange={(e) => setPages(e.target.value)}
              title="Select how many pages to scan or auto-detect all pages"
            >
              <option value="all">⚡ All Pages (Auto-Detect Catalog)</option>
              <option value="10">Up to 10 Pages</option>
              <option value="5">Up to 5 Pages (Fast Scan)</option>
              <option value="2">Up to 2 Pages (Quick Preview)</option>
            </select>
          </div>

          {/* Official Brand Toggle */}
          <label className="compact-brand-toggle" htmlFor="officialToggle" title="Strictly filters authentic LEGO sets">
            <input
              type="checkbox"
              id="officialToggle"
              checked={officialOnly}
              onChange={(e) => setOfficialOnly(e.target.checked)}
            />
            <span className="toggle-pill-thumb"></span>
            <span className="compact-brand-text">🛡️ Official LEGO</span>
          </label>

          {/* Scan Button */}
          <button
            type="button"
            className="compact-scan-btn"
            onClick={fetchDeals}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner mini-spinner"></span>
                <span>Scanning...</span>
              </>
            ) : (
              <>
                <span>🔍</span>
                <span>Scan Deals</span>
              </>
            )}
          </button>
        </div>

        {/* Row 2: Slim Deal Search Input */}
        <div className="compact-search-row">
          <div className="compact-search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              className="compact-search-input"
              placeholder="Search in scanned deals (e.g. Ninjago, Star Wars, Technic, City, set #)..."
              value={dealSearchQuery}
              onChange={(e) => setDealSearchQuery(e.target.value)}
            />
            {dealSearchQuery && (
              <button
                type="button"
                className="search-clear-btn"
                onClick={() => setDealSearchQuery('')}
                title="Clear search"
              >
                ✕
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      {deals.length > 0 && (
        <div className="stats-bar">
          <div className="stats-chips">
            <div className="stat-chip">
              <span className="stat-label">Deals Found:</span>
              <span className="stat-val">{deals.length}</span>
            </div>
            <div className="stat-chip">
              <span className="stat-label">Avg Discount:</span>
              <span className="stat-val">{avgDiscount}%</span>
            </div>
            <div className="stat-chip savings">
              <span className="stat-label">Max Savings:</span>
              <span className="stat-val">₹{maxSavings.toLocaleString('en-IN')}</span>
            </div>
            {deals.some((d) => d.cached) && (
              <div className="stat-chip" style={{ background: 'rgba(59, 130, 246, 0.15)', borderColor: 'rgba(59, 130, 246, 0.35)', color: '#93c5fd' }}>
                <span className="stat-label">Source:</span>
                <span className="stat-val">⚡ Live Verified Deals</span>
              </div>
            )}
            {dealSearchQuery && (
              <div className="stat-chip search-stat-chip">
                <span className="stat-label">Filtered:</span>
                <span className="stat-val matching-val">
                  {filteredDeals.length} matches
                </span>
                <span className="search-active-pill">
                  "{dealSearchQuery}"
                  <button
                    type="button"
                    className="chip-remove"
                    onClick={() => setDealSearchQuery('')}
                    title="Remove filter"
                  >
                    ✕
                  </button>
                </span>
              </div>
            )}
            <div className="brand-filter-indicator">
              {officialOnly ? '🛡️ Official LEGO' : '🧱 All Brands'}
            </div>
          </div>

          <div className="action-tools">
            <div className="sort-wrapper">
              <span className="sort-label">Sort:</span>
              <select
                className="custom-dropdown sort-dropdown"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="discount_desc">Highest Discount</option>
                <option value="price_asc">Lowest Price</option>
                <option value="price_desc">Highest Price</option>
                <option value="savings_desc">Highest Savings (₹)</option>
              </select>
            </div>
            <button type="button" className="btn-outline" onClick={downloadCSV}>
              <span>📥</span> Export CSV
            </button>
          </div>
        </div>
      )}

      {/* Closest Match / Active Deals Notification Banner */}
      {deals.some((d) => d.closest_match) && (
        <div
          className="closest-match-banner"
          style={{
            background: 'linear-gradient(135deg, rgba(255, 193, 7, 0.12) 0%, rgba(255, 153, 0, 0.08) 100%)',
            border: '1px solid rgba(255, 193, 7, 0.35)',
            borderRadius: '10px',
            padding: '12px 18px',
            marginBottom: '18px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            color: '#ffc107',
            fontSize: '0.92rem',
          }}
        >
          <span style={{ fontSize: '1.3rem' }}>⚡</span>
          <div>
            <strong>Verified Live Deals Active:</strong> Limited sets currently found at {minDisc}%–{maxDisc}% on {platform === 'both' ? 'these platforms' : platform}. Showing highest discount verified LEGO deals available right now!
          </div>
        </div>
      )}

      {/* Grid or Empty/Loading State */}
      <div className="deals-grid">
        {loading ? (
          <div className="empty-state">
            <div
              className="spinner"
              style={{
                width: 44,
                height: 44,
                borderWidth: 3,
                borderColor: 'rgba(255,193,7,0.2)',
                borderTopColor: '#ffc107',
                margin: '0 auto 16px',
              }}
            ></div>
            <h3>Scanning Amazon India & Flipkart for {minDisc}%–{maxDisc}% Discounts...</h3>
            <p>
              Filtering for {officialOnly ? 'authentic LEGO official sets' : 'all building brick sets'}{' '}
              across {pages} pages.
            </p>
          </div>
        ) : error ? (
          <div className="empty-state">
            <div className="icon">⚠️</div>
            <h3>Scan Encountered an Issue</h3>
            <p>{error}</p>
            <button
              type="button"
              className="compact-scan-btn"
              style={{ marginTop: 14 }}
              onClick={fetchDeals}
            >
              Retry Scan
            </button>
          </div>
        ) : sortedDeals.length === 0 ? (
          <div className="empty-state">
            <div className="icon">🧱</div>
            <h3>No Deals Found Matching Criteria</h3>
            <p>
              {dealSearchQuery
                ? `No scanned sets match "${dealSearchQuery}". Try clearing your search or pick an option below:`
                : `No sets found with ${minDisc}%–${maxDisc}% discount on ${platform === 'both' ? 'current scan' : platform}. Click below to view top active LEGO deals:`}
            </p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', justifyContent: 'center', marginTop: '16px' }}>
              <button
                type="button"
                className="compact-preset-btn active"
                onClick={() => {
                  setDealSearchQuery('');
                  applyPreset(10, 90);
                }}
              >
                🚀 View 10%–90% (All Active Deals)
              </button>
              <button
                type="button"
                className="compact-preset-btn"
                onClick={() => {
                  setDealSearchQuery('');
                  applyPreset(40, 50);
                }}
              >
                🔥 View 40%–50% Deals
              </button>
              {platform !== 'both' && (
                <button
                  type="button"
                  className="compact-seg-btn"
                  style={{ borderColor: 'rgba(255,255,255,0.3)', color: '#fff' }}
                  onClick={() => {
                    setDealSearchQuery('');
                    handlePlatformChange('both');
                  }}
                >
                  ⚡ Search Both Stores
                </button>
              )}
              {dealSearchQuery && (
                <button
                  type="button"
                  className="btn-outline"
                  onClick={() => setDealSearchQuery('')}
                >
                  Clear "{dealSearchQuery}"
                </button>
              )}
            </div>
          </div>
        ) : (
          sortedDeals.map((deal) => {
            const isAmazon = deal.platform === 'Amazon.in';
            return (
              <div className="deal-card" key={deal.id || deal.url}>
                <div className="card-thumb">
                  <span className="badge-discount">{deal.discount}% OFF</span>
                  <span
                    className={`badge-platform ${isAmazon ? 'badge-amazon' : 'badge-flipkart'}`}
                  >
                    {deal.platform}
                  </span>
                  {deal.cached && (
                    <span
                      style={{
                        position: 'absolute',
                        bottom: '8px',
                        left: '8px',
                        background: 'rgba(0, 0, 0, 0.75)',
                        color: '#4ade80',
                        fontSize: '0.7rem',
                        fontWeight: '600',
                        padding: '2px 7px',
                        borderRadius: '6px',
                        backdropFilter: 'blur(4px)',
                        border: '1px solid rgba(74, 222, 128, 0.35)',
                      }}
                    >
                      ✓ Verified Deal
                    </span>
                  )}
                  <img
                    src={deal.image || fallbackImg}
                    alt={deal.title}
                    loading="lazy"
                    referrerPolicy="no-referrer"
                    onError={(e) => {
                      e.target.src = fallbackImg;
                    }}
                  />
                </div>
                <div className="card-body">
                  <h4 className="product-title" title={deal.title}>
                    {deal.title}
                  </h4>
                  <div className="price-row">
                    <span className="current-price">₹{deal.price?.toLocaleString('en-IN')}</span>
                    {deal.mrp && deal.mrp > deal.price && (
                      <span className="mrp">₹{deal.mrp.toLocaleString('en-IN')}</span>
                    )}
                    {deal.savings > 0 && (
                      <span className="savings-pill">Save ₹{deal.savings.toLocaleString('en-IN')}</span>
                    )}
                  </div>
                  <div className="card-footer">
                    <span className="rating-text">
                      {deal.rating ? `★ ${deal.rating}` : 'Official Set'}
                    </span>
                    <a
                      href={deal.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-buy"
                      style={{
                        background: isAmazon ? 'rgba(255,153,0,0.15)' : 'rgba(40,116,240,0.15)',
                        borderColor: isAmazon ? 'rgba(255,153,0,0.4)' : 'rgba(40,116,240,0.4)',
                        color: '#fff',
                      }}
                    >
                      Buy on {isAmazon ? 'Amazon' : 'Flipkart'} ↗
                    </a>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

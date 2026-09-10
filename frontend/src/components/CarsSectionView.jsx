import React, { useState, useEffect, useMemo } from 'react';

export default function CarsSectionView() {
  const [store, setStore] = useState('amazon');
  const [category, setCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [cars, setCars] = useState([]);
  const [sortBy, setSortBy] = useState('featured');
  const [error, setError] = useState(null);

  const categories = [
    { id: 'all', label: '🏎️ All Cars' },
    { id: 'formula 1', label: '🏁 Formula 1 (F1)' },
    { id: 'supercar', label: '🚀 Supercars' },
    { id: 'technic', label: '⚙️ Technic Cars' },
    { id: 'movie & iconic', label: '🎬 Movie & Iconic' },
  ];

  const quickSearchTags = [
    'F1',
    'Red Bull',
    'Ferrari',
    'McLaren',
    'Mercedes',
    'Lamborghini',
    'Porsche',
    'Bugatti',
    'Technic',
    'Batmobile',
    'Skyline',
  ];

  const fetchCars = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const query = new URLSearchParams({
        platform: store,
        category,
        refresh: forceRefresh ? 'true' : 'false',
        pages: '2',
      });
      const res = await fetch(`/api/cars?${query.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setCars(data.cars || []);
    } catch (err) {
      setError(err.message || 'Failed to load cars.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCars();
  }, [store, category]);

  const filteredCars = useMemo(() => {
    if (!searchQuery.trim()) return cars;
    const q = searchQuery.toLowerCase().trim();
    return cars.filter((car) => {
      const title = (car.title || '').toLowerCase();
      const cat = (car.category || '').toLowerCase();
      const platform = (car.platform || '').toLowerCase();
      return title.includes(q) || cat.includes(q) || platform.includes(q);
    });
  }, [cars, searchQuery]);

  const sortedCars = useMemo(() => {
    return [...filteredCars].sort((a, b) => {
      if (sortBy === 'price_asc') return (a.price || 999999) - (b.price || 999999);
      if (sortBy === 'price_desc') return (b.price || 0) - (a.price || 0);
      if (sortBy === 'discount_desc') return (b.discount || 0) - (a.discount || 0);
      return 0;
    });
  }, [filteredCars, sortBy]);

  const fallbackImg = 'https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=500&auto=format&fit=crop&q=60';

  return (
    <div className="cars-view-container">
      {/* Compact, Small Controls Panel */}
      <div className="compact-filter-bar car-filter-bar">
        {/* Row 1: Header + Store Switcher */}
        <div className="filter-row-top">
          <div className="compact-title-group">
            <span className="compact-tag-racing">🏁 F1 & SUPERCARS</span>
            <h3 className="compact-heading">LEGO Cars Catalog</h3>
          </div>

          {/* Platform Segmented Switch - Amazon is DEFAULT */}
          <div className="compact-segment">
            <button
              type="button"
              className={`compact-seg-btn ${store === 'amazon' ? 'active-amazon' : ''}`}
              onClick={() => setStore('amazon')}
              title="Search LEGO cars on Amazon India"
            >
              <span>🛒 Amazon.in</span>
              <span className="default-mini-pill">DEFAULT</span>
            </button>
            <button
              type="button"
              className={`compact-seg-btn ${store === 'flipkart' ? 'active-flipkart' : ''}`}
              onClick={() => setStore('flipkart')}
              title="Search LEGO cars on Flipkart"
            >
              <span>🛍️ Flipkart</span>
            </button>
            <button
              type="button"
              className={`compact-seg-btn ${store === 'both' ? 'active' : ''}`}
              onClick={() => setStore('both')}
              title="Search LEGO cars across both stores"
            >
              <span>⚡ Both</span>
            </button>
          </div>

          {/* Category Quick Chips in Row 1 if space permits */}
          <div className="compact-category-pills">
            {categories.map((c) => (
              <button
                key={c.id}
                type="button"
                className={`compact-chip-btn ${category === c.id ? 'active' : ''}`}
                onClick={() => setCategory(c.id)}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>

        {/* Row 2: Search Bar + Quick Keyword Tags */}
        <div className="compact-car-search-row">
          <div className="compact-search-box flex-search">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              className="compact-search-input"
              placeholder="Search F1, Red Bull, Ferrari, Technic, Batmobile, set #..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                type="button"
                className="search-clear-btn"
                onClick={() => setSearchQuery('')}
                title="Clear search"
              >
                ✕
              </button>
            )}
          </div>

          {/* Quick Keyword Pills Inline */}
          <div className="compact-quick-tags">
            {quickSearchTags.map((tag) => {
              const isActive = searchQuery.toLowerCase() === tag.toLowerCase();
              return (
                <button
                  key={tag}
                  type="button"
                  className={`compact-tag-btn ${isActive ? 'active' : ''}`}
                  onClick={() => setSearchQuery(isActive ? '' : tag)}
                >
                  {tag}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Stats & Tools Bar */}
      <div className="stats-bar">
        <div className="stats-chips">
          <div className="stat-chip">
            <span className="stat-label">Store:</span>
            <span
              className="stat-val"
              style={{
                color:
                  store === 'amazon'
                    ? 'var(--amazon-orange)'
                    : store === 'flipkart'
                    ? 'var(--flipkart-blue)'
                    : '#fff',
              }}
            >
              {store === 'amazon' ? 'Amazon.in' : store === 'flipkart' ? 'Flipkart' : 'All Stores'}
            </span>
          </div>

          <div className="stat-chip">
            <span className="stat-label">Total Cars:</span>
            <span className="stat-val">{cars.length}</span>
          </div>

          {searchQuery && (
            <div className="stat-chip search-stat-chip">
              <span className="stat-label">Filtered:</span>
              <span className="stat-val matching-val">
                {filteredCars.length} matches
              </span>
              <span className="search-active-pill">
                "{searchQuery}"
                <button
                  type="button"
                  className="chip-remove"
                  onClick={() => setSearchQuery('')}
                  title="Remove search"
                >
                  ✕
                </button>
              </span>
            </div>
          )}

          <div className="brand-filter-indicator">
            🏎️ {category === 'all' ? 'ALL VEHICLES' : category.toUpperCase()}
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
              <option value="featured">Featured / Best Match</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="discount_desc">Highest Discount</option>
            </select>
          </div>

          <button
            type="button"
            className="btn-outline"
            onClick={() => fetchCars(true)}
            disabled={loading}
            title="Fetch fresh results from store"
          >
            <span>🔄</span> Refresh
          </button>
        </div>
      </div>

      {/* Cars Grid */}
      <div className="deals-grid">
        {loading ? (
          <div className="empty-state">
            <div
              className="spinner"
              style={{
                width: 44,
                height: 44,
                borderWidth: 3,
                borderColor: 'rgba(239,68,68,0.25)',
                borderTopColor: '#ef4444',
                margin: '0 auto 16px',
              }}
            ></div>
            <h3>Loading LEGO Cars on {store === 'amazon' ? 'Amazon India' : store === 'flipkart' ? 'Flipkart' : 'both platforms'}...</h3>
            <p>Fetching Formula 1, Speed Champions, and Technic supercar models.</p>
          </div>
        ) : error ? (
          <div className="empty-state">
            <div className="icon">⚠️</div>
            <h3>Could not load LEGO cars</h3>
            <p>{error}</p>
            <button
              type="button"
              className="compact-scan-btn"
              style={{ marginTop: 14, background: '#ef4444' }}
              onClick={() => fetchCars(true)}
            >
              Retry Connection
            </button>
          </div>
        ) : sortedCars.length === 0 ? (
          <div className="empty-state">
            <div className="icon">🏎️</div>
            <h3>No Cars Found Matching "{searchQuery || category}"</h3>
            <p>
              {searchQuery
                ? `No models found matching "${searchQuery}". Try a different keyword or click below to restore full catalog:`
                : 'Try viewing all cars or switching the store section above:'}
            </p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', justifyContent: 'center', marginTop: '16px' }}>
              <button
                type="button"
                className="compact-chip-btn active"
                onClick={() => {
                  setSearchQuery('');
                  setCategory('all');
                }}
              >
                🏎️ View All Cars
              </button>
              {store !== 'amazon' && (
                <button
                  type="button"
                  className="compact-seg-btn active-amazon"
                  onClick={() => {
                    setSearchQuery('');
                    setStore('amazon');
                  }}
                >
                  🛒 Switch to Amazon.in
                </button>
              )}
              {searchQuery && (
                <button
                  type="button"
                  className="btn-outline"
                  onClick={() => setSearchQuery('')}
                >
                  Clear "{searchQuery}"
                </button>
              )}
            </div>
          </div>
        ) : (
          sortedCars.map((car) => {
            const isAmazon = car.platform === 'Amazon.in';
            return (
              <div className="deal-card" key={car.id || car.url}>
                <div className="card-thumb">
                  {car.discount > 0 && (
                    <span className="badge-discount">{car.discount}% OFF</span>
                  )}
                  <span
                    className={`badge-platform ${isAmazon ? 'badge-amazon' : 'badge-flipkart'}`}
                  >
                    {car.platform}
                  </span>
                  {car.category && (
                    <span className="badge-category">{car.category}</span>
                  )}
                  <img
                    src={car.image || fallbackImg}
                    alt={car.title}
                    loading="lazy"
                    onError={(e) => {
                      e.target.src = fallbackImg;
                    }}
                  />
                </div>
                <div className="card-body">
                  <h4 className="product-title" title={car.title}>
                    {car.title}
                  </h4>
                  <div className="price-row">
                    <span className="current-price">
                      {car.price ? `₹${car.price.toLocaleString('en-IN')}` : 'Check Store'}
                    </span>
                    {car.mrp && car.mrp > car.price && (
                      <span className="mrp">₹{car.mrp.toLocaleString('en-IN')}</span>
                    )}
                    {car.savings > 0 && (
                      <span className="savings-pill">Save ₹{car.savings.toLocaleString('en-IN')}</span>
                    )}
                  </div>
                  <div className="card-footer">
                    <span className="rating-text">
                      {car.rating ? `★ ${car.rating}` : '🏎️ Official LEGO'}
                    </span>
                    <a
                      href={car.url}
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

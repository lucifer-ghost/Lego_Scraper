import React, { useState, useEffect, useMemo } from 'react';

export default function CarsSectionView({ onToast }) {
  const [store, setStore] = useState('all');
  const [category, setCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [cars, setCars] = useState([]);
  const [sortBy, setSortBy] = useState('featured');
  const [error, setError] = useState(null);

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

  const fetchCars = async (targetStore = store, forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const query = new URLSearchParams({
        platform: targetStore,
        category: 'all',
        refresh: forceRefresh ? 'true' : 'false',
        pages: '2',
      });
      const res = await fetch(`/api/cars?${query.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const list = data.cars || [];
      setCars(list);
      if (forceRefresh && onToast) {
        onToast("Catalog Refreshed", `Loaded ${list.length} verified LEGO models across all stores!`, "success", "⚡");
      }
    } catch (err) {
      setError(err.message || 'Failed to load cars.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCars(store);
  }, [store]);

  const handleStoreChange = (newStore) => {
    setStore(newStore);
    fetchCars(newStore);
    const storeLabels = {
      all: 'All 4 Stores',
      amazon: 'Amazon.in',
      flipkart: 'Flipkart',
      hamleys: 'Hamleys India',
      mybrickhouse: 'MyBrickHouse India',
    };
    if (onToast) {
      onToast("Store Filter", `Switched to ${storeLabels[newStore] || newStore}`, "info", "🏪");
    }
  };

  const handleCategoryChange = (newCat) => {
    setCategory(newCat);
    const labels = {
      all: 'All Cars',
      'formula 1': 'Formula 1',
      supercar: 'Supercars',
      technic: 'Technic',
      'movie & iconic': 'Movie & Iconic',
    };
    if (onToast) {
      onToast("Category Selected", `Showing ${labels[newCat] || newCat}`, "info", "🏁");
    }
  };

  const categoryCounts = useMemo(() => {
    return {
      all: cars.length,
      'formula 1': cars.filter((c) => (c.category || '').toLowerCase() === 'formula 1').length,
      supercar: cars.filter((c) => (c.category || '').toLowerCase() === 'supercar').length,
      technic: cars.filter((c) => (c.category || '').toLowerCase() === 'technic').length,
      'movie & iconic': cars.filter((c) => (c.category || '').toLowerCase() === 'movie & iconic').length,
    };
  }, [cars]);

  const categories = [
    { id: 'all', label: `🏎️ All Cars (${categoryCounts.all || 0})` },
    { id: 'formula 1', label: `🏁 Formula 1 (${categoryCounts['formula 1'] || 0})` },
    { id: 'supercar', label: `🚀 Supercars (${categoryCounts.supercar || 0})` },
    { id: 'technic', label: `⚙️ Technic (${categoryCounts.technic || 0})` },
    { id: 'movie & iconic', label: `🎬 Movie & Iconic (${categoryCounts['movie & iconic'] || 0})` },
  ];

  const filteredCars = useMemo(() => {
    let list = cars;
    if (category !== 'all') {
      const catLow = category.toLowerCase();
      list = list.filter((c) => (c.category || '').toLowerCase() === catLow);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter((car) => {
        const title = (car.title || '').toLowerCase();
        const cat = (car.category || '').toLowerCase();
        const platform = (car.platform || '').toLowerCase();
        return title.includes(q) || cat.includes(q) || platform.includes(q);
      });
    }
    return list;
  }, [cars, category, searchQuery]);

  const sortedCars = useMemo(() => {
    return [...filteredCars].sort((a, b) => {
      if (sortBy === 'price_asc') return (a.price || 999999) - (b.price || 999999);
      if (sortBy === 'price_desc') return (b.price || 0) - (a.price || 0);
      if (sortBy === 'discount_desc') return (b.discount || 0) - (a.discount || 0);
      return 0;
    });
  }, [filteredCars, sortBy]);

  const fallbackImg = 'https://m.media-amazon.com/images/I/81A19lSMmcL._AC_UL320_.jpg';

  return (
    <div className="cars-view-container">
      {/* Overview Hero Showcase Banner */}
      <div className="cars-hero-banner">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="live-dot"></span>
            OFFICIAL LEGO RACING PADDOCK
          </div>
          <h2 className="hero-title">LEGO Cars & F1 Speed Champions</h2>
          <p className="hero-desc">
            Explore authentic Formula 1 team racers (Oracle Red Bull RB20, Ferrari SF-24, McLaren, Mercedes-AMG W15), Technic supercars, and iconic cinema builds with verified live pricing across Amazon, Flipkart, Hamleys & MyBrickHouse.
          </p>
          <div className="hero-stats">
            <div className="hero-stat">
              <strong>{categoryCounts['formula 1'] || 45}</strong>
              <span>🏁 F1 Racers</span>
            </div>
            <div className="hero-stat">
              <strong>{categoryCounts.supercar || 40}</strong>
              <span>🚀 Supercars</span>
            </div>
            <div className="hero-stat">
              <strong>{categoryCounts.technic || 35}</strong>
              <span>⚙️ Technic</span>
            </div>
            <div className="hero-stat">
              <strong>{cars.length || 150}</strong>
              <span>⚡ Total Models</span>
            </div>
          </div>
        </div>
        <div className="hero-visual">
          <img
            src="https://m.media-amazon.com/images/I/81A19lSMmcL._AC_UL600_.jpg"
            alt="LEGO Speed Champions Oracle Red Bull Racing RB20 F1"
            className="hero-car-img"
            loading="eager"
            referrerPolicy="no-referrer"
          />
          <div className="hero-car-glow"></div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="compact-filter-bar car-filter-bar">
        {/* Row 1: Header + Store Switcher */}
        <div className="filter-row-top">
          <div className="compact-title-group">
            <span className="compact-tag-racing">🏁 F1 & SUPERCARS</span>
            <h3 className="compact-heading">Filter Garage</h3>
          </div>

          {/* Platform Segmented Switch */}
          <div className="compact-segment">
            <button
              type="button"
              className={`compact-seg-btn ${store === 'all' || store === 'both' ? 'active' : ''}`}
              onClick={() => handleStoreChange('all')}
              title="Search LEGO cars across all stores"
            >
              <span>⚡ All Stores</span>
            </button>
            <button
              type="button"
              className={`compact-seg-btn ${store === 'amazon' ? 'active-amazon' : ''}`}
              onClick={() => handleStoreChange('amazon')}
              title="Search LEGO cars on Amazon India"
            >
              <span>🛒 Amazon.in</span>
            </button>
            <button
              type="button"
              className={`compact-seg-btn ${store === 'flipkart' ? 'active-flipkart' : ''}`}
              onClick={() => handleStoreChange('flipkart')}
              title="Search LEGO cars on Flipkart"
            >
              <span>🛍️ Flipkart</span>
            </button>
            <button
              type="button"
              className={`compact-seg-btn ${store === 'hamleys' ? 'active-hamleys' : ''}`}
              onClick={() => handleStoreChange('hamleys')}
              title="Search LEGO cars on Hamleys India"
            >
              <span>🧸 Hamleys</span>
            </button>
            <button
              type="button"
              className={`compact-seg-btn ${store === 'mybrickhouse' ? 'active-mybrickhouse' : ''}`}
              onClick={() => handleStoreChange('mybrickhouse')}
              title="Search LEGO cars on MyBrickHouse India"
            >
              <span>🧱 MyBrickHouse</span>
            </button>
          </div>

          {/* Category Quick Chips */}
          <div className="compact-category-pills">
            {categories.map((c) => (
              <button
                key={c.id}
                type="button"
                className={`compact-chip-btn ${category === c.id ? 'active' : ''}`}
                onClick={() => handleCategoryChange(c.id)}
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
              placeholder="Search F1, Red Bull, Ferrari, McLaren, Mercedes, Technic, Batmobile, Skyline..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const q = searchQuery.trim();
                  if (onToast) {
                    if (q) {
                      onToast("Search Results", `Found ${filteredCars.length} models for "${q}"`, "success", "🔍");
                    } else {
                      onToast("Search Cleared", `Showing all ${cars.length} models`, "info", "🔍");
                    }
                  }
                }
              }}
            />
            {searchQuery && (
              <button
                type="button"
                className="search-clear-btn"
                onClick={() => {
                  setSearchQuery('');
                  if (onToast) onToast("Search Cleared", `Showing all ${cars.length} models`, "info", "🔍");
                }}
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
                  onClick={() => {
                    const next = isActive ? '' : tag;
                    setSearchQuery(next);
                    if (onToast && next) {
                      const count = cars.filter((c) => {
                        const title = (c.title || '').toLowerCase();
                        const cat = (c.category || '').toLowerCase();
                        return title.includes(next.toLowerCase()) || cat.includes(next.toLowerCase());
                      }).length;
                      onToast("Quick Search", `Filtered to "${next}" (${count} models)`, "success", "🏎️");
                    }
                  }}
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
                    : store === 'hamleys'
                    ? '#fb7185'
                    : store === 'mybrickhouse'
                    ? '#2dd4bf'
                    : '#fff',
              }}
            >
              {store === 'amazon'
                ? 'Amazon.in'
                : store === 'flipkart'
                ? 'Flipkart'
                : store === 'hamleys'
                ? 'Hamleys'
                : store === 'mybrickhouse'
                ? 'MyBrickHouse'
                : 'All Stores'}
            </span>
          </div>

          <div className="stat-chip">
            <span className="stat-label">Matching Cars:</span>
            <span className="stat-val">{filteredCars.length}</span>
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
            onClick={() => fetchCars(store, true)}
            disabled={loading}
            title="Fetch fresh live results from store"
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
            <h3>Loading LEGO Cars on {store === 'amazon' ? 'Amazon India' : store === 'flipkart' ? 'Flipkart' : store === 'hamleys' ? 'Hamleys' : store === 'mybrickhouse' ? 'MyBrickHouse' : 'all 4 platforms'}...</h3>
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
              onClick={() => fetchCars(store, true)}
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
                🏎️ View All Cars ({categoryCounts.all})
              </button>
              <button
                type="button"
                className="compact-chip-btn"
                onClick={() => {
                  setSearchQuery('');
                  setCategory('formula 1');
                }}
              >
                🏁 View Formula 1 ({categoryCounts['formula 1']})
              </button>
              {store !== 'all' && store !== 'both' && (
                <button
                  type="button"
                  className="compact-seg-btn active"
                  onClick={() => {
                    setSearchQuery('');
                    handleStoreChange('all');
                  }}
                >
                  ⚡ View All Stores
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
            const isFlipkart = car.platform === 'Flipkart';
            const isHamleys = car.platform === 'Hamleys';
            const isMyBrickHouse = car.platform === 'MyBrickHouse';

            const badgeClass = isAmazon
              ? 'badge-amazon'
              : isFlipkart
              ? 'badge-flipkart'
              : isHamleys
              ? 'badge-hamleys'
              : 'badge-mybrickhouse';

            const buyBtnStyle = isAmazon
              ? { background: 'rgba(255,153,0,0.15)', borderColor: 'rgba(255,153,0,0.4)', color: '#fff' }
              : isFlipkart
              ? { background: 'rgba(40,116,240,0.15)', borderColor: 'rgba(40,116,240,0.4)', color: '#fff' }
              : isHamleys
              ? { background: 'rgba(225,29,72,0.15)', borderColor: 'rgba(225,29,72,0.4)', color: '#fff' }
              : { background: 'rgba(13,148,136,0.15)', borderColor: 'rgba(13,148,136,0.4)', color: '#fff' };

            const storeLabel = isAmazon
              ? 'Amazon'
              : isFlipkart
              ? 'Flipkart'
              : isHamleys
              ? 'Hamleys'
              : 'MyBrickHouse';

            return (
              <div className="deal-card" key={car.id || car.url}>
                <div className="card-thumb">
                  <img
                    src={car.image || fallbackImg}
                    alt={car.title}
                    loading="lazy"
                    referrerPolicy="no-referrer"
                    onError={(e) => {
                      e.target.src = fallbackImg;
                    }}
                  />
                  {car.discount > 0 && (
                    <span className="badge-discount">{car.discount}% OFF</span>
                  )}
                  <span
                    className={`badge-platform ${badgeClass}`}
                  >
                    {car.platform}
                  </span>
                  {car.category && (
                    <span className="badge-category">{car.category}</span>
                  )}
                </div>
                <div className="card-body">
                  <h4 className="product-title" title={car.title}>
                    {car.title}
                  </h4>
                  <div className="price-row">
                    <span className="current-price">
                      {car.price ? `₹${Number(car.price).toLocaleString('en-IN', { maximumFractionDigits: 2 })}` : 'Check Store'}
                    </span>
                    {car.mrp && car.mrp > car.price && (
                      <span className="mrp">₹{Number(car.mrp).toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
                    )}
                    {car.savings > 0 && (
                      <span className="savings-pill">Save ₹{Number(car.savings).toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
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
                      style={buyBtnStyle}
                    >
                      Buy on {storeLabel} ↗
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

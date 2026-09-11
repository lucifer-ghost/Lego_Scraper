import React, { useState, useCallback, useRef } from 'react';
import Navbar from './components/Navbar';
import DealsRadarView from './components/DealsRadarView';
import CarsSectionView from './components/CarsSectionView';
import Footer from './components/Footer';
import ToastContainer from './components/Toast';

export default function App() {
  const [activeTab, setActiveTab] = useState('cars');
  const [toasts, setToasts] = useState([]);
  const toastTimers = useRef({});

  const dismissToast = useCallback((id) => {
    if (toastTimers.current[id]) {
      clearTimeout(toastTimers.current[id]);
      delete toastTimers.current[id];
    }
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((title, message = '', type = 'success', icon = '') => {
    const id = Date.now() + Math.random().toString(36).substr(2, 4);
    const defaultIcon = type === 'info' ? 'ℹ️' : type === 'warning' ? '⚠️' : '✓';
    const newToast = {
      id,
      title,
      message,
      type,
      icon: icon || defaultIcon,
    };

    setToasts((prev) => {
      const updated = [...prev, newToast];
      // Keep up to 3 toasts active at once
      if (updated.length > 3) {
        const removed = updated.shift();
        if (toastTimers.current[removed.id]) {
          clearTimeout(toastTimers.current[removed.id]);
          delete toastTimers.current[removed.id];
        }
      }
      return updated;
    });

    // Auto dismiss after 3.6s
    toastTimers.current[id] = setTimeout(() => {
      dismissToast(id);
    }, 3600);
  }, [dismissToast]);

  return (
    <div className="app-shell">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      
      <main className="container">
        {activeTab === 'deals' ? (
          <DealsRadarView onToast={showToast} />
        ) : (
          <CarsSectionView onToast={showToast} />
        )}
      </main>

      <Footer />

      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}


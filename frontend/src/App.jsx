import React, { useState } from 'react';
import Navbar from './components/Navbar';
import DealsRadarView from './components/DealsRadarView';
import CarsSectionView from './components/CarsSectionView';

export default function App() {
  const [activeTab, setActiveTab] = useState('deals');

  return (
    <div className="app-shell">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      
      <main className="container">
        {activeTab === 'deals' ? (
          <DealsRadarView />
        ) : (
          <CarsSectionView />
        )}
      </main>
    </div>
  );
}

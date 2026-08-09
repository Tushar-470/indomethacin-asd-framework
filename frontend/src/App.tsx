import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DrugLibrary from './pages/DrugLibrary';
import PolymerLibrary from './pages/PolymerLibrary';
import Screening from './pages/Screening';
import Results from './pages/Results';
import History from './pages/History';
import { fetchVersion } from './api';

function App() {
  const [version, setVersion] = useState<any>(null);

  useEffect(() => {
    fetchVersion().then(setVersion).catch(console.error);
  }, []);

  return (
    <BrowserRouter>
      <div className="sidebar">
        <h2 style={{ color: 'var(--primary)', marginBottom: '2rem' }}>ASD Framework</h2>
        <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>Dashboard</NavLink>
        <NavLink to="/drugs" className={({ isActive }) => isActive ? 'active' : ''}>Drug Library</NavLink>
        <NavLink to="/polymers" className={({ isActive }) => isActive ? 'active' : ''}>Polymer Library</NavLink>
        <NavLink to="/screening" className={({ isActive }) => isActive ? 'active' : ''}>Screening</NavLink>
        <NavLink to="/history" className={({ isActive }) => isActive ? 'active' : ''}>Analysis History</NavLink>
        <div style={{ marginTop: 'auto', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          {version ? `Engine: ${version.version}` : 'Loading version...'}
        </div>
      </div>
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard version={version} />} />
          <Route path="/drugs" element={<DrugLibrary />} />
          <Route path="/polymers" element={<PolymerLibrary />} />
          <Route path="/screening" element={<Screening />} />
          <Route path="/results/:id" element={<Results />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;

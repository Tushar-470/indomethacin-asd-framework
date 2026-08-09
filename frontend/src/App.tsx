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
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ color: 'var(--primary)', margin: 0, fontSize: '1.4rem' }}>ASD Framework</h2>
          <small style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Polymer Screening Engine</small>
        </div>

        <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>📊 Dashboard</NavLink>
        <NavLink to="/drugs" className={({ isActive }) => isActive ? 'active' : ''}>💊 Drug Library</NavLink>
        <NavLink to="/polymers" className={({ isActive }) => isActive ? 'active' : ''}>🧪 Polymer Library</NavLink>
        <NavLink to="/screening" className={({ isActive }) => isActive ? 'active' : ''}>🚀 Screening Workspace</NavLink>
        <NavLink to="/history" className={({ isActive }) => isActive ? 'active' : ''}>📜 Analysis History</NavLink>

        <div style={{ marginTop: 'auto', fontSize: '0.8rem', color: 'var(--text-secondary)', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
          <div>Engine v{version ? version.engine_version : '1.0.0'}</div>
          <div>Status: <span style={{ color: 'var(--success)' }}>Online</span></div>
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

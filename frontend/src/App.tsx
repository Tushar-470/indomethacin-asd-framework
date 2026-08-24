import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DrugLibrary from './pages/DrugLibrary';
import PolymerLibrary from './pages/PolymerLibrary';
import Screening from './pages/Screening';
import Results from './pages/Results';
import History from './pages/History';
import { fetchVersion } from './api';
import Sidebar from './components/layout/Sidebar';

function App() {
  const [version, setVersion] = useState<any>(null);

  useEffect(() => {
    fetchVersion().then(setVersion).catch(console.error);
  }, []);

  return (
    <BrowserRouter>
      <Sidebar version={version} />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard version={version} />} />
          <Route path="/drugs" element={<DrugLibrary />} />
          <Route path="/polymers" element={<PolymerLibrary />} />
          <Route path="/screening" element={<Screening />} />
          <Route path="/results/:id" element={<Results />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;

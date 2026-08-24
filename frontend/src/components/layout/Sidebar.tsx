import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Pill, FlaskConical, Play, Clock, ShieldCheck } from 'lucide-react';

interface SidebarProps {
  version: any;
}

const Sidebar: React.FC<SidebarProps> = ({ version }) => {
  const engineBaseline = version?.engine_version || 'v1.5.0-FOUR-CRITERION-FREEZE';

  return (
    <aside className='sidebar'>
      <div className='sidebar-header'>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <img src="/logo-symbol.svg" alt="PharmaPolySCOPE Symbol" style={{ width: '24px', height: '24px' }} />
          <h2 style={{ fontSize: '15px', fontWeight: 600, margin: 0, color: 'var(--color-primary-text)', letterSpacing: '-0.02em' }}>
            PharmaPoly<span style={{ fontWeight: 700, color: 'var(--color-primary-action)' }}>SCOPE</span>
          </h2>
        </div>
        <p style={{ fontSize: '11px', color: 'var(--color-muted-text)', margin: '2px 0 0 0' }}>
          Computational Polymer Screening
        </p>
      </div>

      <nav className='sidebar-nav'>
        <div className='sidebar-section'>
          <div className='sidebar-section-title'>Workstation</div>
          <NavLink to='/' className={({isActive}) => isActive ? 'active' : ''}>
            <LayoutDashboard size={16} /> <span>Dashboard</span>
          </NavLink>
        </div>
        <div className='sidebar-section'>
          <div className='sidebar-section-title'>Data Libraries</div>
          <NavLink to='/drugs' className={({isActive}) => isActive ? 'active' : ''}>
            <Pill size={16} /> <span>Drug Library</span>
          </NavLink>
          <NavLink to='/polymers' className={({isActive}) => isActive ? 'active' : ''}>
            <FlaskConical size={16} /> <span>Polymer Library</span>
          </NavLink>
        </div>
        <div className='sidebar-section'>
          <div className='sidebar-section-title'>Screening & Audit</div>
          <NavLink to='/screening' className={({isActive}) => isActive ? 'active' : ''}>
            <Play size={16} /> <span>Run Screening</span>
          </NavLink>
          <NavLink to='/history' className={({isActive}) => isActive ? 'active' : ''}>
            <Clock size={16} /> <span>Analysis History</span>
          </NavLink>
        </div>
      </nav>
      
      <div className='sidebar-footer'>
        <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--color-muted-text)', fontWeight: 600 }}>
          Scientific Baseline
        </div>
        <div className="mono" style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-primary-action)', marginTop: '2px' }}>
          {engineBaseline}
        </div>
        <div style={{ fontSize: '11px', color: 'var(--color-secondary-text)', marginTop: '2px' }}>
          Decision Engine Online
        </div>
        <div style={{ fontSize: '10px', color: 'var(--color-muted-text)', marginTop: '6px', borderTop: '1px solid var(--color-border)', paddingTop: '4px' }}>
          Developed by Tushar Mathapati
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

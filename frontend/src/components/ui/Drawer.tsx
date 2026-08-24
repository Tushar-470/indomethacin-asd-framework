import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  width?: number;
}

const Drawer: React.FC<DrawerProps> = ({ isOpen, onClose, title, children, width = 480 }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const drawerContent = (
    <div className="drawer-overlay" onClick={handleOverlayClick} aria-modal="true" role="dialog" aria-labelledby="drawer-title">
      <div className="drawer-panel" style={{ width: `${width}px`, position: 'fixed', right: 0, top: 0, bottom: 0, backgroundColor: 'var(--color-surface)', zIndex: 50, display: 'flex', flexDirection: 'column' }}>
        <div className="drawer-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', borderBottom: '1px solid var(--color-border)' }}>
          <h2 id="drawer-title" style={{ margin: 0, fontSize: '1.25rem' }}>{title}</h2>
          <button onClick={onClose} aria-label="Close drawer" style={{ background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
            <X size={20} />
          </button>
        </div>
        <div className="drawer-content" style={{ padding: '1rem', overflowY: 'auto', flex: 1 }}>
          {children}
        </div>
      </div>
    </div>
  );

  if (typeof document === 'undefined') return null;
  return createPortal(drawerContent, document.body);
};

export default Drawer;

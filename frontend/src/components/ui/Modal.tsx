import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'default' | 'wide' | 'xl';
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, size = 'default' }) => {
  const modalRef = useRef<HTMLDivElement>(null);

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

  const sizeClass = size !== 'default' ? ` ${size}` : '';

  const modalContent = (
    <div className="modal-overlay" onClick={handleOverlayClick} aria-modal="true" role="dialog" aria-labelledby="modal-title">
      <div className={`modal-panel${sizeClass}`} ref={modalRef}>
        <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 id="modal-title" style={{ margin: 0, fontSize: '1.25rem' }}>{title}</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close modal" style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>
        <div className="modal-content" style={{ marginTop: '1rem' }}>
          {children}
        </div>
      </div>
    </div>
  );

  // Fallback to div if document.body is not available (e.g., SSR)
  if (typeof document === 'undefined') return null;
  return createPortal(modalContent, document.body);
};

export default Modal;

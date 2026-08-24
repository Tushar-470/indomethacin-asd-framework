import React from 'react';

export interface LoadingStateProps {
  rows?: number;
  message?: string;
}

const LoadingState: React.FC<LoadingStateProps> = ({ rows = 5, message }) => {
  return (
    <div style={{ padding: '1rem 0' }}>
      {message && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', color: 'var(--color-secondary-text)' }}>
          <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} />
          <span>{message}</span>
        </div>
      )}
      <div className="skeleton">
        {Array.from({ length: rows }).map((_, index) => (
          <div key={index} className="skeleton-row" style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
            <div className="skeleton-cell" style={{ height: '1.5rem', width: '30%', backgroundColor: 'var(--color-border)', borderRadius: '4px' }}></div>
            <div className="skeleton-cell" style={{ height: '1.5rem', width: '40%', backgroundColor: 'var(--color-border)', borderRadius: '4px' }}></div>
            <div className="skeleton-cell" style={{ height: '1.5rem', width: '20%', backgroundColor: 'var(--color-border)', borderRadius: '4px' }}></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LoadingState;

import React, { ReactNode } from 'react';

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}

const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action }) => {
  return (
    <div className="empty-state" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem 1rem', textAlign: 'center' }}>
      {icon && <div className="empty-state-icon" style={{ marginBottom: '1rem', color: 'var(--color-muted-text)' }}>{icon}</div>}
      <h3 className="empty-state-title" style={{ margin: '0 0 0.5rem 0', color: 'var(--color-primary-text)' }}>{title}</h3>
      <p className="empty-state-description" style={{ margin: '0 0 1.5rem 0', color: 'var(--color-secondary-text)', maxWidth: '400px' }}>{description}</p>
      {action && <div className="empty-state-action">{action}</div>}
    </div>
  );
};

export default EmptyState;

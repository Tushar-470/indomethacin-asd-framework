import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'primary' | 'secondary' | 'outline';
}

const Badge: React.FC<BadgeProps> = ({ variant = 'primary', children, className = '', ...props }) => {
  const resolvedVariant = variant === 'outline' ? 'primary' : variant;
  const classes = ['badge', `badge-${resolvedVariant}`, className].filter(Boolean).join(' ');
  return (
    <span className={classes} {...props}>
      {children}
    </span>
  );
};

export default Badge;

import React from 'react';

interface RankingBarProps {
  score: number;
  maxWidth?: number;
}

const RankingBar: React.FC<RankingBarProps> = ({ score, maxWidth = 200 }) => {
  const clampedScore = Math.max(0, Math.min(1, score));
  const width = clampedScore * maxWidth;

  return (
    <div className="ranking-bar" style={{ width: maxWidth, backgroundColor: 'var(--color-border)', height: '8px', position: 'relative' }}>
      <div 
        className="ranking-bar-fill" 
        style={{ width, backgroundColor: 'var(--color-primary-action)', height: '100%', position: 'absolute', top: 0, left: 0 }} 
      />
    </div>
  );
};

export default RankingBar;

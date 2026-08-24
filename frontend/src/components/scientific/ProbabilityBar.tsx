import React from 'react';
import RankIndicator from './RankIndicator';

export interface ProbabilityBarProps {
  polymerName?: string;
  probability: number;
  rank?: number;
}

const ProbabilityBar: React.FC<ProbabilityBarProps> = ({ polymerName, probability, rank }) => {
  const probVal = typeof probability === 'number' ? probability : 0;
  const probPercent = Math.min(100, Math.max(0, probVal <= 1.0 ? probVal * 100 : probVal));
  const formattedProb = `${probPercent.toFixed(1)}%`;
  
  return (
    <div className="probability-bar-container" style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%' }}>
      {rank !== undefined && <RankIndicator rank={rank} />}
      {polymerName && <span className="polymer-name" style={{ minWidth: '100px', fontWeight: 500 }}>{polymerName}</span>}
      <div className="ranking-bar" style={{ flex: 1, backgroundColor: 'var(--color-border)', height: '10px', borderRadius: '2px', overflow: 'hidden' }}>
        <div 
          className="ranking-bar-fill" 
          style={{ width: `${probPercent}%`, backgroundColor: 'var(--color-primary-action)', height: '100%' }} 
        />
      </div>
      <span className="probability-value text-numeric" style={{ minWidth: '45px', textAlign: 'right' }}>{formattedProb}</span>
    </div>
  );
};

export default ProbabilityBar;

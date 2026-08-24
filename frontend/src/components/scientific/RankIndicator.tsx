import React from 'react';

interface RankIndicatorProps {
  rank: number;
}

const RankIndicator: React.FC<RankIndicatorProps> = ({ rank }) => {
  const rankClass = rank <= 3 ? `rank-${rank}` : '';
  const paddedRank = rank.toString().padStart(2, '0');

  return (
    <span className={`rank-indicator text-numeric ${rankClass}`}>
      {paddedRank}
    </span>
  );
};

export default RankIndicator;

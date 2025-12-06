import React from 'react';

interface GhostButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

export default function GhostButton({ children, onClick, className = '' }: GhostButtonProps) {
  return (
    <button 
      onClick={onClick}
      className={`px-8 py-3 rounded-full text-white/60 font-medium
                 bg-white/[0.03] hover:bg-white/[0.08] hover:text-white
                 border border-white/5 backdrop-blur-md transition-all ${className}`}
    >
      {children}
    </button>
  );
}


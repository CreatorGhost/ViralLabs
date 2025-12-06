import React from 'react';

interface LiquidPodProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: 'violet' | 'cyan' | 'emerald' | 'rose';
}

const glowColors = {
  violet: 'bg-violet-500/20',
  cyan: 'bg-cyan-500/20',
  emerald: 'bg-emerald-500/20',
  rose: 'bg-rose-500/20',
};

export default function LiquidPod({ children, className = '', glowColor = 'violet' }: LiquidPodProps) {
  return (
    <div className={`relative rounded-[32px] bg-[#1a1b26]/40 backdrop-blur-xl border border-white/10 shadow-2xl overflow-hidden ${className}`}>
      {/* Gloss Reflection Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />
      
      {/* Inner Glow Mesh */}
      <div className={`absolute -top-24 -right-24 w-64 h-64 ${glowColors[glowColor]} blur-[80px] rounded-full`} />
      
      {/* Content */}
      <div className="relative z-10 p-8">
        {children}
      </div>
    </div>
  );
}


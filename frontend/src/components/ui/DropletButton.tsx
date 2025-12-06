import { motion } from 'framer-motion';
import { RefreshCw } from 'lucide-react';
import React from 'react';

interface DropletButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}

export default function DropletButton({ 
  children, 
  onClick, 
  disabled = false, 
  loading = false, 
  className = '' 
}: DropletButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      onClick={onClick}
      disabled={disabled || loading}
      className={`relative px-8 py-3 rounded-full font-semibold text-white 
                 bg-gradient-to-b from-violet-500 to-violet-700
                 shadow-[0_0_20px_rgba(139,92,246,0.5),inset_0_2px_0_rgba(255,255,255,0.2)]
                 border border-violet-400/30
                 disabled:opacity-50 disabled:cursor-not-allowed
                 ${className}`}
    >
      <span className="relative z-10 drop-shadow-md flex items-center gap-2">
        {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
        {children}
      </span>
    </motion.button>
  );
}


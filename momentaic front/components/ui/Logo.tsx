import React from 'react';
import { Link } from 'react-router-dom';
import { cn } from '../../lib/utils';

interface LogoProps {
  className?: string;
  collapsed?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ className, collapsed }) => {
  return (
    <Link to="/" className={cn("flex items-center gap-3 group select-none", className)}>
      <div className="relative w-10 h-10 flex items-center justify-center">
        <img
          src="/logo.png"
          alt="MomentAIc Logo"
          className="w-full h-full object-contain drop-shadow-lg"
        />
      </div>

      {!collapsed && (
        <div className="flex flex-col">
          <span className="font-sans text-xl font-bold tracking-tight leading-none text-white">
            MOMENT<span className="text-transparent bg-clip-text bg-gradient-to-r from-[#3b82f6] to-[#06b6d4]">.AI.C</span>
          </span>
          <span className="font-mono text-[9px] tracking-[0.2em] text-gray-500 group-hover:text-gray-300 transition-colors">
            OPERATING SYSTEM
          </span>
        </div>
      )}
    </Link>
  );
};
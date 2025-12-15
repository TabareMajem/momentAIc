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
        <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full drop-shadow-lg">
           <defs>
              <linearGradient id="grad1" x1="10" y1="90" x2="30" y2="50" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#a855f7" />
                  <stop offset="100%" stopColor="#d8b4fe" />
              </linearGradient>
              <linearGradient id="grad2" x1="40" y1="90" x2="60" y2="30" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#60a5fa" />
              </linearGradient>
              <linearGradient id="grad3" x1="70" y1="90" x2="90" y2="10" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#06b6d4" />
                  <stop offset="100%" stopColor="#22d3ee" />
              </linearGradient>
           </defs>
           
           {/* Bar 1 (Purple) */}
           <path d="M15 85 L35 65 L35 85 L15 85 Z" fill="url(#grad1)" className="group-hover:-translate-y-1 transition-transform duration-300 ease-out" style={{transformOrigin: 'bottom'}} />
           
           {/* Bar 2 (Blue) */}
           <path d="M40 85 L60 45 L60 85 L40 85 Z" fill="url(#grad2)" className="group-hover:-translate-y-2 transition-transform duration-300 ease-out delay-75" style={{transformOrigin: 'bottom'}} />
           
           {/* Arrow (Cyan) */}
           <path d="M65 85 L65 40 L85 20 L85 35 L95 20 L80 10 L80 25 L65 40 Z" fill="url(#grad3)" className="group-hover:-translate-y-1 group-hover:translate-x-1 transition-transform duration-300 ease-out delay-150" />
           <path d="M65 85 L65 45 L80 30 L80 85 Z" fill="url(#grad3)" opacity="0.5" />
        </svg>
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
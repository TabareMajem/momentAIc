
import React from 'react';
import { Lock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from './Button';
import { cn } from '../../lib/utils';
import { useAuthStore } from '../../stores/auth-store';

interface PremiumLockProps {
  children: React.ReactNode;
  isLocked: boolean;
  minTier?: 'growth' | 'god_mode';
  message?: string;
  className?: string;
}

export const PremiumLock: React.FC<PremiumLockProps> = ({ 
  children, 
  isLocked, 
  minTier = 'growth',
  message = "UPGRADE TO ACCESS",
  className 
}) => {
  if (!isLocked) return <>{children}</>;

  return (
    <div className={cn("relative overflow-hidden rounded-xl", className)}>
      <div className="filter blur-md opacity-30 pointer-events-none select-none">
        {children}
      </div>
      
      <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-black/10 backdrop-blur-[2px]">
        <div className="bg-[#0a0a0a]/90 border border-white/10 p-6 rounded-xl shadow-2xl text-center max-w-sm mx-4">
          <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4 border border-white/10">
            <Lock className="w-6 h-6 text-gray-400" />
          </div>
          <h3 className="text-white font-bold font-mono text-lg mb-2">{message}</h3>
          <p className="text-gray-500 text-xs font-mono mb-6 uppercase tracking-wide">
            This protocol requires <span className="text-[#00f0ff]">{minTier.replace('_', ' ')}</span> clearance.
          </p>
          <Link to="/settings">
            <Button variant="cyber" size="sm" className="w-full">
              UPGRADE CLEARANCE
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

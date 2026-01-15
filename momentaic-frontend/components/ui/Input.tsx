import React from 'react';
import { cn } from '../../lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label className="text-xs font-bold uppercase tracking-widest text-gray-500 ml-1">
            {label}
          </label>
        )}
        <div className="relative group">
            <input
              className={cn(
                'flex h-12 w-full rounded-lg border border-white/10 bg-[#0a0a0a] px-4 py-2 text-sm text-white ring-offset-black file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-700 focus-visible:outline-none focus-visible:border-[#00f0ff] focus-visible:ring-1 focus-visible:ring-[#00f0ff]/50 disabled:cursor-not-allowed disabled:opacity-50 font-mono transition-all duration-300',
                error && 'border-red-500 focus-visible:border-red-500 focus-visible:ring-red-500/50',
                className
              )}
              ref={ref}
              {...props}
            />
            {/* Corner accents for cyber feel */}
            <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/20 rounded-tr-lg pointer-events-none group-hover:border-[#00f0ff]/50 transition-colors"></div>
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/20 rounded-bl-lg pointer-events-none group-hover:border-[#00f0ff]/50 transition-colors"></div>
        </div>
        {error && <p className="text-xs text-red-500 font-mono mt-1">{error}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";
import React from 'react';
import { cn } from '../../lib/utils';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="w-full space-y-1">
        {label && (
          <label className="text-xs font-bold uppercase tracking-widest text-gray-500 ml-1">
            {label}
          </label>
        )}
        <div className="relative group">
          <textarea
            className={cn(
              'flex min-h-[80px] w-full rounded-lg border border-white/10 bg-[#0a0a0a] px-4 py-3 text-sm text-white ring-offset-black placeholder:text-gray-700 focus-visible:outline-none focus-visible:border-[#00f0ff] focus-visible:ring-1 focus-visible:ring-[#00f0ff]/50 disabled:cursor-not-allowed disabled:opacity-50 font-mono transition-all duration-300 resize-y',
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
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>
    );
  }
);
Textarea.displayName = "Textarea";
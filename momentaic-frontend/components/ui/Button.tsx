import React from 'react';
import { cn } from '../../lib/utils';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'cyber';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    const variants = {
      default: 'btn-brand text-white border border-transparent shadow-lg',
      cyber: 'btn-brand text-white border border-transparent shadow-[0_0_15px_rgba(59,130,246,0.5)] relative overflow-hidden group',
      secondary: 'bg-white text-black hover:bg-gray-200 border-none',
      outline: 'border border-white/10 bg-white/5 text-white hover:bg-white/10 hover:border-brand-blue/50',
      ghost: 'hover:bg-white/5 text-gray-400 hover:text-white',
      destructive: 'bg-red-900/50 text-red-200 border border-red-800 hover:bg-red-900',
    };

    const sizes = {
      sm: 'h-8 px-4 text-[10px] tracking-widest uppercase rounded-lg',
      md: 'h-11 px-6 py-2 text-xs tracking-widest uppercase font-bold rounded-xl',
      lg: 'h-14 px-8 text-sm tracking-[0.2em] uppercase font-black rounded-xl',
    };

    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center transition-all duration-300 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 relative overflow-hidden group',
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {variant === 'cyber' && (
          <div className="absolute inset-0 translate-x-[-100%] group-hover:animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent pointer-events-none" />
        )}
        <div className="relative flex items-center gap-2 z-10">
            {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            {children}
        </div>
      </button>
    );
  }
);
Button.displayName = "Button";
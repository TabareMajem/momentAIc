import React from 'react';
import { cn } from '../../lib/utils';

export function Card({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn(
      "tech-panel relative bg-[#0a0a0a]/80 text-gray-100 transition-all duration-300 group overflow-hidden rounded-xl border border-white/5 shadow-2xl backdrop-blur-sm",
      className
    )} {...props}>
      {/* Subtle Noise Texture - Replaced with Local */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-overlay bg-noise-pattern"></div>

      {/* Hover Glow Gradient */}
      <div className="absolute -inset-px bg-gradient-to-r from-[#00f0ff]/0 via-[#00f0ff]/10 to-[#00f0ff]/0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}

export function CardHeader({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col space-y-1.5 p-6 border-b border-white/5", className)} {...props}>{children}</div>;
}

export function CardTitle({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("font-bold leading-none tracking-tight text-lg font-mono text-white uppercase group-hover:text-[#00f0ff] transition-colors duration-300", className)} {...props}>{children}</h3>;
}

export function CardDescription({ className, children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-xs text-gray-500 mt-2 leading-relaxed font-mono tracking-wide", className)} {...props}>{children}</p>;
}

export function CardContent({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6", className)} {...props}>{children}</div>;
}

export function CardFooter({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex items-center p-6 pt-0 border-t border-white/5 bg-black/20", className)} {...props}>{children}</div>;
}
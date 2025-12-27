
import React from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'success' | 'warning' | 'error' | 'outline' | 'purple' | 'cyber';
  className?: string;
  children?: React.ReactNode;
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variants = {
    default: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
    success: 'bg-green-100 text-green-700 border-green-200 border',
    warning: 'bg-yellow-100 text-yellow-700 border-yellow-200 border',
    error: 'bg-red-100 text-red-700 border-red-200 border',
    purple: 'bg-purple-900/50 text-purple-200 border border-purple-500/50',
    outline: 'text-gray-700 border border-gray-300',
    cyber: 'bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/50 shadow-[0_0_10px_rgba(0,240,255,0.2)]',
  };

  return (
    <div className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2", variants[variant], className)} {...props} />
  );
}

import React from 'react';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils';

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export const Dialog: React.FC<DialogProps> = ({ isOpen, onClose, title, description, children, footer }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Content */}
      <div className="relative z-50 w-full max-w-lg transform rounded-2xl bg-[#0a0a0a] border border-white/10 p-8 shadow-2xl transition-all overflow-hidden">
        {/* Theme Accents */}
        <div className="absolute inset-0 bg-cyber-grid opacity-5 pointer-events-none"></div>
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1 bg-gradient-to-r from-transparent via-[#00f0ff] to-transparent opacity-50"></div>

        <div className="relative z-10 flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-white uppercase tracking-tight">{title}</h2>
            {description && (
              <p className="text-xs text-gray-400 font-mono mt-2 tracking-wide">{description}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-500 hover:text-white transition-all"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="relative z-10 mb-8 font-mono">
          {children}
        </div>

        {footer && (
          <div className="relative z-10 flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-6 border-t border-white/5">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
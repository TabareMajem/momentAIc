import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/auth-store';
import { useStartupStore } from '../../stores/startup-store';
import { ChevronDown, Building2, Plus, LogOut, Check } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/Badge';

export function StartupSelector() {
    const { user, logout } = useAuthStore();
    const { startups, activeStartupId, setActiveStartup, fetchStartups, isLoading } = useStartupStore();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();

    // Fetch startups on mount if authenticated
    useEffect(() => {
        if (user && startups.length === 0) {
            fetchStartups();
        }
    }, [user, fetchStartups]);

    // Close dropdown on click outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelect = (id: string) => {
        setActiveStartup(id);
        setIsOpen(false);
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const activeStartup = startups.find(s => s.id === activeStartupId);

    if (isLoading && startups.length === 0) {
        return <div className="animate-pulse bg-white/5 h-10 w-48 rounded" />;
    }

    return (
        <div className="relative" ref={dropdownRef}>
            {/* The Selector Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-3 bg-black/40 border border-white/10 hover:border-[#00f0ff]/50 px-4 py-2 rounded-lg transition-all group min-w-[200px]"
            >
                <div className="p-1.5 rounded bg-gradient-to-br from-purple-500/20 to-cyan-500/20 group-hover:from-purple-500/40 group-hover:to-cyan-500/40 transition-colors">
                    <Building2 className="w-4 h-4 text-[#00f0ff]" />
                </div>

                <div className="flex-1 text-left">
                    <div className="text-xs text-gray-500 font-mono uppercase tracking-widest line-clamp-1">
                        Active Context
                    </div>
                    <div className="text-sm font-bold text-white truncate max-w-[120px]">
                        {activeStartup ? activeStartup.name : "Select Startup"}
                    </div>
                </div>

                <ChevronDown className={cn(
                    "w-4 h-4 text-gray-400 transition-transform duration-200",
                    isOpen && "rotate-180 text-[#00f0ff]"
                )} />
            </button>

            {/* The Dropdown Menu */}
            {isOpen && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-[#0a0a0a] border border-[#00f0ff]/30 rounded-xl shadow-[0_10px_40px_rgba(0,0,0,0.8)] z-50 overflow-hidden backdrop-blur-xl animate-in fade-in slide-in-from-top-2 duration-200">

                    {/* Startup List */}
                    <div className="max-h-[300px] overflow-y-auto py-2">
                        {startups.length === 0 && (
                            <div className="px-4 py-3 text-sm text-gray-500 font-mono text-center">
                                No startups found.
                            </div>
                        )}

                        {startups.map(startup => (
                            <button
                                key={startup.id}
                                onClick={() => handleSelect(startup.id)}
                                className={cn(
                                    "w-full text-left px-4 py-3 flex items-center justify-between hover:bg-white/5 transition-colors group",
                                    activeStartupId === startup.id && "bg-[#00f0ff]/5"
                                )}
                            >
                                <div className="flex-1 min-w-0 pr-4">
                                    <div className="text-sm font-bold text-white truncate group-hover:text-[#00f0ff] transition-colors">
                                        {startup.name}
                                    </div>
                                    <div className="text-xs text-gray-500 font-mono flex gap-2 mt-1">
                                        <span className="capitalize">{startup.industry}</span>
                                        <span>•</span>
                                        <span className="uppercase text-purple-400">{startup.stage}</span>
                                    </div>
                                </div>
                                {activeStartupId === startup.id && (
                                    <Check className="w-4 h-4 text-[#00f0ff] flex-shrink-0" />
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Actions Menu */}
                    <div className="border-t border-white/10 p-2 bg-black/40">
                        <button
                            onClick={() => {
                                setIsOpen(false);
                                navigate('/onboarding/genius');
                            }}
                            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[#00f0ff] hover:bg-[#00f0ff]/10 rounded-lg transition-colors font-mono uppercase tracking-widest"
                        >
                            <Plus className="w-4 h-4" /> Launch New Startup
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

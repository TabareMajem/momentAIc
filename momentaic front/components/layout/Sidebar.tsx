
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Rocket, Bot, MessageSquare, TrendingUp, Settings, LogOut, Menu, X, ShieldAlert, Network, Eye, Zap, BarChart2
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuthStore } from '../../stores/auth-store';
import { Logo } from '../ui/Logo';

export function Sidebar() {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [isOpen, setIsOpen] = React.useState(false);

  const navigation = [
    { name: 'MISSION_CONTROL', href: '/dashboard', icon: LayoutDashboard },
    { name: 'GROWTH_ENGINE', href: '/growth', icon: BarChart2 },
    { name: 'STARTUPS', href: '/startups', icon: Rocket },
    { name: 'AGENTS_MARKET', href: '/agents', icon: Bot },
    { name: 'COMM_LINK', href: '/agents/chat', icon: MessageSquare },
    { name: 'AGENT_FORGE', href: '/agent-forge', icon: Network },
    { name: 'VISION_PORTAL', href: '/vision-portal', icon: Eye },
    { name: 'INVEST_RADAR', href: '/investment', icon: TrendingUp },
    { name: 'CONFIG', href: '/settings', icon: Settings },
  ];

  if (user?.role === 'admin') {
      navigation.push({ name: 'GOD_MODE', href: '/admin', icon: ShieldAlert });
  }

  // Calculate Credit Color
  const creditPercent = user ? (user.credits / (user.subscription_tier === 'starter' ? 50 : 500)) * 100 : 0;
  const creditColor = creditPercent < 20 ? 'text-red-500' : 'text-[#00f0ff]';

  return (
    <>
      {/* Mobile Top Bar */}
      <div className="md:hidden fixed top-0 left-0 z-[60] p-4 w-full flex items-center justify-between pointer-events-none">
         <button 
            className="pointer-events-auto w-12 h-12 bg-black/50 backdrop-blur-md border border-white/10 rounded-full flex items-center justify-center text-white shadow-lg active:scale-95 transition-transform"
            onClick={() => setIsOpen(!isOpen)}
         >
             {isOpen ? <X size={20} className="text-white" /> : <Menu size={20} />}
         </button>
      </div>

      {/* Mobile Overlay Navigation */}
      <div 
        className={cn(
          "fixed inset-0 z-50 bg-[#020202]/95 backdrop-blur-xl transition-all duration-500 ease-in-out md:hidden flex flex-col",
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        )}
      >
          <div className="flex items-center justify-center h-24 border-b border-white/10">
              <Logo collapsed={false} />
          </div>
          
          <div className="flex-1 px-6 py-8 space-y-2 overflow-y-auto">
             {navigation.map((item, i) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setIsOpen(false)}
                  style={{ transitionDelay: `${i * 50}ms` }}
                  className={cn(
                      "flex items-center p-4 border rounded-xl transition-all transform",
                      isOpen ? "translate-x-0 opacity-100" : "-translate-x-8 opacity-0",
                      location.pathname === item.href 
                        ? "bg-brand-gradient border-transparent text-white shadow-lg"
                        : "bg-white/5 border-transparent text-gray-400 hover:bg-white/10"
                  )}
                >
                   <item.icon className="mr-4 w-5 h-5" />
                   <span className="font-mono font-bold text-sm tracking-widest">{item.name}</span>
                </Link>
             ))}
             
             <div className="mt-8 pt-8 border-t border-white/10">
                 <button onClick={logout} className="w-full py-4 border border-red-500/30 bg-red-500/5 text-red-500 font-bold font-mono rounded-xl hover:bg-red-500/10 transition-colors uppercase tracking-widest text-xs">
                     DISCONNECT_SESSION
                 </button>
             </div>
          </div>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex fixed inset-y-0 left-0 z-40 w-64 bg-[#020202] border-r border-white/5 text-gray-300 flex-col font-mono">
        <div className="h-24 flex items-center px-6 border-b border-white/5 bg-[#050505]">
          <Logo />
        </div>

        <nav className="flex-1 py-6 px-3 space-y-1 overflow-y-auto scrollbar-hide">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center px-4 py-3 text-[10px] font-bold transition-all duration-200 group relative tracking-[0.15em] rounded-lg mb-1",
                  isActive 
                    ? "text-white bg-white/5 border border-brand-blue/30" 
                    : "text-gray-500 hover:text-white hover:bg-white/5 border border-transparent"
                )}
              >
                <item.icon className={cn(
                    "mr-3 h-4 w-4 transition-colors", 
                    isActive ? "text-brand-cyan" : "text-gray-600 group-hover:text-gray-400"
                )} />
                {item.name}
                {isActive && (
                    <div className="absolute right-0 inset-y-0 w-1 bg-gradient-to-b from-brand-purple to-brand-cyan rounded-l-full"></div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Credit Display & User Footer */}
        <div className="p-4 border-t border-white/5 bg-[#050505] space-y-4">
          
          {/* Credits HUD */}
          <div className="bg-[#111] rounded-lg p-3 border border-white/10">
              <div className="flex justify-between items-center mb-1">
                  <span className="text-[9px] uppercase text-gray-500 tracking-widest flex items-center gap-1">
                      <Zap className="w-3 h-3 text-yellow-500" /> COMPUTE CREDITS
                  </span>
                  <span className={cn("text-xs font-bold font-mono", creditColor)}>
                      {user?.subscription_tier === 'god_mode' ? '∞' : user?.credits}
                  </span>
              </div>
              {user?.subscription_tier !== 'god_mode' && (
                  <div className="h-1 w-full bg-gray-800 rounded-full overflow-hidden">
                      <div 
                        className={cn("h-full rounded-full transition-all duration-500", creditPercent < 20 ? 'bg-red-500' : 'bg-brand-cyan')}
                        style={{ width: `${Math.min(creditPercent, 100)}%` }}
                      ></div>
                  </div>
              )}
          </div>

          <div className="flex items-center px-3 py-2 border border-white/10 bg-black/50 rounded-lg">
            <div className="h-8 w-8 bg-brand-gradient flex items-center justify-center text-white font-bold text-xs rounded-full shadow-lg">
                {user?.full_name.charAt(0)}
            </div>
            <div className="ml-3 min-w-0">
              <p className="text-xs font-bold text-white truncate uppercase tracking-wider">{user?.full_name}</p>
              <p className="text-[9px] text-gray-500 truncate font-mono">{user?.role === 'admin' ? 'GOD_MODE' : user?.subscription_tier.toUpperCase() + ' TIER'}</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

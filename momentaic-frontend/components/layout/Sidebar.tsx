
import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Settings, LogOut, Menu, X, Zap, Shield, ChevronDown,
  Plug, Bell, FlaskConical, Megaphone, Network, Eye, Bot, BarChart2,
  Activity, Users, Sparkles, BookOpen, Globe, Target, Mic, Phone,
  TrendingUp, Terminal, DollarSign, Compass, ChevronRight
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useAuthStore } from '../../stores/auth-store';
import { Logo } from '../ui/Logo';
import { StartupSelector } from '../dashboard/StartupSelector';
import { useTranslation } from 'react-i18next';
import { LanguageSelector } from './LanguageSelector';
import { FEATURE_REGISTRY, useFeatureStore, getRecommendedFeatures } from '../../stores/feature-store';
import { useStartupStore } from '../../stores/startup-store';

// Map icon strings to actual components
const ICON_MAP: Record<string, any> = {
  LayoutDashboard, Shield, Settings, Zap, Activity, TrendingUp, Network,
  Sparkles, BookOpen, BarChart2, Phone, Target, Globe, Plug, Bell,
  FlaskConical, Terminal, DollarSign, Eye, Bot, Megaphone, Mic, Users,
};

export function Sidebar() {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { enabledFeatures, toggleFeature } = useFeatureStore();
  const { startups, activeStartupId } = useStartupStore();
  const [isOpen, setIsOpen] = React.useState(false);
  const [moreOpen, setMoreOpen] = React.useState(false);

  // Get essential features (always shown)
  const essentialFeatures = FEATURE_REGISTRY.filter(f => f.tier === 'essential');

  // Get user-activated features (non-essential that are enabled)
  const activatedFeatures = FEATURE_REGISTRY.filter(
    f => f.tier !== 'essential' && enabledFeatures.includes(f.id)
  );

  // Get smart recommendations based on active startup's stage
  const activeStartup = startups.find(s => s.id === activeStartupId);
  const stage = activeStartup?.stage || 'idea';
  const recommended = getRecommendedFeatures(stage, enabledFeatures);

  // Credits
  const creditPercent = user ? (user.credits / (user.subscription_tier === 'starter' ? 50 : 500)) * 100 : 0;
  const creditColor = creditPercent < 20 ? 'text-red-500' : 'text-[#00f0ff]';

  // Push Notifications
  const { isSupported, isSubscribed, subscribe, checkStatus } = useNotificationStore();
  React.useEffect(() => { checkStatus(); }, [checkStatus]);

  const handleEnablePush = async () => {
    const success = await subscribe();
    if (success) alert("Push notifications enabled!");
  };

  // Renders a single nav link
  const NavLink = ({ name, href, icon: iconName, isRecommended }: { name: string; href: string; icon: string; isRecommended?: boolean }) => {
    const isActive = location.pathname === href;
    const Icon = ICON_MAP[iconName] || Shield;
    return (
      <Link
        to={href}
        onClick={() => setIsOpen(false)}
        className={cn(
          "flex items-center px-4 py-2.5 text-[10px] font-bold transition-all duration-200 group relative tracking-[0.15em] rounded-lg mb-0.5",
          isActive
            ? "text-white bg-white/5 border border-brand-blue/30"
            : "text-gray-500 hover:text-white hover:bg-white/5 border border-transparent"
        )}
      >
        <Icon className={cn(
          "mr-3 h-4 w-4 transition-colors",
          isActive ? "text-brand-cyan" : "text-gray-600 group-hover:text-gray-400"
        )} />
        <span className="flex-1">{name}</span>
        {isRecommended && !isActive && (
          <span className="w-1.5 h-1.5 rounded-full bg-[#00f0ff] animate-pulse" />
        )}
        {isActive && (
          <div className="absolute right-0 inset-y-0 w-1 bg-gradient-to-b from-brand-purple to-brand-cyan rounded-l-full" />
        )}
      </Link>
    );
  };

  // Main nav content (shared between mobile and desktop)
  const NavContent = () => (
    <>
      {/* Essential Features */}
      {essentialFeatures.map(f => (
        <NavLink key={f.id} name={f.name} href={f.href} icon={f.icon} />
      ))}

      {/* User-Activated Features */}
      {activatedFeatures.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="px-4 mb-2 text-[9px] font-bold text-purple-400 tracking-[0.2em]">✦ ACTIVE</div>
          {activatedFeatures.map(f => (
            <NavLink key={f.id} name={f.name} href={f.href} icon={f.icon} />
          ))}
        </div>
      )}

      {/* Smart Recommendations */}
      {recommended.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="px-4 mb-2 text-[9px] font-bold text-[#00f0ff]/60 tracking-[0.2em]">⚡ RECOMMENDED</div>
          {recommended.map(f => (
            <button
              key={f.id}
              onClick={() => {
                toggleFeature(f.id);
                navigate(f.href);
                setIsOpen(false);
              }}
              className="w-full flex items-center px-4 py-2.5 text-[10px] font-bold text-gray-600 hover:text-[#00f0ff] hover:bg-[#00f0ff]/5 border border-transparent hover:border-[#00f0ff]/20 rounded-lg transition-all tracking-[0.15em] group mb-0.5"
            >
              {(() => { const Icon = ICON_MAP[f.icon] || Shield; return <Icon className="mr-3 h-4 w-4 text-gray-700 group-hover:text-[#00f0ff]" />; })()}
              <span className="flex-1 text-left">{f.name}</span>
              <span className="text-[8px] text-[#00f0ff]/40 group-hover:text-[#00f0ff] font-mono">+ADD</span>
            </button>
          ))}
        </div>
      )}

      {/* LP Portal + Feature Arsenal */}
      <div className="mt-4 pt-4 border-t border-white/5 space-y-1">
        <Link
          to="/invest"
          onClick={() => setIsOpen(false)}
          className="flex items-center px-4 py-2.5 text-[10px] font-bold text-red-400 bg-red-500/5 hover:bg-red-500/10 border border-transparent hover:border-red-500/30 rounded-lg transition-all tracking-[0.15em] uppercase"
        >
          <Target className="mr-3 h-4 w-4 text-red-400" />
          LP Portal
        </Link>
        <Link
          to="/features"
          onClick={() => setIsOpen(false)}
          className={cn(
            "flex items-center px-4 py-2.5 text-[10px] font-bold transition-all tracking-[0.15em] rounded-lg uppercase group",
            location.pathname === '/features'
              ? "text-white bg-purple-500/10 border border-purple-500/30"
              : "text-purple-400/60 hover:text-purple-400 bg-purple-500/5 hover:bg-purple-500/10 border border-transparent hover:border-purple-500/20"
          )}
        >
          <Compass className="mr-3 h-4 w-4" />
          <span className="flex-1">Feature Arsenal</span>
          <ChevronRight className="w-3 h-3 opacity-50 group-hover:opacity-100" />
        </Link>
      </div>
    </>
  );

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

      {/* Mobile Overlay */}
      <div
        className={cn(
          "fixed inset-0 z-50 bg-[#020202]/95 backdrop-blur-xl transition-all duration-500 ease-in-out md:hidden flex flex-col",
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        )}
      >
        <div className="flex items-center justify-center h-24 border-b border-white/10">
          <Logo collapsed={false} />
        </div>
        <div className="px-4 py-3 border-b border-white/10">
          <StartupSelector />
        </div>
        <div className="flex-1 px-6 py-6 space-y-1 overflow-y-auto">
          <NavContent />
        </div>
        <div className="p-4 border-t border-white/10 space-y-3">
          <div className="bg-[#111] rounded-lg p-3 border border-white/10">
            <div className="flex justify-between items-center mb-1">
              <span className="text-[9px] uppercase text-gray-500 tracking-widest flex items-center gap-1">
                <Zap className="w-3 h-3 text-yellow-500" /> CREDITS
              </span>
              <span className={cn("text-xs font-bold font-mono", creditColor)}>
                {user?.subscription_tier === 'god_mode' ? '∞' : user?.credits}
              </span>
            </div>
            {user?.subscription_tier !== 'god_mode' && (
              <div className="h-1 w-full bg-gray-800 rounded-full overflow-hidden">
                <div className={cn("h-full rounded-full transition-all duration-500", creditPercent < 20 ? 'bg-red-500' : 'bg-brand-cyan')} style={{ width: `${Math.min(creditPercent, 100)}%` }} />
              </div>
            )}
          </div>
          <button onClick={logout} className="w-full py-3 border border-red-500/30 bg-red-500/5 text-red-500 font-bold font-mono rounded-xl hover:bg-red-500/10 transition-colors uppercase tracking-widest text-xs">
            DISCONNECT
          </button>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex fixed inset-y-0 left-0 z-40 w-64 bg-[#020202] border-r border-white/5 text-gray-300 flex-col font-mono">
        <div className="h-20 flex items-center px-6 border-b border-white/5 bg-[#050505]">
          <Logo />
        </div>

        <div className="px-3 py-3 border-b border-white/5">
          <StartupSelector />
        </div>

        <nav className="flex-1 py-4 px-3 overflow-y-auto scrollbar-hide">
          <NavContent />
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-white/5 bg-[#050505] space-y-3">
          {isSupported && !isSubscribed && (
            <button
              onClick={handleEnablePush}
              className="w-full flex items-center justify-center py-2 bg-brand-purple/20 border border-brand-purple/50 text-brand-purple hover:bg-brand-purple/30 rounded-lg transition-all text-[10px] font-bold tracking-widest uppercase"
            >
              <Bell className="w-3 h-3 mr-2" /> ENABLE ALERTS
            </button>
          )}

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
                <div className={cn("h-full rounded-full transition-all duration-500", creditPercent < 20 ? 'bg-red-500' : 'bg-brand-cyan')} style={{ width: `${Math.min(creditPercent, 100)}%` }} />
              </div>
            )}
          </div>

          <div className="flex -mx-4 items-center justify-center pt-1">
            <LanguageSelector />
          </div>

          <div className="flex items-center px-3 py-2 border border-white/10 bg-black/50 rounded-lg">
            <div className="h-8 w-8 bg-brand-gradient flex items-center justify-center text-white font-bold text-xs rounded-full shadow-lg">
              {user?.full_name?.charAt(0)}
            </div>
            <div className="ml-3 min-w-0">
              <p className="text-xs font-bold text-white truncate uppercase tracking-wider">{user?.full_name}</p>
              <p className="text-[9px] text-gray-500 truncate font-mono">{user?.role === 'admin' ? 'GOD_MODE' : (user?.subscription_tier?.toUpperCase() || '') + ' TIER'}</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

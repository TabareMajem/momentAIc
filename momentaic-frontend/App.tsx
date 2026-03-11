
import React, { useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { useAuthStore } from './stores/auth-store';
import { ToastProvider } from './components/ui/Toast';
import { WowTourProvider } from './components/tour/WowTourProvider';
import { ErrorBoundary } from './components/ErrorBoundary';
import { analytics } from './lib/firebase';
import { logEvent } from 'firebase/analytics';

// Pages
import LandingPage from './pages/LandingPage';
import IntelHub from './pages/intel/index';
import ArticleDetail from './pages/intel/ArticleDetail';
import LoginPage from './pages/Login';
import SignupPage from './pages/Signup';
import InvestorsPage from './pages/Investors';
import Dashboard from './pages/Dashboard';
import StartupsList from './pages/StartupsList';
import StartupNew from './pages/StartupNew';
import StartupDetail from './pages/StartupDetail';
import AgentChat from './pages/AgentChat';
import AgentsMarket from './pages/AgentsMarket';
import InvestmentDashboard from './pages/InvestmentDashboard';
import IntegrationsPage from './pages/IntegrationsPage';
import LeaderboardPage from './pages/LeaderboardPage';
import MissionPage from './pages/MissionPage';
import ReferralDashboard from './pages/ReferralDashboard';
import SocialProofStudio from './pages/SocialProofStudio';
import OnboardingWizard from './pages/OnboardingWizard';
import RegionFomoPage from './pages/RegionFomoPage';
import PrivacyPolicy from './pages/PrivacyPolicy';
import AmbassadorDashboard from './pages/AmbassadorDashboard';
import AutoPilotOnboarding from './pages/AutoPilotOnboarding';

import TheVault from './pages/TheVault';
import PowerPlays from './pages/PowerPlays';
import InnovatorLab from './pages/InnovatorLab';
import GeniusOnboarding from './pages/GeniusOnboarding';
import WowOnboarding from './pages/WowOnboarding';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

import { OnboardingTour } from './components/OnboardingTour';
import FromLovable from './pages/FromLovable';
import FromBolt from './pages/FromBolt';

// Lazy-loaded heavy pages (code-splitting)
const AgentForge = lazy(() => import('./pages/AgentForge'));
const VisionPortal = lazy(() => import('./pages/VisionPortal'));
const GrowthEngine = lazy(() => import('./pages/GrowthEngine'));
const CharacterFactory = lazy(() => import('./pages/CharacterFactory'));
const GuerrillaWarfare = lazy(() => import('./pages/GuerrillaWarfare'));
const TelemetryCore = lazy(() => import('./pages/TelemetryCore'));
const FeatureArsenal = lazy(() => import('./pages/FeatureArsenal'));
const AutonomySettings = lazy(() => import('./pages/AutonomySettings'));
const BusinessPulse = lazy(() => import('./pages/BusinessPulse'));
const ViralSwarm = lazy(() => import('./pages/ViralSwarm'));
const GlobalCampaign = lazy(() => import('./pages/GlobalCampaign'));
const EmpireBuilder = lazy(() => import('./pages/EmpireBuilder'));
const InvestorDeck = lazy(() => import('./pages/InvestorDeck'));
const WarRoomDashboard = lazy(() => import('./pages/WarRoomDashboard'));
const ExperimentsLab = lazy(() => import('./pages/ExperimentsLab'));
const Campaigns = lazy(() => import('./pages/Campaigns'));
const Referrals = lazy(() => import('./pages/ReferralDashboard'));
const SupportHQ = lazy(() => import('./pages/SupportPage'));
const AgentComposability = lazy(() => import('./pages/AgentComposability'));
const HitLDashboard = lazy(() => import('./pages/HitLDashboard'));

// Sniper Agent
const SniperPage = lazy(() => import('./pages/SniperPage'));

// Media Agent
const MediaPage = lazy(() => import('./pages/MediaPage'));

// Content Agent
const ContentPage = lazy(() => import('./pages/ContentPage'));

// Moby Agent
const MobyPage = lazy(() => import('./pages/MobyPage'));

// Gatekeeper Agent
const GatekeeperPage = lazy(() => import('./pages/GatekeeperPage'));

// Lemlist Domination Agent
const LemlistPage = lazy(() => import('./pages/LemlistPage'));

// Legal Agent
const LegalPage = lazy(() => import('./pages/LegalPage'));

// Recruiting Agent
const RecruitingPage = lazy(() => import('./pages/RecruitingPage'));

// Support Agent
const SupportAgentPage = lazy(() => import('./pages/SupportAgentPage'));

// Procurement Agent
const ProcurementPage = lazy(() => import('./pages/ProcurementPage'));

// Marketing Clay
const MarketingClayPage = lazy(() => import('./pages/MarketingClayPage'));

// Workflow Agent
const WorkflowPage = lazy(() => import('./pages/WorkflowPage'));

// Moby Autonomous Agent
const MobyAutonomousPage = lazy(() => import('./pages/MobyAutonomousPage'));

// Admin Panel
const AdminPage = lazy(() => import('./pages/AdminPage'));

// Agent Hub
const AgentHubPage = lazy(() => import('./pages/AgentHubPage'));

// Settings
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

// Influencer Scraper
const ScraperDashboard = lazy(() => import('./pages/ScraperDashboard'));
const ScraperOnboarding = lazy(() => import('./pages/ScraperOnboarding'));
const GhostBoard = lazy(() => import('./pages/GhostBoard'));
const GTMCommandCenter = lazy(() => import('./pages/GTMCommandCenter'));
const Blog = lazy(() => import('./pages/Blog'));
import { ResearchWhitepaper } from './components/marketing/ResearchWhitepaper';

const PageLoader = () => (
  <div className="min-h-[50vh] flex flex-col items-center justify-center gap-4 animate-in fade-in duration-500">
    <div className="relative w-12 h-12">
      <div className="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
      <div className="absolute inset-0 border-4 border-indigo-500 rounded-full border-t-transparent animate-spin"></div>
    </div>
    <span className="animate-pulse text-indigo-400 font-mono text-sm tracking-widest uppercase">Initializing Interface</span>
  </div>
);

const ProtectedLayout = () => {
  return (
    <div className="flex min-h-screen bg-[#0A0A0A] text-[#E0E0E0] font-sans">
      <OnboardingTour />
      <Sidebar />
      <main className="flex-1 md:ml-64 pt-20 p-6 md:p-8 overflow-y-auto bg-[#0A0A0A]">
        <div className="max-w-[1600px] mx-auto animate-fade-in">
          <ErrorBoundary>
            <Suspense fallback={<PageLoader />}>
              <Outlet />
            </Suspense>
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
};

const ProtectedRoute = () => {
  const { isAuthenticated, loadUser, isLoading } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // Track page views
  useEffect(() => {
    if (analytics) {
      logEvent(analytics, 'page_view', {
        page_location: window.location.href,
        page_path: location.pathname
      });
    }
  }, [location.pathname]);

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-[#0A0A0A] text-gray-500 font-sans"><span className="animate-pulse tracking-widest text-xs font-semibold">LOADING CORE...</span></div>;

  if (!isAuthenticated && !localStorage.getItem('access_token')) {
    return <Navigate to="/login" replace />;
  }
  return <ProtectedLayout />;
};

const AdminRoute = () => {
  const { user } = useAuthStore();
  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }
  return <Outlet />;
};

export default function App() {
  return (
    <ToastProvider>
      <WowTourProvider>
        <Router>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/intel" element={<IntelHub />} />
              <Route path="/intel/:slug" element={<ArticleDetail />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/mission" element={<MissionPage />} />
              <Route path="/leaderboard" element={<LeaderboardPage />} />
              <Route path="/join" element={<RegionFomoPage />} />
              <Route path="/ambassador" element={<AmbassadorDashboard />} />
              <Route path="/investors" element={<InvestorsPage />} />
              <Route path="/invest" element={<InvestorDeck />} />

              {/* Redirect deprecated routes to new funnel */}
              <Route path="/start" element={<Navigate to="/signup" replace />} />
              <Route path="/genius" element={<Navigate to="/onboarding/genius" replace />} />

              <Route path="/privacy" element={<PrivacyPolicy />} />
              <Route path="/from-bolt" element={<FromBolt />} />

              {/* Protected Routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/ghost-board" element={<GhostBoard />} />
                <Route path="/hitl" element={<HitLDashboard />} />
                <Route path="/war-room" element={<WarRoomDashboard />} />
                <Route path="/gtm" element={<GTMCommandCenter />} />
                <Route path="/blog" element={<Blog />} />

                {/* Startup Routes */}
                <Route path="/startups" element={<StartupsList />} />
                <Route path="/startups/new" element={<StartupNew />} />
                <Route path="/startups/:id" element={<StartupDetail />} />
                <Route path="/startups/:id/signals" element={<StartupDetail />} />
                <Route path="/startups/:id/sprints" element={<StartupDetail />} />

                {/* Other Routes */}
                <Route path="/onboarding" element={<WowOnboarding />} />
                <Route path="/onboarding/wizard" element={<OnboardingWizard />} />
                <Route path="/onboarding/genius" element={<GeniusOnboarding />} />
                <Route path="/empire-builder" element={<EmpireBuilder />} />
                <Route path="/investment" element={<InvestmentDashboard />} />

                {/* Agent Routes */}
                <Route path="/agents" element={<AgentsMarket />} />
                <Route path="/agents/chat" element={<AgentChat />} />

                {/* AgentForge Routes */}
                <Route path="/agent-forge" element={<AgentForge />} />
                <Route path="/vision-portal" element={<VisionPortal />} />

                {/* Growth Engine */}
                <Route path="/growth" element={<GrowthEngine />} />

                {/* Integrations */}
                <Route path="/integrations" element={<IntegrationsPage />} />
                <Route path="/experiments" element={<ExperimentsLab />} />
                <Route path="/campaigns" element={<Campaigns />} />

                {/* Leaderboard & Community (also accessible when logged in) */}
                <Route path="/rankings" element={<LeaderboardPage />} />

                {/* Core Routes */}
                <Route path="/innovator" element={<InnovatorLab />} />
                <Route path="/guerrilla" element={<GuerrillaWarfare />} />
                <Route path="/vault" element={<TheVault />} />
                <Route path="/settings/autonomy" element={<AutonomySettings />} />
                <Route path="/features" element={<FeatureArsenal />} />
                <Route path="/pulse" element={<BusinessPulse />} />
                <Route path="/characters" element={<CharacterFactory />} />
                <Route path="/telemetry" element={<TelemetryCore />} />
                <Route path="/viral-swarm" element={<ViralSwarm />} />
                <Route path="/global-campaign" element={<GlobalCampaign />} />
                <Route path="/composability" element={<AgentComposability />} />

                {/* Legacy Routes (kept for backward compat) */}
                <Route path="/power-plays" element={<PowerPlays />} />
                <Route path="/referrals" element={<Referrals />} />
                <Route path="/support" element={<SupportHQ />} />
                
                {/* Sniper Agent */}
                <Route path="/sniper" element={<SniperPage />} />
                
                {/* Media Agent */}
                <Route path="/media" element={<MediaPage />} />
                
                {/* Content Agent */}
                <Route path="/content" element={<ContentPage />} />
                
                {/* Moby Agent */}
                <Route path="/moby" element={<MobyPage />} />
                
                {/* Gatekeeper Agent */}
                <Route path="/gatekeeper" element={<GatekeeperPage />} />
                
                {/* Lemlist Domination Agent */}
                {/* Lemlist Domination Agent */}
                <Route path="/lemlist" element={<LemlistPage />} />
                
                {/* Legal Agent */}
                <Route path="/legal" element={<LegalPage />} />
                
                {/* Recruiting Agent */}
                <Route path="/recruiting" element={<RecruitingPage />} />
                
                {/* Support Agent */}
                <Route path="/support-wizard" element={<SupportAgentPage />} />
                
                {/* Procurement Agent */}
                <Route path="/procurement" element={<ProcurementPage />} />
                
                {/* Marketing Clay */}
                <Route path="/growth-engine" element={<MarketingClayPage />} />
                
                {/* Workflow Agent */}
                <Route path="/workflow-architect" element={<WorkflowPage />} />
                
                {/* Moby Autonomous Agent */}
                <Route path="/moby-autonomous" element={<MobyAutonomousPage />} />
                
                {/* Admin Panel */}
                <Route path="/admin" element={<AdminPage />} />
                
                {/* Agent Hub */}
                <Route path="/agent-hub" element={<AgentHubPage />} />
                
                {/* Settings */}
                <Route path="/settings" element={<SettingsPage />} />
                
                {/* Scraper Routes */}
                <Route path="/scraper" element={<ScraperDashboard />} />
                <Route path="/scraper/onboarding" element={<ScraperOnboarding />} />

                {/* Viral Marketing Routes */}
                <Route path="/research" element={<ResearchWhitepaper onBack={() => window.history.back()} />} />
              </Route>
            </Routes>
          </Suspense>
        </Router>
      </WowTourProvider>
    </ToastProvider>
  );
}

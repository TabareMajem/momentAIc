
import React, { useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { useAuthStore } from './stores/auth-store';
import { ToastProvider } from './components/ui/Toast';
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
import Settings from './pages/Settings';
import AdminPanel from './pages/AdminPanel';
import IntegrationsPage from './pages/IntegrationsPage';
import TriggersPage from './pages/TriggersPage';
import LeaderboardPage from './pages/LeaderboardPage';
import MissionPage from './pages/MissionPage';
import CoFounderMatch from './pages/CoFounderMatch';
import ReferralDashboard from './pages/ReferralDashboard';
import SocialProofStudio from './pages/SocialProofStudio';
import OnboardingWizard from './pages/OnboardingWizard';
import RegionFomoPage from './pages/RegionFomoPage';
import PrivacyPolicy from './pages/PrivacyPolicy';
import AmbassadorDashboard from './pages/AmbassadorDashboard';
import AutoPilotOnboarding from './pages/AutoPilotOnboarding';

import TheVault from './pages/TheVault';
import IntegrationBuilder from './pages/IntegrationBuilder';
import PowerPlays from './pages/PowerPlays';
import ExecutorPage from './pages/ExecutorPage';
import InnovatorLab from './pages/InnovatorLab';
import GeniusOnboarding from './pages/GeniusOnboarding';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

import { OnboardingTour } from './components/OnboardingTour';
import FromLovable from './pages/FromLovable';
import FromBolt from './pages/FromBolt';

// Lazy-loaded heavy pages (code-splitting)
const AgentForge = lazy(() => import('./pages/AgentForge'));
const VisionPortal = lazy(() => import('./pages/VisionPortal'));
const GrowthEngine = lazy(() => import('./pages/GrowthEngine'));
const GrowthPlaybook = lazy(() => import('./pages/GrowthPlaybook'));
const CharacterFactory = lazy(() => import('./pages/CharacterFactory'));
const GuerrillaWarfare = lazy(() => import('./pages/GuerrillaWarfare'));
const TelemetryCore = lazy(() => import('./pages/TelemetryCore'));
const OpenClawProxy = lazy(() => import('./pages/OpenClawProxy'));
const CallCenter = lazy(() => import('./pages/CallCenter'));
const FeatureArsenal = lazy(() => import('./pages/FeatureArsenal'));
const LiveAgentView = lazy(() => import('./pages/LiveAgentView'));
const AutonomySettings = lazy(() => import('./pages/AutonomySettings'));
const BusinessPulse = lazy(() => import('./pages/BusinessPulse'));
const ViralSwarm = lazy(() => import('./pages/ViralSwarm'));
const GlobalCampaign = lazy(() => import('./pages/GlobalCampaign'));
const EmpireBuilder = lazy(() => import('./pages/EmpireBuilder'));
const InvestorDeck = lazy(() => import('./pages/InvestorDeck'));
const WarRoomDashboard = lazy(() => import('./pages/WarRoomDashboard'));
const ExperimentsLab = lazy(() => import('./pages/ExperimentsLab'));
const Campaigns = lazy(() => import('./pages/Campaigns'));
import { ResearchWhitepaper } from './components/marketing/ResearchWhitepaper';

const PageLoader = () => (
  <div className="min-h-[50vh] flex items-center justify-center">
    <span className="animate-pulse text-purple-500 font-mono">LOADING...</span>
  </div>
);

const ProtectedLayout = () => {
  return (
    <div className="flex min-h-screen bg-[#050505] text-white">
      <OnboardingTour />
      <Sidebar />
      <main className="flex-1 md:ml-64 pt-20 p-6 md:p-8 overflow-y-auto bg-[#050505]">
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

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-[#050505] text-purple-500 font-mono"><span className="animate-pulse">LOADING...</span></div>;

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
      <Router>
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
          <Route path="/from-lovable" element={<FromLovable />} />
          <Route path="/from-bolt" element={<FromBolt />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/war-room" element={<WarRoomDashboard />} />

            {/* Startup Routes */}
            <Route path="/startups" element={<StartupsList />} />
            <Route path="/startups/new" element={<StartupNew />} />
            <Route path="/startups/:id" element={<StartupDetail />} />
            <Route path="/startups/:id/signals" element={<StartupDetail />} />
            <Route path="/startups/:id/sprints" element={<StartupDetail />} />

            {/* Other Routes */}
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
            <Route path="/growth/playbook" element={<GrowthPlaybook />} />

            {/* Integrations & Triggers */}
            <Route path="/integrations" element={<IntegrationsPage />} />
            <Route path="/triggers" element={<TriggersPage />} />
            <Route path="/experiments" element={<ExperimentsLab />} />
            <Route path="/campaigns" element={<Campaigns />} />

            {/* Leaderboard & Community (also accessible when logged in) */}
            <Route path="/rankings" element={<LeaderboardPage />} />
            <Route path="/cofounder-match" element={<CoFounderMatch />} />

            {/* Core Routes */}
            <Route path="/executor" element={<ExecutorPage />} />
            <Route path="/innovator" element={<InnovatorLab />} />
            <Route path="/guerrilla" element={<GuerrillaWarfare />} />
            <Route path="/vault" element={<TheVault />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/settings/autonomy" element={<AutonomySettings />} />
            <Route path="/features" element={<FeatureArsenal />} />
            <Route path="/pulse" element={<BusinessPulse />} />
            <Route path="/characters" element={<CharacterFactory />} />
            <Route path="/live" element={<LiveAgentView />} />
            <Route path="/telemetry" element={<TelemetryCore />} />
            <Route path="/openclaw" element={<OpenClawProxy />} />
            <Route path="/call-center" element={<CallCenter />} />
            <Route path="/viral-swarm" element={<ViralSwarm />} />
            <Route path="/global-campaign" element={<GlobalCampaign />} />

            {/* Legacy Routes (kept for backward compat) */}
            <Route path="/power-plays" element={<PowerPlays />} />
            <Route path="/builder" element={<IntegrationBuilder />} />

            {/* Admin Routes */}
            <Route element={<AdminRoute />}>
              <Route path="/admin" element={<AdminPanel />} />
            </Route>

            {/* Viral Marketing Routes */}
            <Route path="/research" element={<ResearchWhitepaper onBack={() => window.history.back()} />} />
          </Route>
        </Routes>
      </Router>
    </ToastProvider>
  );
}


import React, { useEffect } from 'react';
import { HashRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { useAuthStore } from './stores/auth-store';
import { ToastProvider } from './components/ui/Toast';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/Login';
import SignupPage from './pages/Signup';
import Dashboard from './pages/Dashboard';
import StartupsList from './pages/StartupsList';
import StartupNew from './pages/StartupNew';
import StartupDetail from './pages/StartupDetail';
import AgentChat from './pages/AgentChat';
import AgentsMarket from './pages/AgentsMarket';
import InvestmentDashboard from './pages/InvestmentDashboard';
import Settings from './pages/Settings';
import AdminPanel from './pages/AdminPanel';
import AgentForge from './pages/AgentForge';
import VisionPortal from './pages/VisionPortal';
import GrowthEngine from './pages/GrowthEngine';
import IntegrationsPage from './pages/IntegrationsPage';
import TriggersPage from './pages/TriggersPage';
import LeaderboardPage from './pages/LeaderboardPage';
import MissionPage from './pages/MissionPage';
import CoFounderMatch from './pages/CoFounderMatch';
import ReferralDashboard from './pages/ReferralDashboard';
import SocialProofStudio from './pages/SocialProofStudio';
import ExperimentsLab from './pages/ExperimentsLab';
import CampaignCenter from './pages/CampaignCenter';
import AmbassadorDashboard from './pages/AmbassadorDashboard';
import OnboardingWizard from './pages/OnboardingWizard';

import { OnboardingTour } from './components/OnboardingTour';

const ProtectedLayout = () => {
  return (
    <div className="flex min-h-screen bg-[#050505]">
      <OnboardingTour />
      <Sidebar />
      <main className="flex-1 md:ml-64 pt-20 p-6 md:p-8 overflow-y-auto bg-[#050505]">
        <div className="max-w-[1600px] mx-auto animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

const ProtectedRoute = () => {
  const { isAuthenticated, loadUser, isLoading } = useAuthStore();
  useEffect(() => { loadUser(); }, []);

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-[#050505] text-[#00f0ff] font-mono">LOADING...</div>;

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
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/mission" element={<MissionPage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />

            {/* Startup Routes */}
            <Route path="/startups" element={<StartupsList />} />
            <Route path="/startups/new" element={<StartupNew />} />
            <Route path="/startups/:id" element={<StartupDetail />} />
            <Route path="/startups/:id/signals" element={<StartupDetail />} />
            <Route path="/startups/:id/sprints" element={<StartupDetail />} />

            {/* Other Routes */}
            <Route path="/onboarding/wizard" element={<OnboardingWizard />} />
            <Route path="/investment" element={<InvestmentDashboard />} />

            {/* Agent Routes */}
            <Route path="/agents" element={<AgentsMarket />} />
            <Route path="/agents/chat" element={<AgentChat />} />

            {/* AgentForge Routes */}
            <Route path="/agent-forge" element={<AgentForge />} />
            <Route path="/vision-portal" element={<VisionPortal />} />

            {/* Growth Engine */}
            <Route path="/growth" element={<GrowthEngine />} />

            {/* Integrations & Triggers */}
            <Route path="/integrations" element={<IntegrationsPage />} />
            <Route path="/triggers" element={<TriggersPage />} />

            {/* Leaderboard & Community (also accessible when logged in) */}
            <Route path="/rankings" element={<LeaderboardPage />} />
            <Route path="/cofounder-match" element={<CoFounderMatch />} />

            import OnboardingWizard from './pages/OnboardingWizard';

            ...

            {/* Other Routes */}
            <Route path="/onboarding/wizard" element={<OnboardingWizard />} />
            <Route path="/investment" element={<InvestmentDashboard />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/referrals" element={<ReferralDashboard />} />
            <Route path="/social-proof" element={<SocialProofStudio />} />
            <Route path="/experiments" element={<ExperimentsLab />} />
            <Route path="/campaigns" element={<CampaignCenter />} />
            <Route path="/ambassador" element={<AmbassadorDashboard />} />

            {/* Admin Routes */}
            <Route element={<AdminRoute />}>
              <Route path="/admin" element={<AdminPanel />} />
            </Route>
          </Route>
        </Routes>
      </Router>
    </ToastProvider>
  );
}


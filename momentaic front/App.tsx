
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

const ProtectedLayout = () => {
    return (
        <div className="flex min-h-screen bg-[#050505]">
            <Sidebar />
            <main className="flex-1 md:ml-64 p-6 md:p-8 overflow-y-auto bg-[#050505]">
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
          
          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            
            {/* Startup Routes */}
            <Route path="/startups" element={<StartupsList />} />
            <Route path="/startups/new" element={<StartupNew />} />
            <Route path="/startups/:id" element={<StartupDetail />} />
            <Route path="/startups/:id/signals" element={<StartupDetail />} />
            <Route path="/startups/:id/sprints" element={<StartupDetail />} />
            
            {/* Agent Routes */}
            <Route path="/agents" element={<AgentsMarket />} />
            <Route path="/agents/chat" element={<AgentChat />} />
            
            {/* AgentForge Routes (New) */}
            <Route path="/agent-forge" element={<AgentForge />} />
            <Route path="/vision-portal" element={<VisionPortal />} />

            {/* Growth Engine (New) */}
            <Route path="/growth" element={<GrowthEngine />} />
            
            {/* Other Routes */}
            <Route path="/investment" element={<InvestmentDashboard />} />
            <Route path="/settings" element={<Settings />} />

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

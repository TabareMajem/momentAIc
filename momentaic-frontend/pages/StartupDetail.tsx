
import React, { useEffect, useState } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { api } from '../lib/api';
import { Startup, SignalScores, StartupCreate } from '../types';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Progress } from '../components/ui/Progress';
import { Skeleton } from '../components/ui/Skeleton';
import { SignalHistoryChart } from '../components/charts/SignalHistoryChart';
import { Github, Globe, ExternalLink, Zap, RefreshCw, Edit } from 'lucide-react';
import SprintManagement from './SprintManagement';
import { MetricsForm } from '../components/startups/MetricsForm';
import { Dialog } from '../components/ui/Dialog';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { useForm } from 'react-hook-form';
import { useToast } from '../components/ui/Toast';

// Simple Tab implementation
const TabButton: React.FC<{ active: boolean, onClick: () => void, children: React.ReactNode }> = ({ active, onClick, children }) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
        active 
          ? 'border-blue-600 text-blue-600' 
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      }`}
    >
      {children}
    </button>
  );
}

export default function StartupDetail() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const [startup, setStartup] = useState<Startup | null>(null);
  const [signals, setSignals] = useState<SignalScores | null>(null);
  const [history, setHistory] = useState<SignalScores[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isEditOpen, setIsEditOpen] = useState(false);
  
  const { register, handleSubmit, reset } = useForm<StartupCreate>();
  const { toast } = useToast();

  // Auto-select tab based on URL
  useEffect(() => {
    if (location.pathname.endsWith('/signals')) setActiveTab('signals');
    else if (location.pathname.endsWith('/sprints')) setActiveTab('sprints');
    else setActiveTab('overview');
  }, [location]);

  const fetchData = async () => {
    if (!id) return;
    try {
        const [startupData, signalsData, historyData] = await Promise.all([
            api.getStartup(id),
            api.getSignalScores(id),
            api.getSignalHistory(id)
        ]);
        setStartup(startupData);
        setSignals(signalsData);
        setHistory(historyData);
        reset(startupData); // Pre-fill edit form
    } catch (e) {
        console.error("Failed to load startup detail", e);
    } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleRecalculate = async () => {
    if (!id) return;
    setLoading(true);
    await api.recalculateSignals(id);
    await fetchData();
    setLoading(false);
  };

  const onUpdateStartup = async (data: StartupCreate) => {
      if (!id) return;
      try {
          await api.updateStartup(id, data);
          toast({ type: 'success', title: 'Startup Updated', message: 'Entity details have been synchronized.' });
          setIsEditOpen(false);
          fetchData();
      } catch (e) {
          toast({ type: 'error', title: 'Update Failed', message: 'Could not write to database.' });
      }
  };

  if (loading) return <div className="p-8"><Skeleton className="h-64 w-full" /></div>;
  if (!startup) return <div>Startup not found</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-gray-900">{startup.name}</h1>
            <Badge variant="outline" className="uppercase">{startup.stage}</Badge>
          </div>
          <p className="text-gray-500 mt-1">{startup.industry} • {startup.team_size} Team Members</p>
        </div>
        <div className="flex gap-2">
            {startup.website && (
                <a href={startup.website} target="_blank" rel="noreferrer">
                    <Button variant="outline" size="sm"><Globe className="w-4 h-4 mr-2"/> Website</Button>
                </a>
            )}
            {startup.github_url && (
                <a href={startup.github_url} target="_blank" rel="noreferrer">
                    <Button variant="outline" size="sm"><Github className="w-4 h-4 mr-2"/> Repo</Button>
                </a>
            )}
            <Button variant="default" size="sm" onClick={() => setIsEditOpen(true)}>
                <Edit className="w-4 h-4 mr-2" /> Edit Details
            </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex space-x-4">
          <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')}>Overview</TabButton>
          <TabButton active={activeTab === 'signals'} onClick={() => setActiveTab('signals')}>Signal Scores</TabButton>
          <TabButton active={activeTab === 'sprints'} onClick={() => setActiveTab('sprints')}>Sprint Management</TabButton>
          <TabButton active={activeTab === 'metrics'} onClick={() => setActiveTab('metrics')}>Metrics</TabButton>
        </div>
      </div>

      {/* Content */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle>About</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-gray-700 whitespace-pre-wrap">{startup.description}</p>
                    </CardContent>
                </Card>
            </div>
            <div className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Current Status</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-1">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500">Signal Score</span>
                                <span className="font-bold">{signals?.composite_score}/100</span>
                            </div>
                            <Progress value={signals?.composite_score || 0} />
                        </div>
                        <div className="pt-4 border-t">
                            <Link to={`/agents/chat?startup=${startup.id}`}>
                                <Button className="w-full" variant="secondary">
                                    <Zap className="w-4 h-4 mr-2 text-blue-600" />
                                    Ask AI Advisor
                                </Button>
                            </Link>
                        </div>
                    </CardContent>
                </Card>
            </div>
          </div>
        )}

        {activeTab === 'signals' && (
           <div className="space-y-6">
             <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Performance Signals</h2>
                <Button variant="outline" size="sm" onClick={handleRecalculate}>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Recalculate
                </Button>
             </div>
             
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                 {[
                     { label: 'Tech Velocity', val: signals?.technical_velocity_score },
                     { label: 'Product Market Fit', val: signals?.pmf_score },
                     { label: 'Capital Efficiency', val: signals?.capital_efficiency_score },
                     { label: 'Founder Performance', val: signals?.founder_performance_score },
                 ].map((s, i) => (
                     <Card key={i}>
                         <CardContent className="pt-6">
                             <div className="text-2xl font-bold mb-1">{s.val}</div>
                             <div className="text-xs text-gray-500 uppercase font-medium">{s.label}</div>
                             <Progress value={s.val || 0} className="mt-3 h-1.5" />
                         </CardContent>
                     </Card>
                 ))}
             </div>

             <Card>
                 <CardHeader>
                     <CardTitle>Score History (30 Days)</CardTitle>
                     <CardDescription>Tracking your startup's momentum over time.</CardDescription>
                 </CardHeader>
                 <CardContent>
                     <SignalHistoryChart data={history} />
                 </CardContent>
             </Card>
           </div>
        )}

        {activeTab === 'sprints' && (
            <SprintManagement startupId={startup.id} />
        )}

        {activeTab === 'metrics' && (
            <MetricsForm startupId={startup.id} />
        )}
      </div>

      {/* Edit Dialog */}
      <Dialog 
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        title="Edit Entity Details"
      >
          <form onSubmit={handleSubmit(onUpdateStartup)} className="space-y-4">
              <Input label="Name" {...register('name', { required: true })} />
              <Textarea label="Description" {...register('description')} className="h-24" />
              <div className="grid grid-cols-2 gap-4">
                  <Input label="Industry" {...register('industry')} />
                  <Input label="Team Size" type="number" {...register('team_size')} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                  <Input label="Website" {...register('website')} />
                  <Input label="GitHub" {...register('github_url')} />
              </div>
              <div className="flex justify-end pt-4">
                  <Button type="submit">Update Entity</Button>
              </div>
          </form>
      </Dialog>
    </div>
  );
}

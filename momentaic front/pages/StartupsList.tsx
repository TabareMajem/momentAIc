
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import { Startup, SignalScores } from '../types';
import { Button } from '../components/ui/Button';
import { StartupCard } from '../components/startups/StartupCard';
import { Skeleton } from '../components/ui/Skeleton';
import { Plus, Search, Lock } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { useAuthStore } from '../stores/auth-store';

export default function StartupsList() {
  const [startups, setStartups] = useState<Startup[]>([]);
  const [signals, setSignals] = useState<Record<string, SignalScores>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  const { getStartupLimit, user } = useAuthStore();
  const limit = getStartupLimit();
  const hasReachedLimit = startups.length >= limit;

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getStartups();
        setStartups(data);
        
        // Fetch latest signals for each startup
        const signalsData: Record<string, SignalScores> = {};
        await Promise.all(data.map(async (s) => {
          try {
            const signal = await api.getSignalScores(s.id);
            signalsData[s.id] = signal;
          } catch (e) {
            // Ignore if no signal data
          }
        }));
        setSignals(signalsData);
      } catch (error) {
        console.error("Failed to fetch startups", error);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredStartups = startups.filter(s => 
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    s.industry?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Startups</h1>
          <p className="text-gray-500 text-sm">
             Portfolio Utilization: <span className={hasReachedLimit ? 'text-red-500 font-bold' : 'text-green-500 font-bold'}>{startups.length}</span> / {limit === 999 ? '∞' : limit} Entities
          </p>
        </div>
        
        {hasReachedLimit ? (
            <Link to="/settings">
                <Button variant="cyber" className="border-red-500/50 text-red-500 bg-red-500/10 hover:bg-red-500/20">
                    <Lock className="w-4 h-4 mr-2" />
                    Limit Reached (Upgrade)
                </Button>
            </Link>
        ) : (
            <Link to="/startups/new">
            <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Startup
            </Button>
            </Link>
        )}
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
        <Input 
          className="pl-9 max-w-md" 
          placeholder="Search startups..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="space-y-3">
              <Skeleton className="h-[200px] w-full rounded-xl" />
            </div>
          ))}
        </div>
      ) : filteredStartups.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredStartups.map(startup => (
            <StartupCard 
              key={startup.id} 
              startup={startup} 
              latestSignal={signals[startup.id]} 
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No startups found</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new startup.</p>
          <div className="mt-6">
             {hasReachedLimit ? (
                 <Link to="/settings"><Button variant="outline">Upgrade Plan</Button></Link>
             ) : (
                <Link to="/startups/new">
                <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    New Startup
                </Button>
                </Link>
             )}
          </div>
        </div>
      )}
    </div>
  );
}

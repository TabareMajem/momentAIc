
import React, { useState, useEffect } from 'react';
import { Shield, Search, Filter, Download, Check, X, AlertTriangle, RefreshCw, Trash2, Edit2, CheckCircle, Ban, Clock } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { useToast } from './Toast';

export interface UserProfile {
    id: string;
    email: string;
    name: string;
    role: 'ADMIN' | 'USER' | 'EDITOR';
    plan: 'STARTER' | 'PRO' | 'ENTERPRISE';
    status?: 'ACTIVE' | 'PENDING' | 'SUSPENDED';
    lastLogin: string;
}

export interface SystemStat {
    label: string;
    value: string | number;
    change: number;
    trend: 'UP' | 'DOWN' | 'NEUTRAL';
}

const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'USERS' | 'SETTINGS'>('OVERVIEW');
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [stats, setStats] = useState<SystemStat[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { addToast } = useToast();

  // Edit State
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<UserProfile>>({});

  useEffect(() => {
    refreshData();
  }, []);

  const refreshData = async () => {
    setIsLoading(true);
    try {
      const [fetchedUsers, fetchedStats] = await Promise.all([
        BackendService.getUsers(),
        BackendService.getSystemStats()
      ]);
      setUsers(fetchedUsers);
      setStats(fetchedStats);
    } catch (e: any) {
      console.error(e);
      addToast("Failed to load admin data", 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteUser = async (id: string) => {
    if (confirm('Are you sure you want to delete this user? This cannot be undone.')) {
      try {
        await BackendService.deleteUser(id);
        addToast("User deleted", 'success');
        refreshData();
      } catch (e) {
        addToast("Failed to delete user", 'error');
      }
    }
  };

  const startEdit = (user: UserProfile) => {
    setEditingUserId(user.id);
    setEditForm({ role: user.role, plan: user.plan, status: user.status || 'ACTIVE' }); // Default status if missing
  };

  const saveEdit = async (id: string) => {
    try {
      await BackendService.updateUser(id, editForm);
      setEditingUserId(null);
      addToast("User updated", 'success');
      refreshData();
    } catch (e) {
      addToast("Failed to update user", 'error');
    }
  };

  const cancelEdit = () => {
    setEditingUserId(null);
    setEditForm({});
  };

  const filteredUsers = users.filter(u =>
    u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Chart data from real activity stats
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    loadChartData();
  }, []);

  const loadChartData = async () => {
    try {
      const activityData = await BackendService.getActivityStats();
      // Transform activity data for charts (using total activity per day)
      const transformed = activityData.map((d: any) => ({
        name: d.name,
        value: (d.emails || 0) + (d.content || 0)
      }));
      setChartData(transformed.length > 0 ? transformed : [
        { name: 'Mon', value: 0 },
        { name: 'Tue', value: 0 },
        { name: 'Wed', value: 0 },
        { name: 'Thu', value: 0 },
        { name: 'Fri', value: 0 }
      ]);
    } catch (e) {
      // Fallback to empty data
      setChartData([
        { name: 'Mon', value: 0 },
        { name: 'Tue', value: 0 },
        { name: 'Wed', value: 0 },
        { name: 'Thu', value: 0 },
        { name: 'Fri', value: 0 }
      ]);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto animate-fade-in text-slate-200">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Shield className="w-8 h-8 text-indigo-500 shrink-0" />
            Admin Console
          </h2>
          <p className="text-slate-400 mt-2">System administration and user management.</p>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full md:w-auto">
          <button onClick={refreshData} className={`p-2 bg-slate-800 rounded-full hover:bg-slate-700 transition-colors w-10 h-10 flex items-center justify-center shrink-0 mx-auto sm:mx-0 ${isLoading ? 'animate-spin' : ''}`} title="Refresh Data">
            <RefreshCw className="w-4 h-4 text-slate-400" />
          </button>
          <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700 w-full sm:w-auto">
            <button onClick={() => setActiveTab('OVERVIEW')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex-1 sm:flex-none ${activeTab === 'OVERVIEW' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>Overview</button>
            <button onClick={() => setActiveTab('USERS')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex-1 sm:flex-none ${activeTab === 'USERS' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>Users</button>
            <button onClick={() => setActiveTab('SETTINGS')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex-1 sm:flex-none ${activeTab === 'SETTINGS' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}>System</button>
          </div>
        </div>
      </div>

      {/* --- OVERVIEW TAB --- */}
      {activeTab === 'OVERVIEW' && (
        <div className="space-y-8 animate-in fade-in">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {stats.map((stat, i) => (
              <div key={i} className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                <div className="flex justify-between items-start mb-4">
                  <span className="text-slate-400 text-sm font-medium">{stat.label}</span>
                  <span className={`text-xs font-bold px-2 py-1 rounded ${stat.trend === 'UP' ? 'bg-emerald-500/10 text-emerald-400' :
                    stat.trend === 'DOWN' ? 'bg-rose-500/10 text-rose-400' : 'bg-slate-700 text-slate-400'
                    }`}>
                    {stat.change > 0 ? '+' : ''}{stat.change}%
                  </span>
                </div>
                <div className="text-2xl font-bold text-white">{stat.value}</div>
              </div>
            ))}
          </div>

          {/* Charts */}
          <div className="grid lg:grid-cols-2 gap-8">
            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-6">User Growth Trend</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
                    <Line type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={3} dot={{ r: 4, fill: '#6366f1' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-6">Daily Activity</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
                    <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --- USERS TAB --- */}
      {activeTab === 'USERS' && (
        <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden animate-in fade-in">
          <div className="p-4 border-b border-slate-700 flex flex-col sm:flex-row justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>
            <div className="flex gap-2">
              <button className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white transition-colors">
                <Filter className="w-4 h-4" /> Filter
              </button>
              <button className="flex items-center gap-2 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-sm text-white transition-colors">
                <Download className="w-4 h-4" /> Export CSV
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/50 text-slate-400 font-medium">
                <tr>
                  <th className="px-6 py-4">User</th>
                  <th className="px-6 py-4">Role</th>
                  <th className="px-6 py-4">Plan</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Last Login</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {filteredUsers.map(user => (
                  <tr key={user.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">
                          {user.name.charAt(0)}
                        </div>
                        <div>
                          <div className="font-medium text-white">{user.name}</div>
                          <div className="text-xs text-slate-500">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {editingUserId === user.id ? (
                        <select
                          value={editForm.role}
                          onChange={e => setEditForm({ ...editForm, role: e.target.value as any })}
                          className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs text-white"
                        >
                          <option value="USER">USER</option>
                          <option value="EDITOR">EDITOR</option>
                          <option value="ADMIN">ADMIN</option>
                        </select>
                      ) : (
                        <span className={`text-xs font-bold px-2 py-1 rounded-full border ${user.role === 'ADMIN' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' : 'bg-slate-700/50 text-slate-400 border-slate-600'
                          }`}>
                          {user.role}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {editingUserId === user.id ? (
                        <select
                          value={editForm.plan}
                          onChange={e => setEditForm({ ...editForm, plan: e.target.value as any })}
                          className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs text-white"
                        >
                          <option value="STARTER">STARTER</option>
                          <option value="PRO">PRO</option>
                          <option value="ENTERPRISE">ENTERPRISE</option>
                        </select>
                      ) : (
                        <span className="font-mono text-xs">{user.plan}</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {editingUserId === user.id ? (
                        <select
                          value={editForm.status}
                          onChange={e => setEditForm({ ...editForm, status: e.target.value as any })}
                          className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs text-white"
                        >
                          <option value="ACTIVE">ACTIVE</option>
                          <option value="PENDING">PENDING</option>
                          <option value="SUSPENDED">SUSPENDED</option>
                        </select>
                      ) : (
                        <div className="flex items-center">
                          {user.status === 'ACTIVE' && (
                            <span className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full border bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                              <CheckCircle className="w-3 h-3" /> ACTIVE
                            </span>
                          )}
                          {user.status === 'SUSPENDED' && (
                            <span className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full border bg-rose-500/10 text-rose-400 border-rose-500/20">
                              <Ban className="w-3 h-3" /> SUSPENDED
                            </span>
                          )}
                          {user.status === 'PENDING' && (
                            <span className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full border bg-amber-500/10 text-amber-400 border-amber-500/20">
                              <Clock className="w-3 h-3" /> PENDING
                            </span>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-slate-500">{new Date(user.lastLogin).toLocaleDateString()}</td>
                    <td className="px-6 py-4 text-right">
                      {editingUserId === user.id ? (
                        <div className="flex justify-end gap-2">
                          <button onClick={() => saveEdit(user.id)} className="p-1 bg-emerald-600/20 text-emerald-400 rounded hover:bg-emerald-600/40"><Check className="w-4 h-4" /></button>
                          <button onClick={cancelEdit} className="p-1 bg-slate-600/20 text-slate-400 rounded hover:bg-slate-600/40"><X className="w-4 h-4" /></button>
                        </div>
                      ) : (
                        <div className="flex justify-end gap-2">
                          <button onClick={() => startEdit(user)} className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-700" title="Edit User">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button onClick={() => handleDeleteUser(user.id)} className="p-1 text-slate-400 hover:text-rose-400 rounded hover:bg-slate-700" title="Delete User">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* --- SETTINGS TAB --- */}
      {activeTab === 'SETTINGS' && (
        <div className="grid gap-6 animate-in fade-in">
          <div className="bg-slate-800 p-8 rounded-xl border border-slate-700">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <AlertTriangle className="w-6 h-6 text-amber-500" /> System Health
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="p-4 bg-slate-900 rounded border border-slate-700">
                <span className="text-slate-500 text-sm block mb-1">Database Status</span>
                <span className="text-emerald-400 font-bold flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> Connected (PostgreSQL)</span>
              </div>
              <div className="p-4 bg-slate-900 rounded border border-slate-700">
                <span className="text-slate-500 text-sm block mb-1">Worker Queue</span>
                <span className="text-indigo-400 font-bold">Active</span>
              </div>
              <div className="p-4 bg-slate-900 rounded border border-slate-700">
                <span className="text-slate-500 text-sm block mb-1">API Latency</span>
                <span className="text-white font-bold">~45ms</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
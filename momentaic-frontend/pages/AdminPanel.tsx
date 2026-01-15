
import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { AdminStats, User } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Users, DollarSign, Activity, Server, Search, ShieldAlert } from 'lucide-react';
import { useToast } from '../components/ui/Toast';

export default function AdminPanel() {
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        const load = async () => {
            const [s, u] = await Promise.all([api.getAdminStats(), api.getAdminUsers()]);
            setStats(s);
            setUsers(u);
            setLoading(false);
        };
        load();
    }, []);

    const handleBan = (userId: string) => {
        setUsers(prev => prev.map(u => 
            u.id === userId ? { ...u, status: u.status === 'banned' ? 'active' : 'banned' } : u
        ));
        toast({ type: 'info', title: 'User Status Updated', message: `User ${userId} privileges modified.` });
    };

    const handleEdit = (user: User) => {
         toast({ type: 'info', title: 'Edit Mode Locked', message: 'Direct database modification requires root access override.' });
    };

    if (loading) return <div className="p-8 font-mono text-[#00f0ff]">INITIALIZING_ADMIN_PROTOCOL...</div>;

    return (
        <div className="space-y-8 animate-fade-in text-gray-200">
            <div className="flex justify-between items-center border-b border-white/10 pb-6">
                <div>
                    <h1 className="text-3xl font-black tracking-tighter text-white font-mono">GOD_MODE // ADMIN</h1>
                    <p className="text-gray-500 font-mono text-sm mt-1">SYSTEM OVERVIEW & USER CONTROL</p>
                </div>
                <Badge variant="outline" className="border-[#ff003c] text-[#ff003c] bg-[#ff003c]/10 animate-pulse">
                    LIVE CONNECTION
                </Badge>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                    { label: 'TOTAL USERS', value: stats?.total_users, icon: <Users className="text-[#00f0ff]"/> },
                    { label: 'ACTIVE SUBS', value: stats?.active_subscriptions, icon: <Activity className="text-[#00ff9d]"/> },
                    { label: 'REVENUE', value: `$${(stats?.total_revenue || 0).toLocaleString()}`, icon: <DollarSign className="text-[#ffee00]"/> },
                    { label: 'AGENTS LIVE', value: stats?.agents_deployed, icon: <Server className="text-[#2563eb]"/> },
                ].map((stat, i) => (
                    <Card key={i} className="bg-[#0a0a0a] border-white/10">
                        <CardContent className="p-6 flex items-center justify-between">
                            <div>
                                <div className="text-xs font-mono text-gray-500 mb-1">{stat.label}</div>
                                <div className="text-2xl font-bold font-mono text-white">{stat.value}</div>
                            </div>
                            <div className="p-3 bg-white/5 rounded-none border border-white/10">
                                {stat.icon}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Users Table */}
            <Card className="bg-[#0a0a0a] border-white/10 overflow-hidden">
                <CardHeader className="border-b border-white/10 bg-[#111]">
                    <div className="flex justify-between items-center">
                        <CardTitle className="font-mono text-sm uppercase">User Database</CardTitle>
                        <div className="flex gap-2">
                             <input className="bg-black border border-white/20 px-3 py-1 text-sm font-mono text-white focus:outline-none focus:border-[#2563eb]" placeholder="SEARCH_ID..." />
                             <Button variant="outline" size="sm" className="border-white/20 hover:bg-white/10"><Search className="w-4 h-4"/></Button>
                        </div>
                    </div>
                </CardHeader>
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-white/10 text-xs font-mono text-gray-500 uppercase">
                                <th className="p-4">User</th>
                                <th className="p-4">Role</th>
                                <th className="p-4">Tier</th>
                                <th className="p-4">Status</th>
                                <th className="p-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="text-sm font-mono">
                            {users.map(user => (
                                <tr key={user.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                    <td className="p-4">
                                        <div className="font-bold text-white">{user.full_name}</div>
                                        <div className="text-xs text-gray-500">{user.email}</div>
                                    </td>
                                    <td className="p-4">
                                        <span className={`px-2 py-0.5 text-[10px] border ${user.role === 'admin' ? 'border-[#ff003c] text-[#ff003c]' : 'border-gray-600 text-gray-400'}`}>
                                            {user.role.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="p-4">
                                        <Badge variant="secondary" className="bg-white/10 text-white rounded-none border-0">
                                            {user.subscription_tier.toUpperCase()}
                                        </Badge>
                                    </td>
                                    <td className="p-4">
                                        <div className="flex items-center gap-2">
                                            <div className={`w-2 h-2 rounded-full ${user.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                                            <span className={user.status === 'active' ? 'text-green-500' : 'text-red-500'}>
                                                {user.status.toUpperCase()}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="p-4 text-right">
                                        <Button variant="ghost" size="sm" onClick={() => handleEdit(user)} className="text-gray-400 hover:text-white hover:bg-white/10">
                                            EDIT
                                        </Button>
                                        <Button variant="ghost" size="sm" onClick={() => handleBan(user.id)} className="text-[#ff003c] hover:bg-[#ff003c]/10">
                                            {user.status === 'active' ? 'BAN' : 'UNBAN'}
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}

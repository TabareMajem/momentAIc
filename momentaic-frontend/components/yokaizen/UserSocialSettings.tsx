import React, { useEffect, useState } from 'react';
import { BackendService } from '../../services/backendService';
import { Linkedin, Github, CheckCircle, XCircle, Link, RefreshCw } from 'lucide-react';
import { useToast } from './Toast';

const UserSocialSettings: React.FC = () => {
    const [connections, setConnections] = useState<any>({ linkedin: null, github: null });
    const [isLoading, setIsLoading] = useState(true);
    const { addToast } = useToast();

    useEffect(() => {
        loadConnections();

        // Check for URL params for success/error messages after redirect
        const params = new URLSearchParams(window.location.search);
        if (params.get('success')) {
            addToast(`Successfully connected ${params.get('success') === 'linkedin_connected' ? 'LinkedIn' : 'GitHub'}!`, 'success');
        }
        if (params.get('error')) {
            addToast('Connection failed. Please try again.', 'error');
        }
    }, []);

    const loadConnections = async () => {
        try {
            const data = await BackendService.getSocialConnections();
            setConnections(data);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleConnect = (platform: 'linkedin' | 'github') => {
        // Redirect to backend auth flow
        window.location.href = `${BackendService.API_URL}/social/${platform}/authorize?token=${localStorage.getItem('token')}`;
    };

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Link className="w-5 h-5 text-indigo-400" />
                Social Connections (Real Mode)
            </h3>

            <div className="grid md:grid-cols-2 gap-4">
                {/* LinkedIn Card */}
                <div className={`p-4 rounded-xl border flex flex-col gap-4 transition-all ${connections.linkedin ? 'bg-indigo-900/20 border-indigo-500/50' : 'bg-slate-950 border-slate-800'}`}>
                    <div className="flex justify-between items-start">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-[#0077b5] rounded-lg text-white">
                                <Linkedin className="w-6 h-6" />
                            </div>
                            <div>
                                <h4 className="font-bold text-slate-200">LinkedIn</h4>
                                <p className="text-xs text-slate-500">Post updates & articles</p>
                            </div>
                        </div>
                        {connections.linkedin ? (
                            <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-1 rounded-full flex items-center gap-1 font-bold">
                                <CheckCircle className="w-3 h-3" /> Connected
                            </span>
                        ) : (
                            <span className="bg-slate-800 text-slate-500 text-xs px-2 py-1 rounded-full flex items-center gap-1 font-bold">
                                <XCircle className="w-3 h-3" /> Disconnected
                            </span>
                        )}
                    </div>

                    {connections.linkedin ? (
                        <div className="mt-auto pt-4 border-t border-indigo-500/20">
                            <p className="text-xs text-indigo-300">Profile ID: {connections.linkedin.profileId}</p>
                            <p className="text-[10px] text-slate-500 mt-1">Expires: {new Date(connections.linkedin.expiresAt).toLocaleDateString()}</p>
                            <button className="mt-2 text-xs text-slate-400 hover:text-white underline" onClick={() => handleConnect('linkedin')}>Reconnect</button>
                        </div>
                    ) : (
                        <button
                            onClick={() => handleConnect('linkedin')}
                            className="mt-2 w-full bg-[#0077b5] hover:bg-[#006097] text-white py-2 rounded-lg font-bold text-sm transition-colors flex items-center justify-center gap-2"
                        >
                            Connect LinkedIn
                        </button>
                    )}
                </div>

                {/* GitHub Card */}
                <div className={`p-4 rounded-xl border flex flex-col gap-4 transition-all ${connections.github ? 'bg-slate-800/40 border-slate-600/50' : 'bg-slate-950 border-slate-800'}`}>
                    <div className="flex justify-between items-start">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-slate-800 rounded-lg text-white border border-slate-700">
                                <Github className="w-6 h-6" />
                            </div>
                            <div>
                                <h4 className="font-bold text-slate-200">GitHub</h4>
                                <p className="text-xs text-slate-500">Workflow Agent Commits</p>
                            </div>
                        </div>
                        {connections.github ? (
                            <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-1 rounded-full flex items-center gap-1 font-bold">
                                <CheckCircle className="w-3 h-3" /> Connected
                            </span>
                        ) : (
                            <span className="bg-slate-800 text-slate-500 text-xs px-2 py-1 rounded-full flex items-center gap-1 font-bold">
                                <XCircle className="w-3 h-3" /> Disconnected
                            </span>
                        )}
                    </div>

                    {connections.github ? (
                        <div className="mt-auto pt-4 border-t border-slate-700/50">
                            <p className="text-xs text-slate-300">Account: {connections.github.profileId}</p>
                            <button className="mt-2 text-xs text-slate-400 hover:text-white underline" onClick={() => handleConnect('github')}>Reconnect</button>
                        </div>
                    ) : (
                        <button
                            onClick={() => handleConnect('github')}
                            className="mt-2 w-full bg-slate-800 hover:bg-slate-700 text-white py-2 rounded-lg font-bold text-sm transition-colors flex items-center justify-center gap-2 border border-slate-700"
                        >
                            Connect GitHub
                        </button>
                    )}
                </div>
            </div>

            <p className="text-xs text-slate-500 mt-6 flex items-center gap-2">
                <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
                Status refreshes automatically. Connecting users grants Agents permission to act on your behalf.
            </p>
        </div>
    );
};

export default UserSocialSettings;

import React, { useState, useEffect } from 'react';
import { Target, User, RefreshCw, Copy, Check, AlertCircle, Plus, Trash2, X, Upload } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { SniperTarget } from '../../types';
import { useToast } from './Toast';

const SniperAgent: React.FC = () => {
  const [targets, setTargets] = useState<SniperTarget[]>([]);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const { addToast } = useToast();

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTargetName, setNewTargetName] = useState('');
  const [newTargetUrl, setNewTargetUrl] = useState('');
  const [newCompanyUrl, setNewCompanyUrl] = useState('');
  const [newTargetProfile, setNewTargetProfile] = useState('');

  useEffect(() => {
    loadTargets();
  }, []);

  const loadTargets = async () => {
    try {
      const data = await BackendService.getTargets();
      setTargets(data);
    } catch (e) {
      console.error("Failed to load targets", e);
    }
  };

  const handleAddTarget = async (e: React.FormEvent) => {
    e.preventDefault();
    const newTarget = {
      name: newTargetName,
      linkedinUrl: newTargetUrl,
      companyUrl: newCompanyUrl,
      rawProfileText: newTargetProfile,
    };

    try {
      await BackendService.createTarget(newTarget);
      await loadTargets();
      setIsModalOpen(false);
      // Reset form
      setNewTargetName('');
      setNewTargetUrl('');
      setNewCompanyUrl('');
      setNewTargetProfile('');
      addToast('Target added to queue successfully', 'success');
    } catch (e) {
      addToast('Failed to add target', 'error');
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Remove this target?')) {
      try {
        await BackendService.deleteTarget(id);
        await loadTargets();
        addToast('Target removed', 'info');
      } catch (e) {
        addToast('Failed to delete target', 'error');
      }
    }
  };

  const handleGenerate = async (target: SniperTarget) => {
    setLoadingId(target.id);
    try {
      const result = await BackendService.generateIcebreaker(target.id);
      // Result is the updated target object from backend
      setTargets(prev => prev.map(t => t.id === target.id ? result : t));
      await BackendService.refreshProfile(); // Update credits in UI
      addToast('Icebreaker generated successfully', 'success');
    } catch (e: any) {
      console.error(e);
      addToast(e.message || "Failed to generate icebreaker", 'error');
    } finally {
      setLoadingId(null);
    }
  };

  const handleBulkUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const response = await BackendService.sniperBulkUpload(file);
      if (response.success) {
        addToast(`Successfully imported ${response.count} targets`, 'success');
        await loadTargets();
      }
    } catch (e: any) {
      console.error(e);
      addToast(e.response?.data?.error || "Failed to upload CSV", 'error');
    }
    // Reset input
    e.target.value = '';
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    addToast('Copied to clipboard', 'success');
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto animate-fade-in relative">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Target className="w-8 h-8 text-rose-500 shrink-0" />
            Agent A: The Sniper
          </h2>
          <p className="text-slate-400 mt-2">Hyper-personalized outbound generation. No templates allowed.</p>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full lg:w-auto">
          <div className="bg-rose-500/10 text-rose-400 px-4 py-2 rounded-full border border-rose-500/20 text-sm font-medium w-full sm:w-auto text-center shrink-0">
            Queue: {targets.filter(t => t.status === 'NEW').length} Targets
          </div>
          <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
            <label className="cursor-pointer bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors border border-slate-600 w-full sm:w-auto whitespace-nowrap">
              <Upload className="w-4 h-4 shrink-0" /> Import CSV
              <input type="file" accept=".csv" className="hidden" onChange={handleBulkUpload} />
            </label>
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors shadow-lg shadow-rose-900/20 w-full sm:w-auto whitespace-nowrap"
            >
              <Plus className="w-4 h-4 shrink-0" /> Add Target
            </button>
          </div>
        </div>
      </div>

      {targets.length === 0 && (
        <div className="text-center py-20 bg-slate-800/50 rounded-xl border border-slate-700 border-dashed">
          <User className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl text-slate-300 font-bold">No Targets in Queue</h3>
          <p className="text-slate-500 mb-6">Add a prospect to start generating icebreakers.</p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-slate-700 hover:bg-slate-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
          >
            Add Your First Target
          </button>
        </div>
      )}

      <div className="grid gap-6">
        {targets.map((target) => (
          <div key={target.id} className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden group">
            <div className="p-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center shrink-0">
                    <User className="text-slate-400" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-xl font-semibold text-white truncate w-full max-w-[200px] sm:max-w-[300px]">{target.name}</h3>
                    <p className="text-sm text-indigo-400 truncate w-full max-w-[200px] sm:max-w-[300px]">{target.linkedinUrl}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 w-full md:w-auto justify-between md:justify-end">
                  {target.status === 'NEW' ? (
                    <button
                      onClick={() => handleGenerate(target)}
                      disabled={!!loadingId}
                      className="flex items-center justify-center w-full md:w-auto gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 text-sm md:text-base whitespace-nowrap"
                    >
                      {loadingId === target.id ? <RefreshCw className="w-4 h-4 shrink-0 animate-spin" /> : <Target className="w-4 h-4 shrink-0" />}
                      Generate Hook
                    </button>
                  ) : (
                    <span className="bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full text-xs font-medium border border-emerald-500/20 shrink-0">
                      Ready
                    </span>
                  )}
                  <button
                    onClick={() => handleDelete(target.id)}
                    className="p-2 text-slate-500 hover:text-rose-400 transition-colors shrink-0 bg-slate-800 border border-slate-700 rounded-lg md:border-none md:bg-transparent"
                    title="Delete Target"
                  >
                    <Trash2 className="w-4 h-4 ml-auto" />
                  </button>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Scraped Profile Data</h4>
                  <p className="text-slate-300 text-sm leading-relaxed opacity-80 italic">
                    "{target.rawProfileText}"
                  </p>
                </div>

                {target.icebreaker ? (
                  <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 p-4 rounded-lg border border-indigo-500/30 relative">
                    <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2">AI Generated Icebreaker</h4>
                    <p className="text-white text-lg font-medium leading-relaxed">
                      {target.icebreaker}
                    </p>
                    <button
                      onClick={() => copyToClipboard(target.icebreaker!, target.id)}
                      className="absolute top-3 right-3 text-slate-400 hover:text-white transition-colors p-1 rounded bg-slate-800/50"
                    >
                      {copiedId === target.id ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                ) : loadingId === target.id ? (
                  <div className="border border-slate-800 rounded-lg p-6 space-y-3">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-4 h-4 bg-indigo-500/20 rounded animate-pulse"></div>
                      <div className="h-3 w-24 bg-indigo-500/20 rounded animate-pulse"></div>
                    </div>
                    <div className="h-4 w-full bg-slate-800 rounded animate-pulse"></div>
                    <div className="h-4 w-5/6 bg-slate-800 rounded animate-pulse"></div>
                    <div className="h-4 w-4/6 bg-slate-800 rounded animate-pulse"></div>
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-slate-700 rounded-lg flex items-center justify-center text-slate-500 text-sm p-6 group-hover:border-slate-600 transition-colors">
                    Waiting for generation...
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add Target Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 w-full max-w-lg rounded-xl border border-slate-700 shadow-2xl overflow-hidden animate-in zoom-in-95 flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-slate-800 flex justify-between items-center shrink-0">
              <h3 className="text-xl font-bold text-white">Add New Target</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white"><X className="w-6 h-6" /></button>
            </div>
            <form onSubmit={handleAddTarget} className="p-6 space-y-4 overflow-y-auto">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Target Name</label>
                <input required value={newTargetName} onChange={e => setNewTargetName(e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-rose-500 outline-none" placeholder="e.g. Elon Musk" />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">LinkedIn URL</label>
                <input value={newTargetUrl} onChange={e => setNewTargetUrl(e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-rose-500 outline-none" placeholder="e.g. linkedin.com/in/elon" />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Company URL (Optional)</label>
                <input value={newCompanyUrl} onChange={e => setNewCompanyUrl(e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-rose-500 outline-none" placeholder="e.g. https://tesla.com" />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Profile Text / Notes</label>
                <textarea required value={newTargetProfile} onChange={e => setNewTargetProfile(e.target.value)} className="w-full h-32 bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-rose-500 outline-none" placeholder="Paste their 'About' section or recent post content here..." />
              </div>
              <div className="pt-4 flex justify-end gap-3 shrink-0">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-slate-400 hover:text-white">Cancel</button>
                <button type="submit" className="bg-rose-600 hover:bg-rose-500 text-white px-6 py-2 rounded-lg font-bold shadow-lg shadow-rose-900/20">Add Target</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SniperAgent;
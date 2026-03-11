import React, { useState, useEffect } from 'react';
import { ShieldAlert, Mail, BrainCircuit, AlertCircle, PlusCircle, Trash2, Send } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { Lead } from '../../types';
import { useToast } from './Toast';

const GatekeeperAgent: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const { addToast } = useToast();

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    try {
      const data = await BackendService.getLeads();
      setLeads(data);
    } catch (e) {
      console.error("Failed to load leads", e);
    }
  };

  const handleAnalyze = async (lead: Lead) => {
    setProcessingId(lead.id);
    try {
      const analysis = await BackendService.analyzeLead(lead.id);
      // Backend returns the updated lead object
      setLeads(prev => prev.map(l => l.id === lead.id ? analysis : l));
      addToast('Lead analyzed successfully', 'success');
    } catch (e: any) {
      console.error(e);
      addToast(e.message || "Analysis failed", 'error');
    } finally {
      setProcessingId(null);
    }
  };

  const simulateInboundLead = async () => {
    const names = ["TechNova Inc", "Spam King", "Serious Buyer LLC", "Partner Connect"];
    const messages = [
      "We are looking for enterprise AI solutions, budget approved.",
      "I can get you 10,000 likes on Instagram for $5.",
      "Is your API compatible with legacy SAP systems?",
      "We would like to discuss a reseller partnership opportunity."
    ];

    const randomIdx = Math.floor(Math.random() * names.length);

    const payload = {
      name: names[randomIdx],
      email: `contact@${names[randomIdx].replace(/ /g, '').toLowerCase()}.com`,
      message: messages[randomIdx],
      source: 'WEB_FORM'
    };

    try {
      // Hit the public webhook
      await fetch('/api/gatekeeper/inbound', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      addToast('New inbound lead received (Webhook Triggered)', 'info');
      // Wait a bit for DB consistency then reload
      setTimeout(loadLeads, 1000);
    } catch (e) {
      addToast('Failed to simulate lead', 'error');
    }
  };

  const clearLead = async (id: string, action: 'deleted' | 'archived') => {
    try {
      // Call backend to archive
      await BackendService.archiveLead(id);
      const updated = leads.filter(l => l.id !== id);
      setLeads(updated);
      addToast(action === 'deleted' ? 'Lead deleted' : 'Lead archived', 'info');
    } catch (e: any) {
      addToast('Failed to archive lead', 'error');
    }
  };

  const sendReply = async (id: string) => {
    try {
      await BackendService.replyToLead(id);
      const updated = leads.filter(l => l.id !== id);
      setLeads(updated);
      addToast('Reply sent and lead status updated!', 'success');
    } catch (e: any) {
      addToast('Failed to send reply', 'error');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'QUALIFIED': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'SPAM': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'TIRE_KICKER': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'PARTNERSHIP': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      default: return 'text-slate-400 bg-slate-700/50 border-slate-600';
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <ShieldAlert className="w-8 h-8 text-emerald-500 shrink-0" />
            Agent B: The Gatekeeper
          </h2>
          <p className="text-slate-400 mt-2">Automated inbound triage. Never waste time on bad leads.</p>
        </div>
        <button
          onClick={simulateInboundLead}
          className="flex items-center justify-center w-full md:w-auto gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <PlusCircle className="w-4 h-4 shrink-0" /> Simulate Inbound Lead
        </button>
      </div>

      {leads.length === 0 && (
        <div className="text-center py-20 border-2 border-dashed border-slate-700 rounded-xl">
          <p className="text-slate-500 mb-4">No pending leads in the queue.</p>
          <button onClick={simulateInboundLead} className="text-emerald-400 font-bold hover:underline">Generate Test Lead</button>
        </div>
      )}

      <div className="grid gap-4">
        {leads.map((lead) => (
          <div key={lead.id} className={`bg-slate-800 rounded-xl border ${lead.status === 'PENDING' ? 'border-slate-700' : 'border-slate-700/50'} overflow-hidden transition-all hover:border-slate-600`}>
            <div className="p-6 flex flex-col md:flex-row gap-6">
              {/* Left: Lead Info */}
              <div className="flex-1">
                <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 mb-3 pr-8">
                  <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center shrink-0">
                    <Mail className="w-5 h-5 text-slate-300" />
                  </div>
                  <div className="flex-1 min-w-[150px]">
                    <h3 className="font-semibold text-white truncate text-sm sm:text-base">{lead.name}</h3>
                    <p className="text-xs text-slate-400 truncate">{lead.email}</p>
                  </div>
                  <div className={`sm:ml-auto px-3 py-1 rounded-full text-xs font-bold border shrink-0 ${getStatusColor(lead.status)}`}>
                    {lead.status}
                  </div>
                </div>
                <div className="bg-slate-900/50 p-3 rounded border border-slate-700/50">
                  <p className="text-slate-300 text-sm italic">"{lead.message}"</p>
                </div>
                <div className="mt-2 text-xs text-slate-500">
                  Received: {new Date(lead.timestamp).toLocaleString()}
                </div>
              </div>

              {/* Right: Action / Analysis */}
              <div className="md:w-1/2 border-l border-slate-700 md:pl-6 flex flex-col justify-center">
                {lead.status === 'PENDING' ? (
                  <div className="text-center py-4 relative">
                    <p className="text-slate-500 text-sm mb-4">Awaiting classification...</p>
                    <button
                      onClick={() => handleAnalyze(lead)}
                      disabled={!!processingId}
                      className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg font-medium transition-colors shadow-lg shadow-emerald-900/20 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {processingId === lead.id ? (
                        <BrainCircuit className="w-5 h-5 animate-pulse" />
                      ) : (
                        <ShieldAlert className="w-5 h-5" />
                      )}
                      Analyze & Triage
                    </button>
                    <button onClick={() => clearLead(lead.id, 'deleted')} className="absolute top-0 right-0 text-slate-600 hover:text-rose-500 p-2">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500 relative">
                    <button onClick={() => clearLead(lead.id, 'deleted')} className="absolute -top-1 -right-1 text-slate-600 hover:text-rose-500 p-1">
                      <Trash2 className="w-3 h-3" />
                    </button>
                    <div>
                      <h4 className="text-xs font-bold text-slate-500 uppercase mb-1">AI Reasoning</h4>
                      <p className="text-sm text-slate-300">{lead.analysis?.reasoning}</p>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-500 uppercase mb-1">Suggested Draft</h4>
                      <div className="bg-slate-900 p-3 rounded border border-slate-700 text-sm text-indigo-200 font-mono leading-relaxed">
                        {lead.analysis?.suggestedReply}
                      </div>
                    </div>
                    <div className="flex gap-3 pt-2">
                      <button onClick={() => clearLead(lead.id, 'archived')} className="flex-1 bg-white/5 hover:bg-white/10 text-white text-xs py-2 rounded border border-white/10 whitespace-nowrap">Archive</button>
                      <button onClick={() => sendReply(lead.id)} className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs py-2 rounded shadow-lg shadow-indigo-900/20 flex items-center justify-center gap-1 whitespace-nowrap">
                        <Send className="w-3 h-3 shrink-0" /> Send Reply
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GatekeeperAgent;
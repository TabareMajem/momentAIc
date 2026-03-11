
import React, { useState, useEffect } from 'react';
import { Workflow, ArrowRight, Copy, Check, Download, Trash2, Settings, Power, UploadCloud, Play, AlertCircle, Code2, Zap, Info, FileJson, AlertTriangle, Layers, Cpu, Network, Save } from 'lucide-react';
import { generateN8nWorkflow } from '../../services/geminiService';
import { BackendService } from '../../services/backendService';
import { pushWorkflowToN8n, triggerN8nWebhook, checkN8nConnection } from '../../services/n8nService';
import { validateWorkflow } from '../../services/workflowEngine';
import { useToast } from './Toast';

export interface N8nConfig {
  baseUrl: string;
  apiKey: string;
}

export interface YokaizenWorkflow {
  name?: string;
  nodes: any[];
  edges?: any[];
  connections?: any;
}

const MULTI_AGENT_DEMO_JSON = JSON.stringify({
  "name": "Yokaizen Multi-Agent Workflow",
  "nodes": [
    { "id": "orchestrator", "type": "ai_analysis", "name": "Master Orchestrator", "config": { "model": "claude-3-sonnet" } },
    { "id": "research", "type": "ai_agent_tool", "name": "Research Agent", "config": { "agent_config": { "model": "gpt-4o" } } },
    { "id": "writer", "type": "ai_agent_tool", "name": "Content Agent", "config": { "agent_config": { "model": "claude-3-haiku" } } },
    { "id": "coder", "type": "ai_agent_tool", "name": "Technical Agent", "config": { "agent_config": { "model": "claude-3-sonnet" } } },
    { "id": "browser", "type": "browser_automation", "name": "Scraper Tool", "config": { "antiDetection": { "enabled": true } } }
  ]
}, null, 2);

const WorkflowAgent: React.FC = () => {
  const { addToast } = useToast();
  const [activeMode, setActiveMode] = useState<'BUILDER' | 'IMPORTER'>('BUILDER');

  // Builder State
  const [prompt, setPrompt] = useState('');
  const [workflowJson, setWorkflowJson] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Importer State
  const [importedJson, setImportedJson] = useState('');
  const [parsedWorkflow, setParsedWorkflow] = useState<YokaizenWorkflow | null>(null);
  const [auditReport, setAuditReport] = useState<any>(null);

  // N8n Integration State
  const [showSettings, setShowSettings] = useState(false);
  const [n8nConfig, setN8nConfig] = useState<N8nConfig>({ baseUrl: '', apiKey: '' });
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'IDLE' | 'CHECKING' | 'SUCCESS' | 'ERROR'>('IDLE');

  const [pushStatus, setPushStatus] = useState<'IDLE' | 'PUSHING' | 'SUCCESS' | 'ERROR'>('IDLE');
  const [pushFeedback, setPushFeedback] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  // Library State
  const [savedWorkflows, setSavedWorkflows] = useState<any[]>([]);

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      // Assuming BackendService is imported or defined elsewhere
      const data = await BackendService.getWorkflows();
      setSavedWorkflows(data);
    } catch (e) {
      console.error("Failed to load workflows", e);
    }
  };

  const handleSaveWorkflow = async () => {
    if (!workflowJson) return;
    try {
      const parsed = JSON.parse(workflowJson);
      // Simple heuristic to extract name or use prompt
      const name = parsed.name || prompt.slice(0, 20) || "Untitled Workflow";

      // Assuming BackendService is imported or defined elsewhere
      await BackendService.saveWorkflow({
        name,
        nodes: parsed.nodes || [],
        edges: parsed.connections || parsed.edges || []
      });

      // Assuming addToast is imported or defined elsewhere
      addToast("Workflow saved to library", 'success');
      loadWorkflows();
    } catch (e: any) {
      // Assuming addToast is imported or defined elsewhere
      addToast("Failed to save workflow", 'error');
    }
  };

  useEffect(() => {
    const savedConfig = localStorage.getItem('n8n_config');
    if (savedConfig) {
      setN8nConfig(JSON.parse(savedConfig));
    }
  }, []);

  const saveConfig = () => {
    localStorage.setItem('n8n_config', JSON.stringify(n8nConfig));
    handleCheckConnection();
  };

  const handleCheckConnection = async () => {
    setConnectionStatus('CHECKING');
    const success = await checkN8nConnection(n8nConfig);
    if (success) {
      setConnectionStatus('SUCCESS');
      setIsConnected(true);
      setTimeout(() => setShowSettings(false), 1500);
    } else {
      setConnectionStatus('ERROR');
      setIsConnected(false);
    }
  };

  const handleGenerate = async () => {
    if (!prompt) return;
    setIsProcessing(true);
    setError(null);
    setWorkflowJson('');
    try {
      const json = await generateN8nWorkflow(prompt);
      setWorkflowJson(json);
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Failed to generate workflow");
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePushToN8n = async () => {
    if (!workflowJson || !isConnected) return;
    setPushStatus('PUSHING');
    setPushFeedback(null);
    try {
      const parsedJson = JSON.parse(workflowJson);
      const result = await pushWorkflowToN8n(n8nConfig, parsedJson, prompt.slice(0, 30));
      setPushStatus('SUCCESS');
      setPushFeedback({
        type: 'success',
        message: `Workflow successfully created! ID: ${result.id}`
      });
    } catch (e: any) {
      console.error(e);
      setPushStatus('ERROR');
      setPushFeedback({
        type: 'error',
        message: `Push failed: ${e.message}`
      });
    }
  };

  const handleImportAnalysis = () => {
    try {
      const parsed = JSON.parse(importedJson);
      setParsedWorkflow(parsed);
      const report = validateWorkflow(parsed);
      setAuditReport(report);
    } catch (e) {
      setError("Invalid JSON format");
    }
  };

  const loadDemo = () => {
    setImportedJson(MULTI_AGENT_DEMO_JSON);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(workflowJson);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto animate-fade-in text-slate-200">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Workflow className="w-8 h-8 text-cyan-400 shrink-0" />
            Agent E: Workflow Architect
          </h2>
          <p className="text-slate-400 mt-2">Design, Build, and Audit your autonomous systems.</p>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full md:w-auto">
          <div className="bg-slate-800 p-1 rounded-lg border border-slate-700 flex w-full sm:w-auto justify-between">
            <button
              onClick={() => setActiveMode('BUILDER')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex-1 sm:flex-none ${activeMode === 'BUILDER' ? 'bg-cyan-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
            >
              AI Generator
            </button>
            <button
              onClick={() => setActiveMode('IMPORTER')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex-1 sm:flex-none ${activeMode === 'IMPORTER' ? 'bg-cyan-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
            >
              Audit & Execute
            </button>
          </div>

          {activeMode === 'BUILDER' && (
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${isConnected ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400' : 'bg-slate-800 border-slate-600 text-slate-400 hover:text-white'}`}
            >
              {isConnected ? <Power className="w-4 h-4" /> : <Settings className="w-4 h-4" />}
              {isConnected ? "n8n Connected" : "Connect n8n"}
            </button>
          )}
        </div>
      </div>

      {/* --- BUILDER MODE --- */}
      {activeMode === 'BUILDER' && (
        <div className="animate-in fade-in">
          {showSettings && (
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-8 shadow-xl animate-in slide-in-from-top-4">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Settings className="w-5 h-5 text-cyan-400" />
                Bridge Configuration
              </h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">n8n Instance URL</label>
                  <input
                    type="text"
                    value={n8nConfig.baseUrl}
                    onChange={(e) => setN8nConfig({ ...n8nConfig, baseUrl: e.target.value })}
                    placeholder="https://n8n.yourdomain.com"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-cyan-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">API Key</label>
                  <input
                    type="password"
                    value={n8nConfig.apiKey}
                    onChange={(e) => setN8nConfig({ ...n8nConfig, apiKey: e.target.value })}
                    placeholder="n8n_api_..."
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-cyan-500 outline-none"
                  />
                </div>
              </div>
              <div className="mt-6 flex flex-col sm:flex-row items-center gap-4">
                <button
                  onClick={saveConfig}
                  disabled={connectionStatus === 'CHECKING'}
                  className="w-full sm:w-auto bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-2 rounded-lg font-bold flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {connectionStatus === 'CHECKING' ? "Checking..." : "Save & Connect"}
                </button>
                {connectionStatus === 'SUCCESS' && <span className="text-emerald-400 text-sm flex items-center gap-1"><Check className="w-4 h-4 shrink-0" /> Connected Successfully</span>}
                {connectionStatus === 'ERROR' && <span className="text-rose-400 text-sm flex items-center gap-1"><AlertCircle className="w-4 h-4 shrink-0" /> Connection Failed (Check URL/CORS)</span>}
              </div>
            </div>
          )}

          <div className="grid lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 shadow-xl">
                <div className="flex justify-between items-center mb-3">
                  <label className="block text-sm font-bold text-slate-300 flex items-center gap-2">
                    <Code2 className="w-4 h-4 text-cyan-500" />
                    Blueprint Description
                  </label>
                  {prompt && (
                    <button onClick={() => setPrompt('')} className="text-xs text-slate-500 hover:text-white flex items-center gap-1 transition-colors">
                      <Trash2 className="w-3 h-3" /> Clear
                    </button>
                  )}
                </div>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g., Every Monday at 9am, fetch data from Google Sheets, use Gemini to summarize it, and send an email via Gmail."
                  className="w-full h-48 bg-slate-900 border border-slate-700 rounded-lg p-4 text-slate-200 focus:ring-2 focus:ring-cyan-500 outline-none resize-none placeholder:text-slate-600 transition-all"
                />

                <div className="mt-4 flex justify-end">
                  <button
                    onClick={handleGenerate}
                    disabled={isProcessing || !prompt}
                    className="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg font-bold flex items-center gap-2 transition-all disabled:opacity-50 shadow-lg shadow-cyan-900/20 hover:scale-[1.02]"
                  >
                    {isProcessing ? <Workflow className="w-5 h-5 animate-spin" /> : <ArrowRight className="w-5 h-5" />}
                    {isProcessing ? "Architecting..." : "Build Blueprint"}
                  </button>
                </div>
              </div>
            </div>

            <div className="flex flex-col h-[600px]">
              <div className="bg-slate-800 rounded-t-xl border-x border-t border-slate-700 px-4 py-3 flex justify-between items-center">
                <span className="text-xs font-mono text-cyan-400">workflow.json</span>
                <div className="flex gap-2">
                  {workflowJson && (
                    <button
                      onClick={handleSaveWorkflow}
                      className="flex items-center gap-2 text-xs px-3 py-1.5 rounded border border-slate-600 bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors font-bold"
                    >
                      <Save className="w-3 h-3" /> Save to Library
                    </button>
                  )}
                  {workflowJson && isConnected && (
                    <button
                      onClick={handlePushToN8n}
                      disabled={pushStatus === 'PUSHING'}
                      className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded border transition-colors font-bold ${pushStatus === 'SUCCESS'
                        ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                        : pushStatus === 'ERROR'
                          ? 'bg-rose-500/20 border-rose-500 text-rose-400'
                          : 'bg-indigo-600 border-indigo-500 text-white hover:bg-indigo-500'
                        }`}
                    >
                      {pushStatus === 'PUSHING' && <UploadCloud className="w-3 h-3 animate-bounce" />}
                      {pushStatus === 'IDLE' ? "Push to n8n" : pushStatus === 'PUSHING' ? 'Pushing...' : pushStatus === 'SUCCESS' ? 'Success' : 'Retry Push'}
                    </button>
                  )}
                </div>
              </div>
              {pushFeedback && (
                <div className={`px-4 py-2 text-xs flex items-start gap-2 border-x border-slate-700 ${pushFeedback.type === 'success' ? 'bg-emerald-500/10 text-emerald-300 border-b-emerald-500/20' : 'bg-rose-500/10 text-rose-300 border-b-rose-500/20'}`}>
                  {pushFeedback.type === 'success' ? <Check className="w-4 h-4 shrink-0 mt-0.5" /> : <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />}
                  <span className="break-all">{pushFeedback.message}</span>
                </div>
              )}
              <div className="flex-1 overflow-hidden rounded-b-xl border-x border-b border-slate-700 bg-slate-900 shadow-xl relative group">
                {workflowJson ? (
                  <div className="absolute inset-0 overflow-auto p-4 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                    <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap break-words leading-relaxed">
                      {workflowJson}
                    </pre>
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-slate-600">
                    <Workflow className="w-12 h-12 mb-3 opacity-20" />
                    <p className="text-sm">Generated blueprint will appear here</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --- IMPORTER / AUDIT MODE --- */}
      {activeMode === 'IMPORTER' && (
        <div className="animate-in fade-in grid lg:grid-cols-2 gap-8 h-[calc(100vh-12rem)]">
          <div className="flex flex-col gap-4 h-full">
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 flex-1 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-white flex items-center gap-2"><FileJson className="w-5 h-5 text-amber-500" /> Import Workflow Definition</h3>
                <div className="flex gap-2">
                  <button onClick={loadDemo} className="text-xs bg-slate-700 hover:bg-slate-600 text-white px-2 py-1 rounded">Load Demo</button>
                  <button
                    onClick={() => { setImportedJson(''); setParsedWorkflow(null); setAuditReport(null); }}
                    className="text-xs text-slate-500 hover:text-white"
                  >
                    Clear
                  </button>
                </div>
              </div>

              {/* Saved Workflows List */}
              <div className="mb-4">
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Saved Workflows</label>
                <select
                  onChange={(e) => {
                    if (e.target.value) {
                      const wf = savedWorkflows.find(w => w.id === e.target.value);
                      if (wf) {
                        setImportedJson(JSON.stringify({ nodes: wf.nodes, connections: wf.edges }, null, 2));
                      }
                    }
                  }}
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm outline-none focus:ring-2 focus:ring-amber-500"
                >
                  <option value="">-- Select from Library --</option>
                  {savedWorkflows.map(w => (
                    <option key={w.id} value={w.id}>{w.name} ({new Date(w.createdAt).toLocaleDateString()})</option>
                  ))}
                </select>
              </div>

              <textarea
                value={importedJson}
                onChange={e => setImportedJson(e.target.value)}
                placeholder="Paste complex Yokaizen or n8n JSON here..."
                className="flex-1 w-full bg-slate-900 border border-slate-700 rounded-lg p-4 font-mono text-xs text-slate-300 focus:ring-2 focus:ring-amber-500 outline-none resize-none leading-relaxed"
              />
              <button
                onClick={handleImportAnalysis}
                disabled={!importedJson}
                className="mt-4 bg-amber-600 hover:bg-amber-700 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Zap className="w-4 h-4" /> Run System Audit
              </button>
            </div>
          </div>

          <div className="flex flex-col gap-4 h-full overflow-hidden">
            {auditReport ? (
              <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 h-full overflow-y-auto">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-white">Audit Report</h3>
                  <div className={`px-4 py-1.5 rounded-full text-sm font-bold border ${auditReport.compatible ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                    {auditReport.compatible ? 'SYSTEM READY' : 'REQUIRES UPGRADE'}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                  <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
                    <span className="text-slate-500 text-xs uppercase font-bold">Compatibility Score</span>
                    <div className="text-3xl font-bold text-white mt-1">{auditReport.score}%</div>
                  </div>
                  <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
                    <span className="text-slate-500 text-xs uppercase font-bold">Node Support</span>
                    <div className="text-3xl font-bold text-white mt-1">{auditReport.supportedNodes} <span className="text-sm text-slate-500 font-normal">/ {auditReport.totalNodes}</span></div>
                  </div>
                </div>

                {auditReport.issues.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-sm font-bold text-rose-400 mb-3 flex items-center gap-2"><AlertTriangle className="w-4 h-4" /> Issues Identified</h4>
                    <div className="space-y-2">
                      {auditReport.issues.map((issue: string, i: number) => (
                        <div key={i} className={`p-3 rounded text-sm flex items-start gap-3 border ${issue.includes('CRITICAL') ? 'bg-rose-500/10 border-rose-500/20 text-rose-200' : 'bg-amber-500/10 border-amber-500/20 text-amber-200'}`}>
                          <div className={`w-1.5 h-1.5 rounded-full mt-2 shrink-0 ${issue.includes('CRITICAL') ? 'bg-rose-500' : 'bg-amber-500'}`} />
                          {issue}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="border-t border-slate-700 pt-6">
                  <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2"><Network className="w-4 h-4 text-slate-400" /> Validated Node Graph</h4>
                  <div className="space-y-2 pl-4 border-l-2 border-slate-700">
                    {parsedWorkflow?.nodes.map((node, i) => (
                      <div key={node.id} className="relative pb-6 last:pb-0">
                        <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-slate-600 border-2 border-slate-900" />
                        <div className="bg-slate-900 p-3 rounded border border-slate-700 flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-mono text-slate-300">{node.name}</span>
                            {node.id.includes('orchestrator') && <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 rounded">HUB</span>}
                          </div>
                          <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">{node.type}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            ) : (
              <div className="bg-slate-800 rounded-xl border border-slate-700 p-12 h-full flex flex-col items-center justify-center text-slate-500">
                <Cpu className="w-16 h-16 mb-4 opacity-20" />
                <p>Waiting for workflow definition...</p>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};

export default WorkflowAgent;

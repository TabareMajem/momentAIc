import React, { useState, useCallback, useMemo } from 'react';
import ReactFlow, {
    addEdge,
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    Connection,
    Edge,
    Node,
    Handle,
    Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { api } from '../lib/api';
import { useStartupStore } from '../stores/startup-store';
import { Button } from '../components/ui/Button';
import {
    Target, FileText, TrendingUp, Eye, Shield, Terminal, Brain,
    Zap, Globe, Cpu, Play, Loader2, Plus, Trash2, Sparkles
} from 'lucide-react';

// ─── AGENT DEFINITIONS ───
const AVAILABLE_AGENTS = [
    { id: 'sales_agent', name: 'Sales Hunter', icon: Target, color: '#22c55e', desc: 'Lead gen & outbound' },
    { id: 'content_strategy_agent', name: 'Content Engine', icon: FileText, color: '#3b82f6', desc: 'Blog, social, SEO' },
    { id: 'growth_hacker', name: 'Growth Hacker', icon: TrendingUp, color: '#f59e0b', desc: 'Conversion optimization' },
    { id: 'competitor_intel', name: 'Competitor Intel', icon: Eye, color: '#ef4444', desc: 'Market surveillance' },
    { id: 'legal_agent', name: 'Legal Sentinel', icon: Shield, color: '#8b5cf6', desc: 'Contracts & compliance' },
    { id: 'devops_agent', name: 'DevOps Guard', icon: Terminal, color: '#06b6d4', desc: 'Infra & deployment' },
    { id: 'orchestrator', name: 'Orchestrator', icon: Brain, color: '#a855f7', desc: 'Multi-agent coordinator' },
    { id: 'viral_content', name: 'Viral Engine', icon: Zap, color: '#ec4899', desc: 'Viral hooks & TikTok' },
    { id: 'planning_agent', name: 'War Planner', icon: Globe, color: '#14b8a6', desc: 'Predictive war gaming' },
    { id: 'business_copilot', name: 'Biz Strategist', icon: Cpu, color: '#f97316', desc: 'Business strategy' },
];

// ─── CUSTOM NODE COMPONENT ───
function AgentNode({ data }: { data: any }) {
    const agent = AVAILABLE_AGENTS.find(a => a.id === data.agentType) || AVAILABLE_AGENTS[0];
    const Icon = agent.icon;

    return (
        <div
            className="bg-[#0a0a0f] border-2 rounded-xl p-4 min-w-[220px] shadow-lg transition-all hover:shadow-xl group"
            style={{ borderColor: `${agent.color}60` }}
        >
            <Handle type="target" position={Position.Top} className="!bg-purple-500 !border-purple-400 !w-3 !h-3" />

            <div className="flex items-center gap-3 mb-3">
                <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center border"
                    style={{ backgroundColor: `${agent.color}20`, borderColor: `${agent.color}40` }}
                >
                    <Icon className="w-5 h-5" style={{ color: agent.color }} />
                </div>
                <div>
                    <div className="text-sm font-bold text-white">{agent.name}</div>
                    <div className="text-[9px] font-mono text-gray-500 uppercase tracking-wider">{agent.desc}</div>
                </div>
            </div>

            <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: agent.color }} />
                    <span className="text-[9px] font-mono text-gray-500">READY</span>
                </div>
                <span className="text-[9px] font-mono" style={{ color: `${agent.color}AA` }}>
                    NODE_{data.agentType?.slice(0, 4).toUpperCase()}
                </span>
            </div>

            <Handle type="source" position={Position.Bottom} className="!bg-purple-500 !border-purple-400 !w-3 !h-3" />
        </div>
    );
}

const nodeTypes = { agentNode: AgentNode };

// ─── MAIN COMPONENT ───
export default function AgentComposability() {
    const { activeStartupId } = useStartupStore();
    const [isExecuting, setIsExecuting] = useState(false);
    const [executionResult, setExecutionResult] = useState<any>(null);
    const [goalInput, setGoalInput] = useState('');

    // Initial demo nodes
    const initialNodes: Node[] = [
        { id: '1', type: 'agentNode', position: { x: 250, y: 0 }, data: { agentType: 'competitor_intel' } },
        { id: '2', type: 'agentNode', position: { x: 50, y: 200 }, data: { agentType: 'planning_agent' } },
        { id: '3', type: 'agentNode', position: { x: 450, y: 200 }, data: { agentType: 'content_strategy_agent' } },
        { id: '4', type: 'agentNode', position: { x: 250, y: 400 }, data: { agentType: 'sales_agent' } },
    ];

    const initialEdges: Edge[] = [
        { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#a855f7' } },
        { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#a855f7' } },
        { id: 'e2-4', source: '2', target: '4', animated: true, style: { stroke: '#a855f7' } },
        { id: 'e3-4', source: '3', target: '4', animated: true, style: { stroke: '#a855f7' } },
    ];

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: '#a855f7' } }, eds)),
        [setEdges]
    );

    const addAgentNode = (agentType: string) => {
        const newId = `${Date.now()}`;
        const newNode: Node = {
            id: newId,
            type: 'agentNode',
            position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
            data: { agentType },
        };
        setNodes((nds) => [...nds, newNode]);
    };

    const clearCanvas = () => {
        setNodes([]);
        setEdges([]);
        setExecutionResult(null);
    };

    const executeDAG = async () => {
        if (!activeStartupId) {
            alert('Please select a startup first.');
            return;
        }
        setIsExecuting(true);
        setExecutionResult(null);
        try {
            const dagPayload = {
                nodes: nodes.map(n => ({ id: n.id, agent_type: n.data.agentType })),
                edges: edges.map(e => ({ source: e.source, target: e.target })),
                initial_input: goalInput || 'Analyze the market and create a comprehensive growth strategy.',
            };
            const result = await api.executeAgentDAG(activeStartupId, dagPayload);
            setExecutionResult(result);
        } catch (err: any) {
            setExecutionResult({ error: err?.message || 'DAG execution failed' });
        } finally {
            setIsExecuting(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#020202] text-white flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/10">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center border border-purple-500/30">
                        <Sparkles className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black font-mono tracking-tight">AGENT COMPOSABILITY</h1>
                        <p className="text-xs font-mono text-gray-500">Drag-and-Drop DAG Builder // Connect Agents Like Zapier Nodes</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button
                        onClick={clearCanvas}
                        className="h-9 px-4 bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 font-mono text-xs"
                    >
                        <Trash2 className="w-3 h-3 mr-2" /> CLEAR
                    </Button>
                    <Button
                        onClick={executeDAG}
                        disabled={isExecuting || nodes.length === 0}
                        className="h-9 px-6 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white font-mono text-xs shadow-lg shadow-purple-900/30"
                    >
                        {isExecuting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                        {isExecuting ? 'EXECUTING...' : 'EXECUTE DAG'}
                    </Button>
                </div>
            </div>

            {/* Goal Input */}
            <div className="px-6 py-3 border-b border-white/5 bg-[#050508]">
                <div className="flex items-center gap-3 max-w-4xl">
                    <span className="text-[10px] font-mono text-gray-500 whitespace-nowrap">GOAL:</span>
                    <input
                        value={goalInput}
                        onChange={(e) => setGoalInput(e.target.value)}
                        placeholder="e.g., Analyze competitors and launch a counter-campaign..."
                        className="flex-1 bg-transparent border-b border-white/10 focus:border-purple-500 text-sm font-mono text-white outline-none py-2 placeholder:text-gray-600"
                    />
                </div>
            </div>

            <div className="flex flex-1 overflow-hidden">
                {/* Agent Palette */}
                <div className="w-64 border-r border-white/10 bg-[#050508] p-4 overflow-y-auto">
                    <div className="text-[10px] font-mono text-gray-500 uppercase tracking-widest mb-4">
                        ☰ AGENT PALETTE
                    </div>
                    <div className="space-y-2">
                        {AVAILABLE_AGENTS.map(agent => {
                            const Icon = agent.icon;
                            return (
                                <button
                                    key={agent.id}
                                    onClick={() => addAgentNode(agent.id)}
                                    className="w-full flex items-center gap-3 p-3 bg-white/5 border border-white/10 rounded-lg hover:border-purple-500/40 hover:bg-purple-500/5 transition-all text-left group"
                                >
                                    <div className="w-8 h-8 rounded flex items-center justify-center border" style={{ backgroundColor: `${agent.color}15`, borderColor: `${agent.color}30` }}>
                                        <Icon className="w-4 h-4" style={{ color: agent.color }} />
                                    </div>
                                    <div>
                                        <div className="text-xs font-bold text-white group-hover:text-purple-400 transition-colors">{agent.name}</div>
                                        <div className="text-[9px] font-mono text-gray-600">{agent.desc}</div>
                                    </div>
                                    <Plus className="w-3 h-3 text-gray-600 ml-auto group-hover:text-purple-400 transition-colors" />
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* React Flow Canvas */}
                <div className="flex-1 relative">
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onConnect={onConnect}
                        nodeTypes={nodeTypes}
                        fitView
                        style={{ background: '#020202' }}
                    >
                        <Background color="#333" gap={20} />
                        <Controls style={{ button: { backgroundColor: '#1a1a2e', borderColor: '#333' } }} />
                        <MiniMap
                            nodeColor={(node) => {
                                const agent = AVAILABLE_AGENTS.find(a => a.id === node.data?.agentType);
                                return agent?.color || '#a855f7';
                            }}
                            style={{ backgroundColor: '#0a0a0f', border: '1px solid rgba(255,255,255,0.1)' }}
                        />
                    </ReactFlow>

                    {nodes.length === 0 && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div className="text-center">
                                <Sparkles className="w-12 h-12 text-gray-700 mx-auto mb-4" />
                                <p className="text-gray-600 font-mono text-sm">Click agents on the left to add them to the canvas</p>
                                <p className="text-gray-700 font-mono text-xs mt-1">Then connect them by dragging from one handle to another</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Execution Results Panel */}
                {executionResult && (
                    <div className="w-80 border-l border-white/10 bg-[#050508] p-4 overflow-y-auto">
                        <div className="text-[10px] font-mono text-purple-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Zap className="w-3 h-3" /> EXECUTION RESULTS
                        </div>
                        {executionResult.error ? (
                            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-xs font-mono text-red-400">
                                {executionResult.error}
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {Object.entries(executionResult).map(([key, value]: [string, any]) => (
                                    <div key={key} className="bg-white/5 border border-white/10 rounded-lg p-3">
                                        <div className="text-[9px] font-mono text-purple-400 uppercase mb-1">{key}</div>
                                        <p className="text-xs font-mono text-gray-400 whitespace-pre-wrap">
                                            {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

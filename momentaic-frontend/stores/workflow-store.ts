
import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import { WorkflowNode, WorkflowEdge, WorkflowLog, ApprovalRequest } from '../types';

interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  logs: WorkflowLog[];
  selectedNodeId: string | null;
  isRunning: boolean;
  approvalQueue: ApprovalRequest[];
  
  // Actions
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  addNode: (node: WorkflowNode) => void;
  removeNode: (id: string) => void; // New
  addEdge: (edge: WorkflowEdge) => void;
  selectNode: (id: string | null) => void;
  addLog: (level: WorkflowLog['level'], message: string, nodeId?: string) => void;
  clearLogs: () => void;
  setRunning: (isRunning: boolean) => void;
  updateNodeStatus: (id: string, status: WorkflowNode['data']['status']) => void;
  addApprovalRequest: (req: ApprovalRequest) => void;
  resolveApproval: (id: string, decision: 'approved' | 'rejected') => void;
  resetWorkflow: () => void;
}

export const useWorkflowStore = create<WorkflowState>()((set, get) => ({
  nodes: [],
  edges: [],
  logs: [],
  selectedNodeId: null,
  isRunning: false,
  approvalQueue: [],

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  
  addNode: (node) => set((state) => ({ nodes: [...state.nodes, node] })),

  removeNode: (id) => set((state) => ({
    nodes: state.nodes.filter(n => n.id !== id),
    edges: state.edges.filter(e => e.source !== id && e.target !== id), // Cleanup edges
    selectedNodeId: state.selectedNodeId === id ? null : state.selectedNodeId
  })),
  
  addEdge: (edge) => set((state) => ({ edges: [...state.edges, edge] })),
  
  selectNode: (id) => set({ selectedNodeId: id }),
  
  addLog: (level, message, nodeId) => set((state) => ({
    logs: [...state.logs, {
      id: uuidv4(),
      timestamp: new Date().toLocaleTimeString(),
      level,
      message,
      nodeId
    }]
  })),

  clearLogs: () => set({ logs: [] }),

  setRunning: (isRunning) => set({ isRunning }),

  updateNodeStatus: (id, status) => set((state) => ({
    nodes: state.nodes.map(n => n.id === id ? { ...n, data: { ...n.data, status } } : n)
  })),

  addApprovalRequest: (req) => set((state) => ({
    approvalQueue: [...state.approvalQueue, req]
  })),

  resolveApproval: (id, decision) => set((state) => ({
    approvalQueue: state.approvalQueue.filter(req => req.id !== id),
  })),

  resetWorkflow: () => set({ 
    nodes: [], 
    edges: [], 
    logs: [], 
    selectedNodeId: null, 
    isRunning: false, 
    approvalQueue: [] 
  })
}));

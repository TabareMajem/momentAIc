
import { WorkflowNode, WorkflowEdge, NodeType } from '../types';
import { v4 as uuidv4 } from 'uuid';

/**
 * AgentForge Graph Generator
 * 
 * SECURITY NOTE: All AI calls must go through the backend API.
 * This frontend module uses heuristic-based workflow generation.
 * For AI-powered generation, use the backend /api/v1/agents/forge endpoint.
 */

export async function analyzeTaskAndGenerateGraph(prompt: string): Promise<{ nodes: WorkflowNode[], edges: WorkflowEdge[] }> {
    // Simulate processing delay for UX
    await new Promise(resolve => setTimeout(resolve, 1500));

    const nodes: WorkflowNode[] = [];
    const edges: WorkflowEdge[] = [];

    // Start Node
    const startId = 'node-start';
    nodes.push({
        id: startId,
        type: 'start',
        position: { x: 50, y: 300 },
        data: { label: 'Start Trigger', status: 'idle', description: 'Manual or Webhook trigger' }
    });

    const lowercasePrompt = prompt.toLowerCase();
    let lastNodeId = startId;
    let xOffset = 300;

    const addStep = (type: NodeType, label: string, desc: string, config?: any) => {
        const id = uuidv4();
        nodes.push({
            id,
            type,
            position: { x: xOffset, y: 300 },
            data: { label, description: desc, status: 'idle', config }
        });
        edges.push({ id: uuidv4(), source: lastNodeId, target: id, animated: true });
        lastNodeId = id;
        xOffset += 300;
    };

    // Intelligent keyword matching for workflow generation
    if (lowercasePrompt.includes('scrape') || lowercasePrompt.includes('visit') || lowercasePrompt.includes('web') || lowercasePrompt.includes('browse')) {
        addStep('browser', 'Web Scraper', 'Headless browser execution', { url: 'https://example.com' });
    }

    if (lowercasePrompt.includes('analyze') || lowercasePrompt.includes('summarize') || lowercasePrompt.includes('ai') || lowercasePrompt.includes('process')) {
        addStep('supervisor', 'AI Processor', 'Backend AI analysis unit');
    }

    if (lowercasePrompt.includes('save') || lowercasePrompt.includes('database') || lowercasePrompt.includes('slack') || lowercasePrompt.includes('salesforce') || lowercasePrompt.includes('email') || lowercasePrompt.includes('notify')) {
        addStep('mcp', 'External Tool', 'MCP Integration');
    }

    if (lowercasePrompt.includes('approve') || lowercasePrompt.includes('review') || lowercasePrompt.includes('human') || lowercasePrompt.includes('manual')) {
        addStep('human', 'Human Approval', 'Wait for sign-off');
    }

    // Default step if nothing matched
    if (nodes.length === 1) {
        addStep('supervisor', 'General Task', 'Processing user request via backend AI');
    }

    // End Node
    const endId = 'node-end';
    nodes.push({
        id: endId,
        type: 'end',
        position: { x: xOffset, y: 300 },
        data: { label: 'Finish', status: 'idle' }
    });
    edges.push({ id: uuidv4(), source: lastNodeId, target: endId, animated: true });

    return { nodes, edges };
}

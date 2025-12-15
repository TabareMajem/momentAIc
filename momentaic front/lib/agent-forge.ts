
import { GoogleGenAI, Type } from "@google/genai";
import { WorkflowNode, WorkflowEdge, NodeType } from '../types';
import { v4 as uuidv4 } from 'uuid';

// Heuristic fallback for when API key is missing or generation fails
async function heuristicGeneration(prompt: string): Promise<{ nodes: WorkflowNode[], edges: WorkflowEdge[] }> {
  await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate thinking

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
  
  // Simple keyword matching
  if (lowercasePrompt.includes('scrape') || lowercasePrompt.includes('visit') || lowercasePrompt.includes('web')) {
      addStep('browser', 'Web Scraper', 'Headless browser execution', { url: 'https://example.com' });
  }

  if (lowercasePrompt.includes('analyze') || lowercasePrompt.includes('summarize') || lowercasePrompt.includes('ai')) {
      addStep('supervisor', 'AI Processor', 'Gemini 2.5 logic unit');
  }

  if (lowercasePrompt.includes('save') || lowercasePrompt.includes('database') || lowercasePrompt.includes('slack') || lowercasePrompt.includes('salesforce')) {
      addStep('mcp', 'External Tool', 'MCP Integration');
  }

  if (lowercasePrompt.includes('approve') || lowercasePrompt.includes('review')) {
      addStep('human', 'Human Approval', 'Wait for sign-off');
  }

  if (nodes.length === 1) {
     addStep('supervisor', 'General Task', 'Processing user request');
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

export async function analyzeTaskAndGenerateGraph(prompt: string): Promise<{ nodes: WorkflowNode[], edges: WorkflowEdge[] }> {
  // Safer environment variable access
  const apiKey = typeof process !== 'undefined' ? process.env?.API_KEY : undefined;

  // If no API Key, use heuristic
  if (!apiKey) {
     console.warn("AgentForge: No API_KEY found. Using heuristic mode.");
     return heuristicGeneration(prompt);
  }

  try {
      const ai = new GoogleGenAI({ apiKey: apiKey });
      
      const response = await ai.models.generateContent({
          model: 'gemini-2.5-flash',
          config: {
              responseMimeType: 'application/json',
              responseSchema: {
                  type: Type.OBJECT,
                  properties: {
                      steps: {
                          type: Type.ARRAY,
                          items: {
                              type: Type.OBJECT,
                              properties: {
                                  id: { type: Type.STRING },
                                  type: { type: Type.STRING, enum: ['webhook', 'supervisor', 'browser', 'mcp', 'human'] },
                                  label: { type: Type.STRING },
                                  description: { type: Type.STRING },
                                  details: { type: Type.STRING, description: "System prompt or specific configuration" }
                              },
                              required: ['id', 'type', 'label', 'description']
                          }
                      },
                      connections: {
                          type: Type.ARRAY,
                          items: {
                              type: Type.OBJECT,
                              properties: {
                                  from: { type: Type.STRING },
                                  to: { type: Type.STRING }
                              },
                              required: ['from', 'to']
                          }
                      }
                  }
              },
              systemInstruction: `You are the Architect Engine for AgentForge. 
              Convert natural language business requirements into a structured workflow graph.
              
              Node Types:
              - 'webhook': Entry points, triggers.
              - 'browser': Scraping, web interaction, research.
              - 'supervisor': AI analysis, decision making, summarization.
              - 'mcp': External tools (Slack, Salesforce, Database, Email).
              - 'human': Approval steps, reviews.

              Create a logical flow. If the user asks for a complex task, break it down.`
          },
          contents: `Create a workflow for: ${prompt}`
      });
      
      const data = JSON.parse(response.text || "{}");
      if (!data.steps || !data.connections) throw new Error("Invalid graph format");

      const nodes: WorkflowNode[] = [];
      const edges: WorkflowEdge[] = [];
      const idMap = new Map<string, string>(); // Map AI IDs to UUIDs to prevent collision
      
      let xOffset = 300;

      // Always start with Start Node
      const startId = 'node-start';
      nodes.push({
        id: startId,
        type: 'start',
        position: { x: 50, y: 300 },
        data: { label: 'Start', status: 'idle', description: 'Trigger' }
      });

      // Map AI steps to Nodes
      data.steps.forEach((step: any, index: number) => {
          const nodeId = uuidv4();
          idMap.set(step.id, nodeId);

          nodes.push({
              id: nodeId,
              type: step.type as NodeType,
              position: { x: xOffset, y: 300 + (index % 2 === 0 ? 0 : 60) }, // Staggered layout
              data: {
                  label: step.label,
                  description: step.description,
                  status: 'idle',
                  systemInstruction: step.type === 'supervisor' ? step.details : undefined,
                  config: step.type === 'browser' || step.type === 'mcp' ? { details: step.details } : undefined
              }
          });
          xOffset += 300;
      });

      // Always end with End Node
      const endId = 'node-end';
      nodes.push({
          id: endId,
          type: 'end',
          position: { x: xOffset, y: 300 },
          data: { label: 'End', status: 'idle' }
      });

      // Edges
      // 1. Start -> First Node
      if (data.steps.length > 0) {
          edges.push({ 
              id: uuidv4(), 
              source: startId, 
              target: idMap.get(data.steps[0].id) || data.steps[0].id, 
              animated: true 
          });
      } else {
          edges.push({ id: uuidv4(), source: startId, target: endId, animated: true });
      }

      // 2. Inter-node connections
      data.connections.forEach((conn: any) => {
          const from = idMap.get(conn.from) || conn.from;
          const to = idMap.get(conn.to) || conn.to;
          if (from && to) {
            edges.push({ id: uuidv4(), source: from, target: to, animated: true });
          }
      });

      // 3. Last Node -> End (if not connected explicitly or just heuristic)
      // We check if the last step has any outgoing connection in the AI response
      if (data.steps.length > 0) {
          const lastStep = data.steps[data.steps.length - 1];
          const lastStepId = idMap.get(lastStep.id);
          const hasOutgoing = data.connections.some((c: any) => c.from === lastStep.id);
          
          if (!hasOutgoing && lastStepId) {
              edges.push({ id: uuidv4(), source: lastStepId, target: endId, animated: true });
          }
      }

      return { nodes, edges };

  } catch (e) {
      console.error("Gemini Architect failed:", e);
      return heuristicGeneration(prompt);
  }
}

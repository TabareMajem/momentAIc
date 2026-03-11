
import { YokaizenWorkflow, WorkflowNode } from '../types';

interface CompatibilityReport {
    compatible: boolean;
    score: number;
    issues: string[];
    supportedNodes: number;
    totalNodes: number;
}

// Capabilities mapping
const CAPABILITIES = {
    'ai_analysis': true, // Supported via Gemini
    'ai_generation': true, // Supported via Gemini
    'ai_agent_tool': true, // Supported via Gemini (logic only, orchestration missing)
    'browser_automation': false, // Partial support (Scraping yes, full interaction no)
    'mcp_tool_call': false, // Needs specific implementation
    'data_transformer': true, // Logic based
};

const SPECIFIC_TOOL_SUPPORT: Record<string, boolean> = {
    'did_ai_video_generation': false, // No D-ID integration
    'blender_3d_integration': false, // No 3D Engine
    'analytics_attribution_engine': false, // No Data Warehouse
};

export const validateWorkflow = (workflow: YokaizenWorkflow): CompatibilityReport => {
    const issues: string[] = [];
    let supportedCount = 0;

    // Architecture Checks
    const hasOrchestrator = workflow.nodes.some(n => n.id.includes('orchestrator'));
    const hasAgentAsTool = workflow.nodes.some(n => n.type === 'ai_agent_tool');

    if (hasOrchestrator && hasAgentAsTool) {
        issues.push("CRITICAL: Recursive 'Agent-as-Tool' orchestration layer is missing. Agents will run in isolation.");
    }

    workflow.nodes.forEach(node => {
        let isNodeSupported = false;

        // Check Type Support
        if (CAPABILITIES[node.type as keyof typeof CAPABILITIES]) {
            isNodeSupported = true;
        }

        // Check Specific Tool Support (for MCP calls)
        if (node.type === 'mcp_tool_call' && node.config.toolName) {
            if (!SPECIFIC_TOOL_SUPPORT[node.config.toolName]) {
                isNodeSupported = false;
                issues.push(`Node '${node.name}' requires tool '${node.config.toolName}' (Not Integrated)`);
            }
        }

        // Check Browser Automation Depth
        if (node.type === 'browser_automation' || (node.type === 'ai_agent_tool' && node.config?.tools_available?.includes('browser_automation'))) {
            // Check if specific deep automation configs are present
            const config = node.config?.agent_config || node.config;
            if (config?.antiDetection?.enabled || config?.tools_available?.includes('browser_automation')) {
                isNodeSupported = false;
                issues.push(`Node '${node.name}' requires Headless Browser Cluster (Anti-Detect/Scraping)`);
            }
        }

        // Model Mismatch Warnings (Auto-Remapping)
        const model = node.config?.model || node.config?.agent_config?.model;
        if (model) {
            if (model.includes('claude')) {
                issues.push(`WARNING: Node '${node.name}' requests '${model}'. Remapping to 'gemini-2.5-flash'.`);
            } else if (model.includes('gpt')) {
                issues.push(`WARNING: Node '${node.name}' requests '${model}'. Remapping to 'gemini-3-pro'.`);
            }
        }

        if (isNodeSupported) supportedCount++;
    });

    // Weighted Score: Orchestration/Infra is worth 50% of the functionality
    let score = Math.round((supportedCount / workflow.nodes.length) * 100);

    // Penalize heavily for missing infrastructure even if nodes are "supported" logically
    if (issues.some(i => i.includes("CRITICAL"))) score = Math.min(score, 45);

    return {
        compatible: score === 100,
        score,
        issues,
        supportedNodes: supportedCount,
        totalNodes: workflow.nodes.length
    };
};

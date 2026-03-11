import { N8nConfig, N8nWorkflowData } from '../types';

/**
 * Pushes a workflow definition to an n8n instance via its public API.
 * Note: The n8n instance must be accessible from the browser (CORS headers may need to be configured on n8n).
 */
export const pushWorkflowToN8n = async (config: N8nConfig, workflowData: N8nWorkflowData, name: string = "AI Generated Workflow") => {
  try {
    // Clean up URL to ensure no trailing slash
    const baseUrl = config.baseUrl.replace(/\/$/, "");
    
    // Construct the payload expected by n8n /api/v1/workflows
    const payload = {
      name: `${name} - ${new Date().toLocaleString()}`,
      nodes: workflowData.nodes || [],
      connections: workflowData.connections || {},
      settings: workflowData.settings || {},
      active: false // Default to inactive for safety
    };

    const response = await fetch(`${baseUrl}/api/v1/workflows`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-N8N-API-KEY': config.apiKey
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`N8n API Error (${response.status}): ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Failed to push workflow to n8n:", error);
    throw error;
  }
};

/**
 * Triggers a generic webhook.
 * Useful for testing flows that start with a Webhook node.
 */
export const triggerN8nWebhook = async (webhookUrl: string, method: 'GET' | 'POST', payload?: string) => {
  try {
    const options: RequestInit = {
      method: method,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (method === 'POST' && payload) {
      // Validate JSON before sending
      try {
        JSON.parse(payload);
      } catch (e) {
        throw new Error("Payload must be valid JSON");
      }
      options.body = payload;
    }

    const response = await fetch(webhookUrl, options);
    
    // Attempt to read response, might be text or json
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
      return await response.json();
    } else {
      return await response.text();
    }
  } catch (error) {
    console.error("Failed to trigger webhook:", error);
    throw error;
  }
};

/**
 * Checks connectivity to n8n instance
 */
export const checkN8nConnection = async (config: N8nConfig): Promise<boolean> => {
  try {
    const baseUrl = config.baseUrl.replace(/\/$/, "");
    // Trying to fetch user info or simple endpoint to validate key
    const response = await fetch(`${baseUrl}/api/v1/users`, {
        method: 'GET',
        headers: {
          'X-N8N-API-KEY': config.apiKey
        }
    });
    return response.ok;
  } catch (e) {
    console.warn("Connection check failed (might be CORS):", e);
    // If it's a CORS error, we might strictly fail, or let the user try anyway if they know what they are doing.
    // For now, we assume failure.
    return false;
  }
};
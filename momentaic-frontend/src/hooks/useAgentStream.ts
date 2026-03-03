import { useState, useEffect, useCallback, useRef } from 'react';

export interface AgentActivity {
    id: string;
    agent: string;
    action: string;
    status: 'started' | 'running' | 'completed' | 'failed' | 'waiting_approval';
    details?: string;
    startup_id?: string;
    timestamp: string;
    metadata?: Record<string, any>;
}

export interface AgentStatus {
    agent: string;
    status: 'idle' | 'scanning' | 'executing' | 'waiting_approval' | 'error';
    lastActivityAt: string;
    currentTask?: string;
}

interface UseAgentStreamResult {
    activities: AgentActivity[];
    agentStatuses: Record<string, AgentStatus>;
    isConnected: boolean;
    error: Error | null;
    clearActivities: () => void;
}

export function useAgentStream(startupId?: string): UseAgentStreamResult {
    const [activities, setActivities] = useState<AgentActivity[]>([]);
    const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>({});
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

    const connect = useCallback(() => {
        try {
            // In a real app, this would use the actual API URL
            const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
            const url = startupId
                ? `${wsUrl}/api/v1/activity/ws/${startupId}`
                : `${wsUrl}/api/v1/activity/ws`;

            const ws = new WebSocket(url);

            ws.onopen = () => {
                setIsConnected(true);
                setError(null);
                console.log('Agent Activity Stream connected');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'activity') {
                        const activity = data.payload as AgentActivity;

                        // Add to activity feed (keep last 100)
                        setActivities(prev => [activity, ...prev].slice(0, 100));

                        // Update agent status
                        setAgentStatuses(prev => {
                            const currentStatus = prev[activity.agent] || {
                                agent: activity.agent,
                                status: 'idle',
                                lastActivityAt: activity.timestamp
                            };

                            let newStatus = currentStatus.status;
                            if (activity.status === 'started' || activity.status === 'running') {
                                newStatus = activity.action.includes('scan') ? 'scanning' : 'executing';
                            } else if (activity.status === 'waiting_approval') {
                                newStatus = 'waiting_approval';
                            } else if (activity.status === 'failed') {
                                newStatus = 'error';
                            } else if (activity.status === 'completed') {
                                newStatus = 'idle';
                            }

                            return {
                                ...prev,
                                [activity.agent]: {
                                    agent: activity.agent,
                                    status: newStatus,
                                    lastActivityAt: activity.timestamp,
                                    currentTask: newStatus !== 'idle' ? activity.details || activity.action : undefined
                                }
                            };
                        });
                    }
                } catch (e) {
                    console.error('Error parsing agent activity:', e);
                }
            };

            ws.onerror = (event) => {
                console.error('WebSocket error:', event);
                setError(new Error('WebSocket connection error'));
                setIsConnected(false);
            };

            ws.onclose = () => {
                setIsConnected(false);
                // Attempt to reconnect after 5 seconds
                reconnectTimeoutRef.current = setTimeout(connect, 5000);
            };

            wsRef.current = ws;
        } catch (e) {
            setError(e instanceof Error ? e : new Error('Failed to connect'));
            setIsConnected(false);
        }
    }, [startupId]);

    useEffect(() => {
        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [connect]);

    const clearActivities = useCallback(() => {
        setActivities([]);
    }, []);

    return { activities, agentStatuses, isConnected, error, clearActivities };
}

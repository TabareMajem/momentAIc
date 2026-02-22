import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Bolt, Plus, ArrowRight, Zap, Target, MessageSquare, CreditCard, Activity, Cpu } from 'lucide-react';
import { useToast } from '../components/ui/Toast';

export default function TriggersPage() {
    const { toast } = useToast();
    const [isCreating, setIsCreating] = useState(false);
    const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
    const [selectedAction, setSelectedAction] = useState<string | null>(null);

    const activeRules = [
        {
            id: '1',
            name: 'Churn Rescue Protocol',
            event: 'Stripe: Subscription Deleted',
            action: 'Deploy Swarm: Customer Success',
            status: 'active',
            icon: CreditCard,
            color: 'text-indigo-400',
            bg: 'bg-indigo-500/20'
        },
        {
            id: '2',
            name: 'Critical Infrastructure Alert',
            event: 'Heartbeat: Escalation Detected',
            action: 'Slack Alert: #war-room',
            status: 'active',
            icon: Activity,
            color: 'text-rose-400',
            bg: 'bg-rose-500/20'
        }
    ];

    const events = [
        { id: 'stripe_payment', name: 'Stripe: New Payment', category: 'payments', icon: CreditCard },
        { id: 'stripe_churn', name: 'Stripe: Subscription Deleted', category: 'payments', icon: CreditCard },
        { id: 'heartbeat_escalation', name: 'System: Heartbeat Escalation', category: 'system', icon: Activity },
        { id: 'yokaizen_lead', name: 'Yokaizen: New Lead Captured', category: 'agents', icon: Target }
    ];

    const actions = [
        { id: 'deploy_swarm', name: 'Deploy Autonomic Swarm', icon: Cpu },
        { id: 'slack_alert', name: 'Send Slack Alert', icon: MessageSquare },
        { id: 'email_user', name: 'Draft Email to Customer', icon: Zap }
    ];

    const handleSave = () => {
        toast({ type: 'success', title: 'Automation Saved', message: 'The trigger engine is now live and monitoring.' });
        setIsCreating(false);
        setSelectedEvent(null);
        setSelectedAction(null);
    };

    return (
        <div className="space-y-6 max-w-7xl mx-auto">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                        <Bolt className="w-8 h-8 text-brand-cyan" />
                        Trigger Engine
                    </h1>
                    <p className="text-gray-400 text-base mt-2">
                        Build Zapier-style automations linking real-world events to Agent Swarm deployments.
                    </p>
                </div>
                {!isCreating && (
                    <Button variant="cyber" onClick={() => setIsCreating(true)} className="px-6">
                        <Plus className="w-5 h-5 mr-2" />
                        New Automation
                    </Button>
                )}
            </div>

            {isCreating ? (
                <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                    <Card className="border-brand-cyan/20">
                        <CardHeader>
                            <CardTitle className="text-xl">Build Dynamic Workflow</CardTitle>
                            <CardDescription>Wire external synapses directly into your Agent Swarms</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-8">

                            {/* IF BLOCK */}
                            <div className="relative border border-gray-800 rounded-lg p-6 bg-gray-900/50 pt-8 mt-4">
                                <div className="absolute -top-3 left-6 bg-brand-cyan/20 border border-brand-cyan/50 text-brand-cyan px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                                    IF THIS EVENT HAPPENS...
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-2">
                                    {events.map((evt) => (
                                        <button
                                            key={evt.id}
                                            onClick={() => setSelectedEvent(evt.id)}
                                            className={`p-5 rounded-xl flex flex-col items-center justify-center gap-4 border-2 transition-all ${selectedEvent === evt.id
                                                    ? 'border-brand-cyan bg-brand-cyan/10 text-white shadow-[0_0_15px_rgba(0,255,255,0.2)]'
                                                    : 'border-gray-800 hover:border-gray-600 hover:bg-gray-800/50 text-gray-400'
                                                }`}
                                        >
                                            <evt.icon className={`w-8 h-8 ${selectedEvent === evt.id ? 'text-brand-cyan' : ''}`} />
                                            <span className="text-sm text-center font-medium leading-tight">{evt.name}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="flex justify-center -my-6 z-10 relative">
                                <div className="bg-gray-900 p-3 rounded-full border-2 border-gray-800 shadow-xl">
                                    <ArrowRight className="w-6 h-6 text-gray-400 transform rotate-90" />
                                </div>
                            </div>

                            {/* THEN BLOCK */}
                            <div className="relative border border-gray-800 rounded-lg p-6 bg-gray-900/50 pt-8">
                                <div className="absolute -top-3 left-6 bg-brand-purple/20 border border-brand-purple/50 text-brand-purple px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                                    THEN DEPLOY THIS ACTION...
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-2">
                                    {actions.map((act) => (
                                        <button
                                            key={act.id}
                                            onClick={() => setSelectedAction(act.id)}
                                            className={`p-5 rounded-xl flex flex-col items-center justify-center gap-4 border-2 transition-all ${selectedAction === act.id
                                                    ? 'border-brand-purple bg-brand-purple/10 text-white shadow-[0_0_15px_rgba(168,85,247,0.2)]'
                                                    : 'border-gray-800 hover:border-gray-600 hover:bg-gray-800/50 text-gray-400'
                                                }`}
                                        >
                                            <act.icon className={`w-8 h-8 ${selectedAction === act.id ? 'text-brand-purple' : ''}`} />
                                            <span className="text-sm text-center font-medium leading-tight">{act.name}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* AGENT SELECTOR (Conditional) */}
                            {selectedAction === 'deploy_swarm' && (
                                <div className="relative border border-gray-800 rounded-lg p-6 bg-gray-900/50 pt-8 animate-in fade-in duration-300">
                                    <div className="absolute -top-3 left-6 bg-brand-cyan/20 border border-brand-cyan/50 text-brand-cyan px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                                        TARGET SWARM
                                    </div>
                                    <select className="w-full bg-black/50 border-2 border-gray-800 text-white text-base rounded-xl focus:ring-brand-cyan focus:border-brand-cyan block p-4 mt-2">
                                        <option>Customer Success Agents (Win-back protocol)</option>
                                        <option>Outbound Sales Agents (Competitor extraction)</option>
                                        <option>Engineering Swarm (Triage & PagerDuty)</option>
                                        <option>Social Architect (AstroTurf narrative spin)</option>
                                    </select>
                                </div>
                            )}

                            <div className="flex justify-end gap-4 pt-6 border-t border-gray-800">
                                <Button variant="ghost" onClick={() => setIsCreating(false)} className="px-6">Cancel</Button>
                                <Button variant="cyber" disabled={!selectedEvent || !selectedAction} onClick={handleSave} className="px-8 shadow-[0_0_20px_rgba(0,255,255,0.4)]">
                                    Activate Protocol
                                </Button>
                            </div>

                        </CardContent>
                    </Card>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-6">
                    {activeRules.map((rule) => (
                        <Card key={rule.id} className="border-gray-800 bg-gray-900/40 hover:bg-gray-900/60 hover:border-gray-700 transition-all group">
                            <CardContent className="p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
                                <div className="flex items-center gap-5">
                                    <div className={`p-4 rounded-xl shadow-lg ${rule.bg}`}>
                                        <rule.icon className={`w-8 h-8 ${rule.color}`} />
                                    </div>
                                    <div>
                                        <h3 className="text-xl text-white font-bold flex items-center gap-3">
                                            {rule.name}
                                            <Badge variant="cyber" className="bg-green-500/10 text-green-400 border-green-500/20 text-[10px] py-1 px-2 uppercase tracking-widest shadow-[0_0_10px_rgba(34,197,94,0.3)]">Active</Badge>
                                        </h3>
                                        <div className="flex items-center gap-3 text-sm text-gray-400 mt-3">
                                            <Badge className="bg-black/50 text-gray-300 font-medium px-3 py-1 border-gray-700">IF {rule.event}</Badge>
                                            <ArrowRight className="w-4 h-4 text-gray-500" />
                                            <span className="text-gray-300 font-medium">THEN {rule.action}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex gap-3 w-full sm:w-auto opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-300">
                                    <Button variant="outline" className="w-full sm:w-auto text-gray-300 hover:text-white border-gray-700 hover:border-gray-500">View Logs</Button>
                                    <Button variant="outline" className="w-full sm:w-auto text-rose-400 hover:bg-rose-500/10 hover:text-rose-400 border-gray-700 hover:border-rose-500/30">Suspend</Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}

                    <div className="text-center p-12 border-2 border-dashed border-gray-800 rounded-2xl bg-gradient-to-b from-black/0 to-gray-900/30 mt-6 relative overflow-hidden group hover:border-gray-700 transition-colors">
                        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-brand-cyan/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>
                        <div className="relative z-10 flex flex-col items-center">
                            <div className="p-4 bg-gray-900 rounded-full border border-gray-800 mb-4 shadow-xl">
                                <Target className="w-8 h-8 text-gray-500 group-hover:text-brand-cyan transition-colors duration-500" />
                            </div>
                            <h3 className="text-lg text-gray-200 font-bold tracking-tight mb-2">Trigger Engine is Standing By</h3>
                            <p className="text-gray-500 max-w-md mx-auto">Wire more external sensory inputs (Webhooks, Stripe, Yokaizen) directly into your autonomous workforce to grant them proactive capabilities.</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

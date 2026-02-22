import React, { useState } from 'react';
import { useAuthStore } from '../stores/auth-store';
import { api } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { User, CreditCard, LogOut, CheckCircle, Zap, Loader2, PhoneCall, MessageSquare, Link as LinkIcon } from 'lucide-react';
import { SubscriptionTier } from '../types';
import { useToast } from '../components/ui/Toast';

export default function Settings() {
    const { user, logout, upgradeTier } = useAuthStore();
    const { toast } = useToast();
    const [loadingTier, setLoadingTier] = useState<string | null>(null);
    const [twilioSid, setTwilioSid] = useState('');
    const [twilioToken, setTwilioToken] = useState('');

    if (!user) return null;

    const handleCheckout = async (tier: SubscriptionTier) => {
        setLoadingTier(tier);
        try {
            toast({ type: 'info', title: 'Processing', message: 'Connecting to Stripe secure gateway...' });

            const response = await api.createCheckoutSession(tier);

            // In production, we would redirect here:
            // if (response.url) window.location.href = response.url;

            // For Demo: Simulate successful return from Stripe
            upgradeTier(tier);
            toast({ type: 'success', title: 'Payment Successful', message: `Welcome to ${tier.toUpperCase()} tier.` });
        } catch (error) {
            console.error(error);
            toast({ type: 'error', title: 'Checkout Failed', message: 'Unable to initialize payment protocol.' });
        } finally {
            setLoadingTier(null);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold text-white">Account Settings</h1>

            <Card>
                <CardHeader>
                    <div className="flex items-center gap-4">
                        <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-2xl font-bold">
                            {user.full_name.charAt(0)}
                        </div>
                        <div>
                            <CardTitle>{user.full_name}</CardTitle>
                            <CardDescription>{user.email}</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input label="Full Name" defaultValue={user.full_name} disabled />
                        <Input label="Email Address" defaultValue={user.email} disabled />
                    </div>
                </CardContent>
            </Card>

            {/* Link to Autonomy Settings */}
            <Card className="border-brand-cyan/20 bg-brand-cyan/5 hover:border-brand-cyan/40 transition-colors cursor-pointer" onClick={() => window.location.href = '/settings/autonomy'}>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-brand-cyan/20 rounded-lg">
                                <Zap className="w-5 h-5 text-brand-cyan" />
                            </div>
                            <div>
                                <CardTitle className="text-lg">Proactive Agent Control</CardTitle>
                                <CardDescription>Configure your AI workforce autonomy levels</CardDescription>
                            </div>
                        </div>
                        <span className="text-brand-cyan text-sm font-medium">Configure →</span>
                    </div>
                </CardHeader>
            </Card>

            {/* AUTOPILOT MODE - Project PHOENIX */}
            <Card className="border-purple-500/20 bg-purple-500/5">
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-purple-500/20 rounded-lg">
                                <Zap className="w-5 h-5 text-purple-400" />
                            </div>
                            <div>
                                <CardTitle className="text-lg">Autopilot Mode</CardTitle>
                                <CardDescription>Let AI agents act autonomously</CardDescription>
                            </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                className="sr-only peer"
                                defaultChecked={false}
                                onChange={(e) => {
                                    const enabled = e.target.checked;
                                    toast({
                                        type: enabled ? 'success' : 'info',
                                        title: enabled ? 'Autopilot Activated' : 'Autopilot Disabled',
                                        message: enabled
                                            ? 'AI agents will now execute without approval.'
                                            : 'Actions will be queued for your approval.'
                                    });
                                    // TODO: Persist to backend
                                }}
                            />
                            <div className="w-14 h-7 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-purple-500"></div>
                        </label>
                    </div>
                </CardHeader>
                <CardContent className="text-sm text-gray-500 space-y-3">
                    <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-purple-400" />
                        <span><strong>ON:</strong> Posts scheduled, emails sent, leads contacted automatically</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-gray-400" />
                        <span><strong>OFF:</strong> Everything queued for your review and approval</span>
                    </div>
                </CardContent>
            </Card>

            {/* TELECOM CONFIGURATION */}
            <h2 className="text-xl font-bold text-white pt-4">Telecom Integrations</h2>
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500/20 rounded-lg">
                            <PhoneCall className="w-5 h-5 text-blue-400" />
                        </div>
                        <div>
                            <CardTitle className="text-lg">Twilio BYOK (Bring Your Own Key)</CardTitle>
                            <CardDescription>Connect your Twilio account to provision real phone numbers for your AI agents.</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                            label="Twilio Account SID"
                            type="password"
                            placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                            value={twilioSid}
                            onChange={(e) => setTwilioSid(e.target.value)}
                        />
                        <Input
                            label="Twilio Auth Token"
                            type="password"
                            placeholder="Enter Auth Token"
                            value={twilioToken}
                            onChange={(e) => setTwilioToken(e.target.value)}
                        />
                    </div>
                </CardContent>
                <CardFooter className="flex justify-end">
                    <Button onClick={() => {
                        // Persist to local storage for now to make it easy for the demo
                        localStorage.setItem('twilio_sid', twilioSid);
                        localStorage.setItem('twilio_token', twilioToken);
                        toast({ type: 'success', title: 'Keys Saved', message: 'Twilio integration activated.' });
                    }}>
                        Save API Keys
                    </Button>
                </CardFooter>
            </Card>

            {/* EXTERNAL INTEGRATIONS */}
            <h2 className="text-xl font-bold text-white pt-4">External Integrations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* STRIPE */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-indigo-500/20 rounded-lg">
                                <CreditCard className="w-5 h-5 text-indigo-400" />
                            </div>
                            <div>
                                <CardTitle className="text-lg">Stripe Billing</CardTitle>
                                <CardDescription>Trigger actions based on MRR, Churn, and new Customers.</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
                            <CheckCircle className="w-4 h-4 text-green-400" />
                            Connected as `acct_1M...`
                        </div>
                        <Button variant="outline" className="w-full text-gray-300">
                            Manage Connection
                        </Button>
                    </CardContent>
                </Card>

                {/* SLACK */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-amber-500/20 rounded-lg">
                                <MessageSquare className="w-5 h-5 text-amber-400" />
                            </div>
                            <div>
                                <CardTitle className="text-lg">Slack Workspace</CardTitle>
                                <CardDescription>Allow agents to DM you or post alerts to #channels.</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
                            <LinkIcon className="w-4 h-4 text-gray-400" />
                            Not Connected
                        </div>
                        <Button variant="cyber" className="w-full bg-amber-500/20 text-amber-500 hover:bg-amber-500 hover:text-black border-none">
                            Connect Workspace
                        </Button>
                    </CardContent>
                </Card>
            </div>

            <h2 className="text-xl font-bold text-white pt-4">Subscription Protocol</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* STARTER */}
                <Card className={user.subscription_tier === 'starter' ? 'border-brand-blue ring-1 ring-brand-blue' : ''}>
                    <CardHeader>
                        <CardTitle className="text-lg">Starter</CardTitle>
                        <div className="text-2xl font-bold">$9<span className="text-sm text-gray-500 font-normal">/mo</span></div>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm text-gray-500">
                        <div className="flex items-center gap-2"><Zap className="w-3 h-3" /> 50 Credits/mo</div>
                        <div className="flex items-center gap-2"><CheckCircle className="w-3 h-3" /> 1 Active Startup</div>
                        <div className="flex items-center gap-2"><CheckCircle className="w-3 h-3" /> Basic Agents</div>
                    </CardContent>
                    <CardFooter>
                        {user.subscription_tier === 'starter' ? (
                            <Button disabled className="w-full">Current Plan</Button>
                        ) : (
                            <Button
                                variant="outline"
                                className="w-full"
                                onClick={() => handleCheckout('starter')}
                                isLoading={loadingTier === 'starter'}
                                disabled={!!loadingTier}
                            >
                                Downgrade
                            </Button>
                        )}
                    </CardFooter>
                </Card>

                {/* GROWTH */}
                <Card className={user.subscription_tier === 'growth' ? 'border-brand-purple ring-1 ring-brand-purple bg-brand-purple/5' : ''}>
                    <CardHeader>
                        <CardTitle className="text-lg">Growth</CardTitle>
                        <div className="text-2xl font-bold">$49<span className="text-sm text-gray-500 font-normal">/mo</span></div>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm text-gray-500">
                        <div className="flex items-center gap-2"><Zap className="w-3 h-3 text-brand-purple" /> 500 Credits/mo</div>
                        <div className="flex items-center gap-2"><CheckCircle className="w-3 h-3 text-brand-purple" /> 3 Active Startups</div>
                        <div className="flex items-center gap-2"><CheckCircle className="w-3 h-3 text-brand-purple" /> Sales & Dev Agents</div>
                    </CardContent>
                    <CardFooter>
                        {user.subscription_tier === 'growth' ? (
                            <Button disabled className="w-full">Current Plan</Button>
                        ) : (
                            <Button
                                variant="cyber"
                                className="w-full"
                                onClick={() => handleCheckout('growth')}
                                isLoading={loadingTier === 'growth'}
                                disabled={!!loadingTier}
                            >
                                Select Growth
                            </Button>
                        )}
                    </CardFooter>
                </Card>

                {/* GOD MODE */}
                <Card className={user.subscription_tier === 'god_mode' ? 'border-brand-cyan ring-1 ring-brand-cyan bg-brand-cyan/5' : ''}>
                    <CardHeader>
                        <CardTitle className="text-lg text-brand-cyan">God Mode</CardTitle>
                        <div className="text-2xl font-bold">$99<span className="text-sm text-gray-500 font-normal">/mo</span></div>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm text-gray-500">
                        <div className="flex items-center gap-2"><Zap className="w-3 h-3 text-brand-cyan" /> Unlimited Credits</div>
                        <div className="flex items-center gap-2"><CheckCircle className="w-3 h-3 text-brand-cyan" /> Unlimited Startups</div>
                        <div className="flex items-center gap-2"><CheckCircle className="w-3 h-3 text-brand-cyan" /> All Premium Agents</div>
                    </CardContent>
                    <CardFooter>
                        {user.subscription_tier === 'god_mode' ? (
                            <Button disabled className="w-full">Current Plan</Button>
                        ) : (
                            <Button
                                variant="cyber"
                                className="w-full border-brand-cyan text-brand-cyan hover:bg-brand-cyan hover:text-black"
                                onClick={() => handleCheckout('god_mode')}
                                isLoading={loadingTier === 'god_mode'}
                                disabled={!!loadingTier}
                            >
                                Activate God Mode
                            </Button>
                        )}
                    </CardFooter>
                </Card>
            </div>

            <div className="flex justify-start pt-8">
                <Button variant="destructive" onClick={logout}>
                    <LogOut className="w-4 h-4 mr-2" />
                    Sign Out
                </Button>
            </div>
        </div>
    );
}
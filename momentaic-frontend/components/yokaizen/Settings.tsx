
import React, { useState, useEffect, useRef } from 'react';
import { User, Bell, Shield, Save, Check, CreditCard, Zap, HelpCircle, Loader2, Sparkles, Upload, Crown, AlertCircle, Settings as SettingsIcon, Lock, Unlock } from 'lucide-react';
import { StorageService } from '../../services/storage';
import { UserProfile } from '../../types';
import { initiateCheckout, CREDIT_PACKS, SUBSCRIPTION_PLANS } from '../../services/paymentService';
import { useToast } from './Toast';
import UserSocialSettings from './UserSocialSettings';

interface SettingsProps {
    initialTab?: 'PROFILE' | 'BILLING';
    autoSelectPlanId?: string | null;
}

const Settings: React.FC<SettingsProps> = ({ initialTab = 'PROFILE', autoSelectPlanId }) => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const [activeTab, setActiveTab] = useState<'PROFILE' | 'BILLING'>(initialTab);

    // Form State for Profile
    const [formName, setFormName] = useState('');
    const [formEmail, setFormEmail] = useState('');
    const [formRole, setFormRole] = useState<'USER' | 'ADMIN' | 'EDITOR'>('USER');
    const [formPlan, setFormPlan] = useState<'STARTER' | 'PRO' | 'ENTERPRISE'>('STARTER');
    const [avatarSimulated, setAvatarSimulated] = useState(false);

    // Payment State
    const [isPurchasing, setIsPurchasing] = useState<string | null>(null); // ID of item being purchased
    const [showSuccessConfetti, setShowSuccessConfetti] = useState(false);
    const [purchasedItemName, setPurchasedItemName] = useState('');
    const planSectionRef = useRef<HTMLDivElement>(null);

    const { addToast } = useToast();

    useEffect(() => {
        const currentUser = StorageService.getUser();
        if (currentUser) {
            setUser(currentUser);
            setFormName(currentUser.name);
            setFormEmail(currentUser.email);
            setFormRole(currentUser.role);
            setFormPlan(currentUser.plan);
        }
    }, []);

    // Auto-scroll to plan if coming from Landing Page
    useEffect(() => {
        if (activeTab === 'BILLING' && autoSelectPlanId && planSectionRef.current) {
            setTimeout(() => {
                planSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
                addToast("Select 'Upgrade' to complete your purchase.", 'info');
            }, 500);
        }
    }, [activeTab, autoSelectPlanId]);

    const handleSave = () => {
        if (!user) return;
        setIsSaving(true);

        // In a real app, changing Role/Plan via profile settings is restricted.
        // We allow it here for "Simulation Mode" to test the UI.
        const updatedUser: UserProfile = {
            ...user,
            name: formName,
            email: formEmail,
            role: formRole,
            plan: formPlan
        };

        StorageService.updateUserInDb(updatedUser);
        setUser(updatedUser);

        // Dispatch event so Sidebar and other components update immediately
        window.dispatchEvent(new Event('user-update'));

        setTimeout(() => {
            setIsSaving(false);
            setSaved(true);
            addToast('Profile & Simulation settings updated', 'success');
            setTimeout(() => setSaved(false), 2000);
        }, 800);
    };

    const handleAvatarUpload = () => {
        setAvatarSimulated(true);
        addToast("Avatar upload simulated. Looks good!", 'info');
    };

    const handlePurchase = async (id: string, type: 'CREDIT' | 'SUBSCRIPTION', amountOrPlan: number | string, itemName: string) => {
        if (!user) return;
        setIsPurchasing(id);
        setShowSuccessConfetti(false);

        try {
            // 1. Call Payment Service (Simulated)
            const result = await initiateCheckout(id, type);
            if (!result.success) throw new Error(result.message);

            // 2. Simulate Webhook Callback / Success
            setTimeout(() => {
                if (type === 'CREDIT') {
                    StorageService.deductCredits(-(amountOrPlan as number)); // Negative deduction = Addition
                    addToast(`Successfully added ${(amountOrPlan as number).toLocaleString()} credits!`, 'success');
                } else {
                    // Subscription Upgrade
                    user.plan = amountOrPlan as any;
                    setFormPlan(amountOrPlan as any);
                    StorageService.updateUserInDb(user);
                    addToast(`Plan upgraded to ${amountOrPlan}!`, 'success');
                }

                const updatedUser = StorageService.getUser(); // Fetch updated user
                setUser(updatedUser);
                setPurchasedItemName(itemName);

                setIsPurchasing(null);
                setShowSuccessConfetti(true);

                // Clear confetti after a few seconds
                // setTimeout(() => setShowSuccessConfetti(false), 5000);
            }, 2000);

        } catch (e: any) {
            setIsPurchasing(null);
            addToast(`Payment failed: ${e.message}`, 'error');
        }
    };

    if (!user) return <div className="p-6 text-slate-400 flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Loading profile...</div>;

    return (
        <div className="p-6 max-w-5xl mx-auto animate-fade-in text-slate-200">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
                <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                    <SettingsIcon className="w-8 h-8 text-indigo-500 shrink-0" />
                    Settings
                </h2>
                <div className="flex w-full md:w-auto bg-slate-800 p-1 rounded-lg border border-slate-700">
                    <button
                        onClick={() => setActiveTab('PROFILE')}
                        className={`flex-1 md:flex-none px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'PROFILE' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                    >
                        Profile & Simulation
                    </button>
                    <button
                        onClick={() => setActiveTab('BILLING')}
                        className={`flex-1 md:flex-none px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'BILLING' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                    >
                        Plans & Billing
                    </button>
                </div>
            </div>

            {/* PROFILE TAB */}
            {activeTab === 'PROFILE' && (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2">
                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-8">
                        <div className="flex flex-col md:flex-row items-start gap-8">
                            {/* Avatar Sim */}
                            <div className="flex flex-col items-center gap-3 w-full md:w-auto">
                                <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-3xl font-bold text-white shadow-xl border-4 border-slate-800 relative overflow-hidden group cursor-pointer" onClick={handleAvatarUpload}>
                                    {avatarSimulated ? <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`} alt="avatar" className="w-full h-full object-cover" /> : user.name.charAt(0).toUpperCase()}
                                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Upload className="w-6 h-6 text-white" />
                                    </div>
                                </div>
                                <button onClick={handleAvatarUpload} className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium">
                                    Change Avatar
                                </button>
                            </div>

                            <div className="flex-1 space-y-6 w-full">
                                <div className="grid md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Full Name</label>
                                        <input
                                            type="text"
                                            value={formName}
                                            onChange={(e) => setFormName(e.target.value)}
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Email Address</label>
                                        <input
                                            type="email"
                                            value={formEmail}
                                            onChange={(e) => setFormEmail(e.target.value)}
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                {/* DEV SIMULATION SECTION */}
                                <div className="bg-slate-900/50 p-4 rounded-lg border border-indigo-500/20">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Shield className="w-4 h-4 text-indigo-400" />
                                        <span className="text-xs font-bold text-indigo-400 uppercase">Developer Simulation Override</span>
                                    </div>
                                    <div className="grid md:grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Simulate Role</label>
                                            <select
                                                value={formRole}
                                                onChange={(e) => setFormRole(e.target.value as any)}
                                                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-all cursor-pointer"
                                            >
                                                <option value="USER">Standard User</option>
                                                <option value="ADMIN">System Administrator</option>
                                            </select>
                                            <p className="text-[10px] text-slate-500 mt-1">Switch to ADMIN to see the "Admin Panel" in sidebar.</p>
                                        </div>
                                        <div>
                                            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Simulate Plan</label>
                                            <select
                                                value={formPlan}
                                                onChange={(e) => setFormPlan(e.target.value as any)}
                                                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-all cursor-pointer"
                                            >
                                                <option value="STARTER">Starter ($9/mo)</option>
                                                <option value="PRO">Pro ($29/mo)</option>
                                                <option value="ENTERPRISE">Enterprise</option>
                                            </select>
                                            <p className="text-[10px] text-slate-500 mt-1">Unlock Pro features like Veo Video & Viral Engine.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Social Connection Settings */}
                    <UserSocialSettings />

                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                        <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                            <Bell className="w-5 h-5 text-pink-400" /> Notifications
                        </h3>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-700">
                                <div>
                                    <p className="text-sm font-medium text-white">Daily Digest</p>
                                    <p className="text-xs text-slate-500">Receive a daily summary of agent activities via email.</p>
                                </div>
                                <div className="w-12 h-6 rounded-full bg-indigo-600 relative cursor-pointer transition-colors hover:bg-indigo-500"><div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-white shadow-md"></div></div>
                            </div>
                            <div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-700">
                                <div>
                                    <p className="text-sm font-medium text-white">Security Alerts</p>
                                    <p className="text-xs text-slate-500">Notify me about new logins or suspicious activity.</p>
                                </div>
                                <div className="w-12 h-6 rounded-full bg-slate-700 relative cursor-pointer transition-colors"><div className="absolute top-1 left-1 w-4 h-4 rounded-full bg-slate-400 shadow-md"></div></div>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end pt-4 border-t border-slate-800">
                        <button
                            onClick={handleSave}
                            disabled={isSaving}
                            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-3 rounded-lg font-bold transition-all shadow-lg shadow-emerald-900/20 disabled:opacity-70 hover:scale-105 active:scale-95"
                        >
                            {isSaving ? <><Loader2 className="w-4 h-4 animate-spin" /> Saving...</> : saved ? <><Check className="w-4 h-4" /> Saved</> : <><Save className="w-4 h-4" /> Save Changes</>}
                        </button>
                    </div>
                </div>
            )}

            {/* BILLING TAB */}
            {activeTab === 'BILLING' && (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 relative">
                    {showSuccessConfetti && (
                        <div className="absolute inset-0 z-50 bg-slate-900/90 backdrop-blur-md flex items-center justify-center animate-in fade-in rounded-xl">
                            <div className="bg-slate-800 p-10 rounded-2xl border border-emerald-500/50 shadow-2xl flex flex-col items-center max-w-sm text-center relative overflow-hidden">
                                <div className="absolute inset-0 bg-emerald-500/10 animate-pulse"></div>
                                <div className="w-24 h-24 bg-emerald-500 rounded-full flex items-center justify-center mb-6 animate-bounce shadow-lg shadow-emerald-500/30 z-10">
                                    <Check className="w-12 h-12 text-white" />
                                </div>
                                <h3 className="text-3xl font-bold text-white mb-2 z-10">Success!</h3>
                                <p className="text-slate-300 mb-1 z-10">{purchasedItemName}</p>
                                <p className="text-emerald-400 font-medium z-10">Activated Successfully</p>
                                <button
                                    onClick={() => setShowSuccessConfetti(false)}
                                    className="mt-8 bg-slate-700 hover:bg-slate-600 text-white px-8 py-3 rounded-lg transition-colors font-bold z-10"
                                >
                                    Done
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Current Plan Status */}
                    <div className="bg-gradient-to-r from-indigo-900/50 to-purple-900/50 rounded-xl border border-indigo-500/30 p-8 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
                        <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-6">
                            <div>
                                <p className="text-indigo-300 font-bold uppercase tracking-wider text-xs mb-1">Current Subscription</p>
                                <div className="flex items-center gap-3">
                                    <h3 className="text-4xl font-bold text-white">{user.plan}</h3>
                                    <span className="px-2 py-1 bg-white/10 rounded text-xs font-mono text-indigo-200 border border-white/10">Active</span>
                                </div>
                                <p className="text-slate-400 text-sm max-w-md mt-2">
                                    {user.plan === 'STARTER' && "Starter Plan. Good for basics."}
                                    {user.plan === 'PRO' && "Pro Plan. You have Hybrid Key Access enabled."}
                                    {user.plan === 'ENTERPRISE' && "Unlimited power. Dedicated support."}
                                </p>
                            </div>
                            <div className="text-right bg-slate-900/50 p-6 rounded-xl border border-slate-700/50 backdrop-blur-sm min-w-[200px]">
                                <p className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">Available Credits</p>
                                <p className="text-4xl font-mono font-bold text-emerald-400">{user.credits?.toLocaleString()}</p>
                                <p className="text-xs text-slate-500 mt-1">
                                    {user.credits > 0 ? 'Platform Balance' : <span className="text-amber-400 flex items-center justify-end gap-1"><AlertCircle className="w-3 h-3" /> Bal: 0. Using Hybrid Key?</span>}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* API Configuration */}
                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                        <div className="flex flex-col md:flex-row justify-between items-start mb-6 gap-4">
                            <div>
                                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                                    <CreditCard className="w-5 h-5 text-amber-400" /> Payment & Hybrid Mode
                                </h3>
                                <p className="text-sm text-slate-400 mt-1 max-w-xl">
                                    We use a Hybrid Billing Model. Your subscription includes a massive credit pack.
                                    If you run out, you can either buy more credits OR switch to "BYO Key" mode to pay Google directly.
                                </p>
                            </div>

                            <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-700 shrink-0">
                                <button
                                    onClick={() => { setUser({ ...user, apiMode: 'PLATFORM' }); StorageService.updateUserInDb({ ...user, apiMode: 'PLATFORM' }); }}
                                    className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all flex items-center gap-2 ${user.apiMode === 'PLATFORM' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
                                >
                                    <Zap className="w-3 h-3" /> Platform Billing
                                </button>
                                <button
                                    onClick={() => {
                                        if (user.plan === 'STARTER') {
                                            addToast("Upgrade to PRO to unlock BYO Key mode.", 'error');
                                            return;
                                        }
                                        setUser({ ...user, apiMode: 'PERSONAL' });
                                        StorageService.updateUserInDb({ ...user, apiMode: 'PERSONAL' });
                                    }}
                                    className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all flex items-center gap-2 ${user.apiMode === 'PERSONAL' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
                                >
                                    {user.plan === 'STARTER' ? <Lock className="w-3 h-3" /> : <Unlock className="w-3 h-3" />} BYO API Key
                                </button>
                            </div>
                        </div>

                        {user.apiMode === 'PERSONAL' ? (
                            <div className="animate-in fade-in">
                                <div className="bg-amber-500/10 border border-amber-500/20 p-4 rounded-lg flex gap-3 mb-4">
                                    <HelpCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                                    <div className="text-sm text-amber-200">
                                        <p className="font-bold mb-1">Hybrid Mode Active</p>
                                        <p>You are bypassing Yokaizen credits and paying Google directly. Your API key is stored locally in your browser.</p>
                                    </div>
                                </div>
                                <input
                                    type="password"
                                    value={user.personalApiKey || ''}
                                    onChange={(e) => {
                                        const newVal = e.target.value;
                                        setUser({ ...user, personalApiKey: newVal });
                                        StorageService.updateUserInDb({ ...user, personalApiKey: newVal });
                                    }}
                                    placeholder="AIzaSy..."
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono"
                                />
                                <div className="flex justify-end mt-4">
                                    <p className="text-xs text-slate-500 mr-auto pt-2">Auto-saving...</p>
                                </div>
                            </div>
                        ) : (
                            <div className="animate-in fade-in space-y-12">

                                {/* Subscription Tiers */}
                                <div ref={planSectionRef} className="scroll-mt-24">
                                    <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                                        <Crown className="w-4 h-4 text-amber-400" /> Subscription Plans
                                    </h4>
                                    <div className="grid md:grid-cols-3 gap-4">
                                        {SUBSCRIPTION_PLANS.map((plan) => {
                                            const isCurrent = user.plan === plan.tier;
                                            const isSelected = autoSelectPlanId === plan.id;
                                            return (
                                                <button
                                                    key={plan.id}
                                                    onClick={() => !isCurrent && handlePurchase(plan.id, 'SUBSCRIPTION', plan.tier, `${plan.name} Plan`)}
                                                    disabled={!!isPurchasing || isCurrent}
                                                    className={`relative p-6 rounded-xl border transition-all text-left group flex flex-col h-full ${isCurrent
                                                        ? 'bg-slate-800 border-indigo-500 ring-1 ring-indigo-500 cursor-default'
                                                        : isSelected
                                                            ? 'bg-slate-900 border-amber-500 ring-2 ring-amber-500 scale-[1.02] shadow-xl'
                                                            : 'bg-slate-900 border-slate-700 hover:border-indigo-500 hover:scale-[1.02]'
                                                        }`}
                                                >
                                                    <div className="flex justify-between items-start mb-4">
                                                        <h5 className={`text-lg font-bold ${plan.popular ? 'text-indigo-400' : 'text-white'}`}>{plan.name}</h5>
                                                        {isCurrent && <span className="bg-indigo-500 text-white text-[10px] px-2 py-1 rounded font-bold">CURRENT</span>}
                                                        {isSelected && !isCurrent && <span className="bg-amber-500 text-slate-900 text-[10px] px-2 py-1 rounded font-bold animate-pulse">SELECTED</span>}
                                                    </div>
                                                    <div className="mb-6">
                                                        <span className="text-3xl font-bold text-white">{plan.price}</span>
                                                        <span className="text-slate-500 text-sm">{plan.period}</span>
                                                    </div>
                                                    <ul className="space-y-3 mb-8 flex-1">
                                                        {plan.features.map((f, i) => (
                                                            <li key={i} className="text-xs text-slate-300 flex items-center gap-2">
                                                                <Check className="w-3 h-3 text-emerald-500" /> {f}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                    <div className={`w-full py-2 rounded-lg text-center text-sm font-bold transition-colors flex items-center justify-center gap-2 ${isCurrent ? 'bg-indigo-500/20 text-indigo-300' : 'bg-indigo-600 text-white group-hover:bg-indigo-500'
                                                        }`}>
                                                        {isPurchasing === plan.id ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                                                        {isCurrent ? 'Active Plan' : isPurchasing === plan.id ? 'Processing...' : 'Upgrade'}
                                                    </div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>

                                {/* Credit Packs */}
                                <div>
                                    <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                                        <Zap className="w-4 h-4 text-emerald-400" /> One-Time Credit Top Up
                                    </h4>
                                    <div className="grid md:grid-cols-3 gap-4">
                                        {CREDIT_PACKS.map((pack) => (
                                            <button
                                                key={pack.id}
                                                onClick={() => handlePurchase(pack.id, 'CREDIT', pack.amount, pack.label)}
                                                disabled={!!isPurchasing}
                                                className={`relative p-5 rounded-xl border transition-all hover:scale-105 active:scale-95 text-left group shadow-lg ${pack.popular ? 'bg-emerald-900/20 border-emerald-500/50 ring-1 ring-emerald-500/30' : 'bg-slate-900 border-slate-700 hover:border-slate-500'}`}
                                            >
                                                {isPurchasing === pack.id ? (
                                                    <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm rounded-xl flex flex-col items-center justify-center z-20">
                                                        <Loader2 className="w-6 h-6 text-white animate-spin mb-2" />
                                                        <span className="text-xs text-slate-300 font-medium">Processing...</span>
                                                    </div>
                                                ) : null}

                                                <p className={`text-sm font-bold mb-1 ${pack.popular ? 'text-emerald-200' : 'text-slate-300'}`}>{pack.label}</p>
                                                <p className="text-3xl font-bold text-white mb-3">${pack.price.toFixed(2)}</p>
                                                <div className={`flex items-center gap-1 text-xs font-bold ${pack.popular ? 'text-white' : 'text-emerald-400'}`}>
                                                    <Sparkles className="w-3 h-3" />
                                                    +{pack.amount.toLocaleString()} Credits
                                                </div>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex items-center justify-center gap-2 text-xs text-slate-500 border-t border-slate-800 pt-6">
                                    <Shield className="w-3 h-3" />
                                    Payments processed securely via Stripe Simulation. Credits never expire.
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Settings;

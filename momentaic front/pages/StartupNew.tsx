import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { StartupCreate } from '../types';
import { ArrowLeft, Send, Bot, User, Target, Lightbulb, Zap, Rocket, ShieldAlert } from 'lucide-react';
import { useToast } from '../components/ui/Toast';
import { Card } from '../components/ui/Card';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
    id: string;
    role: 'ai' | 'user';
    text?: string;
    component?: React.ReactNode;
    field?: keyof StartupCreate;
}

interface StrategicInsight {
    industry: string;
    stage: string;
    summary: string;
    insight: string;
    potential_competitors: string[];
    follow_up_question: string;
}

export default function StartupNew() {
    const navigate = useNavigate();
    const { toast } = useToast();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [formData, setFormData] = useState<Partial<StartupCreate>>({ stage: 'idea' });
    const [isTyping, setIsTyping] = useState(false);
    const [step, setStep] = useState(0);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Initial Greeting
    useEffect(() => {
        addAiMessage("Identify yourself. What is the name of your new entity?", 'name');
    }, []);

    // Auto-scroll
    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const addAiMessage = (text: string, field?: keyof StartupCreate) => {
        setIsTyping(true);
        setTimeout(() => {
            setMessages(prev => [...prev, { id: Date.now().toString(), role: 'ai', text, field }]);
            setIsTyping(false);
        }, 800);
    };

    const addCustomComponent = (component: React.ReactNode, field?: keyof StartupCreate) => {
        setIsTyping(true);
        setTimeout(() => {
            setMessages(prev => [...prev, { id: Date.now().toString(), role: 'ai', component, field }]);
            setIsTyping(false);
        }, 800);
    };

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userText = input;
        setInput('');
        setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', text: userText }]);

        const currentField = messages[messages.length - 1]?.field;
        let nextData = { ...formData };

        if (currentField) {
            // @ts-ignore
            nextData[currentField] = userText;
            setFormData(nextData);
        }

        // State Machine for Interview
        switch (step) {
            case 0: // Name -> Description
                addAiMessage(`Acknowledged. ${userText}. Now, describe your mission objectives. What problem are you solving?`, 'description');
                setStep(1);
                break;
            case 1: // Description -> AI Analysis
                setIsTyping(true);

                try {
                    // Call the new "Super Clever" endpoint
                    const analysis = await api.analyzeStartup(userText); // Returns new enriched types

                    // Auto-fill inferred fields
                    nextData.industry = analysis.industry;
                    nextData.stage = analysis.stage as any;
                    setFormData(nextData);

                    // Render Weak/Strong Analysis Card
                    setTimeout(() => {
                        setIsTyping(false);
                        const card = (
                            <div className="space-y-4 w-full">
                                <div className="bg-[#111] border border-[#00f0ff]/20 rounded-xl p-5 shadow-[0_0_30px_rgba(0,240,255,0.1)]">
                                    <div className="flex items-start justify-between mb-4">
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <Target className="w-4 h-4 text-[#00f0ff]" />
                                                <span className="text-xs font-mono text-[#00f0ff] uppercase tracking-widest">Strategic Analysis</span>
                                            </div>
                                            <h3 className="text-lg font-bold text-white leading-tight">{analysis.summary}</h3>
                                        </div>
                                        <div className="bg-[#00f0ff]/10 border border-[#00f0ff]/30 px-3 py-1 rounded text-xs text-[#00f0ff] font-mono uppercase">
                                            {analysis.industry}
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 gap-4">
                                        <div className="bg-[#0a0a0a] rounded-lg p-3 border border-white/5 relative overflow-hidden">
                                            <div className="absolute top-0 left-0 w-1 h-full bg-yellow-500"></div>
                                            <div className="flex items-start gap-3">
                                                <Lightbulb className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />
                                                <div>
                                                    <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Core Insight / Risk</div>
                                                    <p className="text-sm text-gray-300 italic">"{analysis.insight}"</p>
                                                </div>
                                            </div>
                                        </div>

                                        {analysis.potential_competitors.length > 0 && (
                                            <div className="bg-[#0a0a0a] rounded-lg p-3 border border-white/5 relative overflow-hidden">
                                                <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
                                                <div className="flex items-start gap-3">
                                                    <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                                                    <div>
                                                        <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Radar Lock (Competitors)</div>
                                                        <div className="flex flex-wrap gap-2">
                                                            {analysis.potential_competitors.map((comp, i) => (
                                                                <span key={i} className="bg-white/5 px-2 py-0.5 rounded text-xs text-gray-400 border border-white/10">{comp}</span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    <div className="mt-4 pt-4 border-t border-white/10">
                                        <p className="text-sm text-gray-400 font-mono">
                                            <span className="text-[#00f0ff]">{'>'}</span> {analysis.follow_up_question}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        );

                        setMessages(prev => [...prev, { id: Date.now().toString(), role: 'ai', component: card }]);

                        // We are technically skipping the user "confirm industry" step because AI did it better.
                        // We move to step 2 but the context has changed. Step 2 logic expects "Context: user answer".
                        setStep(2);
                    }, 1000);

                } catch (e) {
                    addAiMessage("Analysis offline. Proceeding with manual override. Confirming sector: Technology. Proceeding to initialization.");
                    nextData.industry = "Technology";
                    nextData.stage = "idea";
                    setFormData(nextData);
                    setStep(2);
                    setIsTyping(false);
                }
                break;

            case 2: // Answer to follow-up -> Finalize
                nextData.description = `${nextData.description}\n\nStrategic Context: ${userText}`;
                setFormData(nextData);

                setIsTyping(true);
                addAiMessage("INITIALIZING ENTITY...");
                setTimeout(() => finalizeCreation(nextData), 1000);
                break;
        }
    };

    const finalizeCreation = async (data: Partial<StartupCreate>) => {
        try {
            const payload: StartupCreate = {
                name: data.name || 'Untitled Entity',
                description: data.description,
                industry: data.industry || 'Technology',
                stage: data.stage as any || 'idea',
                website: '',
                github_url: ''
            };

            const newStartup = await api.createStartup(payload);
            setMessages(prev => [...prev, { id: 'final', role: 'ai', text: 'ENTITY INITIALIZED. REDIRECTING TO MISSION CONTROL...' }]);

            setTimeout(() => {
                navigate(`/startups/${newStartup.id}`);
                toast({ type: 'success', title: 'Initialization Complete', message: 'Welcome to the network.' });
            }, 1500);

        } catch (error) {
            setMessages(prev => [...prev, { id: 'err', role: 'ai', text: 'ERROR: DATABASE WRITE FAILED. RETRYING...' }]);
            console.error(error);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto h-[90vh] flex flex-col relative justify-center">
            <div className="absolute inset-0 bg-cyber-grid opacity-5 pointer-events-none"></div>

            <Button variant="ghost" onClick={() => navigate(-1)} className="absolute top-4 left-4 pl-0 text-gray-500 hover:text-white z-50">
                <ArrowLeft className="w-4 h-4 mr-2" /> ABORT
            </Button>

            <Card className="flex-1 flex flex-col bg-[#050505] border-white/10 overflow-hidden shadow-2xl relative rounded-2xl h-full max-h-[800px]">

                {/* Header */}
                <div className="p-4 border-b border-white/10 bg-[#0a0a0a] flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-2 h-2 bg-[#00f0ff] rounded-full animate-pulse"></div>
                        <span className="font-mono text-xs text-[#00f0ff] tracking-[0.2em] uppercase">Genesis_Protocol_V2</span>
                    </div>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
                    <AnimatePresence>
                        {messages.map((msg) => (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                key={msg.id}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div className={`max-w-[85%] flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                    {/* Avatar */}
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border mt-1 ${msg.role === 'ai' ? 'bg-[#00f0ff]/10 border-[#00f0ff]/30 text-[#00f0ff]' : 'bg-white/10 border-white/20 text-white'
                                        }`}>
                                        {msg.role === 'ai' ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                                    </div>

                                    {/* Content */}
                                    {msg.component ? (
                                        msg.component
                                    ) : (
                                        <div className={`p-4 rounded-xl text-sm font-mono leading-relaxed ${msg.role === 'ai'
                                            ? 'bg-[#0a0a0a] border border-white/10 text-gray-300'
                                            : 'bg-[#2563eb] text-white border border-[#2563eb] shadow-[0_0_15px_rgba(37,99,235,0.2)]'
                                            }`}>
                                            {msg.text}
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {isTyping && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex justify-start"
                        >
                            <div className="max-w-[80%] flex gap-4">
                                <div className="w-8 h-8 rounded-lg bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] flex items-center justify-center shrink-0 mt-1">
                                    <Bot className="w-4 h-4" />
                                </div>
                                <div className="bg-[#0a0a0a] border border-white/10 px-4 py-3 rounded-xl flex items-center gap-1">
                                    <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce delay-75"></div>
                                    <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce delay-150"></div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                    <div ref={scrollRef} />
                </div>

                {/* Input */}
                <div className="p-4 bg-[#0a0a0a] border-t border-white/10">
                    <form onSubmit={handleSend} className="flex gap-4">
                        <Input
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            placeholder="Data input required..."
                            className="flex-1 bg-black border-white/10 focus:border-[#00f0ff] font-mono text-white placeholder-gray-600"
                            autoFocus
                            disabled={isTyping}
                        />
                        <Button type="submit" variant="cyber" disabled={!input.trim() || isTyping}>
                            <Send className="w-4 h-4" />
                        </Button>
                    </form>
                </div>
            </Card>
        </div>
    );
}

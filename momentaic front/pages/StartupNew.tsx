
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { StartupCreate } from '../types';
import { ArrowLeft, Send, Bot, User, CheckCircle2 } from 'lucide-react';
import { useToast } from '../components/ui/Toast';
import { Card } from '../components/ui/Card';

interface Message {
    id: string;
    role: 'ai' | 'user';
    text: string;
    field?: keyof StartupCreate; // If this message expects a specific field answer
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

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userText = input;
        setInput('');
        setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', text: userText }]);

        // Process Answer based on current step/field
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
                // Call AI to analyze
                try {
                    const analysis = await api.analyzeStartup(userText);

                    // Auto-fill inferred fields
                    nextData.industry = analysis.industry;
                    nextData.stage = analysis.stage as any;
                    setFormData(nextData);

                    // Ask the context-aware follow-up
                    setTimeout(() => {
                        addAiMessage(`Analysis Complete. Sector: ${analysis.industry} | Stage: ${analysis.stage}. \n\n${analysis.follow_up_question}`);
                        setIsTyping(false);
                        setStep(2);
                    }, 1500); // Fake delay for "thinking" effect
                } catch (e) {
                    // Fallback if AI fails
                    addAiMessage("Processing complete. Confirming sector: Technology. Proceeding to initialization.");
                    nextData.industry = "Technology";
                    nextData.stage = "idea";
                    setFormData(nextData);
                    setStep(2);
                    setIsTyping(false);
                }
                break;
            case 2: // Answer to follow-up -> Finalize
                // Append context to description for richer profile
                nextData.description = `${nextData.description}\n\nContext: ${userText}`;
                setFormData(nextData);

                setIsTyping(true);
                addAiMessage("INITIALIZING ENTITY...");
                setTimeout(() => finalizeCreation(nextData), 1000);
                break;
        }
    };

    const finalizeCreation = async (data: Partial<StartupCreate>) => {
        try {
            // Construct final payload
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
        <div className="max-w-2xl mx-auto h-[80vh] flex flex-col relative">
            <Button variant="ghost" onClick={() => navigate(-1)} className="absolute -top-12 left-0 pl-0 text-gray-500 hover:text-white">
                <ArrowLeft className="w-4 h-4 mr-2" /> ABORT SEQUENCE
            </Button>

            <Card className="flex-1 flex flex-col bg-[#050505] border-white/10 overflow-hidden shadow-2xl relative">
                <div className="absolute inset-0 bg-cyber-grid opacity-5 pointer-events-none"></div>

                {/* Header */}
                <div className="p-4 border-b border-white/10 bg-[#0a0a0a] flex items-center gap-3">
                    <div className="w-2 h-2 bg-[#00f0ff] rounded-full animate-pulse"></div>
                    <span className="font-mono text-xs text-[#00f0ff] tracking-[0.2em] uppercase">Founding_Protocol_V1</span>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                {/* Avatar */}
                                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${msg.role === 'ai' ? 'bg-[#00f0ff]/10 border-[#00f0ff]/30 text-[#00f0ff]' : 'bg-white/10 border-white/20 text-white'}`}>
                                    {msg.role === 'ai' ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                                </div>

                                {/* Bubble */}
                                <div className={`p-4 rounded-xl text-sm font-mono leading-relaxed ${msg.role === 'ai'
                                        ? 'bg-[#0a0a0a] border border-white/10 text-gray-300'
                                        : 'bg-[#2563eb] text-white border border-[#2563eb] shadow-[0_0_15px_rgba(37,99,235,0.2)]'
                                    }`}>
                                    {msg.text}
                                </div>
                            </div>
                        </div>
                    ))}

                    {isTyping && (
                        <div className="flex justify-start">
                            <div className="max-w-[80%] flex gap-4">
                                <div className="w-8 h-8 rounded-lg bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] flex items-center justify-center shrink-0">
                                    <Bot className="w-4 h-4" />
                                </div>
                                <div className="bg-[#0a0a0a] border border-white/10 px-4 py-3 rounded-xl flex items-center gap-1">
                                    <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce delay-75"></div>
                                    <div className="w-1.5 h-1.5 bg-[#00f0ff] rounded-full animate-bounce delay-150"></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={scrollRef} />
                </div>

                {/* Input */}
                <div className="p-4 bg-[#0a0a0a] border-t border-white/10">
                    <form onSubmit={handleSend} className="flex gap-4">
                        <Input
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            placeholder="Type your response..."
                            className="flex-1 bg-black border-white/10 focus:border-[#00f0ff] font-mono"
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

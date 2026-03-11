import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Globe, Loader, Bot, User, Link as LinkIcon, AlertCircle } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

interface Message {
    role: 'user' | 'ai';
    content: string;
    timestamp: Date;
}

const SupportAgent: React.FC = () => {
    const [query, setQuery] = useState('');
    const [contextUrl, setContextUrl] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [isThinking, setIsThinking] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const { addToast } = useToast();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!query.trim()) return;

        const userMsg: Message = { role: 'user', content: query, timestamp: new Date() };
        setMessages(prev => [...prev, userMsg]);
        setQuery('');
        setIsThinking(true);

        try {
            const history = messages.map(m => ({ role: m.role, content: m.content }));
            const response = await BackendService.answerSupportQuery(userMsg.content, history, contextUrl);

            if (response.success) {
                const aiMsg: Message = { role: 'ai', content: response.answer, timestamp: new Date() };
                setMessages(prev => [...prev, aiMsg]);
            } else {
                addToast(response.error || "Failed to get answer", 'error');
            }
        } catch (error) {
            console.error(error);
            addToast("Failed to connect to Support Agent", 'error');
        } finally {
            setIsThinking(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="p-6 max-w-5xl mx-auto animate-fade-in h-[calc(100vh-2rem)] flex flex-col">
            <div className="mb-6 text-center sm:text-left">
                <h2 className="text-3xl font-bold text-white flex flex-col sm:flex-row items-center justify-center sm:justify-start gap-3">
                    <MessageSquare className="w-8 h-8 text-indigo-500 shrink-0" />
                    Support Sage
                </h2>
                <p className="text-slate-400 mt-2">AI Customer Support with Context Awareness.</p>
            </div>

            <div className="flex-1 bg-slate-800 rounded-xl border border-slate-700 flex flex-col overflow-hidden shadow-2xl">
                {/* Context Bar */}
                <div className="bg-slate-900/50 p-3 border-b border-slate-700 flex items-center gap-3">
                    <div className="flex items-center gap-2 text-slate-400 text-sm bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 flex-1">
                        <Globe className="w-4 h-4 text-indigo-400" />
                        <input
                            type="text"
                            value={contextUrl}
                            onChange={(e) => setContextUrl(e.target.value)}
                            placeholder="Add context URL (e.g. docs, pricing page)..."
                            className="bg-transparent border-none outline-none text-slate-200 w-full placeholder:text-slate-600"
                        />
                    </div>
                    {contextUrl && (
                        <div className="text-xs text-emerald-400 flex items-center gap-1 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
                            <LinkIcon className="w-3 h-3" /> Context Active
                        </div>
                    )}
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-900/30">
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-50">
                            <Bot className="w-16 h-16 mb-4" />
                            <p>Ask me anything about your product or service.</p>
                        </div>
                    )}

                    {messages.map((msg, i) => (
                        <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {msg.role === 'ai' && (
                                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0 mt-1">
                                    <Bot className="w-5 h-5 text-white" />
                                </div>
                            )}
                            <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user'
                                    ? 'bg-indigo-600 text-white rounded-tr-none'
                                    : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-none'
                                }`}>
                                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                                <span className="text-[10px] opacity-50 mt-2 block">
                                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0 mt-1">
                                    <User className="w-5 h-5 text-slate-300" />
                                </div>
                            )}
                        </div>
                    ))}

                    {isThinking && (
                        <div className="flex gap-4 justify-start animate-pulse">
                            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                            <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-none p-4 flex items-center gap-2">
                                <Loader className="w-4 h-4 animate-spin text-indigo-400" />
                                <span className="text-sm text-slate-400">Thinking...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-slate-800 border-t border-slate-700">
                    <div className="relative">
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Type your message..."
                            className="w-full bg-slate-900 border border-slate-600 rounded-xl pl-4 pr-12 py-3 text-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none resize-none h-14 max-h-32"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!query.trim() || isThinking}
                            className="absolute right-2 top-2 p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg disabled:opacity-50 disabled:bg-slate-700 transition-colors"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                    <p className="text-center text-xs text-slate-500 mt-2">
                        AI can make mistakes. Review generated responses.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default SupportAgent;

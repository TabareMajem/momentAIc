import { useState } from 'react';
import { Send, Cpu, Download, Terminal, CheckCircle } from 'lucide-react';

interface BuildMessage {
    role: 'user' | 'assistant';
    content: string;
    file_url?: string;
}

export default function IntegrationBuilder() {
    const [messages, setMessages] = useState<BuildMessage[]>([
        { role: 'assistant', content: "I am The Builder. I write production-ready Python connectors for any API. What integration do you need today?" }
    ]);
    const [input, setInput] = useState('');
    const [building, setBuilding] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = input;
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setInput('');
        setBuilding(true);

        try {
            // Real API call to Integration Builder Agent
            const response = await fetch('/api/v1/agents/builder/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({ message: userMsg })
            });

            const data = await response.json();

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.response,
                file_url: data.file_url
            }]);
        } catch (err) {
            console.error('Builder Error:', err);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I encountered a connection error. Please try again."
            }]);
        } finally {
            setBuilding(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white p-8 pt-20 flex flex-col">
            <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col">

                <div className="flex items-center gap-3 mb-8">
                    <div className="p-3 bg-brand-gradient rounded-xl">
                        <Cpu className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold">Integration Builder</h1>
                        <p className="text-white/50">Describe the integration. Receive the code.</p>
                    </div>
                </div>

                <div className="flex-1 bg-white/5 border border-white/10 rounded-2xl p-6 mb-6 overflow-y-auto space-y-6">
                    {messages.map((m, i) => (
                        <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] rounded-xl p-4 ${m.role === 'user' ? 'bg-blue-600' : 'bg-[#111] border border-white/10'}`}>
                                <p className="whitespace-pre-wrap">{m.content}</p>

                                {m.file_url && (
                                    <div className="mt-4 p-3 bg-black/50 rounded-lg border border-white/10 flex items-center justify-between group cursor-pointer hover:border-green-500/50 transition-colors">
                                        <div className="flex items-center gap-3">
                                            <Terminal className="w-5 h-5 text-green-400" />
                                            <span className="font-mono text-sm text-green-400">connector.py</span>
                                        </div>
                                        <a href={m.file_url} download className="p-2 hover:bg-white/10 rounded-lg">
                                            <Download className="w-4 h-4 text-white" />
                                        </a>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {building && (
                        <div className="flex justify-start">
                            <div className="bg-[#111] border border-white/10 rounded-xl p-4 flex items-center gap-3">
                                <Cpu className="w-4 h-4 animate-spin text-purple-500" />
                                <span className="text-sm font-mono text-purple-400">Writing code...</span>
                            </div>
                        </div>
                    )}
                </div>

                <div className="relative">
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="e.g. Build a HubSpot connector to sync deals..."
                        className="w-full bg-[#111] border border-white/10 rounded-xl px-6 py-4 pr-16 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                    <button
                        onClick={handleSend}
                        disabled={building || !input.trim()}
                        className="absolute right-2 top-2 p-2 bg-blue-600 rounded-lg hover:bg-blue-500 disabled:opacity-50 transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}

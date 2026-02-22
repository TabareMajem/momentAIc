import { useState, useEffect } from 'react';
import { Download, FileText, FileSpreadsheet, File, Shield, Briefcase, RefreshCw, CheckCircle } from 'lucide-react';

interface VaultFile {
    filename: str;
    url: str;
    size: number;
    created_at: str;
    type: 'PDF' | 'CSV' | 'DOCX' | 'TXT' | 'UNKNOWN';
}

export default function TheVault() {
    const [files, setFiles] = useState<VaultFile[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchFiles();
    }, []);

    const fetchFiles = async () => {
        try {
            const res = await fetch('/api/v1/vault/');
            if (!res.ok) throw new Error(`Status: ${res.status}`);

            const data = await res.json();
            if (Array.isArray(data)) {
                setFiles(data);
            } else {
                console.warn("Vault API returned non-array:", data);
                setFiles([]);
            }
        } catch (err) {
            console.error("Failed to fetch vault", err);
            setFiles([]);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            await fetch('/api/v1/vault/generate-pack', { method: 'POST' });
            // Poll for files
            const interval = setInterval(async () => {
                const res = await fetch('/api/v1/vault');
                const data = await res.json();
                setFiles(data);
                if (data.length >= 3) { // Assume package is done if we have files
                    clearInterval(interval);
                    setGenerating(false);
                }
            }, 3000);

            // Stop polling after 30s
            setTimeout(() => { clearInterval(interval); setGenerating(false); }, 30000);

        } catch (err) {
            console.error(err);
            setGenerating(false);
        }
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'PDF': return <FileText className="w-8 h-8 text-red-400" />;
            case 'CSV': return <FileSpreadsheet className="w-8 h-8 text-green-400" />;
            case 'DOCX': return <FileText className="w-8 h-8 text-blue-400" />;
            default: return <File className="w-8 h-8 text-gray-400" />;
        }
    };

    const formatSize = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white p-8 pt-20">
            <div className="max-w-6xl mx-auto">

                {/* Header */}
                <div className="flex justify-between items-end mb-12">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <Shield className="w-10 h-10 text-yellow-500" />
                            <h1 className="text-4xl font-bold">The Vault</h1>
                        </div>
                        <p className="text-white/60 text-lg">Your repository of AI-generated assets, contracts, and models.</p>
                    </div>

                    {files.length === 0 && !loading && (
                        <button
                            onClick={handleGenerate}
                            disabled={generating}
                            className="bg-white text-black px-6 py-3 rounded-lg font-bold hover:bg-white/90 disabled:opacity-50 flex items-center gap-2"
                        >
                            {generating ? <RefreshCw className="animate-spin w-5 h-5" /> : <Briefcase className="w-5 h-5" />}
                            {generating ? 'Agents Working...' : 'Generate Day 1 Pack'}
                        </button>
                    )}
                </div>

                {/* Content */}
                {loading ? (
                    <div className="text-center py-20 text-white/30">Accessing secure vault...</div>
                ) : files.length === 0 ? (
                    <div className="text-center py-24 border border-white/10 rounded-2xl bg-white/5">
                        <Shield className="w-16 h-16 mx-auto mb-4 text-white/20" />
                        <h3 className="text-2xl font-bold mb-2">Vault Empty</h3>
                        <p className="text-white/50 mb-8 max-w-md mx-auto">
                            Your AI agents haven't generated any deliverables yet. Trigger the Day 1 Pack to get your Strategy Plan, Financial Model, and Legal Contracts.
                        </p>
                        <div className="text-sm text-yellow-500/80 bg-yellow-500/10 inline-block px-4 py-2 rounded-full">
                            🚀 Recommended: Generate Day 1 Pack
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                        {/* Day 1 Section Header */}
                        <div className="col-span-full mb-4 flex items-center gap-2 text-white/40 text-sm font-mono uppercase tracking-widest mt-4 border-b border-white/10 pb-2">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            Verified Deliverables ({files.length})
                        </div>

                        {files.map((file) => (
                            <div key={file.filename} className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors group">
                                <div className="flex justify-between items-start mb-6">
                                    <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                                        {getIcon(file.type)}
                                    </div>
                                    <span className="text-xs font-mono text-white/30 bg-white/5 px-2 py-1 rounded">
                                        {file.type}
                                    </span>
                                </div>

                                <h3 className="text-lg font-bold mb-1 truncate" title={file.filename}>
                                    {file.type === 'PDF' && 'Strategic Business Plan'}
                                    {file.type === 'CSV' && 'Financial Model (12-Mo)'}
                                    {file.type === 'DOCX' && 'Legal Agreement'}
                                    {file.type === 'TXT' && 'Recruiting Packet'}
                                    {!['PDF', 'CSV', 'DOCX', 'TXT'].includes(file.type) && file.filename}
                                </h3>
                                <p className="text-sm text-white/40 mb-6 font-mono truncate">{file.filename}</p>

                                <div className="flex justify-between items-center mt-auto">
                                    <span className="text-xs text-white/30">{formatSize(file.size)}</span>
                                    <a
                                        href={file.url}
                                        download
                                        className="flex items-center gap-2 text-sm font-bold text-white hover:text-blue-400"
                                    >
                                        <Download className="w-4 h-4" /> Download
                                    </a>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

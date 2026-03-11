
import React, { useState, useRef } from 'react';
import { DollarSign, FileText, AlertOctagon, Check, Plus, Upload, Loader2 } from 'lucide-react';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

export interface Invoice {
    id: string;
    vendor: string;
    amount: number;
    date: string;
    items: string[];
    status: 'PENDING' | 'APPROVED' | 'FLAGGED';
    auditReason?: string;
}

const ProcurementAgent: React.FC = () => {
    const [invoices, setInvoices] = useState<Invoice[]>([
        { id: 'INV-001', vendor: 'AWS', amount: 4500, date: '2025-01-15', items: ['Hosting'], status: 'PENDING' }
    ]);
    const [isProcessing, setIsProcessing] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { addToast } = useToast();

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsProcessing(true);
        try {
            const base64 = await new Promise<string>((resolve) => {
                const reader = new FileReader();
                reader.onload = () => resolve((reader.result as string).split(',')[1]);
                reader.readAsDataURL(file);
            });

            const mimeType = file.type;

            // Audit the new file
            const response = await BackendService.auditInvoice(file);

            if (response.success) {
                const result = response.result;
                const newInvoice: Invoice = {
                    id: `INV-${Date.now().toString().slice(-4)}`,
                    vendor: result.vendorName || "Unknown Vendor",
                    amount: result.amount || 0,
                    date: result.date || new Date().toISOString().split('T')[0],
                    items: ["Extracted from Invoice"],
                    status: result.isSuspicious ? 'FLAGGED' : 'APPROVED',
                    auditReason: result.reason
                };
                setInvoices(prev => [newInvoice, ...prev]);
                addToast("Invoice audited successfully", 'success');
            } else {
                addToast(response.error || "Audit failed", 'error');
            }
        } catch (e) {
            console.error(e);
            addToast("Failed to process invoice file", 'error');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleAuditExisting = async (inv: Invoice) => {
        setIsProcessing(true);
        try {
            const response = await BackendService.auditInvoice(inv);
            if (response.success) {
                const result = response.result;
                setInvoices(prev => prev.map(i => i.id === inv.id ? {
                    ...i,
                    status: result.isSuspicious ? 'FLAGGED' : 'APPROVED',
                    auditReason: result.reason
                } : i));
                addToast("Re-audit complete", 'success');
            } else {
                addToast(response.error || "Audit failed", 'error');
            }
        } catch (e) {
            console.error(e);
            addToast("Audit failed", 'error');
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="p-6 max-w-6xl mx-auto animate-fade-in text-slate-200">
            <div className="mb-8 flex flex-col md:flex-row gap-6 justify-between md:items-center">
                <div className="text-center md:text-left">
                    <h2 className="text-3xl font-bold text-white flex justify-center md:justify-start items-center gap-3">
                        <DollarSign className="w-8 h-8 text-emerald-500 shrink-0" />
                        Agent J: The Auditor
                    </h2>
                    <p className="text-slate-400 mt-2">Invoice Anomaly Detection (Image/PDF).</p>
                </div>

                <div className="flex justify-center md:justify-end">
                    <input ref={fileInputRef} type="file" accept="image/*,application/pdf" className="hidden" onChange={handleFileUpload} />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isProcessing}
                        className="w-full md:w-auto sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 md:px-4 md:py-2 rounded-lg font-bold flex items-center justify-center gap-2 disabled:opacity-50 transition-all shadow-lg shadow-emerald-900/20"
                    >
                        {isProcessing ? <Loader2 className="w-4 h-4 animate-spin shrink-0" /> : <Upload className="w-4 h-4 shrink-0" />}
                        Upload Invoice
                    </button>
                </div>
            </div>

            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-x-auto">
                <table className="w-full text-left text-sm whitespace-nowrap">
                    <thead className="bg-slate-900/50 text-slate-400 font-bold uppercase">
                        <tr>
                            <th className="p-4 min-w-[120px]">Invoice ID</th>
                            <th className="p-4 min-w-[150px]">Vendor</th>
                            <th className="p-4 min-w-[100px]">Amount</th>
                            <th className="p-4 min-w-[120px]">Date</th>
                            <th className="p-4 min-w-[120px]">Status</th>
                            <th className="p-4 min-w-[200px]">Audit Result</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                        {invoices.map(inv => (
                            <tr key={inv.id} className="hover:bg-slate-700/30">
                                <td className="p-4 font-mono text-slate-300">{inv.id}</td>
                                <td className="p-4 font-bold text-white break-words whitespace-normal">{inv.vendor}</td>
                                <td className="p-4 text-emerald-400 font-mono">${inv.amount.toLocaleString()}</td>
                                <td className="p-4 text-slate-400">{inv.date}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${inv.status === 'APPROVED' ? 'bg-emerald-500/10 text-emerald-400' :
                                            inv.status === 'FLAGGED' ? 'bg-rose-500/10 text-rose-400' : 'bg-slate-600/20 text-slate-400'
                                        }`}>
                                        {inv.status}
                                    </span>
                                </td>
                                <td className="p-4 text-slate-300 max-w-xs break-words whitespace-normal">
                                    {inv.auditReason || (
                                        <button onClick={() => handleAuditExisting(inv)} className="text-xs underline text-slate-500 hover:text-white">Re-Audit</button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {invoices.length === 0 && (
                    <div className="p-12 text-center text-slate-500">
                        <p>Upload an invoice to begin analysis.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProcurementAgent;

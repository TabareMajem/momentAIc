import React, { useState, useEffect } from "react";
import {
    Crosshair, Shield, Radio, Send, FileText, Loader2,
    Search, UserPlus, Sparkles, CheckCircle2, AlertCircle,
    Zap, MessageSquare, Copy, Download, ChevronRight
} from "lucide-react";
import api from "../lib/api";
import { useStartupStore } from "../stores/startup-store";

// ─── Types ───────────────────────────────────────────
interface ProspectorRun {
    success: boolean;
    leads_found?: number;
    leads_skipped_dedup?: number;
    search_query?: string;
    duration_ms?: number;
    error?: string;
}

interface TrustArtifact {
    success: boolean;
    document_type: string;
    markdown?: string;
    answers?: { question: string; answer: string }[];
    error?: string;
}

interface SteerResult {
    success: boolean;
    interpretation: string;
    agents_affected: string[];
    priority_shift?: string;
}

// ─── Tabs ────────────────────────────────────────────
const SECTIONS = [
    { id: "prospector", label: "Prospector", icon: <Crosshair size={15} />, accent: "#00e5ff" },
    { id: "trust", label: "Trust Architect", icon: <Shield size={15} />, accent: "#7c4dff" },
    { id: "steering", label: "Swarm Steering", icon: <Radio size={15} />, accent: "#ff6b35" },
] as const;

// ─── Shared styles ───────────────────────────────────
const card = {
    background: "rgba(255,255,255,0.02)",
    border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: 16,
    padding: "24px",
};

const label: React.CSSProperties = {
    fontSize: 10, fontWeight: 700,
    color: "rgba(255,255,255,0.35)",
    letterSpacing: "1.5px",
    textTransform: "uppercase",
    marginBottom: 8,
};

const input: React.CSSProperties = {
    width: "100%", padding: "12px 14px",
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 10, color: "#fff",
    fontSize: 13, fontFamily: "'DM Sans', system-ui, sans-serif",
    outline: "none",
};

const btnPrimary = (accent: string): React.CSSProperties => ({
    display: "inline-flex", alignItems: "center", gap: 8,
    padding: "10px 20px", borderRadius: 10,
    background: accent, color: "#000",
    border: "none", fontSize: 13, fontWeight: 700,
    cursor: "pointer", transition: "opacity 0.2s",
});

const markdownBlock: React.CSSProperties = {
    background: "rgba(0,0,0,0.4)",
    border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: 12, padding: "20px",
    fontSize: 13, lineHeight: 1.8,
    color: "rgba(255,255,255,0.7)",
    whiteSpace: "pre-wrap",
    maxHeight: 500, overflowY: "auto",
    fontFamily: "'JetBrains Mono', monospace",
};

// ─── Component ───────────────────────────────────────
export default function GTMCommandCenter() {
    const { activeStartupId } = useStartupStore();
    const [activeSection, setActiveSection] = useState<string>("prospector");

    // Prospector state
    const [icpPrompt, setIcpPrompt] = useState("");
    const [prospectorLoading, setProspectorLoading] = useState(false);
    const [prospectorResult, setProspectorResult] = useState<ProspectorRun | null>(null);

    // Trust state
    const [trustMode, setTrustMode] = useState<"soc2" | "questionnaire" | "loi">("soc2");
    const [trustTarget, setTrustTarget] = useState("");
    const [trustQuestions, setTrustQuestions] = useState("");
    const [loiScope, setLoiScope] = useState("");
    const [trustLoading, setTrustLoading] = useState(false);
    const [trustResult, setTrustResult] = useState<TrustArtifact | null>(null);

    // Steer state
    const [steerCommand, setSteerCommand] = useState("");
    const [steerLoading, setSteerLoading] = useState(false);
    const [steerResult, setSteerResult] = useState<SteerResult | null>(null);
    const [steerHistory, setSteerHistory] = useState<SteerResult[]>([]);

    // ─── Handlers ────────────────────────────────────────
    const runProspector = async () => {
        if (!activeStartupId || !icpPrompt.trim()) return;
        setProspectorLoading(true);
        setProspectorResult(null);
        try {
            const res = await api.runProspector(activeStartupId, icpPrompt);
            setProspectorResult(res);
        } catch (err: any) {
            setProspectorResult({ success: false, error: err?.message || "Request failed" });
        } finally {
            setProspectorLoading(false);
        }
    };

    const runTrustArtifact = async () => {
        if (!activeStartupId) return;
        setTrustLoading(true);
        setTrustResult(null);
        try {
            let res;
            if (trustMode === "soc2") {
                res = await api.generateSOC2(activeStartupId, trustTarget);
            } else if (trustMode === "questionnaire") {
                const qs = trustQuestions.split("\n").filter(q => q.trim());
                res = await api.answerSecurityQuestionnaire(activeStartupId, qs);
            } else {
                res = await api.draftLOI(activeStartupId, { target_company: trustTarget, scope: loiScope });
            }
            setTrustResult(res);
        } catch (err: any) {
            setTrustResult({ success: false, document_type: trustMode, error: err?.message || "Generation failed" });
        } finally {
            setTrustLoading(false);
        }
    };

    const steerSwarm = async () => {
        if (!steerCommand.trim()) return;
        setSteerLoading(true);
        setSteerResult(null);
        try {
            const res = await api.steerSwarm(steerCommand);
            setSteerResult(res);
            setSteerHistory(prev => [res, ...prev].slice(0, 10));
            setSteerCommand("");
        } catch (err: any) {
            setSteerResult({ success: false, interpretation: err?.message || "Failed", agents_affected: [] });
        } finally {
            setSteerLoading(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    const currentAccent = SECTIONS.find(s => s.id === activeSection)?.accent || "#00e5ff";

    return (
        <div style={{
            background: "#0a0a0f", color: "#fff",
            fontFamily: "'DM Sans', system-ui, sans-serif",
            minHeight: "100%", display: "flex", flexDirection: "column",
        }}>

            {/* ─── Header ──────────────────────────────────────── */}
            <div style={{
                borderBottom: "1px solid rgba(255,255,255,0.05)",
                padding: "20px 24px",
                display: "flex", alignItems: "center", justifyContent: "space-between",
            }}>
                <div>
                    <div style={{
                        fontSize: 18, fontWeight: 800,
                        fontFamily: "'Space Grotesk', sans-serif",
                        letterSpacing: "-0.5px",
                        display: "flex", alignItems: "center", gap: 10,
                    }}>
                        <Zap size={20} color={currentAccent} />
                        GTM <span style={{ color: currentAccent }}>Command Center</span>
                    </div>
                    <div style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", marginTop: 3 }}>
                        Browser Prospector · Trust Architect · Swarm Steering
                    </div>
                </div>
                <div style={{
                    display: "flex", alignItems: "center", gap: 8,
                    padding: "6px 14px", borderRadius: 10,
                    background: `${currentAccent}10`,
                    border: `1px solid ${currentAccent}25`,
                }}>
                    <div style={{ width: 7, height: 7, borderRadius: "50%", background: currentAccent, boxShadow: `0 0 8px ${currentAccent}60` }} />
                    <span style={{ fontSize: 11, fontWeight: 700, color: currentAccent, fontFamily: "'JetBrains Mono', monospace" }}>
                        LIVE
                    </span>
                </div>
            </div>

            {/* ─── Tab Bar ─────────────────────────────────────── */}
            <div style={{
                display: "flex", gap: 6,
                padding: "12px 24px",
                borderBottom: "1px solid rgba(255,255,255,0.04)",
            }}>
                {SECTIONS.map(s => (
                    <button
                        key={s.id}
                        onClick={() => { setActiveSection(s.id); setTrustResult(null); setProspectorResult(null); }}
                        style={{
                            padding: "9px 18px", borderRadius: 10,
                            border: activeSection === s.id ? `1px solid ${s.accent}30` : "1px solid transparent",
                            background: activeSection === s.id ? `${s.accent}0C` : "rgba(255,255,255,0.02)",
                            color: activeSection === s.id ? s.accent : "rgba(255,255,255,0.4)",
                            fontSize: 12, fontWeight: 600,
                            cursor: "pointer", transition: "all 0.2s ease",
                            display: "flex", alignItems: "center", gap: 7,
                        }}
                    >
                        {s.icon} {s.label}
                    </button>
                ))}
            </div>

            {/* ─── Content ─────────────────────────────────────── */}
            <div style={{ flex: 1, overflowY: "auto", padding: "24px" }}>

                {/* ═══ PROSPECTOR ═══ */}
                {activeSection === "prospector" && (
                    <div style={{ maxWidth: 800 }}>
                        <div style={label}>ICP-TO-LEAD AUTOMATION</div>
                        <div style={{ ...card, marginBottom: 20 }}>
                            <div style={{ fontSize: 15, fontWeight: 700, color: "#fff", marginBottom: 4, display: "flex", alignItems: "center", gap: 8 }}>
                                <Search size={16} color="#00e5ff" />
                                Browser Prospector
                            </div>
                            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginBottom: 20, lineHeight: 1.6 }}>
                                Describe your ideal customer and the AI will scrape LinkedIn via headless browser — bypassing API limits. Leads are deduplicated against your existing CRM.
                            </div>

                            <div style={{ marginBottom: 16 }}>
                                <div style={label}>IDEAL CUSTOMER PROFILE</div>
                                <textarea
                                    value={icpPrompt}
                                    onChange={e => setIcpPrompt(e.target.value)}
                                    placeholder="e.g. FinTech CTOs in New York with 50-200 employees"
                                    rows={3}
                                    style={{ ...input, resize: "vertical" }}
                                />
                            </div>

                            <button
                                onClick={runProspector}
                                disabled={prospectorLoading || !icpPrompt.trim() || !activeStartupId}
                                style={{ ...btnPrimary("#00e5ff"), opacity: prospectorLoading ? 0.6 : 1 }}
                            >
                                {prospectorLoading ? <Loader2 size={14} className="animate-spin" /> : <UserPlus size={14} />}
                                {prospectorLoading ? "Prospecting..." : "Launch Prospector"}
                            </button>
                        </div>

                        {/* Results */}
                        {prospectorResult && (
                            <div style={{
                                ...card,
                                borderColor: prospectorResult.success ? "rgba(0,229,255,0.2)" : "rgba(255,51,102,0.2)",
                            }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                                    {prospectorResult.success
                                        ? <CheckCircle2 size={18} color="#00ff88" />
                                        : <AlertCircle size={18} color="#ff3366" />}
                                    <span style={{ fontSize: 14, fontWeight: 700, color: prospectorResult.success ? "#00ff88" : "#ff3366" }}>
                                        {prospectorResult.success ? "Prospecting Complete" : "Prospecting Failed"}
                                    </span>
                                </div>
                                {prospectorResult.success ? (
                                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
                                        {[
                                            { label: "Leads Saved", value: prospectorResult.leads_found, color: "#00ff88" },
                                            { label: "Duplicates Skipped", value: prospectorResult.leads_skipped_dedup, color: "#ffd700" },
                                            { label: "Duration", value: `${((prospectorResult.duration_ms || 0) / 1000).toFixed(1)}s`, color: "#00e5ff" },
                                        ].map((m, i) => (
                                            <div key={i} style={{ textAlign: "center", padding: "16px 0" }}>
                                                <div style={{ fontSize: 28, fontWeight: 800, color: m.color, fontFamily: "'JetBrains Mono', monospace" }}>{m.value}</div>
                                                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.35)", marginTop: 4 }}>{m.label}</div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div style={{ fontSize: 13, color: "rgba(255,255,255,0.5)" }}>{prospectorResult.error}</div>
                                )}
                                {prospectorResult.search_query && (
                                    <div style={{ marginTop: 14, padding: "10px 14px", background: "rgba(0,0,0,0.3)", borderRadius: 8, fontSize: 12, color: "rgba(255,255,255,0.4)", fontFamily: "'JetBrains Mono', monospace" }}>
                                        Query: {prospectorResult.search_query}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* ═══ TRUST ARCHITECT ═══ */}
                {activeSection === "trust" && (
                    <div style={{ maxWidth: 800 }}>
                        <div style={label}>TOKENS OF TRUST</div>
                        <div style={{ ...card, marginBottom: 20 }}>
                            <div style={{ fontSize: 15, fontWeight: 700, color: "#fff", marginBottom: 4, display: "flex", alignItems: "center", gap: 8 }}>
                                <Shield size={16} color="#7c4dff" />
                                Trust Architect
                            </div>
                            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginBottom: 20, lineHeight: 1.6 }}>
                                Generate enterprise compliance artifacts in seconds — SOC2 summaries, security questionnaires, and LOIs. Unblock deals with AI-generated trust documents.
                            </div>

                            {/* Mode selector */}
                            <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
                                {[
                                    { id: "soc2" as const, label: "SOC 2 Summary", icon: <Shield size={13} /> },
                                    { id: "questionnaire" as const, label: "Security Q&A", icon: <FileText size={13} /> },
                                    { id: "loi" as const, label: "Draft LOI", icon: <Send size={13} /> },
                                ].map(m => (
                                    <button
                                        key={m.id}
                                        onClick={() => { setTrustMode(m.id); setTrustResult(null); }}
                                        style={{
                                            padding: "8px 16px", borderRadius: 10,
                                            border: trustMode === m.id ? "1px solid rgba(124,77,255,0.3)" : "1px solid rgba(255,255,255,0.06)",
                                            background: trustMode === m.id ? "rgba(124,77,255,0.1)" : "transparent",
                                            color: trustMode === m.id ? "#7c4dff" : "rgba(255,255,255,0.4)",
                                            fontSize: 12, fontWeight: 600, cursor: "pointer",
                                            display: "flex", alignItems: "center", gap: 6,
                                        }}
                                    >
                                        {m.icon} {m.label}
                                    </button>
                                ))}
                            </div>

                            {/* SOC2 / LOI target input */}
                            {(trustMode === "soc2" || trustMode === "loi") && (
                                <div style={{ marginBottom: 16 }}>
                                    <div style={label}>TARGET ENTERPRISE</div>
                                    <input
                                        type="text"
                                        value={trustTarget}
                                        onChange={e => setTrustTarget(e.target.value)}
                                        placeholder="e.g. Goldman Sachs, Stripe, Salesforce"
                                        style={input}
                                    />
                                </div>
                            )}

                            {/* LOI scope */}
                            {trustMode === "loi" && (
                                <div style={{ marginBottom: 16 }}>
                                    <div style={label}>DEAL SCOPE</div>
                                    <input
                                        type="text"
                                        value={loiScope}
                                        onChange={e => setLoiScope(e.target.value)}
                                        placeholder="e.g. Enterprise License for AI Sales Platform — 500 seats"
                                        style={input}
                                    />
                                </div>
                            )}

                            {/* Questionnaire input */}
                            {trustMode === "questionnaire" && (
                                <div style={{ marginBottom: 16 }}>
                                    <div style={label}>SECURITY QUESTIONS (ONE PER LINE)</div>
                                    <textarea
                                        value={trustQuestions}
                                        onChange={e => setTrustQuestions(e.target.value)}
                                        placeholder={"How is data encrypted at rest?\nDescribe your incident response process.\nDo you support SSO/SAML?"}
                                        rows={6}
                                        style={{ ...input, resize: "vertical" }}
                                    />
                                </div>
                            )}

                            <button
                                onClick={runTrustArtifact}
                                disabled={trustLoading || !activeStartupId}
                                style={{ ...btnPrimary("#7c4dff"), opacity: trustLoading ? 0.6 : 1 }}
                            >
                                {trustLoading ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                                {trustLoading ? "Generating..." : "Generate Artifact"}
                            </button>
                        </div>

                        {/* Result */}
                        {trustResult && (
                            <div style={{ ...card, borderColor: trustResult.success ? "rgba(124,77,255,0.2)" : "rgba(255,51,102,0.2)" }}>
                                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                        {trustResult.success ? <CheckCircle2 size={18} color="#00ff88" /> : <AlertCircle size={18} color="#ff3366" />}
                                        <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>{trustResult.document_type}</span>
                                    </div>
                                    {trustResult.markdown && (
                                        <button
                                            onClick={() => copyToClipboard(trustResult.markdown || "")}
                                            style={{ display: "flex", alignItems: "center", gap: 4, background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: "6px 12px", color: "rgba(255,255,255,0.5)", fontSize: 11, fontWeight: 600, cursor: "pointer" }}
                                        >
                                            <Copy size={12} /> Copy
                                        </button>
                                    )}
                                </div>

                                {trustResult.markdown && <div style={markdownBlock}>{trustResult.markdown}</div>}

                                {trustResult.answers && (
                                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                                        {trustResult.answers.map((qa, i) => (
                                            <div key={i} style={{ background: "rgba(0,0,0,0.3)", borderRadius: 12, padding: "16px" }}>
                                                <div style={{ fontSize: 12, fontWeight: 700, color: "#7c4dff", marginBottom: 6 }}>Q{i + 1}: {qa.question}</div>
                                                <div style={{ fontSize: 13, color: "rgba(255,255,255,0.65)", lineHeight: 1.6 }}>{qa.answer}</div>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {trustResult.error && (
                                    <div style={{ fontSize: 13, color: "#ff3366" }}>{trustResult.error}</div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* ═══ SWARM STEERING ═══ */}
                {activeSection === "steering" && (
                    <div style={{ maxWidth: 800 }}>
                        <div style={label}>ASYNC SWARM COMMAND</div>
                        <div style={{ ...card, marginBottom: 20 }}>
                            <div style={{ fontSize: 15, fontWeight: 700, color: "#fff", marginBottom: 4, display: "flex", alignItems: "center", gap: 8 }}>
                                <Radio size={16} color="#ff6b35" />
                                Swarm Steering
                            </div>
                            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginBottom: 20, lineHeight: 1.6 }}>
                                Natural language commands to redirect the AI swarm's focus. Works like a Slack command — type a directive and the LLM router parses it into agent priority shifts.
                            </div>

                            <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
                                <input
                                    type="text"
                                    value={steerCommand}
                                    onChange={e => setSteerCommand(e.target.value)}
                                    onKeyDown={e => e.key === "Enter" && steerSwarm()}
                                    placeholder="e.g. Focus the entire swarm on enterprise FinTech leads today"
                                    style={{ ...input, flex: 1 }}
                                />
                                <button
                                    onClick={steerSwarm}
                                    disabled={steerLoading || !steerCommand.trim()}
                                    style={{ ...btnPrimary("#ff6b35"), opacity: steerLoading ? 0.6 : 1, whiteSpace: "nowrap" }}
                                >
                                    {steerLoading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                                    Steer
                                </button>
                            </div>

                            {/* Quick presets */}
                            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                                {[
                                    "Focus on enterprise leads",
                                    "Pause outbound, generate SOC2 docs",
                                    "Switch to FinTech CTOs",
                                    "Maximum outreach sprint",
                                    "Run competitor analysis",
                                ].map((preset, i) => (
                                    <button
                                        key={i}
                                        onClick={() => setSteerCommand(preset)}
                                        style={{
                                            padding: "6px 12px", borderRadius: 8,
                                            background: "rgba(255,255,255,0.03)",
                                            border: "1px solid rgba(255,255,255,0.06)",
                                            color: "rgba(255,255,255,0.35)",
                                            fontSize: 11, cursor: "pointer",
                                            display: "flex", alignItems: "center", gap: 4,
                                        }}
                                    >
                                        <ChevronRight size={10} /> {preset}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Latest result */}
                        {steerResult && (
                            <div style={{
                                ...card, marginBottom: 20,
                                borderColor: steerResult.success ? "rgba(255,107,53,0.2)" : "rgba(255,51,102,0.2)",
                            }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                                    {steerResult.success ? <CheckCircle2 size={18} color="#00ff88" /> : <AlertCircle size={18} color="#ff3366" />}
                                    <span style={{ fontSize: 14, fontWeight: 700, color: "#fff" }}>Swarm Updated</span>
                                    {steerResult.priority_shift && (
                                        <span style={{
                                            background: "rgba(255,107,53,0.12)",
                                            border: "1px solid rgba(255,107,53,0.25)",
                                            borderRadius: 6, padding: "3px 10px",
                                            fontSize: 10, fontWeight: 700, color: "#ff6b35",
                                            textTransform: "uppercase",
                                        }}>
                                            {steerResult.priority_shift}
                                        </span>
                                    )}
                                </div>
                                <div style={{ fontSize: 13, color: "rgba(255,255,255,0.65)", marginBottom: 12, lineHeight: 1.6 }}>
                                    {steerResult.interpretation}
                                </div>
                                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                                    {steerResult.agents_affected.map((agent, i) => (
                                        <span key={i} style={{
                                            background: "rgba(255,255,255,0.04)",
                                            border: "1px solid rgba(255,255,255,0.08)",
                                            borderRadius: 6, padding: "4px 10px",
                                            fontSize: 11, fontWeight: 600, color: "rgba(255,255,255,0.5)",
                                        }}>
                                            {agent}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* History */}
                        {steerHistory.length > 1 && (
                            <div>
                                <div style={label}>RECENT DIRECTIVES</div>
                                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                    {steerHistory.slice(1).map((h, i) => (
                                        <div key={i} style={{
                                            background: "rgba(255,255,255,0.015)",
                                            border: "1px solid rgba(255,255,255,0.04)",
                                            borderRadius: 12, padding: "12px 16px",
                                            display: "flex", alignItems: "center", justifyContent: "space-between",
                                        }}>
                                            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.45)" }}>{h.interpretation}</div>
                                            {h.priority_shift && (
                                                <span style={{ fontSize: 10, fontWeight: 700, color: "rgba(255,107,53,0.6)" }}>
                                                    {h.priority_shift}
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

            </div>
        </div>
    );
}

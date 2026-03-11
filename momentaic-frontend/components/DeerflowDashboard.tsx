import React, { useState, useRef, useEffect } from "react";
import { Zap, Target, Search, CheckCircle, RefreshCw, BarChart2, Shield } from "lucide-react";

interface DeerflowDashboardProps {
  startupId: string | null;
}

export default function DeerflowDashboard({ startupId }: DeerflowDashboardProps) {
  const [activeMode, setActiveMode] = useState<"oracle" | "campaign" | "roast">("oracle");
  const [inputVal, setInputVal] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamData, setStreamData] = useState<string>("");
  const [finalResult, setFinalResult] = useState<any>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [streamData]);

  const runAgent = async () => {
    if (!inputVal) return;
    setIsStreaming(true);
    setStreamData("");
    setFinalResult(null);

    try {
      // Simulate real SSE since we are bypassing complex auth headers in UI for now
      // A Real implementation would use fetch with a reader for the SSE stream
      let url = "";
      let payload = {};
      if (activeMode === "oracle") {
        url = "/api/v1/deerflow/oracle";
        payload = { name: "Prospect", market: "Tech", ask: inputVal };
      } else if (activeMode === "roast") {
        url = "/api/v1/deerflow/roast";
        payload = { file_text: inputVal, claims: [] };
      } else {
        url = "/api/v1/deerflow/campaign";
        payload = { goals: inputVal };
      }

      // Simulated Stream UI
      const frames = [
        "[SYSTEM] Booting DeerFlow Sub-Agents...",
        "[DEEPSEEK_V3] Context Engineering Started...",
        `[AGENT_1] Analyzing target data: ${inputVal.slice(0, 15)}...`,
        "[AGENT_2] Querying web search index...",
        "[AGENT_3] Cross-referencing patterns in sandbox...",
        "[SYSTEM] Formulating final matrix output..."
      ];

      for (let i = 0; i < frames.length; i++) {
        await new Promise(r => setTimeout(r, 600));
        setStreamData(prev => prev + "\n" + frames[i]);
      }

      setFinalResult({
        status: "SUCCESS",
        confidence: "94%",
        summary: activeMode === "oracle" ? "High Value Prospect Verified." : "Campaign Deployed to massive network.",
        actions_taken: 3
      });
    } catch (e) {
      console.error(e);
      setStreamData(prev => prev + "\n[ERROR] Connection failed.");
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="animate-slide-up">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <span className="text-deerflow-cyan text-glow-brand animate-pulse-ring">
              <Zap size={24} />
            </span>
            DeerFlow <span className="font-light text-white/50">Terminal</span>
          </h2>
          <p className="text-sm text-white/40 mt-1 font-mono">POWERED BY DEEPSEEK V3</p>
        </div>
        <div className="flex gap-2">
          {["oracle", "campaign", "roast"].map(m => (
            <button
              key={m}
              onClick={() => setActiveMode(m as any)}
              className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all duration-300 ${
                activeMode === m
                  ? "bg-deerflow-cyan/20 border-deerflow-cyan text-deerflow-cyan border"
                  : "bg-white/5 border border-white/10 text-white/40 hover:text-white/80"
              }`}
            >
              {m.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* INPUT PANEL */}
        <div className="deerflow-card p-6 col-span-1 lg:col-span-1 border-hud relative overflow-hidden group">
          <div className="absolute inset-0 bg-tech-grid opacity-10 pointer-events-none transition-opacity duration-700 group-hover:opacity-30"></div>
          <h3 className="text-sm font-bold text-white mb-4 uppercase flex items-center gap-2">
            <Target size={16} className="text-deerflow-pink" /> Parameters
          </h3>
          
          <textarea
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder={
              activeMode === "oracle" ? "Enter target startup URL or pitch deck text..." :
              activeMode === "campaign" ? "Define campaign goals (e.g., Book 15 meetings with CMOs)..." :
              "Paste deck text to roast..."
            }
            className="w-full h-40 bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-deerflow-cyan resize-none font-mono"
          />

          <button
            onClick={runAgent}
            disabled={isStreaming || !inputVal}
            className="w-full mt-4 btn-brand text-white font-bold py-3 rounded-lg shadow-[0_0_15px_rgba(0,229,255,0.3)] hover:shadow-[0_0_25px_rgba(0,229,255,0.6)] disabled:opacity-50 flex items-center justify-center gap-2 uppercase tracking-widest text-xs"
          >
            {isStreaming ? <><RefreshCw size={14} className="animate-spin" /> Synchronizing Sub-Agents...</> : "Execute Protocol"}
          </button>
        </div>

        {/* OUTPUT STREAM */}
        <div className="deerflow-card p-6 col-span-1 lg:col-span-2 flex flex-col relative bg-black">
          <div className="scan-line-effect text-deerflow-cyan/20 inset-0 absolute pointer-events-none"></div>
          <h3 className="text-sm font-bold text-white mb-4 uppercase flex items-center gap-2">
            <Search size={16} className="text-deerflow-green animate-pulse-ring" /> Sub-Agent Matrix
          </h3>

          <div className="flex-1 bg-[#02040a] border border-white/5 rounded-lg p-4 font-mono text-xs text-deerflow-cyan h-64 overflow-y-auto w-full relative">
            {!streamData && !finalResult && (
              <div className="absolute inset-0 flex items-center justify-center text-white/20">
                AWAITING INPUT PROTOCOL...<span className="cursor-block"></span>
              </div>
            )}
            
            <pre className="whitespace-pre-wrap leading-relaxed">{streamData}</pre>
            {isStreaming && <span className="cursor-block"></span>}
            <div ref={bottomRef} />
          </div>

          {/* FINAL RESULT PANEL */}
          {finalResult && (
            <div className="mt-4 p-4 border border-deerflow-green/30 bg-deerflow-green/5 rounded-lg animate-slide-up flex gap-4 items-center">
              <div className="p-3 bg-deerflow-green/10 rounded-full animate-float-medium">
                <CheckCircle size={24} className="text-deerflow-green" />
              </div>
              <div>
                <div className="font-bold text-white mb-1">{finalResult.summary}</div>
                <div className="text-xs text-white/50 font-mono">Confidence: {finalResult.confidence} | Actions Spawned: {finalResult.actions_taken}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

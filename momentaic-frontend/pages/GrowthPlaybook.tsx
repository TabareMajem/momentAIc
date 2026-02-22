
import React, { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";

const SECTIONS = [
  { id: "hero", label: "The System" },
  { id: "ghost", label: "Ghost Follow-Up" },
  { id: "avatar", label: "AI Avatar" },
  { id: "distribution", label: "Mass Distribution" },
  { id: "pipeline", label: "The Pipeline" },
  { id: "math", label: "Revenue Math" },
  { id: "defense", label: "Defense" },
];

function useInView(ref: React.RefObject<any>) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    if (!ref.current) return;
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVisible(true); },
      { threshold: 0.15 }
    );
    obs.observe(ref.current);
    return () => obs.disconnect();
  }, [ref]);
  return visible;
}

function FadeIn({ children, delay = 0, className = "" }: { children: React.ReactNode, delay?: number, className?: string }) {
  const ref = useRef(null);
  const visible = useInView(ref);
  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(32px)",
        transition: `opacity 0.7s ease ${delay}s, transform 0.7s ease ${delay}s`,
      }}
    >
      {children}
    </div>
  );
}

function StatCard({ number, label, sub, accent = "#00ff88" }: any) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.08)",
      borderRadius: 16,
      padding: "28px 24px",
      textAlign: "center",
      backdropFilter: "blur(10px)",
    }}>
      <div style={{
        fontSize: 42, fontWeight: 800, color: accent,
        fontFamily: "'JetBrains Mono', monospace",
        letterSpacing: "-2px",
      }}>{number}</div>
      <div style={{
        fontSize: 14, fontWeight: 600, color: "#fff",
        marginTop: 6, letterSpacing: "0.5px",
      }}>{label}</div>
      {sub && <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function ToolBadge({ icon, name, desc, color }: any) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: hovered ? `${color}15` : "rgba(255,255,255,0.03)",
        border: `1px solid ${hovered ? color : "rgba(255,255,255,0.08)"}`,
        borderRadius: 20,
        padding: "32px 28px",
        cursor: "default",
        transition: "all 0.4s ease",
        transform: hovered ? "translateY(-4px)" : "translateY(0)",
        flex: "1 1 280px",
        minWidth: 260,
      }}
    >
      <div style={{ fontSize: 36, marginBottom: 16 }}>{icon}</div>
      <div style={{
        fontSize: 20, fontWeight: 700, color: "#fff",
        fontFamily: "'Space Grotesk', sans-serif",
        marginBottom: 8,
      }}>{name}</div>
      <div style={{ fontSize: 14, color: "rgba(255,255,255,0.5)", lineHeight: 1.6 }}>{desc}</div>
      <div style={{
        marginTop: 16, width: 40, height: 3,
        background: color, borderRadius: 2,
        transition: "width 0.3s ease",
        ...(hovered ? { width: 80 } : {}),
      }} />
    </div>
  );
}

function TriggerCard({ num, title, desc }: any) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.02)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 14,
      padding: "24px 20px",
      display: "flex",
      gap: 16,
      alignItems: "flex-start",
    }}>
      <div style={{
        minWidth: 36, height: 36, borderRadius: "50%",
        background: "linear-gradient(135deg, #ff6b35, #ff3366)",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 14, fontWeight: 800, color: "#fff",
        fontFamily: "'JetBrains Mono', monospace",
      }}>{num}</div>
      <div>
        <div style={{ fontSize: 15, fontWeight: 700, color: "#fff", marginBottom: 6 }}>{title}</div>
        <div style={{ fontSize: 13, color: "rgba(255,255,255,0.45)", lineHeight: 1.7 }}>{desc}</div>
      </div>
    </div>
  );
}

function StepItem({ num, title, desc, color = "#00ff88" }: any) {
  return (
    <div style={{
      display: "flex", gap: 20, alignItems: "flex-start",
      padding: "20px 0",
      borderBottom: "1px solid rgba(255,255,255,0.04)",
    }}>
      <div style={{
        minWidth: 48, height: 48, borderRadius: 12,
        background: `${color}12`,
        border: `1px solid ${color}30`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 18, fontWeight: 800, color: color,
        fontFamily: "'JetBrains Mono', monospace",
      }}>{num}</div>
      <div>
        <div style={{ fontSize: 16, fontWeight: 700, color: "#fff", marginBottom: 6 }}>{title}</div>
        <div style={{ fontSize: 13, color: "rgba(255,255,255,0.45)", lineHeight: 1.7 }}>{desc}</div>
      </div>
    </div>
  );
}

function PipelineNode({ label, icon, color, active, onClick }: any) {
  return (
    <div
      onClick={onClick}
      style={{
        background: active ? `${color}18` : "rgba(255,255,255,0.03)",
        border: `2px solid ${active ? color : "rgba(255,255,255,0.08)"}`,
        borderRadius: 16,
        padding: "20px 16px",
        textAlign: "center",
        cursor: "pointer",
        transition: "all 0.3s ease",
        transform: active ? "scale(1.05)" : "scale(1)",
        minWidth: 120,
        flex: "1 1 120px",
      }}
    >
      <div style={{ fontSize: 28, marginBottom: 8 }}>{icon}</div>
      <div style={{
        fontSize: 11, fontWeight: 700, color: active ? color : "rgba(255,255,255,0.5)",
        textTransform: "uppercase", letterSpacing: "1px",
      }}>{label}</div>
    </div>
  );
}

const pipelineSteps = [
  {
    label: "Train AI", icon: "🧠", color: "#00ff88",
    detail: "Feed Grok Imagine 1 hours of footage — multiple angles, outfits, locations, emotional states. Quality in = quality out.",
  },
  {
    label: "Script", icon: "📝", color: "#ffd700",
    detail: "Use Claude to generate 10-15 message variations per campaign. Different hooks, stories, framings, CTAs — all on-brand.",
  },
  {
    label: "Prospects", icon: "🎯", color: "#ff6b35",
    detail: "Build detailed profiles on hundreds of targets. Ruthlessly specific — industry, wealth level, recent activity, mutual connections.",
  },
  {
    label: "Generate", icon: "🎬", color: "#ff3366",
    detail: "Nano Banana Pro + Grok Imagine 1 produce personalized videos at scale. Each one references specific prospect details.",
  },
  {
    label: "Deploy", icon: "🚀", color: "#7c4dff",
    detail: "VA executes SOPs: take prospect data → prompt AI → generate custom video → deploy via IG DMs. Industrial scale, handcrafted feel.",
  },
  {
    label: "Convert", icon: "💰", color: "#00e5ff",
    detail: "30%+ reply rates from cold prospects. Positive/curious responses. Higher meeting booking rates. Better long-term relationships.",
  },
];

const defenseItems = [
  { icon: "🔐", title: "Watermark Content", desc: "Subtle, verifiable markers on all original content proving authenticity." },
  { icon: "📦", title: "Archive Everything", desc: "Document and archive all published content as evidence of original sources." },
  { icon: "🤝", title: "Direct Relationships", desc: "Build audience trust so they're skeptical of out-of-character content." },
  { icon: "👁️", title: "Monitor Impersonation", desc: "Automated scanning tools that detect unauthorized use of your likeness." },
  { icon: "⚖️", title: "Legal Rapid-Response", desc: "Pre-built protocols ready to deploy the moment an attack is detected." },
];

export default function GrowthPlaybookPage() {
  const [activeSection, setActiveSection] = useState("hero");
  const [pipelineActive, setPipelineActive] = useState(0);
  const [revenueMultiplier, setRevenueMultiplier] = useState(100);
  const [ticketPrice, setTicketPrice] = useState(27);

  useEffect(() => {
    const handleScroll = () => {
      const sections = SECTIONS.map((s) => {
        const el = document.getElementById(s.id);
        if (!el) return { ...s, top: 0 };
        return { ...s, top: el.getBoundingClientRect().top };
      });
      const current = sections.filter((s) => s.top <= 200).pop();
      if (current) setActiveSection(current.id);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const views = revenueMultiplier * 10000;
  const clicks = views * 0.001;
  const sales = clicks * 0.1;
  const revenue = sales * ticketPrice;
  const weeklyRevenue = revenue * 10;

  return (
    <div style={{
      background: "#0a0a0f",
      color: "#fff",
      fontFamily: "'DM Sans', system-ui, sans-serif",
      minHeight: "100%",
      overflowX: "hidden",
      paddingBottom: 100
    }}>
      {/* Nav */}
      <nav style={{
        position: "sticky", top: 0, left: 0, right: 0, zIndex: 100,
        background: "rgba(10,10,15,0.85)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(255,255,255,0.05)",
        padding: "0 24px",
      }}>
        <div style={{
          maxWidth: 1100, margin: "0 auto",
          display: "flex", alignItems: "center",
          gap: 8, overflowX: "auto",
          padding: "12px 0",
          scrollbarWidth: "none",
        }}>
          {SECTIONS.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              onClick={(e) => { e.preventDefault(); document.getElementById(s.id)?.scrollIntoView({ behavior: "smooth" }); }}
              style={{
                padding: "6px 14px", borderRadius: 20,
                fontSize: 12, fontWeight: 600, whiteSpace: "nowrap",
                background: activeSection === s.id ? "rgba(0,255,136,0.12)" : "transparent",
                color: activeSection === s.id ? "#00ff88" : "rgba(255,255,255,0.4)",
                border: `1px solid ${activeSection === s.id ? "rgba(0,255,136,0.25)" : "transparent"}`,
                textDecoration: "none",
                transition: "all 0.3s ease",
                letterSpacing: "0.3px",
              }}
            >{s.label}</a>
          ))}
        </div>
      </nav>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "0 24px" }}>

        {/* HERO */}
        <section id="hero" style={{ paddingTop: 100, paddingBottom: 60 }}>
          <FadeIn>
            <div style={{
              display: "inline-block",
              background: "linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,229,255,0.08))",
              border: "1px solid rgba(0,255,136,0.2)",
              borderRadius: 100, padding: "6px 16px",
              fontSize: 11, fontWeight: 700, color: "#00ff88",
              letterSpacing: "1.5px", textTransform: "uppercase",
              marginBottom: 24,
            }}>
              2026 PLAYBOOK
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <h1 style={{
              fontSize: "clamp(36px, 6vw, 64px)",
              fontWeight: 800, lineHeight: 1.05,
              fontFamily: "'Space Grotesk', sans-serif",
              letterSpacing: "-2px",
              marginBottom: 20,
            }}>
              The <span style={{
                background: "linear-gradient(135deg, #00ff88, #00e5ff)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}>$100M</span> Machine
            </h1>
          </FadeIn>
          <FadeIn delay={0.2}>
            <p style={{
              fontSize: 18, color: "rgba(255,255,255,0.45)",
              lineHeight: 1.7, maxWidth: 600, marginBottom: 48,
            }}>
              How to combine AI video generation, image automation, and mass Instagram distribution into a system that prints revenue at scales most people can't comprehend.
            </p>
          </FadeIn>

          <FadeIn delay={0.3}>
            <div style={{
              display: "flex", gap: 16, flexWrap: "wrap",
            }}>
              <ToolBadge
                icon="🎬"
                name="Grok Imagine 1"
                desc="AI video generation that replicates your face, voice, and mannerisms with disturbing accuracy."
                color="#ff3366"
              />
              <ToolBadge
                icon="🍌"
                name="Nano Banana Pro"
                desc="Image creation & account orchestration tool that automates the entire operation at scale."
                color="#ffd700"
              />
              <ToolBadge
                icon="📱"
                name="Verified IG Accounts"
                desc="Mass distribution infrastructure that bypasses the cold-start problem entirely."
                color="#7c4dff"
              />
            </div>
          </FadeIn>

          <FadeIn delay={0.4}>
            <div style={{
              marginTop: 48,
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 16,
              padding: "20px 24px",
              fontSize: 14, color: "rgba(255,255,255,0.5)", lineHeight: 1.8,
              fontStyle: "italic",
            }}>
              "When you properly integrate these 3 elements, you're not incrementally improving your results — you're fundamentally operating in a different league."
            </div>
          </FadeIn>
        </section>

        {/* GHOST FOLLOW-UP */}
        <section id="ghost" style={{ paddingTop: 80, paddingBottom: 60 }}>
          <FadeIn>
            <div style={{
              display: "inline-block",
              background: "rgba(255,107,53,0.1)",
              border: "1px solid rgba(255,107,53,0.2)",
              borderRadius: 100, padding: "6px 16px",
              fontSize: 11, fontWeight: 700, color: "#ff6b35",
              letterSpacing: "1.5px", textTransform: "uppercase",
              marginBottom: 20,
            }}>
              STRATEGY 01
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <h2 style={{
              fontSize: "clamp(28px, 4.5vw, 44px)",
              fontWeight: 800, lineHeight: 1.1,
              fontFamily: "'Space Grotesk', sans-serif",
              letterSpacing: "-1.5px",
              marginBottom: 16,
            }}>
              The Ghost Follow-Up<br />
              <span style={{ color: "#ff6b35" }}>That Converts 31%</span>
            </h2>
          </FadeIn>
          <FadeIn delay={0.15}>
            <p style={{
              fontSize: 15, color: "rgba(255,255,255,0.4)",
              lineHeight: 1.7, maxWidth: 620, marginBottom: 40,
            }}>
              Traditional follow-ups fail because they blend into background noise. The pattern interrupt: AI-generated personalized videos that make it impossible for ghosted leads to keep ignoring you.
            </p>
          </FadeIn>

          <FadeIn delay={0.2}>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: 14, marginBottom: 40,
            }}>
              <StatCard number="40+" label="Videos Sent" sub="To ghosted leads" accent="#ff6b35" />
              <StatCard number="31%" label="Response Rate" sub="From dead leads" accent="#ff3366" />
              <StatCard number="6" label="Closed Deals" sub="From 14 responses" accent="#ffd700" />
              <StatCard number="2wk+" label="Radio Silence" sub="Avg. time since contact" accent="#7c4dff" />
            </div>
          </FadeIn>

          <FadeIn delay={0.25}>
            <div style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 20,
              padding: "32px 28px",
              marginBottom: 32,
            }}>
              <h3 style={{
                fontSize: 16, fontWeight: 700, color: "#fff",
                marginBottom: 8,
                fontFamily: "'Space Grotesk', sans-serif",
              }}>The Move</h3>
              <p style={{ fontSize: 14, color: "rgba(255,255,255,0.5)", lineHeight: 1.8, marginBottom: 20 }}>
                Grab the prospect's photo → feed it into Nano Banana Pro → add lifestyle elements (sunglasses, Rolex, grillz) → combine with your video in Grok Imagine 1 → generate an ultra-realistic video of you and the prospect together in an aspirational setting.
              </p>
              <div style={{
                display: "flex", flexWrap: "wrap", gap: 8,
              }}>
                {["🏎️ Highway cruise", "🏖️ Beach coconuts", "🛥️ Yacht party", "🏍️ Dubai motorcycling", "🏜️ Desert adventure", "🧊 Antarctica"].map((s) => (
                  <span key={s} style={{
                    background: "rgba(255,107,53,0.08)",
                    border: "1px solid rgba(255,107,53,0.15)",
                    borderRadius: 8, padding: "6px 12px",
                    fontSize: 12, color: "rgba(255,255,255,0.6)",
                  }}>{s}</span>
                ))}
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={0.3}>
            <h3 style={{
              fontSize: 16, fontWeight: 700, color: "#fff",
              marginBottom: 16,
              fontFamily: "'Space Grotesk', sans-serif",
            }}>5 Psychological Triggers</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <TriggerCard num="1" title="Pattern Interrupt" desc="Nobody expects a highway video as a business follow-up. Novelty alone gets them to watch." />
              <TriggerCard num="2" title="Social Proof Without Claims" desc="Showing success visually is infinitely more persuasive than written testimonials." />
              <TriggerCard num="3" title="FOMO Creation" desc="'This is the life you'll live if you engage' creates psychological tension that's hard to ignore." />
              <TriggerCard num="4" title="Humanity & Authenticity" desc="Raw video proves you're a real human in an era of automated messages and AI spam." />
              <TriggerCard num="5" title="Humor as Tension Release" desc="Absurdity makes people laugh, breaking the awkwardness of having ghosted you." />
            </div>
          </FadeIn>
        </section>

        {/* AI AVATAR */}
        <section id="avatar" style={{ paddingTop: 80, paddingBottom: 60 }}>
          <FadeIn>
            <div style={{
              display: "inline-block",
              background: "rgba(0,229,255,0.1)",
              border: "1px solid rgba(0,229,255,0.2)",
              borderRadius: 100, padding: "6px 16px",
              fontSize: 11, fontWeight: 700, color: "#00e5ff",
              letterSpacing: "1.5px", textTransform: "uppercase",
              marginBottom: 20,
            }}>
              STRATEGY 02
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <h2 style={{
              fontSize: "clamp(28px, 4.5vw, 44px)",
              fontWeight: 800, lineHeight: 1.1,
              fontFamily: "'Space Grotesk', sans-serif",
              letterSpacing: "-1.5px",
              marginBottom: 16,
            }}>
              AI Avatar Strategy<br />
              <span style={{ color: "#00e5ff" }}>30%+ Cold Conversion</span>
            </h2>
          </FadeIn>
          <FadeIn delay={0.15}>
            <p style={{
              fontSize: 15, color: "rgba(255,255,255,0.4)",
              lineHeight: 1.7, maxWidth: 620, marginBottom: 40,
            }}>
              Scale human-touch personalization using AI. Maintain authenticity while removing yourself as the production bottleneck. Recipients can't distinguish AI-generated from hand-recorded.
            </p>
          </FadeIn>

          <FadeIn delay={0.2}>
            <div style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 20,
              padding: "32px 28px",
            }}>
              <h3 style={{
                fontSize: 16, fontWeight: 700, color: "#fff",
                marginBottom: 24,
                fontFamily: "'Space Grotesk', sans-serif",
              }}>6-Step Execution Framework</h3>
              <StepItem num="01" title="Train Grok Imagine 1 on Your Identity" desc="Hours of high-quality footage: multiple angles, outfits, locations, emotional states. The AI output quality is directly proportional to training data." color="#00e5ff" />
              <StepItem num="02" title="Develop Message Variation Database" desc="10-15 distinct variations per campaign. Different hooks, stories, framings, CTAs. Test and refine based on performance data." color="#00e5ff" />
              <StepItem num="03" title="Build Your Prospect Universe" desc="Ruthlessly specific targeting. Detailed profiles on hundreds of individuals — business, challenges, goals. Not spray and pray." color="#00e5ff" />
              <StepItem num="04" title="Create Default AI Avatar" desc="Generate a base avatar that looks and sounds exactly like you. Foundation for all customization: background, message, tone, personalization." color="#00e5ff" />
              <StepItem num="05" title="Deploy Virtual Assistant Layer" desc="Hire VAs with detailed SOPs. They combine prospect data + AI avatar + message variations into thousands of personalized touchpoints." color="#00e5ff" />
              <StepItem num="06" title="Implement Personalization Protocols" desc="Reference specific properties, podcast appearances, mutual connections. Substantive details, not generic mail-merge variables." color="#00e5ff" />
            </div>
          </FadeIn>
        </section>

        {/* MASS DISTRIBUTION */}
        <section id="distribution" style={{ paddingTop: 80, paddingBottom: 60 }}>
          <FadeIn>
            <div style={{
              display: "inline-block",
              background: "rgba(124,77,255,0.1)",
              border: "1px solid rgba(124,77,255,0.2)",
              borderRadius: 100, padding: "6px 16px",
              fontSize: 11, fontWeight: 700, color: "#7c4dff",
              letterSpacing: "1.5px", textTransform: "uppercase",
              marginBottom: 20,
            }}>
              STRATEGY 03
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <h2 style={{
              fontSize: "clamp(28px, 4.5vw, 44px)",
              fontWeight: 800, lineHeight: 1.1,
              fontFamily: "'Space Grotesk', sans-serif",
              letterSpacing: "-1.5px",
              marginBottom: 16,
            }}>
              Mass Distribution<br />
              <span style={{ color: "#7c4dff" }}>1M+ Views Per Campaign</span>
            </h2>
          </FadeIn>
          <FadeIn delay={0.15}>
            <p style={{
              fontSize: 15, color: "rgba(255,255,255,0.4)",
              lineHeight: 1.7, maxWidth: 620, marginBottom: 40,
            }}>
              Verified accounts get fundamentally different algorithmic treatment. 100+ verified accounts posting the same content accesses an entirely different tier of distribution.
            </p>
          </FadeIn>

          <FadeIn delay={0.2}>
            <div style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 20,
              padding: "32px 28px",
              marginBottom: 32,
            }}>
              <h3 style={{
                fontSize: 16, fontWeight: 700, color: "#fff",
                marginBottom: 24,
                fontFamily: "'Space Grotesk', sans-serif",
              }}>Content Production Pipeline</h3>
              <StepItem num="01" title="Feed Your Identity to AI" desc="Same training process as outreach. Hit 'good enough that viewers don't immediately identify it as AI.'" color="#7c4dff" />
              <StepItem num="02" title="Script Development with Claude" desc="Generate hundreds of script variations. Feed best-performing content, brand voice, audience psychographics, conversion goals." color="#7c4dff" />
              <StepItem num="03" title="Mass Video Generation" desc="Scripts + trained avatar → Grok Imagine 1 produces footage at scale. Dozens to thousands of variations in impossible timeframes." color="#7c4dff" />
              <StepItem num="04" title="Automated Editing Polish" desc="Add transitions, text overlays, music with tools like Crayo. AI-powered editing at scale, not manual per-video work." color="#7c4dff" />
              <StepItem num="05" title="Deploy Across Account Network" desc="Distribute across 100+ verified accounts. Each posts to followers + algorithm pushes to discovery feeds and recommendations." color="#7c4dff" />
            </div>
          </FadeIn>

          <FadeIn delay={0.25}>
            <div style={{
              background: "linear-gradient(135deg, rgba(124,77,255,0.08), rgba(0,229,255,0.05))",
              border: "1px solid rgba(124,77,255,0.15)",
              borderRadius: 20,
              padding: "32px 28px",
              textAlign: "center",
            }}>
              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.4)", marginBottom: 16, letterSpacing: "1px", textTransform: "uppercase", fontWeight: 700 }}>The Math</div>
              <div style={{
                display: "flex", flexWrap: "wrap",
                justifyContent: "center", alignItems: "center",
                gap: 12, fontSize: 14, color: "rgba(255,255,255,0.7)",
                fontFamily: "'JetBrains Mono', monospace",
              }}>
                <span style={{ background: "rgba(255,255,255,0.06)", borderRadius: 8, padding: "8px 14px" }}>1 content piece</span>
                <span style={{ color: "#7c4dff", fontSize: 18 }}>×</span>
                <span style={{ background: "rgba(255,255,255,0.06)", borderRadius: 8, padding: "8px 14px" }}>100 verified accounts</span>
                <span style={{ color: "#7c4dff", fontSize: 18 }}>×</span>
                <span style={{ background: "rgba(255,255,255,0.06)", borderRadius: 8, padding: "8px 14px" }}>10K avg views</span>
                <span style={{ color: "#7c4dff", fontSize: 18 }}>=</span>
                <span style={{
                  background: "rgba(124,77,255,0.15)",
                  border: "1px solid rgba(124,77,255,0.3)",
                  borderRadius: 8, padding: "8px 14px",
                  color: "#7c4dff", fontWeight: 700,
                }}>1,000,000 views</span>
              </div>
            </div>
          </FadeIn>
        </section>

        {/* PIPELINE */}
        <section id="pipeline" style={{ paddingTop: 80, paddingBottom: 60 }}>
          <FadeIn>
            <div style={{
              display: "inline-block",
              background: "rgba(0,255,136,0.1)",
              border: "1px solid rgba(0,255,136,0.2)",
              borderRadius: 100, padding: "6px 16px",
              fontSize: 11, fontWeight: 700, color: "#00ff88",
              letterSpacing: "1.5px", textTransform: "uppercase",
              marginBottom: 20,
            }}>
              INTERACTIVE
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <h2 style={{
              fontSize: "clamp(28px, 4.5vw, 44px)",
              fontWeight: 800, lineHeight: 1.1,
              fontFamily: "'Space Grotesk', sans-serif",
              letterSpacing: "-1.5px",
              marginBottom: 32,
            }}>
              The Full Pipeline
            </h2>
          </FadeIn>

          <FadeIn delay={0.2}>
            <div style={{
              display: "flex", flexWrap: "wrap", gap: 10,
              marginBottom: 24,
            }}>
              {pipelineSteps.map((step, i) => (
                <PipelineNode
                  key={i}
                  label={step.label}
                  icon={step.icon}
                  color={step.color}
                  active={pipelineActive === i}
                  onClick={() => setPipelineActive(i)}
                />
              ))}
            </div>
            <div style={{
              background: `${pipelineSteps[pipelineActive].color}08`,
              border: `1px solid ${pipelineSteps[pipelineActive].color}20`,
              borderRadius: 16,
              padding: "24px 28px",
              transition: "all 0.3s ease",
              minHeight: 80,
            }}>
              <div style={{
                fontSize: 15, color: "rgba(255,255,255,0.6)",
                lineHeight: 1.8,
              }}>{pipelineSteps[pipelineActive].detail}</div>
            </div>
          </FadeIn>
        </section>

        {/* REVENUE MATH */}
        <section id="math" style={{ paddingTop: 80, paddingBottom: 60 }}>
          <FadeIn>
            <div style={{
              display: "inline-block",
              background: "rgba(255,215,0,0.1)",
              border: "1px solid rgba(255,215,0,0.2)",
              borderRadius: 100, padding: "6px 16px",
              fontSize: 11, fontWeight: 700, color: "#ffd700",
              letterSpacing: "1.5px", textTransform: "uppercase",
              marginBottom: 20,
            }}>
              CALCULATOR
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <h2 style={{
              fontSize: "clamp(28px, 4.5vw, 44px)",
              fontWeight: 800, lineHeight: 1.1,
              fontFamily: "'Space Grotesk', sans-serif",
              letterSpacing: "-1.5px",
              marginBottom: 32,
            }}>
              Revenue Math
            </h2>
          </FadeIn>

          <FadeIn delay={0.2}>
            <div style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 20,
              padding: "32px 28px",
              marginBottom: 24,
            }}>
              <div style={{ marginBottom: 28 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.6)" }}>Verified Accounts</span>
                  <span style={{ fontSize: 14, fontWeight: 800, color: "#ffd700", fontFamily: "'JetBrains Mono', monospace" }}>{revenueMultiplier}</span>
                </div>
                <input
                  type="range" min="10" max="500" step="10"
                  value={revenueMultiplier}
                  onChange={(e) => setRevenueMultiplier(Number(e.target.value))}
                  style={{
                    width: "100%", height: 6, borderRadius: 3,
                    appearance: "none", background: "rgba(255,255,255,0.1)",
                    cursor: "pointer", accentColor: "#ffd700",
                  }}
                />
              </div>
              <div style={{ marginBottom: 28 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.6)" }}>Ticket Price</span>
                  <span style={{ fontSize: 14, fontWeight: 800, color: "#ffd700", fontFamily: "'JetBrains Mono', monospace" }}>${ticketPrice}</span>
                </div>
                <input
                  type="range" min="7" max="997" step="10"
                  value={ticketPrice}
                  onChange={(e) => setTicketPrice(Number(e.target.value))}
                  style={{
                    width: "100%", height: 6, borderRadius: 3,
                    appearance: "none", background: "rgba(255,255,255,0.1)",
                    cursor: "pointer", accentColor: "#ffd700",
                  }}
                />
              </div>

              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                gap: 12,
              }}>
                <StatCard number={views >= 1000000 ? (views / 1000000).toFixed(1) + "M" : (views / 1000).toFixed(0) + "K"} label="Views / Content" accent="#ffd700" />
                <StatCard number={clicks >= 1000 ? (clicks / 1000).toFixed(1) + "K" : clicks.toFixed(0)} label="Clicks (0.1% CTR)" accent="#ff6b35" />
                <StatCard number={sales.toFixed(0)} label="Sales (10% CVR)" accent="#ff3366" />
                <StatCard number={"$" + (revenue >= 1000 ? (revenue / 1000).toFixed(1) + "K" : revenue.toFixed(0))} label="Per Content Piece" accent="#00ff88" />
              </div>

              <div style={{
                marginTop: 24,
                background: "linear-gradient(135deg, rgba(0,255,136,0.08), rgba(255,215,0,0.05))",
                border: "1px solid rgba(0,255,136,0.15)",
                borderRadius: 14,
                padding: "24px 20px",
                textAlign: "center",
              }}>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginBottom: 8, letterSpacing: "1px", textTransform: "uppercase", fontWeight: 700 }}>Weekly Revenue (10 pieces/week)</div>
                <div style={{
                  fontSize: 48, fontWeight: 800, fontFamily: "'JetBrains Mono', monospace",
                  background: "linear-gradient(135deg, #00ff88, #ffd700)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}>
                  ${weeklyRevenue >= 1000000 ? (weeklyRevenue / 1000000).toFixed(2) + "M" : weeklyRevenue >= 1000 ? (weeklyRevenue / 1000).toFixed(1) + "K" : weeklyRevenue.toFixed(0)}
                </div>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.3)", marginTop: 6 }}>at ~zero marginal cost per additional content piece</div>
              </div>
            </div>
          </FadeIn>
        </section>

        {/* DEFENSE */}
        <section id="defense" style={{ paddingTop: 80, paddingBottom: 100 }}>
          <FadeIn>
            <div style={{
              display: "inline-block",
              background: "rgba(255,51,102,0.1)",
              border: "1px solid rgba(255,51,102,0.2)",
              borderRadius: 100, padding: "6px 16px",
              fontSize: 11, fontWeight: 700, color: "#ff3366",
              letterSpacing: "1.5px", textTransform: "uppercase",
              marginBottom: 20,
            }}>
              DEFENSE
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <h2 style={{
              fontSize: "clamp(28px, 4.5vw, 44px)",
              fontWeight: 800, lineHeight: 1.1,
              fontFamily: "'Space Grotesk', sans-serif",
              letterSpacing: "-1.5px",
              marginBottom: 16,
            }}>
              Protect Yourself
            </h2>
          </FadeIn>
          <FadeIn delay={0.15}>
            <p style={{
              fontSize: 15, color: "rgba(255,255,255,0.4)",
              lineHeight: 1.7, maxWidth: 620, marginBottom: 32,
            }}>
              When you scale this fast, you paint a target on your back. The final boss battle isn't getting attention, it's keeping it without getting banned.
            </p>
          </FadeIn>

          <FadeIn delay={0.2}>
            <div style={{
              display: "flex", flexWrap: "wrap", gap: 16,
            }}>
              {defenseItems.map((item, i) => (
                <div key={i} style={{
                  flex: "1 1 240px",
                  background: "rgba(255,51,102,0.05)",
                  border: "1px solid rgba(255,51,102,0.15)",
                  borderRadius: 16, padding: "20px",
                }}>
                  <div style={{ fontSize: 24, marginBottom: 8 }}>{item.icon}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: "#fff", marginBottom: 6 }}>{item.title}</div>
                  <div style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", lineHeight: 1.6 }}>{item.desc}</div>
                </div>
              ))}
            </div>
          </FadeIn>
        </section>

      </div>
    </div>
  );
}

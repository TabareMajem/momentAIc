import React, { useRef } from 'react';
import { Database, Globe, CreditCard, Github, Share2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { motion, useScroll, useTransform } from 'framer-motion';

export function EcosystemSection() {
    const containerRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end start"]
    });

    return (
        <section ref={containerRef} className="py-32 bg-[#020202] relative overflow-hidden">
            {/* Background Gradients */}
            <motion.div
                animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.15, 0.3, 0.15]
                }}
                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] md:w-[800px] md:h-[800px] bg-purple-900/40 rounded-full blur-[120px] pointer-events-none"
            />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8 }}
                    className="text-center mb-24"
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.2, duration: 0.5 }}
                        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-400 font-mono text-xs mb-8 shadow-[0_0_15px_rgba(168,85,247,0.2)]"
                    >
                        <Share2 className="w-4 h-4" />
                        UNIVERSAL_CLIENT_PROTOCOL
                    </motion.div>
                    <h2 className="text-4xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white via-gray-200 to-gray-600 tracking-tighter mb-6">
                        The Neural Ecosystem
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-lg md:text-xl font-light leading-relaxed">
                        MomentAIc isn't just a chatbot. It's an <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 font-mono font-medium">Operating System</span> that connects directly to your tools via the Model Context Protocol (MCP).
                    </p>
                </motion.div>

                <div className="relative h-[400px] md:h-[600px] flex items-center justify-center max-w-4xl mx-auto mt-12">
                    {/* Connecting Lines */}
                    <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-40 xl:opacity-60 z-0 hidden md:block">
                        <defs>
                            <linearGradient id="lineGradCoreV" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stopColor="#a855f7" stopOpacity="0.1" />
                                <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.8" />
                                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1" />
                            </linearGradient>
                            <linearGradient id="lineGradCoreH" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#a855f7" stopOpacity="0.1" />
                                <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.8" />
                                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1" />
                            </linearGradient>
                        </defs>

                        {/* Dynamic Path Lines */}
                        <motion.line
                            x1="50%" y1="50%" x2="50%" y2="10%"
                            stroke="url(#lineGradCoreV)"
                            strokeWidth="1.5"
                            initial={{ pathLength: 0, opacity: 0 }}
                            whileInView={{ pathLength: 1, opacity: 1 }}
                            transition={{ duration: 1.5, ease: "circOut", delay: 0.5 }}
                        />
                        <motion.line
                            x1="50%" y1="50%" x2="90%" y2="50%"
                            stroke="url(#lineGradCoreH)"
                            strokeWidth="1.5"
                            initial={{ pathLength: 0, opacity: 0 }}
                            whileInView={{ pathLength: 1, opacity: 1 }}
                            transition={{ duration: 1.5, ease: "circOut", delay: 0.7 }}
                        />
                        <motion.line
                            x1="50%" y1="50%" x2="50%" y2="90%"
                            stroke="url(#lineGradCoreV)"
                            strokeWidth="1.5"
                            initial={{ pathLength: 0, opacity: 0 }}
                            whileInView={{ pathLength: 1, opacity: 1 }}
                            transition={{ duration: 1.5, ease: "circOut", delay: 0.9 }}
                        />
                        <motion.line
                            x1="50%" y1="50%" x2="10%" y2="50%"
                            stroke="url(#lineGradCoreH)"
                            strokeWidth="1.5"
                            initial={{ pathLength: 0, opacity: 0 }}
                            whileInView={{ pathLength: 1, opacity: 1 }}
                            transition={{ duration: 1.5, ease: "circOut", delay: 1.1 }}
                        />
                    </svg>

                    {/* Orbiting Nodes */}
                    <div className="absolute inset-0 z-10 w-full h-full hidden md:block">
                        {/* Google */}
                        <motion.div
                            className="absolute top-[10%] left-[50%] -translate-x-1/2 -translate-y-1/2"
                            initial={{ opacity: 0, y: -50 }}
                            whileInView={{ opacity: 1, y: "-50%", x: "-50%" }}
                            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.6 }}
                            whileHover={{ scale: 1.05, zIndex: 30 }}
                        >
                            <IntegrationNode icon={<Globe />} label="Google Workspace" color="text-blue-400" border="border-blue-500/30" glow="shadow-[0_0_30px_rgba(59,130,246,0.2)]" />
                        </motion.div>

                        {/* Stripe */}
                        <motion.div
                            className="absolute top-[50%] right-[10%] -translate-x-1/2 -translate-y-1/2"
                            initial={{ opacity: 0, x: 50 }}
                            whileInView={{ opacity: 1, x: "-50%", y: "-50%" }}
                            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.8 }}
                            whileHover={{ scale: 1.05, zIndex: 30 }}
                        >
                            <IntegrationNode icon={<CreditCard />} label="Stripe Finance" color="text-green-400" border="border-green-500/30" glow="shadow-[0_0_30px_rgba(34,197,94,0.2)]" />
                        </motion.div>

                        {/* Github */}
                        <motion.div
                            className="absolute bottom-[10%] left-[50%] -translate-x-1/2 -translate-y-1/2"
                            initial={{ opacity: 0, y: 50 }}
                            whileInView={{ opacity: 1, y: "-50%", x: "-50%" }}
                            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 1.0 }}
                            whileHover={{ scale: 1.05, zIndex: 30 }}
                        >
                            <IntegrationNode icon={<Github />} label="Git Repositories" color="text-gray-300" border="border-white/30" glow="shadow-[0_0_30px_rgba(255,255,255,0.1)]" />
                        </motion.div>

                        {/* Postgres */}
                        <motion.div
                            className="absolute top-[50%] left-[10%] -translate-x-1/2 -translate-y-1/2"
                            initial={{ opacity: 0, x: -50 }}
                            whileInView={{ opacity: 1, x: "-50%", y: "-50%" }}
                            transition={{ type: "spring", stiffness: 100, damping: 20, delay: 1.2 }}
                            whileHover={{ scale: 1.05, zIndex: 30 }}
                        >
                            <IntegrationNode icon={<Database />} label="Postgres Data" color="text-yellow-400" border="border-yellow-500/30" glow="shadow-[0_0_30px_rgba(250,204,21,0.2)]" />
                        </motion.div>
                    </div>

                    {/* Mobile Nodes Grid */}
                    <div className="md:hidden grid grid-cols-2 gap-4 w-full relative z-30 mt-32 px-4">
                        <IntegrationNode icon={<Globe />} label="Workspace" color="text-blue-400" border="border-blue-500/30" glow="shadow-[0_0_30px_rgba(59,130,246,0.2)]" />
                        <IntegrationNode icon={<CreditCard />} label="Finance" color="text-green-400" border="border-green-500/30" glow="shadow-[0_0_30px_rgba(34,197,94,0.2)]" />
                        <IntegrationNode icon={<Github />} label="Git Repos" color="text-gray-300" border="border-white/30" glow="shadow-[0_0_30px_rgba(255,255,255,0.1)]" />
                        <IntegrationNode icon={<Database />} label="Database" color="text-yellow-400" border="border-yellow-500/30" glow="shadow-[0_0_30px_rgba(250,204,21,0.2)]" />
                    </div>

                    {/* Center Brain */}
                    <motion.div
                        initial={{ scale: 0.5, opacity: 0 }}
                        whileInView={{ scale: 1, opacity: 1 }}
                        transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.2 }}
                        className="absolute md:relative z-20 w-40 h-40 md:w-56 md:h-56 bg-[#030303] border border-purple-500/40 rounded-full flex items-center justify-center shadow-[0_0_80px_rgba(168,85,247,0.25)] backdrop-blur-xl -top-20 md:top-auto"
                    >
                        <motion.div
                            animate={{ scale: [1, 1.15, 1], opacity: [0.1, 0.3, 0.1] }}
                            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                            className="absolute inset-0 border border-purple-500 rounded-full"
                        />
                        <motion.div
                            animate={{ scale: [1, 1.3, 1], opacity: [0.05, 0.15, 0.05] }}
                            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
                            className="absolute inset-[-20px] border border-blue-500 rounded-full hidden md:block"
                        />

                        <div className="text-center relative z-10 w-full px-4">
                            <motion.div
                                className="w-12 h-12 md:w-16 md:h-16 mx-auto bg-gradient-to-br from-purple-500/20 to-blue-600/20 rounded-2xl flex items-center justify-center mb-3 border border-purple-500/30 shadow-[0_0_30px_rgba(168,85,247,0.4)]"
                                animate={{ rotate: 360 }}
                                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                            >
                                <div className="w-6 h-6 md:w-8 md:h-8 bg-black/80 rounded-lg border border-purple-500/50" />
                            </motion.div>
                            <div className="text-xl md:text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-white to-blue-300 tracking-tight">CORE</div>
                            <div className="text-[9px] md:text-[11px] font-mono text-purple-400 mt-2 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-500/20 inline-block shadow-[inset_0_0_10px_rgba(168,85,247,0.1)]">MCP_HOST_ONLINE</div>
                        </div>
                    </motion.div>

                </div>
            </div>
        </section>
    );
}

function IntegrationNode({ icon, label, color, border, glow }: any) {
    return (
        <div className={cn(
            "w-full md:w-36 md:h-36 bg-[#050508]/90 backdrop-blur-xl border rounded-2xl flex flex-row md:flex-col items-center justify-start md:justify-center p-4 transition-all duration-500 group cursor-default relative overflow-hidden",
            border, glow
        )}>
            <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className={cn("w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center bg-white/5 md:mb-3 mr-3 md:mr-0 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 border border-white/5 relative z-10", color)}>
                {React.cloneElement(icon, { strokeWidth: 1.5, className: "w-5 h-5 md:w-6 md:h-6" })}
            </div>
            <div className="text-xs md:text-[11px] font-medium text-gray-300 text-left md:text-center tracking-wide relative z-10 w-full md:w-auto">{label}</div>

            {/* Status dot */}
            <div className="absolute top-4 right-4 md:bottom-3 md:left-1/2 md:-translate-x-1/2 md:top-auto md:right-auto flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0">
                <span className="text-[9px] font-mono text-green-500 hidden md:inline">SYNC</span>
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.8)]" />
            </div>
        </div>
    );
}

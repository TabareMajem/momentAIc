import { useState } from 'react';
import { motion } from 'framer-motion';
import { Network, Link, Unplug, ArrowRightLeft, Sparkles, Database, Code, RefreshCw } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export function SynergyLabWidget({ products, onClose }: { products: any[], onClose: () => void }) {
 const [selectedA, setSelectedA] = useState<string>("");
 const [selectedB, setSelectedB] = useState<string>("");
 const [fusing, setFusing] = useState(false);
 const [result, setResult] = useState<any>(null);

 const getProductKey = (name: string) => {
 if (name.includes("Bond")) return "bondquests";
 if (name.includes("Otaku")) return "otaku";
 if (name.includes("Campus")) return "campus";
 if (name.includes("Kids")) return "kids";
 if (name.includes("Forge")) return "agentforge";
 if (name.includes("Moment")) return "momentaic";
 return "yokaizen";
 };

 const handleFuse = async () => {
 if (!selectedA || !selectedB) return;
 setFusing(true);
 setResult(null);

 try {
 const token = localStorage.getItem('token');
 const res = await fetch('/api/v1/admin/synergy/fuse', {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 Authorization: `Bearer ${token}`
 },
 body: JSON.stringify({
 product_a: getProductKey(selectedA),
 product_b: getProductKey(selectedB)
 })
 });
 const data = await res.json();
 setResult(data);
 } catch (e) {
 alert("Fusion failed.");
 } finally {
 setFusing(false);
 }
 };

 return (
 <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-xl font-mono">
 {/* Background Effects */}
 <div className="pointer-events-none fixed inset-0 opacity-20 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] via-black to-black" />
 <div className="pointer-events-none fixed inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03]" />

 <motion.div
 initial={{ scale: 0.9, opacity: 0 }}
 animate={{ scale: 1, opacity: 1 }}
 className="relative w-full max-w-5xl bg-[#0b0c15]/80 border border-[#222222] rounded-3xl p-10 backdrop-blur-2xl overflow-hidden"
 >
 {/* Decorative Elements */}
 <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-[#111111] from-transparent to-transparent" />
 <div className="absolute bottom-0 left-0 w-full h-1 bg-[#111111] from-cyan-500/20 " />

 <div className="flex justify-between items-start mb-12 relative z-10">
 <div>
 <h2 className="text-4xl font-black text-white flex items-center gap-4 tracking-tighter">
 <div className="p-3 bg-[#111111] from-cyan-500 rounded-xl shadow-lg">
 <Network className="w-8 h-8 text-white" />
 </div>
 <span className="bg-clip-text text-transparent bg-[#111111] from-cyan-200 via-white ">
 THE NEXUS
 </span>
 </h2>
 <p className="text-cyan-400 font-mono text-xs tracking-[0.3em] mt-2 uppercase pl-20">
 /// CROSS-PRODUCT SYNERGY PROTOCOL
 </p>
 </div>
 <Button variant="ghost" onClick={onClose} className="text-slate-500 hover:text-white rounded-full w-10 h-10 p-0 flex items-center justify-center border border-white/5 hover:bg-white/10">✕</Button>
 </div>

 {/* Fusion Chamber */}
 <div className="relative flex items-center justify-center gap-12 mb-12 px-8">
 {/* Beam Connector Left */}
 {fusing && <div className="absolute left-[30%] right-[50%] h-[2px] bg-cyan-400 animate-pulse " />}
 {fusing && <div className="absolute left-[50%] right-[30%] h-[2px] bg-purple-400 animate-pulse " />}

 {/* Slot A */}
 <motion.div
 whileHover={{ scale: 1.02 }}
 className="w-1/3 relative z-10"
 >
 <label className="text-[10px] font-bold text-cyan-500 mb-2 block uppercase tracking-widest pl-1">Input Velocity A</label>
 <div className="relative group">
 <div className="absolute -inset-0.5 bg-[#111111] from-cyan-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-500" />
 <select
 className="relative w-full bg-black border border-[#222222] focus:border-cyan-500 rounded-xl p-4 text-white hover:bg-[#111111] transition-colors appearance-none cursor-pointer outline-none"
 onChange={(e) => setSelectedA(e.target.value)}
 value={selectedA}
 >
 <option value="">SELECT ENTITY...</option>
 {products.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
 </select>
 <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">▼</div>
 </div>
 </motion.div>

 {/* Fusion Core */}
 <div className="relative z-20 flex flex-col items-center">
 <div className={`
 w-24 h-24 rounded-full flex items-center justify-center border-4 transition-all duration-1000
 ${fusing
 ? 'border-t-cyan-400 border-r-purple-500 border-b-cyan-400 border-l-purple-500 animate-spin bg-black '
 : 'border-[#222222] bg-[#111111] shadow-xl'}
 `}>
 <Link className={`w-10 h-10 transition-colors duration-500 ${fusing ? 'text-white' : 'text-slate-600'}`} />
 </div>
 {fusing && <div className="absolute -bottom-8 text-[10px] text-purple-400 animate-pulse font-bold tracking-widest">SYNTHESIZING</div>}
 </div>

 {/* Slot B */}
 <motion.div
 whileHover={{ scale: 1.02 }}
 className="w-1/3 relative z-10"
 >
 <label className="text-[10px] font-bold text-purple-500 mb-2 block uppercase tracking-widest pl-1 text-right">Input Velocity B</label>
 <div className="relative group">
 <div className="absolute -inset-0.5 bg-[#111111] from-purple-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-500" />
 <select
 className="relative w-full bg-black border border-[#222222] focus:border-purple-500 rounded-xl p-4 text-white hover:bg-[#111111] transition-colors appearance-none cursor-pointer outline-none text-right"
 onChange={(e) => setSelectedB(e.target.value)}
 value={selectedB}
 >
 <option value="">SELECT ENTITY...</option>
 {products.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
 </select>
 <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">▼</div>
 </div>
 </motion.div>
 </div>

 <div className="text-center mb-10 relative z-10">
 <Button
 size="lg"
 className={`
 relative overflow-hidden w-full py-8 text-xl font-black tracking-[0.2em] rounded-2xl transition-all duration-500
 ${fusing || !selectedA || !selectedB
 ? 'bg-[#111111] text-slate-600 border border-[#222222] cursor-not-allowed'
 : 'bg-white text-black hover:scale-[1.02] '}
 `}
 onClick={handleFuse}
 disabled={fusing || !selectedA || !selectedB}
 >
 <div className="relative z-10 flex items-center justify-center gap-3">
 {fusing ? <RefreshCw className="animate-spin w-6 h-6" /> : <Sparkles className="w-6 h-6 text-purple-600" />}
 {fusing ? 'FUSION IN PROGRESS...' : 'INITIATE FUSION'}
 </div>
 {!fusing && selectedA && selectedB && (
 <div className="absolute inset-0 bg-[#111111] from-cyan-400 opacity-20 animate-gradient-c" />
 )}
 </Button>
 </div>

 {/* Output Console (Holographic Card) */}
 
 {result && (
 <motion.div
 initial={{ opacity: 0, scale: 0.9, y: 20 }}
 animate={{ opacity: 1, scale: 1, y: 0 }}
 exit={{ opacity: 0, scale: 0.9, y: 20 }}
 className="relative bg-black/40 border border-white/10 rounded-2xl p-8 overflow-hidden"
 >
 {/* Card Glow */}
 <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
 <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

 <div className="flex items-start gap-4 mb-6">
 <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
 <Database className="w-6 h-6 text-green-400" />
 </div>
 <div>
 <h3 className="text-2xl font-bold text-white mb-1">{result.synergy_name}</h3>
 <p className="text-slate-400 text-sm italic">"{result.concept_pitch}"</p>
 </div>
 </div>

 <div className="grid grid-cols-2 gap-6 mb-6">
 <div className="p-6 bg-[#0f0f1a] rounded-xl border border-[#222222]/50 hover:border-cyan-500/30 transition-colors">
 <div className="text-xs font-bold text-cyan-400 mb-3 uppercase tracking-wider flex items-center gap-2">
 <ArrowRightLeft className="w-3 h-3" /> Exchange Protocol
 </div>
 <p className="text-sm text-slate-300 leading-relaxed">{result.exchange_terms}</p>
 </div>
 <div className="p-6 bg-[#0f0f1a] rounded-xl border border-[#222222]/50 hover:border-[#222222] transition-colors">
 <div className="text-xs font-bold text-purple-400 mb-3 uppercase tracking-wider flex items-center gap-2">
 <Code className="w-3 h-3" /> System Dialogue
 </div>
 <div className="space-y-2 h-24 overflow-y-auto custom-scrollbar pr-2">
 {result.dialogue_log?.map((line: string, i: number) => (
 <div key={i} className="text-[10px] font-mono text-slate-400 border-l-2 border-[#222222] pl-2">
 {line}
 </div>
 ))}
 </div>
 </div>
 </div>

 <div className="space-y-3 bg-black/30 p-4 rounded-xl border border-white/5">
 <div className="flex items-center gap-3 text-sm text-green-400 font-mono">
 <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
 <span className="opacity-70">ORDER FOR {selectedA}:</span>
 <span className="font-bold">{result.orders_a?.instruction}</span>
 </div>
 <div className="flex items-center gap-3 text-sm text-green-400 font-mono">
 <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
 <span className="opacity-70">ORDER FOR {selectedB}:</span>
 <span className="font-bold">{result.orders_b?.instruction}</span>
 </div>
 </div>

 </motion.div>
 )}
 

 </motion.div>
 </div>
 );
}

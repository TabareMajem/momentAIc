import React, { useState } from 'react';
import { Download, Loader2, Image as ImageIcon, Sparkles } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

interface GeneratedImageProps {
 dataUri: string;
 prompt: string;
 className?: string;
}

export function GeneratedImage({ dataUri, prompt, className }: GeneratedImageProps) {
 const [isLoaded, setIsLoaded] = useState(false);

 const handleDownload = () => {
 const link = document.createElement('a');
 link.href = dataUri;
 link.download = `momentaic-asset-${Date.now()}.png`;
 document.body.appendChild(link);
 link.click();
 document.body.removeChild(link);
 };

 return (
 <div className={cn("relative group rounded-xl overflow-hidden border border-white/10 bg-black/40", className)}>
 {/* Loading State */}
 {!isLoaded && (
 <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#111111]/50 backdrop-blur-sm z-10">
 <Loader2 className="w-8 h-8 text-purple-500 animate-spin mb-2" />
 <span className="text-[10px] text-gray-400 font-mono tracking-widest uppercase animate-pulse">
 Rendering Neural Matrix
 </span>
 </div>
 )}

 {/* The Actual Image natively mapped from the Base64 Data URI */}
 <img
 src={dataUri}
 alt={prompt}
 className={cn(
 "w-full h-auto object-cover transition-all duration-700",
 isLoaded ? "opacity-100 scale-100" : "opacity-0 scale-95"
 )}
 onLoad={() => setIsLoaded(true)}
 />

 {/* Hover UI Overlay */}
 <div className="absolute inset-x-0 bottom-0 p-4 bg-[#111111] from-black/90 via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end">
 <p className="text-xs text-white/90 font-mono line-clamp-2 mb-3 drop-shadow-md">
 <Sparkles className="w-3 h-3 inline mr-1 text-purple-400" />
 {prompt}
 </p>
 <div className="flex items-center gap-2">
 <Button
 size="sm"
 onClick={handleDownload}
 className="h-8 bg-white/10 hover:bg-white/20 text-white border border-white/10 rounded-lg flex-1 font-mono text-xs shadow-lg backdrop-blur-md"
 >
 <Download className="w-3.5 h-3.5 mr-1.5" />
 Download Asset
 </Button>
 </div>
 </div>

 {/* Cyberpunk corner accents */}
 <div className="absolute top-0 left-0 w-8 h-8 rounded-tl-xl border-t-2 border-l-2 border-purple-500/50 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity" />
 <div className="absolute bottom-0 right-0 w-8 h-8 rounded-br-xl border-b-2 border-r-2 border-cyan-500/50 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity" />
 </div>
 );
}

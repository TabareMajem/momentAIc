import React, { useState, useRef, useEffect } from 'react';
import { Mic, Type, Linkedin, Twitter, Sparkles, ArrowRight, Image as ImageIcon, Loader2, Copy, Check, Download, Square, AlertCircle, History, Clock, Rocket } from 'lucide-react';
import { transcribeAudio } from '../../services/geminiService';
import { BackendService } from '../../services/backendService';
import { ContentPiece, AgentType } from '../../types';
import { useToast } from './Toast';

const ContentAgent: React.FC = () => {
  const [inputMode, setInputMode] = useState<'TEXT' | 'AUDIO'>('TEXT');
  const [rawText, setRawText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ContentPiece | null>(null);
  const { addToast } = useToast();

  const [generatingImage, setGeneratingImage] = useState(false);
  const [imageError, setImageError] = useState<string | null>(null);
  const [copiedState, setCopiedState] = useState<string | null>(null);
  const [history, setHistory] = useState<ContentPiece[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Audio State
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await BackendService.getContentHistory();
      setHistory(data);
    } catch (e) {
      console.error("Failed to load history", e);
    }
  };

  const handleProcess = async () => {
    if (!rawText.trim()) return;
    setIsProcessing(true);
    try {
      const result = await BackendService.generateContent(rawText, 'GENERAL');
      // Backend returns the full ContentPiece object
      setResult(result);
      // Refresh history
      loadHistory();
      addToast('Campaign assets generated successfully', 'success');

    } catch (e: any) {
      console.error(e);
      addToast(e.message || "Failed to repurpose content", 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const chunks: BlobPart[] = [];

      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.onloadend = async () => {
          const base64 = (reader.result as string).split(',')[1];
          setIsProcessing(true); // Use processing state for transcription loading
          try {
            const text = await transcribeAudio(base64, 'audio/webm');
            setRawText(prev => prev + (prev ? ' ' : '') + text);
            addToast('Audio transcribed', 'success');
          } catch (e: any) {
            console.error(e);
            addToast(e.message || "Transcription failed", 'error');
          } finally {
            setIsProcessing(false);
          }
        };
        reader.readAsDataURL(blob);

        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      addToast('Recording started', 'info');
    } catch (e) {
      console.error("Microphone access denied", e);
      addToast("Microphone access denied. Check permissions.", 'error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      addToast('Processing audio...', 'info');
    }
  };

  const handleGenerateImage = async () => {
    if (!result?.generatedAssets?.visualPrompt) return;
    setGeneratingImage(true);
    setImageError(null);
    try {
      const response = await BackendService.generateImage(result.generatedAssets.visualPrompt);
      if (response.imageUrl) {
        const updatedResult = {
          ...result,
          generatedAssets: { ...result.generatedAssets!, visualImage: response.imageUrl }
        };
        setResult(updatedResult);
        addToast('Visual generated successfully', 'success');
      } else {
        setImageError("Failed to generate image");
        addToast("Failed to generate image", 'error');
      }
    } catch (e: any) {
      setImageError(e.message || "Failed to generate image");
      addToast(e.message, 'error');
    } finally {
      setGeneratingImage(false);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedState(key);
    addToast('Copied to clipboard', 'success');
    setTimeout(() => setCopiedState(null), 2000);
  };

  const downloadImage = () => {
    if (result?.generatedAssets?.visualImage) {
      const link = document.createElement('a');
      link.href = result.generatedAssets.visualImage;
      link.download = `generated-visual-${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      addToast('Image downloaded', 'success');
    }
  };

  const loadHistoryItem = (item: ContentPiece) => {
    setResult(item);
    setRawText(item.rawIdea);
    setShowHistory(false);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto animate-fade-in relative overflow-x-hidden sm:overflow-x-visible">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-amber-500 shrink-0" />
            Agent C: The Content Machine
          </h2>
          <p className="text-slate-400 mt-2">Turn one brain dump into an omnichannel campaign.</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <button
            onClick={() => {
              const event = new CustomEvent('navigate-to', { detail: AgentType.VIRAL_GROWTH });
              window.dispatchEvent(event);
            }}
            className="flex items-center justify-center w-full sm:w-auto gap-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-lg font-bold shadow-lg shadow-purple-900/20 hover:scale-105 transition-transform text-sm whitespace-nowrap"
          >
            <Rocket className="w-4 h-4 shrink-0" /> Launch Viral Engine
          </button>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center justify-center w-full sm:w-auto gap-2 bg-slate-800 border border-slate-700 hover:bg-slate-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium whitespace-nowrap"
          >
            <History className="w-4 h-4 shrink-0" /> History
          </button>
        </div>
      </div>

      {/* History Sidebar */}
      {showHistory && (
        <div className="absolute top-20 right-4 sm:right-6 z-20 w-[calc(100%-2rem)] sm:w-80 bg-slate-900 border border-slate-700 shadow-2xl rounded-xl h-[500px] sm:h-[600px] max-h-[80vh] overflow-hidden flex flex-col animate-in slide-in-from-right">
          <div className="p-4 border-b border-slate-800 bg-slate-800/50 flex justify-between items-center">
            <h3 className="font-bold text-white">Saved Campaigns</h3>
            <button onClick={() => setShowHistory(false)} className="text-slate-400 hover:text-white"><Square className="w-4 h-4" /></button>
          </div>
          <div className="overflow-y-auto flex-1 p-2 space-y-2">
            {history.length === 0 && <p className="text-center text-slate-500 py-8 text-sm">No history yet.</p>}
            {history.map(item => (
              <button
                key={item.id}
                onClick={() => loadHistoryItem(item)}
                className="w-full text-left p-3 rounded-lg hover:bg-slate-800 border border-transparent hover:border-slate-700 transition-all group"
              >
                <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                  <Clock className="w-3 h-3" />
                  {new Date(item.createdAt).toLocaleDateString()}
                </div>
                <p className="text-slate-300 text-sm line-clamp-2 font-medium group-hover:text-white">
                  {item.rawIdea}
                </p>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
              <h3 className="text-lg font-medium text-white">Input Source</h3>
              <div className="flex bg-slate-900 rounded-lg p-1 w-full sm:w-auto">
                <button
                  onClick={() => setInputMode('TEXT')}
                  className={`flex-1 sm:flex-none px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${inputMode === 'TEXT' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-slate-300'}`}
                >
                  <Type className="w-4 h-4 inline mr-2" /> Text
                </button>
                <button
                  onClick={() => setInputMode('AUDIO')}
                  className={`flex-1 sm:flex-none px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${inputMode === 'AUDIO' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-slate-300'}`}
                >
                  <Mic className="w-4 h-4 inline mr-2" /> Voice
                </button>
              </div>
            </div>

            {inputMode === 'AUDIO' && (
              <div className="mb-4 bg-slate-900/50 p-6 rounded-lg border border-slate-700/50 flex flex-col items-center justify-center gap-4">
                <p className="text-sm text-slate-400">Record your voice note to generate content.</p>
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`w-16 h-16 rounded-full flex items-center justify-center transition-all transform hover:scale-105 ${isRecording ? 'bg-rose-600 hover:bg-rose-700 animate-pulse shadow-lg shadow-rose-900/20' : 'bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-900/20'}`}
                >
                  {isRecording ? <Square className="w-6 h-6 text-white fill-current" /> : <Mic className="w-8 h-8 text-white" />}
                </button>
                <div className="h-6">
                  {isRecording && <span className="text-xs text-rose-400 font-medium animate-pulse">Recording in progress...</span>}
                  {!isRecording && isProcessing && <span className="text-xs text-indigo-400 font-medium flex items-center gap-2"><Loader2 className="w-3 h-3 animate-spin" /> Transcribing...</span>}
                </div>
              </div>
            )}

            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder={inputMode === 'TEXT' ? "Dump your raw thoughts, ideas, or rough notes here..." : "Transcription will appear here after recording..."}
              className="w-full h-64 bg-slate-900 border border-slate-700 rounded-lg p-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            />

            <div className="mt-4 flex justify-end">
              <button
                onClick={handleProcess}
                disabled={isProcessing || !rawText}
                className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-3 rounded-lg font-bold flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? <Sparkles className="w-5 h-5 animate-spin" /> : <ArrowRight className="w-5 h-5" />}
                Ignite Engine (Pro)
              </button>
            </div>
          </div>
        </div>

        {/* Output Section */}
        <div className="space-y-6">
          {!result ? (
            <div className="h-full flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-xl text-slate-600 p-12">
              <Sparkles className="w-16 h-16 mb-4 opacity-20" />
              <p>Waiting for input to generate assets...</p>
            </div>
          ) : (
            <div className="space-y-6 animate-in slide-in-from-right-4 duration-500">

              {/* Visuals Generator */}
              <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div className="bg-purple-500/10 border-b border-purple-500/20 p-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ImageIcon className="w-5 h-5 text-purple-500" />
                    <h4 className="font-bold text-slate-200">Nano Bana Pro Visuals</h4>
                  </div>
                  <div className="flex gap-2">
                    {result.generatedAssets?.visualImage && (
                      <button
                        onClick={downloadImage}
                        className="text-xs bg-slate-700 hover:bg-slate-600 text-white px-3 py-1 rounded flex items-center gap-1"
                      >
                        <Download className="w-3 h-3" /> Download
                      </button>
                    )}
                    {!result.generatedAssets?.visualImage && (
                      <button
                        onClick={handleGenerateImage}
                        disabled={generatingImage}
                        className="text-xs bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded flex items-center gap-1 disabled:opacity-50"
                      >
                        {generatingImage ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                        Generate High-Res
                      </button>
                    )}
                  </div>
                </div>
                <div className="p-4 bg-slate-900">
                  {result.generatedAssets?.visualImage ? (
                    <div className="relative group">
                      <img src={result.generatedAssets.visualImage} alt="Generated" className="w-full rounded-lg shadow-lg" />
                    </div>
                  ) : (
                    <div className="p-4 rounded text-sm text-slate-400 italic border border-slate-700/50 bg-slate-800/50">
                      <span className="font-semibold text-purple-400 not-italic block mb-2">Suggested Prompt:</span>
                      "{result.generatedAssets?.visualPrompt}"
                      {imageError && <p className="text-rose-400 mt-2 not-italic font-bold">Error: {imageError}</p>}
                    </div>
                  )}
                </div>
              </div>

              {/* LinkedIn Asset */}
              <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div className="bg-[#0077b5]/10 border-b border-[#0077b5]/20 p-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Linkedin className="w-5 h-5 text-[#0077b5]" />
                    <h4 className="font-bold text-slate-200">LinkedIn Carousel/Post</h4>
                  </div>
                  <button
                    onClick={() => copyToClipboard(result.generatedAssets?.linkedinPost || "", 'linkedin')}
                    className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
                  >
                    {copiedState === 'linkedin' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copiedState === 'linkedin' ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <div className="p-4 text-sm text-slate-300 whitespace-pre-wrap leading-relaxed bg-slate-900/50">
                  {result.generatedAssets?.linkedinPost}
                </div>
              </div>

              {/* Twitter Thread */}
              <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div className="bg-[#1DA1F2]/10 border-b border-[#1DA1F2]/20 p-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Twitter className="w-5 h-5 text-[#1DA1F2]" />
                    <h4 className="font-bold text-slate-200">Twitter Thread (5 Tweets)</h4>
                  </div>
                  <button
                    onClick={() => copyToClipboard(result.generatedAssets?.twitterThread.join('\n\n') || "", 'twitter')}
                    className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
                  >
                    {copiedState === 'twitter' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copiedState === 'twitter' ? 'Copied' : 'Copy All'}
                  </button>
                </div>
                <div className="p-4 space-y-3 bg-slate-900/50">
                  {result.generatedAssets?.twitterThread.map((tweet, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-700 text-xs flex items-center justify-center text-slate-400 border border-slate-600">
                        {i + 1}
                      </div>
                      <p className="text-sm text-slate-300">{tweet}</p>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContentAgent;
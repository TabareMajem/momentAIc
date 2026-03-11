import React, { useState, useRef } from 'react';
import { Image as ImageIcon, Film, Mic, Wand2, Upload, Play, Download, Square, MonitorPlay, Music, AlertCircle, Sparkles, Video, Users } from 'lucide-react';
import { transcribeAudio, generateSpeech } from '../../services/geminiService';
import { BackendService } from '../../services/backendService';
import { useToast } from './Toast';

type MediaType = 'IMAGE_EDITOR' | 'VIDEO_STUDIO' | 'AUDIO_STUDIO' | 'UGC_AVATAR';

const MediaAgent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<MediaType>('IMAGE_EDITOR');
  const { addToast } = useToast();

  // Shared State
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Image Editor State
  const [imagePrompt, setImagePrompt] = useState('');
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);

  // Video Studio State
  const [videoPrompt, setVideoPrompt] = useState('');
  const [videoAspectRatio, setVideoAspectRatio] = useState<'16:9' | '9:16'>('16:9');
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null);

  // Audio Studio State
  const [audioText, setAudioText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [generatedAudio, setGeneratedAudio] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // UGC Avatar State
  const [productImage, setProductImage] = useState<string | null>(null);
  const [characterImage, setCharacterImage] = useState<string | null>(null);
  const [avatarPrompt, setAvatarPrompt] = useState('');
  const [avatarResultImage, setAvatarResultImage] = useState<string | null>(null);
  const [avatarVideoModel, setAvatarVideoModel] = useState<'VEO' | 'KLING' | 'SEEDANCE'>('SEEDANCE');
  const [avatarVideoUrl, setAvatarVideoUrl] = useState<string | null>(null);
  const [avatarStep, setAvatarStep] = useState<1 | 2>(1);

  // --- Handlers ---

  // Image Handling
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
        addToast("Image uploaded successfully", 'success');
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageEdit = async () => {
    if (!imagePrompt) return; // We'll ignore uploadedImage for now as backend only supports prompt
    setIsProcessing(true);
    setError(null);
    try {
      const response = await BackendService.generateImage(imagePrompt);
      if (response.imageUrl) {
        setResultImage(response.imageUrl);
        addToast("Image generated successfully", 'success');
      }
    } catch (e: any) {
      setError(e.message || "Failed to generate image.");
      addToast(e.message, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  // Video Handling
  const handleVideoGenerate = async () => {
    if (!videoPrompt) return;
    setIsProcessing(true);
    setError(null);
    setGeneratedVideoUrl(null);
    addToast("Starting Veo generation (this may take ~1-2 minutes)...", 'info');

    try {
      // 1. Submit Job
      const { id: jobId } = await BackendService.generateVideo(videoPrompt);
      addToast("Job submitted. Processing...", 'info');

      // 2. Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const status = await BackendService.getVideoStatus(jobId);
          if (status.state === 'completed') {
            clearInterval(pollInterval);
            setGeneratedVideoUrl(status.result); // Result is the video URL
            setIsProcessing(false);
            addToast("Video generated successfully", 'success');
          } else if (status.state === 'failed') {
            clearInterval(pollInterval);
            setIsProcessing(false);
            setError("Video generation failed.");
            addToast("Video generation failed", 'error');
          }
          // If active/waiting, continue polling
        } catch (e) {
          console.error("Polling error", e);
          // Don't stop polling on transient errors, but maybe limit retries in prod
        }
      }, 5000); // Poll every 5s

    } catch (e: any) {
      console.error("Veo Error:", e);
      setIsProcessing(false);
      setError(e.message || "Video generation failed");
      addToast("Video generation failed", 'error');
    }
  };

  // Audio Handling
  const startRecording = async () => {
    setError(null);
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
          setIsProcessing(true);
          try {
            const text = await transcribeAudio(base64, 'audio/webm');
            setTranscription(text);
            addToast("Audio transcribed", 'success');
          } catch (e: any) {
            setError(e.message || "Transcription failed");
            addToast(e.message, 'error');
          } finally {
            setIsProcessing(false);
          }
        };
        reader.readAsDataURL(blob);
        // Stop tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      addToast("Recording started", 'info');
    } catch (e) {
      setError("Microphone access denied. Please check your browser permissions.");
      addToast("Microphone access denied", 'error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      addToast("Processing audio...", 'info');
    }
  };

  const handleTTS = async () => {
    if (!audioText) return;
    setIsProcessing(true);
    setError(null);
    try {
      const base64 = await generateSpeech(audioText);
      if (base64) {
        setGeneratedAudio(base64);
        addToast("Audio generated", 'success');
      }
    } catch (e: any) {
      setError(e.message || "Text-to-speech generation failed.");
      addToast(e.message, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudio = () => {
    if (generatedAudio) {
      const audio = new Audio(`data:audio/mp3;base64,${generatedAudio}`);
      audio.play();
    }
  };

  // UGC Avatar Handlers
  const handleProductUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setProductImage(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleCharacterUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setCharacterImage(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleAvatarImageGenerate = async () => {
    if (!productImage || !characterImage || !avatarPrompt) return;
    setIsProcessing(true);
    setError(null);
    setAvatarStep(1);
    try {
      const prodB64 = productImage.split(',')[1];
      const charB64 = characterImage.split(',')[1];
      const response = await BackendService.generateAvatarImage(prodB64, charB64, avatarPrompt);
      if (response.imageUrl) {
        setAvatarResultImage(response.imageUrl);
        setAvatarStep(2);
        addToast('Avatar image generated!', 'success');
      } else {
        addToast(response.message || 'No image data returned', 'info');
      }
    } catch (e: any) {
      setError(e.message || 'Avatar image generation failed');
      addToast(e.message, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAvatarVideoGenerate = async () => {
    if (!avatarResultImage) return;
    setIsProcessing(true);
    setError(null);
    setAvatarStep(2);
    setAvatarVideoUrl(null);
    addToast(`Starting ${avatarVideoModel} video generation...`, 'info');
    try {
      const imgB64 = avatarResultImage.startsWith('data:') ? avatarResultImage.split(',')[1] : avatarResultImage;
      const response = await BackendService.generateAvatarVideo(imgB64, avatarPrompt, avatarVideoModel);
      if (response.videoUrl) {
        setAvatarVideoUrl(response.videoUrl);
        setIsProcessing(false);
        addToast('Avatar video generated!', 'success');
      } else if (response.taskId) {
        addToast(`Job submitted. Polling for result...`, 'info');
        // Auto-poll for PIAPI tasks (Kling/Seedance)
        const pollInterval = setInterval(async () => {
          try {
            const status = await BackendService.getAvatarVideoStatus(response.taskId, avatarVideoModel);
            if (status.status === 'completed' && status.videoUrl) {
              clearInterval(pollInterval);
              setAvatarVideoUrl(status.videoUrl);
              setIsProcessing(false);
              addToast('Avatar video ready!', 'success');
            } else if (status.status === 'failed' || status.status === 'error') {
              clearInterval(pollInterval);
              setIsProcessing(false);
              setError('Video generation failed on the server.');
              addToast('Video generation failed', 'error');
            }
          } catch (e) { /* continue polling */ }
        }, 8000);
      } else {
        setIsProcessing(false);
        addToast('Video generation submitted', 'success');
      }
    } catch (e: any) {
      setError(e.message || 'Avatar video generation failed');
      addToast(e.message, 'error');
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto animate-fade-in text-slate-200">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Film className="w-8 h-8 text-pink-500 shrink-0" />
            Agent D: Media Studio
          </h2>
          <p className="text-slate-400 mt-2">Generate and edit Image, Video, and Audio assets.</p>
        </div>
        {/* Tabs */}
        <div className="flex flex-wrap bg-slate-800 p-1 rounded-lg border border-slate-700 gap-1 lg:gap-0">
          <button onClick={() => setActiveTab('IMAGE_EDITOR')} className={`flex-1 lg:flex-none whitespace-nowrap px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'IMAGE_EDITOR' ? 'bg-pink-600 text-white shadow-lg' : 'hover:text-white text-slate-400'}`}>
            <ImageIcon className="w-4 h-4 inline mr-2" /> Editor
          </button>
          <button onClick={() => setActiveTab('VIDEO_STUDIO')} className={`flex-1 lg:flex-none whitespace-nowrap px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'VIDEO_STUDIO' ? 'bg-pink-600 text-white shadow-lg' : 'hover:text-white text-slate-400'}`}>
            <MonitorPlay className="w-4 h-4 inline mr-2" /> Veo Video
          </button>
          <button onClick={() => setActiveTab('AUDIO_STUDIO')} className={`flex-1 lg:flex-none whitespace-nowrap px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'AUDIO_STUDIO' ? 'bg-pink-600 text-white shadow-lg' : 'hover:text-white text-slate-400'}`}>
            <Mic className="w-4 h-4 inline mr-2" /> Audio
          </button>
          <button onClick={() => setActiveTab('UGC_AVATAR')} className={`flex-1 lg:flex-none whitespace-nowrap px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'UGC_AVATAR' ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg' : 'hover:text-white text-slate-400'}`}>
            <Sparkles className="w-4 h-4 inline mr-2" /> UGC Avatar
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/20 border border-rose-500/50 text-rose-200 p-4 rounded-lg mb-6 flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 min-h-[500px]">

        {/* --- IMAGE EDITOR --- */}
        {activeTab === 'IMAGE_EDITOR' && (
          <div className="grid lg:grid-cols-2 gap-8 h-full animate-in fade-in">
            <div className="space-y-4">
              <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 flex flex-col items-center justify-center text-center hover:bg-slate-700/30 transition-colors relative h-64">
                {uploadedImage ? (
                  <img src={uploadedImage} alt="Uploaded" className="max-h-full object-contain rounded" />
                ) : (
                  <>
                    <Upload className="w-10 h-10 text-slate-500 mb-2" />
                    <p className="text-sm text-slate-400">Upload image to edit</p>
                  </>
                )}
                <input type="file" accept="image/*" onChange={handleImageUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
              </div>
              <textarea
                value={imagePrompt}
                onChange={(e) => setImagePrompt(e.target.value)}
                placeholder="Describe the edit (e.g., 'Add a neon sign', 'Make it cyberpunk')"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm text-white focus:ring-2 focus:ring-pink-500 outline-none transition-all"
                rows={3}
              />
              <button
                onClick={handleImageEdit}
                disabled={isProcessing || !uploadedImage}
                className="w-full bg-pink-600 hover:bg-pink-700 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2 disabled:opacity-50 shadow-lg shadow-pink-900/20 transition-all"
              >
                {isProcessing ? <Wand2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                Generate Edit (Flash Image)
              </button>
            </div>
            <div className="bg-slate-900 rounded-lg border border-slate-700 flex items-center justify-center p-4">
              {resultImage ? (
                <img src={resultImage} alt="Result" className="max-w-full max-h-[400px] rounded shadow-lg" />
              ) : (
                <p className="text-slate-600 italic">Edited image will appear here...</p>
              )}
            </div>
          </div>
        )}

        {/* --- VIDEO STUDIO --- */}
        {activeTab === 'VIDEO_STUDIO' && (
          <div className="grid lg:grid-cols-2 gap-8 animate-in fade-in">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Video Prompt</label>
                <textarea
                  value={videoPrompt}
                  onChange={(e) => setVideoPrompt(e.target.value)}
                  placeholder="Describe your video in detail (e.g., A cinematic drone shot of a futuristic Tokyo at night, neon lights, raining, 4k)"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm text-white focus:ring-2 focus:ring-pink-500 outline-none transition-all"
                  rows={4}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Start Image (Optional)</label>
                <div className="border-2 border-dashed border-slate-600 rounded-lg p-4 flex items-center gap-4 relative hover:bg-slate-700/30 transition-all">
                  {uploadedImage && <img src={uploadedImage} className="h-12 w-12 object-cover rounded" />}
                  <span className="text-xs text-slate-400 flex-1">{uploadedImage ? 'Image selected' : 'Upload source image for Image-to-Video'}</span>
                  <input type="file" accept="image/*" onChange={handleImageUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-400 mb-2">Aspect Ratio</label>
                <div className="flex gap-4">
                  <button
                    onClick={() => setVideoAspectRatio('16:9')}
                    className={`flex-1 py-2 rounded border transition-all ${videoAspectRatio === '16:9' ? 'border-pink-500 bg-pink-500/10 text-pink-400 font-bold' : 'border-slate-700 text-slate-400 hover:border-slate-600'}`}
                  >
                    16:9 Landscape
                  </button>
                  <button
                    onClick={() => setVideoAspectRatio('9:16')}
                    className={`flex-1 py-2 rounded border transition-all ${videoAspectRatio === '9:16' ? 'border-pink-500 bg-pink-500/10 text-pink-400 font-bold' : 'border-slate-700 text-slate-400 hover:border-slate-600'}`}
                  >
                    9:16 Portrait
                  </button>
                </div>
              </div>

              <button
                onClick={handleVideoGenerate}
                disabled={isProcessing || !videoPrompt}
                className="w-full bg-pink-600 hover:bg-pink-700 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2 disabled:opacity-50 shadow-lg shadow-pink-900/20 transition-all"
              >
                {isProcessing ? <Wand2 className="w-4 h-4 animate-spin" /> : <Film className="w-4 h-4" />}
                Generate Video (Veo)
              </button>
              <p className="text-xs text-slate-500 text-center">*Takes 1-2 minutes. Requires Paid Google Cloud Project.</p>
            </div>

            <div className="bg-slate-900 rounded-lg border border-slate-700 flex items-center justify-center p-4 min-h-[300px]">
              {generatedVideoUrl ? (
                <div className="w-full">
                  <video controls autoPlay loop src={generatedVideoUrl} className="w-full rounded-lg shadow-2xl border border-pink-500/20" />
                  <div className="mt-4 flex justify-center">
                    <a href={generatedVideoUrl} download className="text-xs text-pink-400 hover:text-pink-300 flex items-center gap-1">
                      <Download className="w-3 h-3" /> Download MP4
                    </a>
                  </div>
                </div>
              ) : (
                <div className="text-center text-slate-600">
                  {isProcessing ? (
                    <div className="flex flex-col items-center animate-pulse">
                      <Film className="w-12 h-12 mb-4 text-pink-500" />
                      <p className="text-pink-400 font-medium">Generating Video...</p>
                      <p className="text-xs mt-2">This may take a minute.</p>
                    </div>
                  ) : (
                    <>
                      <Film className="w-12 h-12 mx-auto mb-2 opacity-20" />
                      <p>Video preview will appear here</p>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* --- AUDIO STUDIO --- */}
        {activeTab === 'AUDIO_STUDIO' && (
          <div className="grid md:grid-cols-2 gap-8 animate-in fade-in">
            {/* Transcription */}
            <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Mic className="w-5 h-5 text-emerald-400" /> Speech to Text
              </h3>
              <div className="h-40 bg-slate-800 rounded p-4 mb-4 overflow-y-auto text-sm text-slate-300 border border-slate-700">
                {transcription || "Transcription will appear here..."}
              </div>
              <button
                onClick={isRecording ? stopRecording : startRecording}
                className={`w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-all ${isRecording ? 'bg-rose-600 hover:bg-rose-700 shadow-lg shadow-rose-900/20' : 'bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-900/20'}`}
              >
                {isRecording ? (
                  <> <Square className="w-4 h-4 fill-current animate-pulse" /> Stop Recording </>
                ) : (
                  <> <Mic className="w-4 h-4" /> Start Recording </>
                )}
              </button>
            </div>

            {/* TTS */}
            <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Music className="w-5 h-5 text-amber-400" /> Text to Speech
              </h3>
              <textarea
                value={audioText}
                onChange={(e) => setAudioText(e.target.value)}
                placeholder="Enter text to convert to speech..."
                className="w-full h-40 bg-slate-800 border border-slate-700 rounded mb-4 p-3 text-sm text-white focus:ring-2 focus:ring-amber-500 outline-none resize-none transition-all"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleTTS}
                  disabled={isProcessing || !audioText}
                  className="flex-1 bg-amber-600 hover:bg-amber-700 text-white py-3 rounded-lg font-medium disabled:opacity-50 shadow-lg shadow-amber-900/20 transition-all"
                >
                  {isProcessing ? "Generating..." : "Generate Audio"}
                </button>
                {generatedAudio && (
                  <button onClick={playAudio} className="px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-all hover:scale-105">
                    <Play className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* --- UGC AVATAR STUDIO --- */}
        {activeTab === 'UGC_AVATAR' && (
          <div className="animate-in fade-in space-y-6">
            <div className="text-center mb-4">
              <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">UGC Avatar Studio</h3>
              <p className="text-slate-400 text-sm mt-1">Upload a product image + character anchor → Gemini 3 generates the scene → animate with Veo or Kling</p>
            </div>

            {/* Step 1: Image Inputs + Generate */}
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Product Image */}
              <div className="bg-slate-900/60 rounded-xl border border-slate-700 p-4">
                <label className="block text-sm font-medium text-purple-300 mb-2">📦 Product Image</label>
                <div className="border-2 border-dashed border-purple-500/30 rounded-lg h-48 flex flex-col items-center justify-center relative hover:bg-purple-500/5 transition-colors">
                  {productImage ? (
                    <img src={productImage} alt="Product" className="max-h-full object-contain rounded" />
                  ) : (
                    <>
                      <Upload className="w-8 h-8 text-purple-400/50 mb-2" />
                      <p className="text-xs text-slate-500">Upload product photo</p>
                    </>
                  )}
                  <input type="file" accept="image/*" onChange={handleProductUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
                </div>
              </div>

              {/* Character Image */}
              <div className="bg-slate-900/60 rounded-xl border border-slate-700 p-4">
                <label className="block text-sm font-medium text-pink-300 mb-2">🧑 Character / Anchor</label>
                <div className="border-2 border-dashed border-pink-500/30 rounded-lg h-48 flex flex-col items-center justify-center relative hover:bg-pink-500/5 transition-colors">
                  {characterImage ? (
                    <img src={characterImage} alt="Character" className="max-h-full object-contain rounded" />
                  ) : (
                    <>
                      <Users className="w-8 h-8 text-pink-400/50 mb-2" />
                      <p className="text-xs text-slate-500">Upload character/person</p>
                    </>
                  )}
                  <input type="file" accept="image/*" onChange={handleCharacterUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
                </div>
              </div>

              {/* Prompt + Generate */}
              <div className="bg-slate-900/60 rounded-xl border border-slate-700 p-4 flex flex-col">
                <label className="block text-sm font-medium text-slate-300 mb-2">✨ Scene Prompt</label>
                <textarea
                  value={avatarPrompt}
                  onChange={(e) => setAvatarPrompt(e.target.value)}
                  placeholder="e.g., The character holding the product in a futuristic neon-lit studio, professional UGC style"
                  className="flex-1 bg-slate-800 border border-slate-700 rounded-lg p-3 text-sm text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all resize-none mb-3"
                  rows={3}
                />
                <button
                  onClick={handleAvatarImageGenerate}
                  disabled={isProcessing || !productImage || !characterImage || !avatarPrompt}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2 disabled:opacity-40 shadow-lg shadow-purple-900/30 transition-all"
                >
                  {isProcessing && avatarStep === 1 ? <Wand2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                  Step 1: Generate Avatar (Gemini 3)
                </button>
              </div>
            </div>

            {/* Step 2: Result Image + Video Generation */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Generated Avatar Image */}
              <div className="bg-slate-900 rounded-xl border border-slate-700 p-4 min-h-[300px] flex items-center justify-center">
                {avatarResultImage ? (
                  <img src={avatarResultImage} alt="Generated Avatar" className="max-w-full max-h-[400px] rounded-lg shadow-2xl border border-purple-500/20" />
                ) : (
                  <div className="text-center text-slate-600">
                    <Sparkles className="w-12 h-12 mx-auto mb-2 opacity-20" />
                    <p>Generated avatar image will appear here</p>
                  </div>
                )}
              </div>

              {/* Video Generation Controls + Result */}
              <div className="space-y-4">
                <div className="bg-slate-900/60 rounded-xl border border-slate-700 p-4">
                  <label className="block text-sm font-medium text-slate-300 mb-3">🎬 Video Model</label>
                  <div className="flex flex-col sm:flex-row gap-3 mb-4">
                    <button
                      onClick={() => setAvatarVideoModel('VEO')}
                      className={`flex-1 py-2.5 rounded-lg border text-sm font-medium transition-all ${avatarVideoModel === 'VEO'
                        ? 'border-blue-500 bg-blue-500/10 text-blue-400 shadow-lg shadow-blue-900/20'
                        : 'border-slate-700 text-slate-400 hover:border-slate-600'
                        }`}
                    >
                      🌊 Google Veo
                    </button>
                    <button
                      onClick={() => setAvatarVideoModel('KLING')}
                      className={`flex-1 py-2.5 rounded-lg border text-sm font-medium transition-all ${avatarVideoModel === 'KLING'
                        ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400 shadow-lg shadow-emerald-900/20'
                        : 'border-slate-700 text-slate-400 hover:border-slate-600'
                        }`}
                    >
                      🎥 Kling AI
                    </button>
                    <button
                      onClick={() => setAvatarVideoModel('SEEDANCE')}
                      className={`flex-1 py-2.5 rounded-lg border text-sm font-medium transition-all ${avatarVideoModel === 'SEEDANCE'
                        ? 'border-orange-500 bg-orange-500/10 text-orange-400 shadow-lg shadow-orange-900/20'
                        : 'border-slate-700 text-slate-400 hover:border-slate-600'
                        }`}
                    >
                      🔥 Seedance 2.0
                    </button>
                  </div>
                  <button
                    onClick={handleAvatarVideoGenerate}
                    disabled={isProcessing || !avatarResultImage}
                    className="w-full bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-700 hover:to-emerald-700 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2 disabled:opacity-40 shadow-lg shadow-blue-900/20 transition-all"
                  >
                    {isProcessing && avatarStep === 2 ? <Wand2 className="w-4 h-4 animate-spin" /> : <Video className="w-4 h-4" />}
                    Step 2: Generate Video ({avatarVideoModel})
                  </button>
                </div>

                {/* Video Result */}
                <div className="bg-slate-900 rounded-xl border border-slate-700 p-4 min-h-[200px] flex items-center justify-center">
                  {avatarVideoUrl ? (
                    <div className="w-full">
                      <video controls autoPlay loop src={avatarVideoUrl} className="w-full rounded-lg shadow-2xl border border-emerald-500/20" />
                      <div className="mt-3 flex justify-center">
                        <a href={avatarVideoUrl} download className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
                          <Download className="w-3 h-3" /> Download Video
                        </a>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-slate-600">
                      {isProcessing ? (
                        <div className="flex flex-col items-center animate-pulse">
                          <Film className="w-10 h-10 mb-3 text-blue-500" />
                          <p className="text-blue-400 font-medium text-sm">Generating Video...</p>
                        </div>
                      ) : (
                        <>
                          <Video className="w-10 h-10 mx-auto mb-2 opacity-20" />
                          <p className="text-sm">Video will appear here</p>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default MediaAgent;
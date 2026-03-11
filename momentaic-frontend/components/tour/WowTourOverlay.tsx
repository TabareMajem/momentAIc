import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWowTour } from './WowTourProvider';
import { X, ChevronRight, ChevronLeft, Sparkles, CheckCircle2 } from 'lucide-react';
import { Button } from '../ui/Button';

export const WowTourOverlay = () => {
    const { currentTour, currentStepIndex, nextStep, prevStep, endTour } = useWowTour();

    if (!currentTour) return null;

    const currentStep = currentTour.steps[currentStepIndex];
    const isFirstStep = currentStepIndex === 0;
    const isLastStep = currentStepIndex === currentTour.steps.length - 1;

    // Render the specific icon if provided, otherwise a generic sparkle
    const StepIcon = currentStep.icon || Sparkles;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center pointer-events-auto">
            {/* Darkened backdrop with blur to focus the user */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/60 backdrop-blur-[4px]"
                onClick={endTour}
            />

            {/* Floating Animated Modal */}
            <motion.div
                key={currentStepIndex}
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                className="relative w-full max-w-lg mx-4 bg-[#0A0A0A]/90 border border-white/10 shadow-2xl rounded-3xl overflow-hidden"
            >
                {/* Glowing Background Effect */}
                <div className="absolute top-[-50%] left-[-50%] w-[200%] h-[200%] opacity-20 pointer-events-none">
                    <div className={`absolute inset-0 rounded-full blur-[80px] bg-gradient-to-r ${currentStep.color || 'from-purple-500 to-cyan-500'} mix-blend-screen animate-pulse`} />
                </div>

                {/* Content Container */}
                <div className="relative p-8 z-10">
                    <button
                        onClick={endTour}
                        className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>

                    <div className="flex items-center gap-4 mb-6">
                        <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${currentStep.color || 'from-purple-500 to-cyan-500'} flex items-center justify-center shadow-lg`}>
                            <StepIcon className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <p className="text-xs font-mono uppercase tracking-widest text-gray-400 mb-1">
                                {currentTour.title} // {currentStepIndex + 1}/{currentTour.steps.length}
                            </p>
                            <h2 className="text-2xl font-bold text-white tracking-tight">
                                {currentStep.title}
                            </h2>
                        </div>
                    </div>

                    <p className="text-gray-300 text-lg leading-relaxed mb-8">
                        {currentStep.content}
                    </p>

                    {/* Action Buttons */}
                    <div className="flex items-center justify-between pt-4 border-t border-white/10">
                        <Button
                            variant="ghost"
                            onClick={prevStep}
                            className={`text-gray-400 hover:text-white ${isFirstStep ? 'opacity-0 pointer-events-none' : ''}`}
                        >
                            <ChevronLeft className="w-4 h-4 mr-1" /> Back
                        </Button>

                        <div className="flex gap-2 items-center">
                            <Button
                                variant="ghost"
                                onClick={endTour}
                                className="text-gray-500 hover:text-white"
                            >
                                Skip
                            </Button>
                            <Button
                                variant="default"
                                onClick={nextStep}
                                className={`bg-gradient-to-r ${currentStep.color || 'from-[#111111] to-purple-600'} border-0 shadow-lg group`}
                            >
                                {isLastStep ? (
                                    <>Complete <CheckCircle2 className="w-4 h-4 ml-2" /></>
                                ) : (
                                    <>Next <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" /></>
                                )}
                            </Button>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

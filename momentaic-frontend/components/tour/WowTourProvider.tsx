import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { WowTourOverlay } from './WowTourOverlay';
import { TOURS, TourConfig } from './tourConfigs';

interface WowTourContextType {
    isActive: boolean;
    currentTour: TourConfig | null;
    currentStepIndex: number;
    startTour: (tourId: string) => void;
    nextStep: () => void;
    prevStep: () => void;
    endTour: () => void;
}

const WowTourContext = createContext<WowTourContextType | undefined>(undefined);

export const useWowTour = () => {
    const context = useContext(WowTourContext);
    if (!context) {
        throw new Error('useWowTour must be used within a WowTourProvider');
    }
    return context;
};

export const WowTourProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isActive, setIsActive] = useState(false);
    const [currentTour, setCurrentTour] = useState<TourConfig | null>(null);
    const [currentStepIndex, setCurrentStepIndex] = useState(0);

    const startTour = useCallback((tourId: string) => {
        const tour = TOURS[tourId];
        if (!tour) {
            console.warn(`Tour with ID ${tourId} not found.`);
            return;
        }

        // Check if the user has already seen this tour
        const hasSeen = localStorage.getItem(`wow_tour_${tourId}`);
        if (hasSeen) return;

        setCurrentTour(tour);
        setCurrentStepIndex(0);
        setIsActive(true);
    }, []);

    const endTour = useCallback(() => {
        setIsActive(false);
        setTimeout(() => {
            setCurrentTour((prevTour) => {
                if (prevTour) {
                    localStorage.setItem(`wow_tour_${prevTour.id}`, 'true');
                }
                return null;
            });
            setCurrentStepIndex(0);
        }, 500); // Allow exit animations to finish
    }, []);

    const nextStep = useCallback(() => {
        setCurrentStepIndex((prev) => {
            if (currentTour && prev < currentTour.steps.length - 1) {
                return prev + 1;
            } else {
                endTour();
                return prev;
            }
        });
    }, [currentTour, endTour]);

    const prevStep = useCallback(() => {
        setCurrentStepIndex((prev) => (prev > 0 ? prev - 1 : prev));
    }, []);

    return (
        <WowTourContext.Provider
            value={{
                isActive,
                currentTour,
                currentStepIndex,
                startTour,
                nextStep,
                prevStep,
                endTour,
            }}
        >
            {children}
            {isActive && currentTour && <WowTourOverlay />}
        </WowTourContext.Provider>
    );
};

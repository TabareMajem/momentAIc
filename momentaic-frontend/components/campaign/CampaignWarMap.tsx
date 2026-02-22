import React, { useEffect, useRef, useState } from 'react';
import Globe from 'react-globe.gl';
import * as THREE from 'three';

interface Location {
    id: string;
    lat: number;
    lng: number;
    label: string;
    color: string;
}

interface CampaignWarMapProps {
    activeTargets: string[]; // e.g. ['JP', 'ES', 'EN']
    isDeploying: boolean;
}

// Base Home coordinates (San Francisco)
const HOME_BASE: Location = {
    id: 'HOME',
    lat: 37.7749,
    lng: -122.4194,
    label: 'SF_COMMAND',
    color: '#3b82f6', // blue
};

// Target Coordinates based on Language selection
const TARGET_MAP: Record<string, Location> = {
    'JP': { id: 'JP', lat: 35.6762, lng: 139.6503, label: 'TOKYO_NODE', color: '#f59e0b' }, // amber
    'ES': { id: 'ES', lat: -23.5505, lng: -46.6333, label: 'SAO_PAULO_NODE', color: '#10b981' }, // emerald
    'EN': { id: 'EN', lat: 51.5074, lng: -0.1278, label: 'LONDON_NODE', color: '#a855f7' }, // purple
};

export function CampaignWarMap({ activeTargets, isDeploying }: CampaignWarMapProps) {
    const globeRef = useRef<any>();
    const [arcs, setArcs] = useState<any[]>([]);
    const [rings, setRings] = useState<any[]>([]);

    useEffect(() => {
        if (!globeRef.current) return;

        // Optional: initial spin to show off
        globeRef.current.controls().autoRotate = true;
        globeRef.current.controls().autoRotateSpeed = 0.5;

        // Focus point when idle vs deploying
        if (isDeploying) {
            // Point globe roughly over pacific/atlantic mid point to see SF and targets
            globeRef.current.pointOfView({ lat: 20, lng: -40, altitude: 2.2 }, 2000);
        } else {
            globeRef.current.pointOfView({ lat: 37.7749, lng: -122.4194, altitude: 1.5 }, 2000);
        }
    }, [isDeploying]);

    useEffect(() => {
        if (!isDeploying) {
            setArcs([]);
            setRings([HOME_BASE]);
            return;
        }

        // Build arcs and rings based on active targets
        const newArcs: any[] = [];
        const newRings: any[] = [HOME_BASE];

        activeTargets.forEach((targetKey, idx) => {
            const target = TARGET_MAP[targetKey];
            if (target) {
                // Delay arc creation slightly per target for visual effect
                setTimeout(() => {
                    setArcs(prev => [...prev, {
                        startLat: HOME_BASE.lat,
                        startLng: HOME_BASE.lng,
                        endLat: target.lat,
                        endLng: target.lng,
                        color: [HOME_BASE.color, target.color],
                        label: target.label
                    }]);

                    setRings(prev => [...prev, target]);
                }, idx * 600);
            }
        });

        return () => {
            setArcs([]);
            setRings([HOME_BASE]);
        };
    }, [isDeploying, activeTargets]);

    // Transparent dark theme
    const globeMaterial = new THREE.MeshPhongMaterial();
    globeMaterial.color = new THREE.Color('#020202');
    globeMaterial.emissive = new THREE.Color('#111111');
    globeMaterial.emissiveIntensity = 0.5;
    globeMaterial.shininess = 50;

    return (
        <div className="w-full h-full relative cursor-move flex items-center justify-center overflow-hidden">
            <div className="absolute inset-0 bg-gradient-radial from-blue-900/10 to-transparent pointer-events-none z-10" />
            <Globe
                ref={globeRef}
                height={600}
                width={800}
                backgroundColor="rgba(0,0,0,0)"
                globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
                bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
                globeMaterial={globeMaterial}

                // Arcs configuration
                arcsData={arcs}
                arcStartLat={d => (d as any).startLat}
                arcStartLng={d => (d as any).startLng}
                arcEndLat={d => (d as any).endLat}
                arcEndLng={d => (d as any).endLng}
                arcColor={d => (d as any).color}
                arcDashLength={0.4}
                arcDashGap={0.2}
                arcDashInitialGap={() => Math.random()}
                arcDashAnimateTime={2000}
                arcAltitudeAutoScale={0.3}

                // Rings (pinging targets)
                ringsData={rings}
                ringColor={d => (d as any).color}
                ringMaxRadius={5}
                ringPropagationSpeed={3}
                ringRepeatPeriod={1000}
            />
            {/* Decorative Overlays */}
            <div className="absolute top-4 left-4 z-20 pointer-events-none">
                <div className="text-[10px] font-mono text-purple-400 opacity-70">
                    GLOBE_TELEMETRY: ACTIVE
                </div>
                <div className="text-[10px] font-mono text-blue-400 opacity-70 mt-1">
                    UPLINK: SF_COMMAND_SECURE
                </div>
            </div>
        </div>
    );
}

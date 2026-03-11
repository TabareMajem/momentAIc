
import React from 'react';

interface SkeletonProps {
    className?: string;
}

export const Skeleton = ({ className }: SkeletonProps) => {
    return (
        <div className={`animate-pulse bg-slate-800 rounded-lg ${className}`} />
    );
};

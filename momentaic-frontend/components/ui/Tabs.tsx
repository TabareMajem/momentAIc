import React, { createContext, useContext, useState } from 'react';

interface TabsContextType {
    activeTab: string;
    setActiveTab: (id: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

export const Tabs = ({ defaultValue, children, className = '' }: { defaultValue: string, children: React.ReactNode, className?: string }) => {
    const [activeTab, setActiveTab] = useState(defaultValue);
    return (
        <TabsContext.Provider value={{ activeTab, setActiveTab }}>
            <div className={className}>{children}</div>
        </TabsContext.Provider>
    );
};

export const TabsList = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => {
    return <div className={`flex gap-2 p-1 bg-black/40 border border-white/10 rounded-xl mb-6 ${className}`}>{children}</div>;
};

export const TabsTrigger = ({ value, children }: { value: string, children: React.ReactNode }) => {
    const context = useContext(TabsContext);
    const isActive = context?.activeTab === value;
    return (
        <button
            onClick={() => context?.setActiveTab(value)}
            className={`flex-1 px-4 py-2 rounded-lg text-xs font-mono uppercase tracking-widest transition-all ${isActive ? 'bg-[#00f0ff] text-black font-bold' : 'text-gray-500 hover:text-white hover:bg-white/5'
                }`}
        >
            {children}
        </button>
    );
};

export const TabsContent = ({ value, children }: { value: string, children: React.ReactNode }) => {
    const context = useContext(TabsContext);
    if (context?.activeTab !== value) return null;
    return <div className="animate-fade-in">{children}</div>;
};

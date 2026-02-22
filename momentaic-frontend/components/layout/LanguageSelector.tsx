import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

const LANGUAGES = [
    { code: 'en', label: 'English', flag: '🇺🇸' },
    { code: 'es', label: 'Español', flag: '🇪🇸' },
    { code: 'ja', label: '日本語', flag: '🇯🇵' },
    { code: 'ko', label: '한국어', flag: '🇰🇷' },
    { code: 'pt', label: 'Português', flag: '🇧🇷' },
    { code: 'fr', label: 'Français', flag: '🇫🇷' },
    { code: 'th', label: 'ไทย', flag: '🇹🇭' },
    { code: 'id', label: 'Bahasa', flag: '🇮🇩' },
];

export function LanguageSelector() {
    const { i18n } = useTranslation();

    const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newLang = e.target.value;
        i18n.changeLanguage(newLang);
        // Optional: Sync to backend API here via a dispatch or context if user model wants specific persistence
    };

    return (
        <div className="relative group flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:border-emerald-500/30 transition-colors mx-4">
            <Globe className="w-4 h-4 text-emerald-400 opacity-70 group-hover:opacity-100 transition-opacity" />
            <select
                value={i18n.language}
                onChange={handleLanguageChange}
                className="bg-transparent text-xs font-mono text-gray-300 outline-none cursor-pointer appearance-none pr-4"
                style={{ WebkitAppearance: 'none' }}
            >
                {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code} className="bg-gray-900 text-gray-300">
                        {lang.flag} {lang.label}
                    </option>
                ))}
            </select>
            {/* Down chevron icon custom overlay since appearance-none hides native */}
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
                <svg className="fill-current h-3 w-3" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                </svg>
            </div>
        </div>
    );
}

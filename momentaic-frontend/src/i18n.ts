import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import all dictionaries explicitly to bundle them without a network backend requirement
import commonEN from './locales/en/common.json';
import commonES from './locales/es/common.json';
import commonJP from './locales/jp/common.json';
import commonKO from './locales/ko/common.json';
import commonPT from './locales/pt/common.json';
import commonFR from './locales/fr/common.json';
import commonTH from './locales/th/common.json';
import commonID from './locales/id/common.json';

const resources = {
    en: { common: commonEN },
    es: { common: commonES },
    ja: { common: commonJP }, // using 'ja' as standard locale code for Japanese
    ko: { common: commonKO },
    pt: { common: commonPT },
    fr: { common: commonFR },
    th: { common: commonTH },
    id: { common: commonID },
};

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        defaultNS: 'common',
        fallbackLng: 'en',
        interpolation: {
            escapeValue: false, // react already safes from xss
        },
    });

export default i18n;

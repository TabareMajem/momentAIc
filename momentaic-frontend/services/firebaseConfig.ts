// Import the functions you need from the SDKs you need
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyCSB11SQcLTMaOfI-aSjiyDSXmIjOUBld4",
    authDomain: "bearecosystemweb.firebaseapp.com",
    projectId: "bearecosystemweb",
    storageBucket: "bearecosystemweb.firebasestorage.app",
    messagingSenderId: "299946285478",
    appId: "1:299946285478:web:a6bede84e3ba2e78345767",
    measurementId: "G-6K0EEQ2GKF"
};

// Initialize Firebase
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();

// Initialize Analytics conditionally (only client-side)
let analytics;
if (typeof window !== 'undefined') {
    isSupported().then(yes => yes && (analytics = getAnalytics(app)));
}

export { app, analytics };

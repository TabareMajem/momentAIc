import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAx5uuSihoy0LO8yxWeXhcmvSEzQPFP9eI",
    authDomain: "momentaicapp.firebaseapp.com",
    projectId: "momentaicapp",
    storageBucket: "momentaicapp.firebasestorage.app",
    messagingSenderId: "781939948391",
    appId: "1:781939948391:web:2ed149fc461be961bb4dc2",
    measurementId: "G-TH98XYS8KM"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Analytics conditionally (safely)
let analytics = null;
isSupported().then(supported => {
    if (supported) {
        analytics = getAnalytics(app);
        console.log("🔥 Firebase Analytics initialized");
    } else {
        console.warn("Firebase Analytics not supported in this environment");
    }
});

export { app, analytics };

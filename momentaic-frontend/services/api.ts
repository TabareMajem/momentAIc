import axios from 'axios';

// Use the relative path to go through Nginx to bypass CORS and HTTPS mixed content blockers
const API_URL = import.meta.env.VITE_YOKAIZEN_API_URL || '/yokaizen-api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    // Bridge: Grab the Momentaic access token
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;

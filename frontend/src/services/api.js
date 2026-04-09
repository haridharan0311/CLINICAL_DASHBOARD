import axios from 'axios';

// Create a base Axios instance pointing to your Django server
const api = axios.create({
    baseURL: 'http://localhost:8000/api/', // Change to your production URL later
    headers: {
        'Content-Type': 'application/json',
    },
});

// Intercept requests to attach the JWT token
api.interceptors.request.use(
    (config) => {
        // Assuming you store the token in localStorage upon login
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
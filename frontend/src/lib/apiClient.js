/**
 * API Client - Fresh Version
 */
import axios from 'axios';

// Use environment variable for production, fallback to localhost for development
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 10000,
});

// Token storage
const TOKEN_KEY = 'euonia_token';
const REFRESH_KEY = 'euonia_refresh';

export const getAccessToken = () => localStorage.getItem(TOKEN_KEY);
export const getRefreshToken = () => localStorage.getItem(REFRESH_KEY);

export const setTokens = (access, refresh) => {
    if (access) localStorage.setItem(TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
};

export const clearTokens = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
};

// Add token to requests
apiClient.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    // Debug logging in development
    if (import.meta.env.DEV) {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
});

// Handle 401 errors with improved refresh logic
let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (callback) => {
    refreshSubscribers.push(callback);
};

const onRefreshed = (token) => {
    refreshSubscribers.forEach(callback => callback(token));
    refreshSubscribers = [];
};

apiClient.interceptors.response.use(
    (response) => {
        if (import.meta.env.DEV) {
            console.log(`[API Response] ${response.status} ${response.config.url}`);
        }
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        if (import.meta.env.DEV) {
            console.log(`[API Error] ${error.response?.status} ${originalRequest?.url}`, error.response?.data);
        }

        // Handle 401 errors
        if (error.response?.status === 401 && !originalRequest._retry) {
            // Don't retry refresh endpoint to prevent infinite loop
            if (originalRequest.url?.includes('/auth/refresh')) {
                console.log('[Auth] Refresh token is invalid, logging out');
                clearTokens();
                window.dispatchEvent(new CustomEvent('auth-error'));
                return Promise.reject(error);
            }

            if (isRefreshing) {
                // Wait for the refresh to complete
                return new Promise((resolve) => {
                    subscribeTokenRefresh((token) => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        resolve(apiClient(originalRequest));
                    });
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;
            const refresh = getRefreshToken();

            if (refresh) {
                try {
                    console.log('[Auth] Attempting token refresh...');
                    const res = await axios.post(`${API_URL}/auth/refresh`, {}, {
                        headers: { Authorization: `Bearer ${refresh}` }
                    });
                    const newToken = res.data.access_token;
                    setTokens(newToken, null);
                    console.log('[Auth] Token refreshed successfully');
                    isRefreshing = false;
                    onRefreshed(newToken);
                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                    return apiClient(originalRequest);
                } catch (refreshError) {
                    console.log('[Auth] Refresh failed, clearing tokens and dispatching auth-error');
                    isRefreshing = false;
                    clearTokens();
                    window.dispatchEvent(new CustomEvent('auth-error'));
                    return Promise.reject(refreshError);
                }
            } else {
                console.log('[Auth] No refresh token available');
                clearTokens();
                window.dispatchEvent(new CustomEvent('auth-error'));
            }
        }
        return Promise.reject(error);
    }
);

export default apiClient;

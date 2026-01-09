/**
 * Auth Service
 */
import apiClient, { setTokens, clearTokens } from '../lib/apiClient';

export const authService = {
    register: async ({ name, email, password }) => {
        const res = await apiClient.post('/auth/register', { name, email, password });
        setTokens(res.data.access_token, res.data.refresh_token);
        return res.data;
    },

    login: async ({ email, password }) => {
        const res = await apiClient.post('/auth/login', { email, password });
        setTokens(res.data.access_token, res.data.refresh_token);
        return res.data;
    },

    logout: async () => {
        try { await apiClient.post('/auth/logout'); } catch { }
        clearTokens();
    }
};

export default authService;

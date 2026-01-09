/**
 * Session Service
 * Handles chat sessions and messages
 */
import apiClient from '../lib/apiClient';

export const sessionService = {
    /**
     * Get all sessions (paginated)
     */
    getSessions: async ({ page = 1, perPage = 20 } = {}) => {
        const response = await apiClient.get('/sessions', {
            params: { page, per_page: perPage }
        });
        return response.data;
    },

    /**
     * Get recent sessions
     */
    getRecentSessions: async (limit = 5) => {
        const response = await apiClient.get('/sessions/recent', {
            params: { limit }
        });
        return response.data;
    },

    /**
     * Create new session
     */
    createSession: async ({ title, sessionType = 'screening' } = {}) => {
        const response = await apiClient.post('/sessions/', {
            title,
            session_type: sessionType
        });
        return response.data;
    },

    /**
     * Get session by ID
     */
    getSession: async (sessionId) => {
        const response = await apiClient.get(`/sessions/${sessionId}`);
        return response.data;
    },

    /**
     * Delete session
     */
    deleteSession: async (sessionId) => {
        const response = await apiClient.delete(`/sessions/${sessionId}`);
        return response.data;
    },

    /**
     * Get session messages
     */
    getMessages: async (sessionId) => {
        const response = await apiClient.get(`/sessions/${sessionId}/messages`);
        return response.data;
    },

    /**
     * Send message and get AI response
     */
    sendMessage: async (sessionId, content) => {
        const response = await apiClient.post(`/sessions/${sessionId}/messages`, { content });
        return response.data;
    },

    /**
     * End session and generate insights
     */
    endSession: async (sessionId) => {
        const response = await apiClient.post(`/sessions/${sessionId}/end`);
        return response.data;
    },

    /**
     * Get session insights
     */
    getSessionInsights: async (sessionId) => {
        const response = await apiClient.get(`/sessions/${sessionId}/insights`);
        return response.data;
    },
};

export default sessionService;

/**
 * Insights Service
 * Handles mood trends, emotions, and AI observations
 */
import apiClient from '../lib/apiClient';

export const insightsService = {
    /**
     * Get mood trend data
     */
    getMoodTrend: async (period = 'weekly') => {
        const response = await apiClient.get('/insights/mood-trend', {
            params: { period }
        });
        return response.data;
    },

    /**
     * Get predominant emotions
     */
    getEmotions: async (period = 'weekly') => {
        const response = await apiClient.get('/insights/emotions', {
            params: { period }
        });
        return response.data;
    },

    /**
     * Get AI observations
     */
    getObservations: async ({ limit = 10, unreadOnly = false } = {}) => {
        const response = await apiClient.get('/insights/observations', {
            params: { limit, unread_only: unreadOnly }
        });
        return response.data;
    },

    /**
     * Mark observation as read
     */
    markObservationRead: async (observationId) => {
        const response = await apiClient.post(`/insights/observations/${observationId}/read`);
        return response.data;
    },
};

export default insightsService;

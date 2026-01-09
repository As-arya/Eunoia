/**
 * Screening Service
 * Handles screening flow with adaptive questions
 */
import apiClient from '../lib/apiClient';

export const screeningService = {
    /**
     * Get next question for a screening session
     */
    getNextQuestion: async (sessionId) => {
        const response = await apiClient.get(`/screening/sessions/${sessionId}/next-question`);
        return response.data;
    },

    /**
     * Submit answer and get AI empathy response
     */
    submitAnswer: async (sessionId, questionId, optionId) => {
        const response = await apiClient.post(`/screening/sessions/${sessionId}/answer`, {
            question_id: questionId,
            option_id: optionId
        });
        return response.data;
    },

    /**
     * Get session summary
     */
    getSummary: async (sessionId) => {
        const response = await apiClient.get(`/screening/sessions/${sessionId}/summary`);
        return response.data;
    },

    /**
     * End session early and get summary
     */
    endSessionEarly: async (sessionId) => {
        const response = await apiClient.post(`/screening/sessions/${sessionId}/end`);
        return response.data;
    },
};

export default screeningService;


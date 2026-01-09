/**
 * User Service
 * Handles user profile and preferences
 */
import apiClient from '../lib/apiClient';

export const userService = {
    /**
     * Get current user profile
     */
    getProfile: async () => {
        const response = await apiClient.get('/users/me');
        return response.data;
    },

    /**
     * Update user profile
     */
    updateProfile: async (data) => {
        const response = await apiClient.put('/users/me', data);
        return response.data;
    },

    /**
     * Get user preferences
     */
    getPreferences: async () => {
        const response = await apiClient.get('/users/me/preferences');
        return response.data;
    },

    /**
     * Update user preferences
     */
    updatePreferences: async (data) => {
        const response = await apiClient.put('/users/me/preferences', data);
        return response.data;
    },

    /**
     * Update avatar
     */
    updateAvatar: async (avatarUrl) => {
        const response = await apiClient.put('/users/me/avatar', { avatar_url: avatarUrl });
        return response.data;
    },
};

export default userService;

/**
 * Subscription Service
 * Handles subscription plans and billing
 */
import apiClient from '../lib/apiClient';

export const subscriptionService = {
    /**
     * Get current subscription
     */
    getCurrentSubscription: async () => {
        const response = await apiClient.get('/subscriptions/current');
        return response.data;
    },

    /**
     * Get available plans
     */
    getPlans: async () => {
        const response = await apiClient.get('/subscriptions/plans');
        return response.data;
    },

    /**
     * Subscribe to a plan
     */
    subscribe: async (planType) => {
        const response = await apiClient.post('/subscriptions/subscribe', {
            plan_type: planType
        });
        return response.data;
    },

    /**
     * Cancel subscription
     */
    cancelSubscription: async () => {
        const response = await apiClient.post('/subscriptions/cancel');
        return response.data;
    },
};

export default subscriptionService;

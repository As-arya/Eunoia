/**
 * TanStack Query Hooks for Insights
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { insightsService } from '../services';

// Query Keys
export const insightsKeys = {
    all: ['insights'],
    moodTrend: (period) => [...insightsKeys.all, 'mood-trend', period],
    emotions: (period) => [...insightsKeys.all, 'emotions', period],
    observations: (filters) => [...insightsKeys.all, 'observations', filters],
};

/**
 * Hook to get mood trend
 */
export const useMoodTrend = (period = 'weekly') => {
    return useQuery({
        queryKey: insightsKeys.moodTrend(period),
        queryFn: () => insightsService.getMoodTrend(period),
    });
};

/**
 * Hook to get predominant emotions
 */
export const useEmotions = (period = 'weekly') => {
    return useQuery({
        queryKey: insightsKeys.emotions(period),
        queryFn: () => insightsService.getEmotions(period),
    });
};

/**
 * Hook to get AI observations
 */
export const useObservations = ({ limit = 10, unreadOnly = false } = {}) => {
    return useQuery({
        queryKey: insightsKeys.observations({ limit, unreadOnly }),
        queryFn: () => insightsService.getObservations({ limit, unreadOnly }),
    });
};

/**
 * Hook to mark observation as read
 */
export const useMarkObservationRead = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: insightsService.markObservationRead,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: insightsKeys.all });
        },
    });
};

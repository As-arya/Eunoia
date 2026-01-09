/**
 * TanStack Query Hooks for Subscriptions
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { subscriptionService } from '../services';

// Query Keys
export const subscriptionKeys = {
    all: ['subscriptions'],
    current: () => [...subscriptionKeys.all, 'current'],
    plans: () => [...subscriptionKeys.all, 'plans'],
};

/**
 * Hook to get current subscription
 */
export const useCurrentSubscription = () => {
    return useQuery({
        queryKey: subscriptionKeys.current(),
        queryFn: subscriptionService.getCurrentSubscription,
    });
};

/**
 * Hook to get available plans
 */
export const useSubscriptionPlans = () => {
    return useQuery({
        queryKey: subscriptionKeys.plans(),
        queryFn: subscriptionService.getPlans,
        staleTime: 10 * 60 * 1000, // 10 minutes
    });
};

/**
 * Hook to subscribe to a plan
 */
export const useSubscribe = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: subscriptionService.subscribe,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: subscriptionKeys.current() });
        },
    });
};

/**
 * Hook to cancel subscription
 */
export const useCancelSubscription = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: subscriptionService.cancelSubscription,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: subscriptionKeys.current() });
        },
    });
};

/**
 * TanStack Query Hooks for User Profile Management
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services';

// Query Keys
export const userKeys = {
    all: ['user'],
    profile: () => [...userKeys.all, 'profile'],
    preferences: () => [...userKeys.all, 'preferences'],
};

/**
 * Hook to get current user profile
 */
export const useProfile = () => {
    return useQuery({
        queryKey: userKeys.profile(),
        queryFn: userService.getProfile,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
};

/**
 * Hook to update user profile
 */
export const useUpdateProfile = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: userService.updateProfile,
        onSuccess: (data) => {
            queryClient.setQueryData(userKeys.profile(), data);
        },
    });
};

/**
 * Hook to update avatar
 */
export const useUpdateAvatar = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: userService.updateAvatar,
        onSuccess: (data) => {
            queryClient.setQueryData(userKeys.profile(), data);
        },
    });
};

/**
 * Hook to get user preferences
 */
export const usePreferences = () => {
    return useQuery({
        queryKey: userKeys.preferences(),
        queryFn: userService.getPreferences,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
};

/**
 * Hook to update user preferences
 */
export const useUpdatePreferences = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: userService.updatePreferences,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: userKeys.preferences() });
        },
    });
};

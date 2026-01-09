/**
 * TanStack Query Hooks for Authentication
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '../services';
import { userService } from '../services';
import { getAccessToken } from '../lib/apiClient';

// Query Keys
export const authKeys = {
    user: ['auth', 'user'],
};

/**
 * Hook to get current user profile
 * Only runs if there's an access token
 */
export const useUser = () => {
    return useQuery({
        queryKey: authKeys.user,
        queryFn: userService.getProfile,
        retry: false,
        staleTime: 5 * 60 * 1000, // 5 minutes
        enabled: !!getAccessToken(), // Only fetch if token exists
    });
};

/**
 * Hook for user login
 */
export const useLogin = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: authService.login,
        onSuccess: (data) => {
            queryClient.setQueryData(authKeys.user, data.user);
        },
    });
};

/**
 * Hook for user registration
 */
export const useRegister = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: authService.register,
        onSuccess: (data) => {
            queryClient.setQueryData(authKeys.user, data.user);
        },
    });
};

/**
 * Hook for OAuth login
 */
export const useOAuthLogin = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ provider, tokenData }) => authService.oauthLogin(provider, tokenData),
        onSuccess: (data) => {
            queryClient.setQueryData(authKeys.user, data.user);
        },
    });
};

/**
 * Hook for logout
 */
export const useLogout = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: authService.logout,
        onSuccess: () => {
            queryClient.setQueryData(authKeys.user, null);
            queryClient.clear();
        },
    });
};

/**
 * Hook for forgot password
 */
export const useForgotPassword = () => {
    return useMutation({
        mutationFn: authService.forgotPassword,
    });
};

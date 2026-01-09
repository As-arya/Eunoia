/**
 * Auth Context Provider
 * Provides authentication state throughout the app using TanStack Query
 */
import React, { createContext, useContext, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useUser, useLogin, useRegister, useLogout, authKeys } from '../hooks/useAuth';
import { getAccessToken, clearTokens } from '../lib/apiClient';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const queryClient = useQueryClient();

    // Query for current user
    const {
        data: user,
        isLoading: loading,
        error: userError,
        refetch: refetchUser
    } = useUser();

    // Mutations
    const loginMutation = useLogin();
    const registerMutation = useRegister();
    const logoutMutation = useLogout();

    // Check if user is authenticated
    const isAuthenticated = !!user && !!getAccessToken();

    // Login handler
    const login = useCallback(async (email, password) => {
        const result = await loginMutation.mutateAsync({ email, password });
        return result;
    }, [loginMutation]);

    // Register handler
    const register = useCallback(async (name, email, password) => {
        const result = await registerMutation.mutateAsync({ name, email, password });
        return result;
    }, [registerMutation]);

    // Logout handler
    const logout = useCallback(async () => {
        await logoutMutation.mutateAsync();
        clearTokens();
        queryClient.clear();
    }, [logoutMutation, queryClient]);

    // Update user in cache
    const updateUser = useCallback((userData) => {
        queryClient.setQueryData(authKeys.user, (old) => ({
            ...old,
            ...userData
        }));
    }, [queryClient]);

    const value = {
        user,
        loading,
        error: userError || loginMutation.error || registerMutation.error,
        isAuthenticated,
        login,
        register,
        logout,
        updateUser,
        refetchUser,
        isLoggingIn: loginMutation.isPending,
        isRegistering: registerMutation.isPending,
        isLoggingOut: logoutMutation.isPending,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;

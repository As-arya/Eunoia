/**
 * TanStack Query Hooks for Chat Sessions
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { sessionService } from '../services';

// Query Keys
export const sessionKeys = {
    all: ['sessions'],
    lists: () => [...sessionKeys.all, 'list'],
    list: (filters) => [...sessionKeys.lists(), filters],
    recent: () => [...sessionKeys.all, 'recent'],
    details: () => [...sessionKeys.all, 'detail'],
    detail: (id) => [...sessionKeys.details(), id],
    messages: (id) => [...sessionKeys.detail(id), 'messages'],
    insights: (id) => [...sessionKeys.detail(id), 'insights'],
};

/**
 * Hook to get all sessions (paginated)
 */
export const useSessions = ({ page = 1, perPage = 20 } = {}) => {
    return useQuery({
        queryKey: sessionKeys.list({ page, perPage }),
        queryFn: () => sessionService.getSessions({ page, perPage }),
    });
};

/**
 * Hook to get recent sessions
 */
export const useRecentSessions = (limit = 5) => {
    return useQuery({
        queryKey: sessionKeys.recent(),
        queryFn: () => sessionService.getRecentSessions(limit),
    });
};

/**
 * Hook to get single session
 */
export const useSession = (sessionId) => {
    return useQuery({
        queryKey: sessionKeys.detail(sessionId),
        queryFn: () => sessionService.getSession(sessionId),
        enabled: !!sessionId,
    });
};

/**
 * Hook to get session messages
 */
export const useSessionMessages = (sessionId) => {
    return useQuery({
        queryKey: sessionKeys.messages(sessionId),
        queryFn: () => sessionService.getMessages(sessionId),
        enabled: !!sessionId,
    });
};

/**
 * Hook to get session insights
 */
export const useSessionInsights = (sessionId) => {
    return useQuery({
        queryKey: sessionKeys.insights(sessionId),
        queryFn: () => sessionService.getSessionInsights(sessionId),
        enabled: !!sessionId,
    });
};

/**
 * Hook to create new session
 */
export const useCreateSession = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: sessionService.createSession,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: sessionKeys.lists() });
            queryClient.invalidateQueries({ queryKey: sessionKeys.recent() });
        },
    });
};

/**
 * Hook to send message
 */
export const useSendMessage = (sessionId) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (content) => sessionService.sendMessage(sessionId, content),
        onSuccess: (data) => {
            // Optimistically update messages
            queryClient.setQueryData(sessionKeys.messages(sessionId), (old) => ({
                ...old,
                messages: [...(old?.messages || []), data.user_message, data.ai_response],
            }));
        },
    });
};

/**
 * Hook to end session
 */
export const useEndSession = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: sessionService.endSession,
        onSuccess: (_, sessionId) => {
            queryClient.invalidateQueries({ queryKey: sessionKeys.detail(sessionId) });
            queryClient.invalidateQueries({ queryKey: sessionKeys.insights(sessionId) });
        },
    });
};

/**
 * Hook to delete session
 */
export const useDeleteSession = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: sessionService.deleteSession,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: sessionKeys.lists() });
            queryClient.invalidateQueries({ queryKey: sessionKeys.recent() });
        },
    });
};

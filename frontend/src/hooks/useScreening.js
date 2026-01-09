/**
 * TanStack Query Hooks for Screening Flow
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { screeningService } from '../services';

// Query Keys
export const screeningKeys = {
    all: ['screening'],
    nextQuestion: (sessionId) => [...screeningKeys.all, 'next-question', sessionId],
    summary: (sessionId) => [...screeningKeys.all, 'summary', sessionId],
};

/**
 * Hook to get next adaptive question
 */
export const useNextQuestion = (sessionId) => {
    return useQuery({
        queryKey: screeningKeys.nextQuestion(sessionId),
        queryFn: () => screeningService.getNextQuestion(sessionId),
        enabled: !!sessionId,
        staleTime: 0, // Always fetch fresh question
    });
};

/**
 * Hook to submit answer and get AI empathy response
 */
export const useSubmitAnswer = (sessionId) => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ questionId, optionId }) =>
            screeningService.submitAnswer(sessionId, questionId, optionId),
        onSuccess: () => {
            // Invalidate next question to fetch the new one
            queryClient.invalidateQueries({ queryKey: screeningKeys.nextQuestion(sessionId) });
        },
    });
};

/**
 * Hook to get session summary
 */
export const useScreeningSummary = (sessionId) => {
    return useQuery({
        queryKey: screeningKeys.summary(sessionId),
        queryFn: () => screeningService.getSummary(sessionId),
        enabled: !!sessionId,
    });
};

import React from 'react'
import { useRecentSessions } from '../hooks/useSessions'

const ConversationCard = ({ icon, time, title, subtitle, onClick }) => (
    <div
        onClick={onClick}
        style={{
            backgroundColor: '#162225',
            border: '1px solid #1f3236',
            borderRadius: '20px',
            padding: '16px',
            minWidth: '160px',
            flex: '1',
            textAlign: 'left',
            cursor: 'pointer'
        }}
    >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <div style={{ fontSize: '24px' }}>{icon}</div>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{time}</span>
        </div>

        <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '8px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{title}</h4>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.4', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
            {subtitle}
        </p>
    </div>
)

// Mood to emoji mapping - comprehensive mapping for all emotion tags
const moodEmojis = {
    // Positive emotions
    happy: '😊',
    stable: '😊',
    energetic: '⚡',
    confident: '💪',
    rested: '😴',
    functional: '✨',
    productive: '🎯',
    connected: '❤️',
    supported: '🤝',
    resourceful: '🌟',
    resilient: '💪',
    social: '👥',
    calm: '😌',
    relaxed: '😌',
    focused: '🎯',
    clear: '💡',
    managed: '✅',
    open: '🌱',
    even_tempered: '😊',
    balanced: '⚖️',

    // Anxiety emotions
    anxious: '😰',
    severely_anxious: '😰',
    occasionally_anxious: '😟',
    worried: '😟',
    somewhat_worried: '😟',
    overwhelmed_by_worry: '😰',
    tense: '😬',
    very_tense: '😬',
    cannot_relax: '😣',
    uneasy: '😕',
    catastrophizing: '😰',

    // Sad emotions
    sad: '😢',
    occasionally_sad: '😔',
    depressed: '😢',
    low: '😢',
    lonely: '😔',
    very_lonely: '😢',
    occasionally_lonely: '😔',
    guilty: '😔',
    worthless: '😢',
    self_doubt: '😔',

    // Stress emotions
    stressed: '😓',
    stress: '😓',
    sometimes_busy: '😅',
    strained: '😣',
    conflicted: '😕',
    affected: '😓',
    mildly_affected: '😕',
    severely_affected: '😫',

    // Tired emotions
    tired: '😴',
    fatigued: '😩',
    exhausted: '😫',
    severely_fatigued: '😫',
    disturbed_sleep: '😴',
    insomnia: '🌙',

    // Overwhelmed emotions
    overwhelmed: '😫',
    distressed: '😰',
    scattered: '🤯',
    unfocused: '😵‍💫',
    distracted: '🤔',
    foggy: '🌫️',
    confused: '😵',
    moderate_difficulty: '😓',
    severe_difficulty: '😫',
    mild_difficulty: '😕',

    // Angry emotions
    angry: '😠',
    irritable: '😤',
    very_irritable: '😡',
    occasionally_irritable: '😤',

    // Hopeless/Isolated emotions
    hopeless: '😢',
    isolated: '😔',
    limited_support: '😕',
    withdrawn: '😶',
    avoiding: '😶',
    occasionally_avoiding: '😕',
    limited_coping: '😓',
    no_coping: '😢',
    low_resilience: '😔',
    not_resilient: '😢',
    ambivalent: '😕',
    resistant: '😤',
    dismissive: '😒',

    // Neutral/Default
    neutral: '😐',
    coping: '😊',
    somewhat_supported: '🙂',
    hopeful: '🌟',
    default: '💬'
}

// Helper to format relative time
const formatRelativeTime = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays === 1) return 'Yesterday'
    return `${diffDays} days ago`
}

const RecentConversations = ({ onViewSession, onViewAll }) => {
    const { data, isLoading } = useRecentSessions(5)

    // Use real data only - no demo fallback
    const sessions = data?.sessions || []

    return (
        <div style={{ marginBottom: '32px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Recent Conversations</h3>
                <button onClick={onViewAll} style={{ color: '#5eead4', fontSize: '14px', background: 'none', border: 'none', cursor: 'pointer' }}>View all</button>
            </div>

            <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', paddingBottom: '12px' }}>
                {isLoading ? (
                    <div style={{ color: 'var(--text-secondary)', padding: '20px' }}>Loading...</div>
                ) : sessions.length > 0 ? (
                    sessions.map(session => (
                        <div key={session.id} style={{ minWidth: '160px' }}>
                            <ConversationCard
                                icon={moodEmojis[(session.mood || '').toLowerCase()] || moodEmojis.default}
                                time={formatRelativeTime(session.started_at || session.created_at)}
                                title={session.title || 'Screening Session'}
                                subtitle={session.summary || 'Chat conversation'}
                                onClick={() => onViewSession && onViewSession(session.id)}
                            />
                        </div>
                    ))
                ) : (
                    <div style={{
                        color: 'var(--text-secondary)',
                        padding: '24px',
                        textAlign: 'center',
                        width: '100%',
                        backgroundColor: '#162225',
                        borderRadius: '20px',
                        border: '1px solid #1f3236'
                    }}>
                        <p style={{ marginBottom: '8px' }}>No conversations yet</p>
                        <p style={{ fontSize: '13px' }}>Start a chat to see your history here!</p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default RecentConversations

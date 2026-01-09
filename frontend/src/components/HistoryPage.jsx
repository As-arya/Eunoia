import React from 'react'
import HistoryHeader from './HistoryHeader'
import HistoryItem from './HistoryItem'
import DeepInsightsCard from './DeepInsightsCard'
import { Smile, Frown, Moon, Briefcase, Heart, MessageCircle } from 'lucide-react'
import { useSessions } from '../hooks/useSessions'

// Helper to format date groups
const groupSessionsByDate = (sessions) => {
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    const groups = {
        today: [],
        yesterday: [],
        lastWeek: [],
        older: []
    }

    sessions.forEach(session => {
        const sessionDate = new Date(session.created_at || session.started_at)
        const diffDays = Math.floor((today - sessionDate) / (1000 * 60 * 60 * 24))

        if (diffDays === 0) {
            groups.today.push(session)
        } else if (diffDays === 1) {
            groups.yesterday.push(session)
        } else if (diffDays <= 7) {
            groups.lastWeek.push(session)
        } else {
            groups.older.push(session)
        }
    })

    return groups
}

// Icon mapping by mood
const getMoodIcon = (mood) => {
    const moodLower = (mood || '').toLowerCase()
    const icons = {
        happy: <Smile size={20} color="#2bfdb8" />,
        calm: <Smile size={20} color="#22c55e" />,
        anxious: <Frown size={20} color="#fbbf24" />,
        sad: <Moon size={20} color="#a78bfa" />,
        stressed: <Briefcase size={20} color="#f472b6" />,
        stress: <Briefcase size={20} color="#f472b6" />,
        grateful: <Heart size={20} color="#60a5fa" />,
        neutral: <MessageCircle size={20} color="#8da3a6" />,
        default: <MessageCircle size={20} color="#8da3a6" />
    }
    return icons[moodLower] || icons.default
}

const getMoodColor = (mood) => {
    const moodLower = (mood || '').toLowerCase()
    const colors = {
        happy: '#2bfdb8',
        calm: '#22c55e',
        anxious: '#fbbf24',
        sad: '#a78bfa',
        stressed: '#f472b6',
        stress: '#f472b6',
        grateful: '#60a5fa',
        neutral: '#8da3a6',
        default: '#8da3a6'
    }
    return colors[moodLower] || colors.default
}

const formatTime = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
}

const formatDuration = (minutes) => {
    if (!minutes) return ''
    return `${minutes} min`
}

const HistoryPage = ({ onBack, onViewSession, onUpgrade }) => {
    const { data, isLoading } = useSessions()

    // Use real data only - no demo fallback
    const sessions = data?.sessions || []
    const grouped = groupSessionsByDate(sessions)

    return (
        <div>
            <HistoryHeader onBack={onBack} />

            {isLoading ? (
                <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '40px' }}>Loading...</div>
            ) : (
                <>
                    {/* TODAY SECTION */}
                    {grouped.today.length > 0 && (
                        <>
                            <h2 style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '16px', letterSpacing: '0.05em' }}>TODAY</h2>
                            {grouped.today.map(session => (
                                <HistoryItem
                                    key={session.id}
                                    icon={getMoodIcon(session.mood)}
                                    title={session.title || 'Screening Session'}
                                    description={session.summary || 'Chat session'}
                                    time={formatTime(session.started_at || session.created_at)}
                                    duration={formatDuration(session.duration)}
                                    moodColor={getMoodColor(session.mood)}
                                    onClick={() => onViewSession(session.id)}
                                />
                            ))}
                        </>
                    )}

                    {/* YESTERDAY SECTION */}
                    {grouped.yesterday.length > 0 && (
                        <>
                            <h2 style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, marginTop: '32px', marginBottom: '16px', letterSpacing: '0.05em' }}>YESTERDAY</h2>
                            {grouped.yesterday.map(session => (
                                <HistoryItem
                                    key={session.id}
                                    icon={getMoodIcon(session.mood)}
                                    title={session.title || 'Screening Session'}
                                    description={session.summary || 'Chat session'}
                                    time={formatTime(session.started_at || session.created_at)}
                                    duration={formatDuration(session.duration)}
                                    moodColor={getMoodColor(session.mood)}
                                    onClick={() => onViewSession(session.id)}
                                />
                            ))}
                        </>
                    )}

                    <DeepInsightsCard onUpgrade={onUpgrade} />

                    {/* LAST WEEK SECTION */}
                    {grouped.lastWeek.length > 0 && (
                        <>
                            <h2 style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '16px', letterSpacing: '0.05em' }}>LAST WEEK</h2>
                            {grouped.lastWeek.map(session => (
                                <HistoryItem
                                    key={session.id}
                                    icon={getMoodIcon(session.mood)}
                                    title={session.title || 'Screening Session'}
                                    description={session.summary || 'Chat session'}
                                    time={new Date(session.started_at || session.created_at).toLocaleDateString('en-US', { weekday: 'short' })}
                                    duration={formatDuration(session.duration)}
                                    moodColor={getMoodColor(session.mood)}
                                    onClick={() => onViewSession(session.id)}
                                />
                            ))}
                        </>
                    )}

                    {/* OLDER SECTION */}
                    {grouped.older.length > 0 && (
                        <>
                            <h2 style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, marginTop: '32px', marginBottom: '16px', letterSpacing: '0.05em' }}>OLDER</h2>
                            {grouped.older.map(session => (
                                <HistoryItem
                                    key={session.id}
                                    icon={getMoodIcon(session.mood)}
                                    title={session.title || 'Screening Session'}
                                    description={session.summary || 'Chat session'}
                                    time={new Date(session.started_at || session.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })}
                                    duration={formatDuration(session.duration)}
                                    moodColor={getMoodColor(session.mood)}
                                    onClick={() => onViewSession(session.id)}
                                />
                            ))}
                        </>
                    )}

                    {/* Empty state */}
                    {sessions.length === 0 && (
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                            <p>No conversation history yet.</p>
                            <p style={{ fontSize: '14px' }}>Start a chat to see your history here.</p>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

export default HistoryPage

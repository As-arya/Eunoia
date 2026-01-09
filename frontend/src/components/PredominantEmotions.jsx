import React from 'react'
import { useEmotions } from '../hooks/useInsights'

const EmotionCard = ({ emoji, label, percentage, periodLabel }) => (
    <div style={{
        backgroundColor: '#162225',
        border: '1px solid #1f3236',
        borderRadius: '20px',
        padding: '16px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        flex: 1
    }}>
        <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            backgroundColor: '#1f2937',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px'
        }}>
            {emoji}
        </div>
        <div>
            <div style={{ fontWeight: 600, fontSize: '15px', color: 'white' }}>{label}</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{percentage}% {periodLabel}</div>
        </div>
    </div>
)

// Emotion to emoji mapping (lowercase keys for case-insensitive matching)
const emotionEmojis = {
    // Basic emotions
    calm: '😌',
    anxious: '😰',
    happy: '😊',
    sad: '😢',
    angry: '😠',
    stressed: '😓',
    hopeful: '🌟',
    neutral: '😐',
    // Extended emotions from screening
    stable: '😊',
    depressed: '😢',
    tired: '😓',
    exhausted: '😩',
    rested: '😴',
    energetic: '⚡',
    fatigued: '😓',
    confident: '💪',
    guilty: '😔',
    worthless: '😢',
    focused: '🎯',
    distracted: '🤔',
    overwhelmed: '😰',
    stress: '😓',
    relaxed: '😌',
    tense: '😬',
    irritable: '😠',
    connected: '❤️',
    lonely: '😔',
    isolated: '😢',
    supported: '🤝',
    distressed: '😰',
    low: '😢',
    // Occasionally variants
    occasionally_sad: '😔',
    occasionally_anxious: '😟',
    occasionally_lonely: '😔',
    occasionally_irritable: '😐'
}

const PredominantEmotions = ({ period = 'weekly' }) => {
    const { data, isLoading } = useEmotions(period)

    // Fallback demo data
    const demoEmotions = [
        { emotion: 'calm', percentage: 42 },
        { emotion: 'anxious', percentage: 18 }
    ]

    const emotions = data?.emotions || demoEmotions

    // Dynamic period label
    const periodLabel = {
        daily: 'hari ini',
        weekly: 'of week',
        monthly: 'of month'
    }[period] || 'of week'

    return (
        <div style={{ marginBottom: '32px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>Predominant Emotions</h3>
            <div style={{ display: 'flex', gap: '16px' }}>
                {isLoading ? (
                    <div style={{ color: 'var(--text-secondary)' }}>Loading...</div>
                ) : (
                    emotions.slice(0, 2).map((item, i) => {
                        const emotionName = item.emotion || item.name || 'neutral';
                        return (
                            <EmotionCard
                                key={i}
                                emoji={emotionEmojis[emotionName.toLowerCase()] || '😐'}
                                label={emotionName.charAt(0).toUpperCase() + emotionName.slice(1)}
                                percentage={item.percentage || 0}
                                periodLabel={periodLabel}
                            />
                        );
                    })
                )}
            </div>
        </div>
    )
}

export default PredominantEmotions

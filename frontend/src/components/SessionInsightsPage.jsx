import React, { useState, useEffect } from 'react'
import { ChevronLeft, Share2, Calendar, Smile, Brain, Wind, AlertTriangle, Lightbulb, Sparkles, MessageSquare, Loader2 } from 'lucide-react'
import { sessionService } from '../services'

const MoodTag = ({ icon, label, active = false }) => (
    <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '8px 16px',
        borderRadius: '999px',
        backgroundColor: active ? '#162225' : '#162225',
        border: '1px solid #1f3236',
        fontSize: '13px',
        fontWeight: 500
    }}>
        {icon}
        {label}
    </div>
)

const InsightCard = ({ icon, iconBg, title, description }) => (
    <div style={{
        backgroundColor: '#162225',
        borderRadius: '20px',
        padding: '20px',
        marginBottom: '16px',
        border: '1px solid #1f3236',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '16px',
        textAlign: 'left'
    }}>
        <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '16px',
            backgroundColor: iconBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
        }}>
            {icon}
        </div>
        <div>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>{title}</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>{description}</p>
        </div>
    </div>
)

const SessionInsightsPage = ({ sessionId, onBack, onContinueChat }) => {
    const [session, setSession] = useState(null)
    const [insights, setInsights] = useState(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            if (!sessionId) {
                setIsLoading(false)
                return
            }

            try {
                const [sessionData, insightsData] = await Promise.all([
                    sessionService.getSession(sessionId),
                    sessionService.getSessionInsights(sessionId)
                ])
                setSession(sessionData)
                setInsights(insightsData)
            } catch (error) {
                console.error('Failed to fetch session data:', error)
            } finally {
                setIsLoading(false)
            }
        }

        fetchData()
    }, [sessionId])

    // Format date
    const formatDate = (dateString) => {
        if (!dateString) return 'Recent Session'
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        }) + ' • ' + date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        })
    }

    // Get mood icon
    const getMoodIcon = (mood) => {
        const moodLower = (mood || '').toLowerCase()
        if (moodLower.includes('calm') || moodLower.includes('happy')) return <Smile size={16} color="#2bfdb8" />
        if (moodLower.includes('anxious') || moodLower.includes('stress')) return <Wind size={16} color="#fbbf24" />
        return <Brain size={16} color="#2bfdb8" />
    }

    if (isLoading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
                <Loader2 size={32} color="#2bfdb8" style={{ animation: 'spin 1s linear infinite' }} />
            </div>
        )
    }

    // Use fetched data or fallbacks for display
    const sessionDate = session?.started_at || session?.created_at || insights?.created_at
    const duration = session?.duration || insights?.questions_answered || 0
    const mood = insights?.overall_mood || session?.mood || 'Neutral'
    const summary = insights?.summary || session?.summary || 'No summary available for this session.'
    const primaryTrigger = insights?.primary_emotion || insights?.primary_trigger || 'No trigger identified'
    const recommendation = insights?.recommendation || 'Keep exploring your thoughts'
    const moodImprovement = insights?.mood_improvement || 0
    const keyInsights = insights?.key_insights || []
    const wellnessScore = insights?.wellness_score || 50

    return (
        <div style={{ paddingBottom: '100px' }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '24px',
                paddingTop: '16px'
            }}>
                <button onClick={onBack} style={{ backgroundColor: 'transparent', color: 'white' }}>
                    <ChevronLeft size={24} />
                </button>
                <h1 style={{ fontSize: '18px', fontWeight: 600 }}>Session Insights</h1>
                <button style={{ backgroundColor: 'transparent', color: 'white' }}>
                    <Share2 size={20} />
                </button>
            </div>

            {/* Date & Duration */}
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <div style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    backgroundColor: '#162225',
                    padding: '8px 16px',
                    borderRadius: '999px',
                    border: '1px solid #1f3236',
                    fontSize: '13px',
                    color: 'var(--text-secondary)',
                    marginBottom: '8px'
                }}>
                    <Calendar size={14} color="#2bfdb8" />
                    {formatDate(sessionDate)}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)', letterSpacing: '0.05em' }}>
                    {duration > 0 ? `${duration} MIN SESSION` : 'SESSION COMPLETE'}
                </div>
            </div>

            {/* Mood Tags */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', marginBottom: '32px' }}>
                <MoodTag icon={getMoodIcon(mood)} label={mood} />
            </div>

            {/* Emotional Journey Chart */}
            <div style={{
                backgroundColor: '#162225',
                borderRadius: '20px',
                padding: '20px',
                marginBottom: '24px',
                border: '1px solid #1f3236'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ width: '4px', height: '20px', backgroundColor: '#2bfdb8', borderRadius: '2px' }}></span>
                        Emotional Journey
                    </h3>
                    {moodImprovement !== 0 && (
                        <span style={{
                            backgroundColor: moodImprovement > 0 ? 'rgba(43, 253, 184, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            color: moodImprovement > 0 ? '#2bfdb8' : '#ef4444',
                            padding: '4px 12px',
                            borderRadius: '999px',
                            fontSize: '12px',
                            fontWeight: 600
                        }}>{moodImprovement > 0 ? '+' : ''}{moodImprovement}% {moodImprovement > 0 ? 'Improved' : 'Change'}</span>
                    )}
                </div>

                {/* Dynamic SVG Chart based on score */}
                <svg viewBox="0 0 280 80" style={{ width: '100%', height: '80px', marginBottom: '12px' }} preserveAspectRatio="xMidYMid meet">
                    <defs>
                        <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#2bfdb8" stopOpacity="0.3" />
                            <stop offset="100%" stopColor="#2bfdb8" stopOpacity="0" />
                        </linearGradient>
                    </defs>
                    {/* Background grid */}
                    <line x1="0" y1="20" x2="280" y2="20" stroke="#1f3236" strokeWidth="0.5" strokeDasharray="4" />
                    <line x1="0" y1="40" x2="280" y2="40" stroke="#1f3236" strokeWidth="0.5" strokeDasharray="4" />
                    <line x1="0" y1="60" x2="280" y2="60" stroke="#1f3236" strokeWidth="0.5" strokeDasharray="4" />

                    {/* Dynamic path based on mood - FIXED to reach endpoints */}
                    {(() => {
                        // Calculate end Y position based on score (lower score = higher position = more positive)
                        const score = insights?.score ?? 15;
                        const maxScore = 75; // Typically max is around 75 for 25 questions
                        const normalizedScore = Math.min(score / maxScore, 1);

                        // Start position (left side, neutral-ish position)
                        const startX = 0;
                        const startY = 50; // Middle area

                        // End position (right side, based on final mood)
                        const endX = 280;
                        const endY = 15 + (normalizedScore * 50); // 15-65 range (higher score = lower position = worse mood)

                        // Create intermediate points for a smooth journey
                        const point1X = 70;
                        const point1Y = startY - 5 + (normalizedScore * 10);

                        const point2X = 140;
                        const point2Y = (startY + endY) / 2 + ((score % 10) - 5); // Add some variation

                        const point3X = 210;
                        const point3Y = endY + 8 - (normalizedScore * 5);

                        // Build smooth cubic bezier path that DEFINITELY reaches the end
                        const path = `M${startX},${startY} ` +
                            `C${point1X - 20},${startY - 3} ${point1X - 10},${point1Y} ${point1X},${point1Y} ` +
                            `S${point2X - 20},${point2Y} ${point2X},${point2Y} ` +
                            `S${point3X - 20},${point3Y} ${point3X},${point3Y} ` +
                            `S${endX - 20},${endY} ${endX},${endY}`;

                        // Create fill path (closed at bottom)
                        const fillPath = `${path} L${endX},80 L${startX},80 Z`;

                        return (
                            <>
                                {/* Gradient fill under the curve */}
                                <path d={fillPath} fill="url(#chartGradient)" />
                                {/* Main line */}
                                <path
                                    d={path}
                                    fill="none"
                                    stroke="#2bfdb8"
                                    strokeWidth="2.5"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                                {/* End point indicator */}
                                <circle cx={endX} cy={endY} r="6" fill="#2bfdb8" />
                                <circle cx={endX} cy={endY} r="3" fill="#102220" />
                                {/* Start point indicator */}
                                <circle cx={startX} cy={startY} r="5" fill="#6b7280" />
                                <circle cx={startX} cy={startY} r="2" fill="#1f3236" />
                            </>
                        );
                    })()}
                </svg>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)' }}>
                    <span>START</span>
                    <span>END ({mood.toUpperCase()})</span>
                </div>
            </div>

            {/* Summary Card */}
            <div style={{
                backgroundColor: '#162225',
                borderRadius: '20px',
                padding: '20px',
                marginBottom: '24px',
                border: '1px solid #1f3236',
                textAlign: 'left'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <Sparkles size={20} color="#2bfdb8" />
                    <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Summary</h3>
                </div>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                    {summary}
                </p>
            </div>

            {/* Key Insights */}
            <h2 style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '16px', letterSpacing: '0.05em' }}>KEY INSIGHTS</h2>

            {keyInsights.length > 0 ? (
                keyInsights.map((insight, index) => (
                    <InsightCard
                        key={index}
                        icon={<span style={{ fontSize: '24px' }}>{insight.icon || '💡'}</span>}
                        iconBg={index === 0 ? 'rgba(249, 115, 22, 0.1)' : index === 1 ? 'rgba(167, 139, 250, 0.1)' : 'rgba(43, 253, 184, 0.1)'}
                        title={insight.title || 'Insight'}
                        description={insight.description || 'No description'}
                    />
                ))
            ) : (
                <>
                    <InsightCard
                        icon={<AlertTriangle size={24} color="#f97316" />}
                        iconBg="rgba(249, 115, 22, 0.1)"
                        title="Primary Emotion"
                        description={primaryTrigger}
                    />
                    <InsightCard
                        icon={<Lightbulb size={24} color="#a78bfa" />}
                        iconBg="rgba(167, 139, 250, 0.1)"
                        title="Recommendation"
                        description={recommendation}
                    />
                </>
            )}

            {/* Continue Button */}
            <div style={{
                position: 'fixed',
                bottom: '100px',
                left: '50%',
                transform: 'translateX(-50%)',
                width: 'calc(100% - 48px)',
                maxWidth: '432px'
            }}>
                <button
                    onClick={onContinueChat}
                    style={{
                        width: '100%',
                        padding: '16px',
                        borderRadius: '999px',
                        backgroundColor: '#162225',
                        border: '1px solid #1f3236',
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '15px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        cursor: 'pointer'
                    }}
                >
                    <MessageSquare size={18} />
                    Continue Conversation
                </button>
            </div>

            <style>{`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    )
}

export default SessionInsightsPage

import React, { useState, useEffect, useRef } from 'react'
import { ChevronLeft, History, Loader2, AlertCircle, BarChart2, Home, X, LogOut } from 'lucide-react'
import { sessionService, screeningService } from '../services'

const MessageBubble = ({ sender, content, time, isUser = false }) => (
    <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px'
    }}>
        {!isUser && (
            <span style={{
                fontSize: '11px',
                color: 'var(--text-secondary)',
                marginLeft: '4px',
                marginBottom: '4px'
            }}>
                {sender}
            </span>
        )}
        <div style={{
            maxWidth: '85%',
            padding: '12px 16px',
            borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
            backgroundColor: isUser ? '#2bfdb8' : '#283937',
            color: isUser ? '#102220' : 'white',
            fontSize: '15px',
            lineHeight: '1.5',
            fontWeight: isUser ? 500 : 400,
            border: isUser ? 'none' : '1px solid rgba(255, 255, 255, 0.05)',
            whiteSpace: 'pre-wrap',
            textAlign: 'left'
        }}>
            {content}
        </div>
        {time && (
            <span style={{
                fontSize: '10px',
                color: 'var(--text-secondary)',
                marginTop: '4px',
                marginRight: isUser ? '4px' : 0
            }}>
                {time}
            </span>
        )}
    </div>
)

const OptionButton = ({ text, selected, onClick, disabled }) => (
    <button
        onClick={onClick}
        disabled={disabled}
        style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px',
            borderRadius: '16px',
            backgroundColor: '#1A2C2A',
            border: selected ? '1px solid #2bfdb8' : '1px solid rgba(255, 255, 255, 0.1)',
            color: 'white',
            fontSize: '15px',
            fontWeight: 500,
            textAlign: 'left',
            cursor: disabled ? 'not-allowed' : 'pointer',
            marginBottom: '12px',
            transition: 'all 0.2s ease',
            opacity: disabled ? 0.6 : 1
        }}
    >
        <span>{text}</span>
        <div style={{
            width: '24px',
            height: '24px',
            borderRadius: '50%',
            border: selected ? '2px solid #2bfdb8' : '2px solid rgba(255, 255, 255, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease'
        }}>
            {selected && (
                <div style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: '#2bfdb8'
                }}></div>
            )}
        </div>
    </button>
)

const ChatPage = ({ onBack, onHistory, onSessionComplete }) => {
    const [sessionId, setSessionId] = useState(null)
    const [messages, setMessages] = useState([])
    const [currentQuestion, setCurrentQuestion] = useState(null)
    const [selectedOption, setSelectedOption] = useState(null)
    const [progress, setProgress] = useState('1/25')
    const [isLoading, setIsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isComplete, setIsComplete] = useState(false)
    const [error, setError] = useState(null)
    const [completedSummary, setCompletedSummary] = useState(null)
    const [showEndConfirm, setShowEndConfirm] = useState(false)
    const [isEnding, setIsEnding] = useState(false)
    const [answeredCount, setAnsweredCount] = useState(0)
    const messagesEndRef = useRef(null)
    const hasInitialized = useRef(false) // Prevent double initialization in StrictMode

    // Handle end session early
    const handleEndSession = async () => {
        if (isEnding || !sessionId) return

        setIsEnding(true)
        setError(null)

        try {
            const result = await screeningService.endSessionEarly(sessionId)

            if (result.error) {
                setError(result.error)
                setIsEnding(false)
                setShowEndConfirm(false)
                return
            }

            setIsComplete(true)
            setCompletedSummary(result)
            setShowEndConfirm(false)

            setMessages(prev => [...prev, {
                sender: 'Eunoia',
                content: `🎯 Sesi telah diakhiri!\n\n${result.summary || 'Terima kasih sudah berbagi.'}\n\n💡 ${result.recommendation || 'Jaga kesehatan mentalmu!'}`,
                isUser: false
            }])
        } catch (err) {
            console.error('Failed to end session:', err)
            setError(err.response?.data?.error || 'Gagal mengakhiri sesi. Silakan coba lagi.')
        }

        setIsEnding(false)
    }

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    // Initialize session
    useEffect(() => {
        // Prevent double initialization in React StrictMode
        if (hasInitialized.current) return
        hasInitialized.current = true

        const initSession = async () => {
            setIsLoading(true)
            setError(null)

            try {
                // Create new session
                console.log('Creating session...')
                const session = await sessionService.createSession({
                    title: `Sesi ${new Date().toLocaleDateString('id-ID')}`,
                    sessionType: 'screening'
                })
                console.log('Session created:', session)
                setSessionId(session.id)

                // Get first question
                console.log('Getting first question for session:', session.id)
                const questionData = await screeningService.getNextQuestion(session.id)
                console.log('Question data:', questionData)

                if (questionData.status === 'ongoing' && questionData.question) {
                    setCurrentQuestion(questionData.question)
                    setProgress(questionData.progress || '1/25')
                    setAnsweredCount(0)
                    // Add welcome message AND first question together
                    setMessages([
                        {
                            sender: 'Eunoia',
                            content: 'Halo! Saya Eunoia, teman bicaramu. Mari kita mulai dengan beberapa pertanyaan untuk memahami perasaanmu hari ini. 💙',
                            isUser: false
                        },
                        {
                            sender: 'Eunoia',
                            content: questionData.question.text,
                            isUser: false
                        }
                    ])
                }

                setIsLoading(false)
            } catch (err) {
                console.error('Failed to init session:', err)
                setError(err.response?.data?.error || 'Gagal memulai sesi. Silakan coba lagi.')
                setIsLoading(false)
            }
        }

        initSession()
    }, [])

    // Handle answer submission
    const handleSubmitAnswer = async () => {
        if (!selectedOption || !currentQuestion || isSubmitting) return

        setIsSubmitting(true)
        setError(null)

        const selectedOptionData = currentQuestion.options.find(o => o.id === selectedOption)

        // Add user message
        setMessages(prev => [...prev, {
            sender: 'User',
            content: selectedOptionData.text,
            isUser: true,
            time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
        }])

        try {
            // Submit answer
            const answerResult = await screeningService.submitAnswer(
                sessionId,
                currentQuestion.id,
                selectedOption
            )

            // Get next question
            const nextData = await screeningService.getNextQuestion(sessionId)

            if (nextData.status === 'completed') {
                // Add AI empathy response separately for completion
                if (answerResult.ai_empathy_reply) {
                    setMessages(prev => [...prev, {
                        sender: 'Eunoia',
                        content: answerResult.ai_empathy_reply,
                        isUser: false
                    }])
                }

                // Session complete, get summary
                setIsComplete(true)
                try {
                    const summaryData = await screeningService.getSummary(sessionId)
                    setCompletedSummary(summaryData)

                    setMessages(prev => [...prev, {
                        sender: 'Eunoia',
                        content: `🎯 Sesi telah selesai!\n\n${summaryData.summary || 'Terima kasih sudah berbagi.'}\n\n💡 ${summaryData.recommendation || 'Jaga kesehatan mentalmu!'}`,
                        isUser: false
                    }])
                } catch (summaryErr) {
                    console.error('Failed to get summary:', summaryErr)
                    setCompletedSummary({ primary_trigger: 'Sesi selesai' })
                    setMessages(prev => [...prev, {
                        sender: 'Eunoia',
                        content: '🎯 Sesi screening telah selesai. Terima kasih sudah berbagi perasaanmu!',
                        isUser: false
                    }])
                }
            } else if (nextData.question) {
                // COMBINE: AI empathy response + next question in one message
                setCurrentQuestion(nextData.question)
                setProgress(nextData.progress || progress)
                setSelectedOption(null)
                setAnsweredCount(prev => prev + 1)

                const combinedMessage = answerResult.ai_empathy_reply
                    ? `${answerResult.ai_empathy_reply}\n\n${nextData.question.text}`
                    : nextData.question.text

                setMessages(prev => [...prev, {
                    sender: 'Eunoia',
                    content: combinedMessage,
                    isUser: false
                }])
            }
        } catch (err) {
            console.error('Failed to submit answer:', err)
            setError(err.response?.data?.error || 'Gagal mengirim jawaban. Silakan coba lagi.')
        }

        setIsSubmitting(false)
    }

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'var(--bg-dark)',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000
        }}>
            {/* Gradient overlay */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '200px',
                background: 'linear-gradient(to bottom, rgba(43, 253, 184, 0.1), transparent)',
                pointerEvents: 'none'
            }}></div>

            {/* Header */}
            <header style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                backgroundColor: 'rgba(16, 34, 32, 0.8)',
                backdropFilter: 'blur(10px)',
                borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                position: 'relative',
                zIndex: 10
            }}>
                <button onClick={onBack} style={{ backgroundColor: 'transparent', color: 'white', padding: '8px' }}>
                    <ChevronLeft size={24} />
                </button>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <h1 style={{ fontSize: '18px', fontWeight: 'bold' }}>Eunoia</h1>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        marginTop: '4px',
                        padding: '4px 10px',
                        borderRadius: '999px',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.05)'
                    }}>
                        <div style={{
                            width: '6px',
                            height: '6px',
                            borderRadius: '50%',
                            backgroundColor: isComplete ? '#22c55e' : '#2bfdb8',
                            boxShadow: '0 0 6px rgba(43, 253, 184, 0.6)'
                        }}></div>
                        <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                            {isComplete ? 'Selesai' : progress}
                        </span>
                    </div>
                </div>
                <button onClick={onHistory} style={{ backgroundColor: 'transparent', color: 'white', padding: '8px' }}>
                    <History size={20} />
                </button>
            </header>

            {/* End Session Confirmation Modal */}
            {showEndConfirm && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                    padding: '16px'
                }}>
                    <div style={{
                        backgroundColor: '#1A2C2A',
                        borderRadius: '24px',
                        padding: '24px',
                        maxWidth: '320px',
                        width: '100%',
                        border: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                            <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Akhiri Sesi?</h3>
                            <button
                                onClick={() => setShowEndConfirm(false)}
                                style={{ backgroundColor: 'transparent', color: 'white', padding: '4px' }}
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px', lineHeight: '1.5' }}>
                            Kamu sudah menjawab <strong style={{ color: 'white' }}>{answeredCount}</strong> pertanyaan.
                        </p>

                        {answeredCount < 3 ? (
                            <p style={{ color: '#ef4444', fontSize: '13px', marginBottom: '20px' }}>
                                ⚠️ Minimal 3 pertanyaan harus dijawab untuk mengakhiri sesi.
                            </p>
                        ) : (
                            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
                                Summary akan dibuat berdasarkan jawaban yang sudah ada.
                            </p>
                        )}

                        <div style={{ display: 'flex', gap: '12px' }}>
                            <button
                                onClick={() => setShowEndConfirm(false)}
                                style={{
                                    flex: 1,
                                    padding: '12px',
                                    borderRadius: '12px',
                                    backgroundColor: 'transparent',
                                    border: '1px solid rgba(255, 255, 255, 0.2)',
                                    color: 'white',
                                    fontWeight: 500,
                                    cursor: 'pointer'
                                }}
                            >
                                Lanjutkan
                            </button>
                            <button
                                onClick={handleEndSession}
                                disabled={answeredCount < 3 || isEnding}
                                style={{
                                    flex: 1,
                                    padding: '12px',
                                    borderRadius: '12px',
                                    backgroundColor: answeredCount >= 3 ? '#ef4444' : 'rgba(239, 68, 68, 0.3)',
                                    border: 'none',
                                    color: 'white',
                                    fontWeight: 500,
                                    cursor: answeredCount >= 3 && !isEnding ? 'pointer' : 'not-allowed',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '6px',
                                    opacity: answeredCount < 3 ? 0.5 : 1
                                }}
                            >
                                {isEnding && <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />}
                                Akhiri
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Messages */}
            <main style={{
                flex: 1,
                overflowY: 'auto',
                padding: '24px 16px',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                zIndex: 10
            }}>
                {/* Date separator */}
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
                    <span style={{
                        fontSize: '12px',
                        color: 'var(--text-secondary)',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        padding: '6px 12px',
                        borderRadius: '999px'
                    }}>
                        {new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'short' })}
                    </span>
                </div>

                {/* Error Display */}
                {error && (
                    <div style={{
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        borderRadius: '12px',
                        padding: '12px 16px',
                        marginBottom: '16px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        color: '#ef4444'
                    }}>
                        <AlertCircle size={18} />
                        <span style={{ fontSize: '14px' }}>{error}</span>
                    </div>
                )}

                {isLoading ? (
                    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', flex: 1, gap: '12px' }}>
                        <Loader2 size={32} color="#2bfdb8" style={{ animation: 'spin 1s linear infinite' }} />
                        <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Mempersiapkan sesi...</span>
                    </div>
                ) : (
                    <>
                        {messages.map((msg, index) => (
                            <MessageBubble key={index} {...msg} />
                        ))}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </main>

            {/* Footer with Options */}
            {!isLoading && !isComplete && currentQuestion && currentQuestion.options && (
                <footer style={{
                    padding: '16px',
                    backgroundColor: 'var(--bg-dark)',
                    borderTop: '1px solid rgba(255, 255, 255, 0.05)',
                    position: 'relative',
                    zIndex: 20
                }}>
                    {/* Gradient fade above footer */}
                    <div style={{
                        position: 'absolute',
                        top: '-48px',
                        left: 0,
                        right: 0,
                        height: '48px',
                        background: 'linear-gradient(to top, var(--bg-dark), transparent)',
                        pointerEvents: 'none'
                    }}></div>

                    {/* Option Buttons */}
                    <div style={{ marginBottom: '16px' }}>
                        {currentQuestion.options.map((option) => (
                            <OptionButton
                                key={option.id}
                                text={option.text}
                                selected={selectedOption === option.id}
                                onClick={() => setSelectedOption(option.id)}
                                disabled={isSubmitting}
                            />
                        ))}
                    </div>

                    {/* Submit Button */}
                    <div style={{ display: 'flex', gap: '12px' }}>
                        {/* End Session Button */}
                        <button
                            onClick={() => setShowEndConfirm(true)}
                            disabled={isSubmitting}
                            style={{
                                padding: '16px',
                                borderRadius: '999px',
                                backgroundColor: 'transparent',
                                border: '1px solid rgba(239, 68, 68, 0.5)',
                                color: '#ef4444',
                                fontWeight: 500,
                                fontSize: '14px',
                                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '6px',
                                opacity: isSubmitting ? 0.5 : 1
                            }}
                        >
                            <LogOut size={16} />
                            Akhiri
                        </button>

                        {/* Continue Button */}
                        <button
                            onClick={handleSubmitAnswer}
                            disabled={!selectedOption || isSubmitting}
                            style={{
                                flex: 1,
                                padding: '16px',
                                borderRadius: '999px',
                                backgroundColor: selectedOption ? '#2bfdb8' : '#1A2C2A',
                                color: selectedOption ? '#0d1f22' : 'rgba(255,255,255,0.5)',
                                fontWeight: 600,
                                fontSize: '16px',
                                border: 'none',
                                cursor: selectedOption && !isSubmitting ? 'pointer' : 'not-allowed',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '8px'
                            }}
                        >
                            {isSubmitting && <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />}
                            {isSubmitting ? 'Mengirim...' : 'Lanjutkan'}
                        </button>
                    </div>
                </footer>
            )}

            {/* Completed state */}
            {isComplete && (
                <footer style={{
                    padding: '16px',
                    backgroundColor: 'var(--bg-dark)',
                    borderTop: '1px solid rgba(255, 255, 255, 0.05)',
                    position: 'relative',
                    zIndex: 20
                }}>
                    {/* Brief Summary */}
                    {completedSummary && (
                        <div style={{
                            backgroundColor: 'rgba(43, 253, 184, 0.1)',
                            borderRadius: '16px',
                            padding: '16px',
                            marginBottom: '16px',
                            border: '1px solid rgba(43, 253, 184, 0.2)',
                            textAlign: 'center'
                        }}>
                            <p style={{ color: '#2bfdb8', fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>
                                ✨ Kesimpulan Sesi
                            </p>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                                Emosi dominan: <strong style={{ color: 'white' }}>{completedSummary.primary_trigger || 'Neutral'}</strong>
                            </p>
                            {completedSummary.mood_improvement !== undefined && completedSummary.mood_improvement > 0 && (
                                <p style={{ color: '#2bfdb8', fontSize: '12px', marginTop: '4px' }}>
                                    +{completedSummary.mood_improvement}% peningkatan mood
                                </p>
                            )}
                        </div>
                    )}

                    {/* View Insights Button */}
                    <button
                        onClick={() => onSessionComplete?.(sessionId)}
                        style={{
                            width: '100%',
                            padding: '16px',
                            borderRadius: '999px',
                            backgroundColor: '#2bfdb8',
                            color: '#0d1f22',
                            fontWeight: 600,
                            fontSize: '16px',
                            border: 'none',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            marginBottom: '12px'
                        }}
                    >
                        <BarChart2 size={18} />
                        Lihat Detail Insights
                    </button>

                    {/* Back to Home Button */}
                    <button
                        onClick={onBack}
                        style={{
                            width: '100%',
                            padding: '14px',
                            borderRadius: '999px',
                            backgroundColor: 'transparent',
                            color: 'white',
                            fontWeight: 500,
                            fontSize: '15px',
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px'
                        }}
                    >
                        <Home size={18} />
                        Kembali ke Home
                    </button>
                </footer>
            )}

            <style>{`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    )
}

export default ChatPage

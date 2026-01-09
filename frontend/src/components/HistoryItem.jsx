import React from 'react'

const HistoryItem = ({ icon, title, description, time, duration, moodColor, onClick }) => {
    return (
        <div
            onClick={onClick}
            style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '16px',
                backgroundColor: '#162225',
                border: '1px solid #1f3236',
                borderRadius: '20px',
                padding: '16px',
                marginBottom: '12px',
                position: 'relative',
                cursor: 'pointer'
            }}
        >
            {/* Icon Area */}
            <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#1f2937',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
            }}>
                {icon}
            </div>

            {/* Content */}
            <div style={{ flex: 1, textAlign: 'left' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '4px' }}>{title}</h3>
                    {/* Mood Indicator Dot */}
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: moodColor }}></div>
                </div>

                <p style={{
                    fontSize: '13px',
                    color: 'var(--text-secondary)',
                    lineHeight: '1.4',
                    marginBottom: '8px',
                    display: '-webkit-box',
                    WebkitLineClamp: 2, /* Limits to 2 lines */
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                }}>
                    {description}
                </p>

                <div style={{ fontSize: '12px', color: '#5eead4', fontWeight: 500 }}>
                    {time} • <span style={{ color: 'var(--text-secondary)' }}>{duration}</span>
                </div>
            </div>
        </div>
    )
}

export default HistoryItem

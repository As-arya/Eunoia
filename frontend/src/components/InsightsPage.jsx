import React, { useState } from 'react'
import { ChevronLeft } from 'lucide-react'
import MoodTrendChart from './MoodTrendChart'
import PredominantEmotions from './PredominantEmotions'
import AIObservations from './AIObservations'

const TimeFilter = ({ label, active, onClick }) => (
    <button
        onClick={onClick}
        style={{
            padding: '8px 16px',
            borderRadius: '999px',
            backgroundColor: active ? '#162b2e' : 'transparent',
            color: active ? 'white' : '#6b7280',
            fontSize: '13px',
            fontWeight: 500,
            transition: 'all 0.2s',
            flex: 1
        }}
    >
        {label}
    </button>
)

const InsightsPage = ({ onBack }) => {
    const [filter, setFilter] = useState('weekly')

    return (
        <div style={{ paddingBottom: '40px' }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: '24px',
                paddingTop: '16px',
                position: 'relative'
            }}>
                <button onClick={onBack} style={{ backgroundColor: 'transparent', color: 'white', position: 'absolute', left: 0 }}>
                    <ChevronLeft size={24} />
                </button>
                <h1 style={{ fontSize: '18px', fontWeight: 600, margin: '0 auto' }}>Emotional Insight</h1>
            </div>

            {/* Filter Segmented Control */}
            <div style={{
                backgroundColor: '#162225',
                borderRadius: '999px',
                padding: '4px',
                display: 'flex',
                marginBottom: '32px'
            }}>
                <TimeFilter label="Daily" active={filter === 'daily'} onClick={() => setFilter('daily')} />
                <TimeFilter label="Weekly" active={filter === 'weekly'} onClick={() => setFilter('weekly')} />
                <TimeFilter label="Monthly" active={filter === 'monthly'} onClick={() => setFilter('monthly')} />
            </div>

            <MoodTrendChart period={filter} />
            <PredominantEmotions period={filter} />
            <AIObservations />

        </div>
    )
}

export default InsightsPage

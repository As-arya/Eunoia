import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { useMoodTrend } from '../hooks/useInsights'

const EmotionalInsight = ({ onViewInsights }) => {
    const { data, isLoading } = useMoodTrend('weekly')

    // Default empty state
    const defaultData = {
        trend: 'neutral',
        change_percentage: 0,
        data_points: []
    }

    const moodData = data || defaultData
    const hasData = moodData.data_points && moodData.data_points.length > 0
    const isImproving = moodData.trend === 'improving' || moodData.change_percentage > 0
    const changeValue = Math.abs(moodData.change_percentage || 0)

    // Get chart data points  
    const chartData = hasData ? moodData.data_points : [30, 40, 35, 45, 50, 55, 60] // Only show placeholder visual

    return (
        <div style={{ marginBottom: '32px' }}>
            <h3 style={{ fontSize: '18px', marginBottom: '16px', fontWeight: 600, textAlign: 'left' }}>Emotional Insight</h3>

            <div
                onClick={onViewInsights}
                style={{
                    backgroundColor: '#162225',
                    borderRadius: '24px',
                    padding: '20px',
                    position: 'relative',
                    overflow: 'hidden',
                    border: '1px solid #1f3236',
                    cursor: 'pointer',
                    textAlign: 'left'
                }}
            >
                <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '4px' }}>Weekly Mood Trend</div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                        <span style={{ fontSize: '24px', fontWeight: 'bold', color: 'white' }}>
                            {isLoading ? 'Loading...' : hasData ? (isImproving ? 'Improving' : 'Stable') : 'Start tracking'}
                        </span>
                        {hasData && changeValue > 0 && (
                            <div style={{
                                backgroundColor: isImproving ? 'rgba(43, 253, 184, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                color: isImproving ? '#4ade80' : '#ef4444',
                                padding: '4px 8px',
                                borderRadius: '999px',
                                fontSize: '12px',
                                fontWeight: 600,
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                            }}>
                                {isImproving ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                {isImproving ? '+' : '-'}{changeValue}%
                            </div>
                        )}
                    </div>
                </div>

                {/* Chart Bars */}
                <div style={{
                    display: 'flex',
                    alignItems: 'flex-end',
                    gap: '6px',
                    height: '40px',
                    position: 'absolute',
                    right: '24px',
                    bottom: '24px',
                    opacity: hasData ? 0.8 : 0.3
                }}>
                    {chartData.map((h, i) => (
                        <div key={i} style={{
                            width: '6px',
                            height: `${typeof h === 'object' ? h.score || h.value : h}%`,
                            backgroundColor: i === chartData.length - 1 ? '#2bfdb8' : '#2d4a52',
                            borderRadius: '4px'
                        }}></div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default EmotionalInsight

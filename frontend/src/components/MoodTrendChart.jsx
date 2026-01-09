import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { useMoodTrend } from '../hooks/useInsights'

const MoodTrendChart = ({ period = 'weekly' }) => {
    const { data, isLoading, error } = useMoodTrend(period)

    // Fallback demo data
    const demoData = {
        trend: 'stable',
        change_percentage: 0,
        summary: "Mulai sesi screening untuk melacak mood-mu.",
        data_points: [
            { label: 'M', value: 60 },
            { label: 'T', value: 60 },
            { label: 'W', value: 60 },
            { label: 'T', value: 60 },
            { label: 'F', value: 60 },
            { label: 'S', value: 60 },
            { label: 'S', value: 60 }
        ]
    }

    // Show error state if API fails
    if (error) {
        return (
            <div style={{
                backgroundColor: '#162225',
                borderRadius: '24px',
                padding: '20px',
                border: '1px solid #1f3236',
                marginBottom: '32px',
                textAlign: 'center'
            }}>
                <p style={{ color: '#ef4444', marginBottom: '8px' }}>Gagal memuat data mood</p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Silakan coba refresh halaman</p>
            </div>
        )
    }

    const moodData = data || demoData
    const isImproving = moodData.trend === 'improving' || moodData.change_percentage > 0

    // Dynamic period label
    const periodLabel = {
        daily: 'Daily',
        weekly: 'Weekly',
        monthly: 'Monthly'
    }[period] || 'Weekly'

    return (
        <div style={{
            backgroundColor: '#162225',
            borderRadius: '24px',
            padding: '20px',
            border: '1px solid #1f3236',
            marginBottom: '32px'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '4px' }}>{periodLabel} Mood Trend</div>
                    <h2 style={{ fontSize: '24px', fontWeight: 'bold' }}>
                        {isLoading ? 'Loading...' : (moodData.trend === 'improving' ? 'Improving' : moodData.trend === 'declining' ? 'Declining' : 'Stable')}
                    </h2>
                </div>
                <div style={{
                    backgroundColor: isImproving ? 'rgba(43, 253, 184, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: isImproving ? '#4ade80' : '#ef4444',
                    padding: '6px 10px',
                    borderRadius: '999px',
                    fontSize: '13px',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                }}>
                    {isImproving ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                    {isImproving ? '+' : ''}{moodData.change_percentage || 0}%
                </div>
            </div>

            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.5', marginBottom: '32px' }}>
                {moodData.summary}
            </p>

            {/* Chart Visualization */}
            <div style={{ position: 'relative', height: '120px', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', padding: '0 8px' }}>
                <svg viewBox="0 0 280 80" style={{ position: 'absolute', bottom: '30px', left: 0, right: 0, width: '100%', height: '80px', overflow: 'visible' }}>
                    <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor="#2bfdb8" stopOpacity="0.2" />
                            <stop offset="100%" stopColor="#2bfdb8" stopOpacity="0" />
                        </linearGradient>
                    </defs>
                    {(() => {
                        const dataPoints = moodData.data_points || moodData.data || demoData.data_points;
                        if (!dataPoints || dataPoints.length === 0) return null;

                        // Calculate points for the chart
                        const width = 280;
                        const height = 80;
                        const points = dataPoints.map((point, i) => {
                            const x = (i / (dataPoints.length - 1)) * width;
                            // Convert value/score (0-100) to Y coordinate (inverted: higher value = lower Y)
                            const value = point.value ?? point.score ?? 50;
                            const y = height - (value / 100) * (height - 10);
                            return { x, y };
                        });

                        // Create smooth curve path using bezier curves
                        let pathD = `M${points[0].x},${points[0].y}`;
                        for (let i = 1; i < points.length; i++) {
                            const prev = points[i - 1];
                            const curr = points[i];
                            const cpx1 = prev.x + (curr.x - prev.x) / 3;
                            const cpx2 = prev.x + 2 * (curr.x - prev.x) / 3;
                            pathD += ` C${cpx1},${prev.y} ${cpx2},${curr.y} ${curr.x},${curr.y}`;
                        }

                        // Create fill path (close at bottom)
                        const fillPath = pathD + ` L${points[points.length - 1].x},${height} L${points[0].x},${height} Z`;

                        return (
                            <>
                                <path d={fillPath} fill="url(#gradient)" />
                                <path d={pathD} fill="none" stroke="#2bfdb8" strokeWidth="2" strokeLinecap="round" />
                                {/* Highlight current day point */}
                                {points.map((point, i) => (
                                    i === points.length - 1 && (
                                        <circle key={i} cx={point.x} cy={point.y} r="4" fill="#2bfdb8" />
                                    )
                                ))}
                            </>
                        );
                    })()}
                </svg>

                {/* X Axis Labels */}
                {(moodData.data_points || moodData.data || demoData.data_points).map((point, i, arr) => (
                    <div key={i} style={{
                        textAlign: 'center',
                        zIndex: 1,
                        width: '24px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '8px'
                    }}>
                        <span style={{
                            fontSize: '12px',
                            color: i === arr.length - 1 ? '#2bfdb8' : '#6b7280',
                            fontWeight: i === arr.length - 1 ? 'bold' : 'normal'
                        }}>{point.label || point.day}</span>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default MoodTrendChart

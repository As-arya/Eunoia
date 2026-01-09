import React from 'react'
import { Lightbulb, Moon, Heart, Brain } from 'lucide-react'
import { useObservations } from '../hooks/useInsights'

const ObservationCard = ({ icon, title, description }) => (
    <div style={{
        backgroundColor: '#162225',
        borderRadius: '20px',
        padding: '20px',
        marginBottom: '16px',
        border: '1px solid #1f3236',
        textAlign: 'left'
    }}>
        <div style={{ display: 'flex', gap: '16px' }}>
            <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '12px',
                backgroundColor: '#2e364f',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
            }}>
                {icon}
            </div>
            <div style={{ textAlign: 'left', flex: 1 }}>
                <h4 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '4px', textAlign: 'left' }}>{title}</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: '1.5', textAlign: 'left' }}>{description}</p>
            </div>
        </div>
    </div>
)

// Icon mapping by observation type
const getObservationIcon = (type) => {
    switch (type) {
        case 'pattern':
            return <Lightbulb size={20} color="#a78bfa" fill="#a78bfa" />
        case 'sleep':
            return <Moon size={20} color="#f472b6" fill="#f472b6" />
        case 'emotion':
            return <Heart size={20} color="#f87171" fill="#f87171" />
        default:
            return <Brain size={20} color="#60a5fa" fill="#60a5fa" />
    }
}

const AIObservations = () => {
    const { data, isLoading } = useObservations({ limit: 3 })

    // Use real data - no demo fallback, show empty state instead
    const observations = data?.observations || []

    return (
        <div>
            <div style={{ marginBottom: '16px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 600 }}>AI Observations</h3>
            </div>

            {isLoading ? (
                <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '20px' }}>Loading...</div>
            ) : observations.length === 0 ? (
                <div style={{
                    backgroundColor: '#162225',
                    borderRadius: '20px',
                    padding: '24px',
                    border: '1px solid #1f3236',
                    textAlign: 'center'
                }}>
                    <Brain size={32} color="#6b7280" style={{ marginBottom: '12px' }} />
                    <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                        Belum ada observasi AI.
                    </p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
                        Selesaikan beberapa sesi screening untuk mendapatkan insights.
                    </p>
                </div>
            ) : (
                observations.map((obs) => (
                    <ObservationCard
                        key={obs.id}
                        icon={getObservationIcon(obs.type)}
                        title={obs.title || 'Observasi'}
                        description={obs.description || 'Tidak ada detail'}
                    />
                ))
            )}
        </div>
    )
}

export default AIObservations

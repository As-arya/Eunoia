import React from 'react'
import { PlusSquare, Sparkles } from 'lucide-react'

const DeepInsightsCard = ({ onUpgrade }) => {
    return (
        <div
            onClick={onUpgrade}
            style={{
                background: 'linear-gradient(135deg, #102428 0%, #0d1f22 100%)',
                borderRadius: '24px',
                padding: '20px',
                border: '1px solid rgba(43, 253, 184, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginTop: '24px',
                marginBottom: '24px',
                cursor: 'pointer'
            }}
        >
            <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <div style={{
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        backgroundColor: '#2bfdb8',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <Sparkles size={14} color="#0d1f22" fill="#0d1f22" />
                    </div>
                    <h3 style={{ fontSize: '15px', fontWeight: 'bold' }}>Unlock Deep Insights</h3>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    Get unlimited history & emotional trends.
                </p>
            </div>

            <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#2bfdb8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 15px rgba(43, 253, 184, 0.3)'
            }}>
                <PlusSquare size={20} color="#0d1f22" />
            </div>
        </div>
    )
}

export default DeepInsightsCard

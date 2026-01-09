import React from 'react'
import { Gem } from 'lucide-react'
import logoGold from '../assets/logo-gold.png'

const EunoiaPlus = ({ onUpgrade }) => {
    return (
        <div style={{
            background: 'linear-gradient(135deg, #0f2e35 0%, #0d1f22 100%)',
            borderRadius: '24px',
            padding: '24px',
            border: '1px solid rgba(43, 253, 184, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '24px',
            position: 'relative',
            overflow: 'hidden'
        }}>
            <div style={{ position: 'relative', zIndex: 1, maxWidth: '60%', textAlign: 'left' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <Gem size={20} color="#2bfdb8" fill="#2bfdb8" />
                    <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>Euonia Plus</h3>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px', lineHeight: '1.4' }}>
                    Unlock unlimited chats & <br />deeper emotional analytics.
                </p>
                <button
                    onClick={onUpgrade}
                    style={{
                        backgroundColor: '#384649',
                        color: 'white',
                        padding: '10px 20px',
                        borderRadius: '12px',
                        fontWeight: 600,
                        fontSize: '13px',
                        border: 'none',
                        cursor: 'pointer'
                    }}
                >
                    Upgrade Now
                </button>
            </div>

            {/* Large Gold Logo on Right */}
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <img src={logoGold} alt="Euonia Plus Logo" style={{ width: '120px', height: 'auto', objectFit: 'contain' }} />
            </div>
        </div>
    )
}

export default EunoiaPlus

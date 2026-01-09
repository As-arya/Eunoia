import React from 'react'
import { MessageSquarePlus } from 'lucide-react'
import logoGreen from '../assets/logo-green.png'

const Hero = ({ onStartChat }) => {
    return (
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            {/* Icon Placeholder similar to the logo in image */}
            <div style={{
                margin: '0 auto 8px',
                width: '100%',
                maxWidth: '280px',
                height: '160px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                <img src={logoGreen} alt="Euonia Logo" style={{ width: 'auto', height: '100%', objectFit: 'contain', maxWidth: '100%' }} />
            </div>

            <h2 style={{ fontSize: '28px', marginBottom: '8px', fontWeight: 600 }}>What brings you here?</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', lineHeight: '1.6' }}>
                I'm here to listen. Let's process your<br />thoughts together.
            </p>

            <button
                onClick={onStartChat}
                style={{
                    background: 'linear-gradient(90deg, #2bfdb8 0%, #08f0d0 100%)',
                    width: '100%',
                    padding: '16px',
                    borderRadius: '999px',
                    color: '#000',
                    fontWeight: 'bold',
                    fontSize: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '12px',
                    boxShadow: '0 4px 15px rgba(43, 253, 184, 0.2)',
                    cursor: 'pointer'
                }}
            >
                <MessageSquarePlus size={20} />
                Start New Chat
            </button>
        </div>
    )
}

export default Hero

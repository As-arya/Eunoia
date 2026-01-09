import React from 'react'
import logoGreen from '../assets/logo-green.png'

const SplashPage = ({ onLogin, onSignup }) => {
    return (
        <div style={{
            height: '100dvh', // Use dynamic viewport height for mobile
            minHeight: '100dvh',
            maxHeight: '100dvh',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '24px',
            backgroundColor: 'var(--bg-dark)',
            color: 'white',
            boxSizing: 'border-box'
        }}>
            {/* Content Area */}
            <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0px'
            }}>
                {/* Logo Area */}
                <div style={{
                    width: '180px',
                    height: '180px',
                    marginBottom: '0px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <img src={logoGreen} alt="Euonia Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                </div>

                <h1 style={{
                    fontSize: '36px',
                    fontWeight: 700,
                    color: 'white',
                    marginBottom: '16px',
                    marginTop: '0px',
                    letterSpacing: '-1px'
                }}>
                    Euonia
                </h1>

                <h2 style={{
                    fontSize: '20px',
                    fontWeight: 700,
                    textAlign: 'center',
                    marginBottom: '8px',
                    marginTop: '0px',
                    maxWidth: '280px',
                    lineHeight: '1.3',
                    color: 'white'
                }}>
                    <span style={{ color: '#2bfdb8' }}>Euonia</span> - Your Mind AI <span style={{ color: '#2bfdb8' }}>Partner</span>
                </h2>

                <p style={{
                    textAlign: 'center',
                    color: '#9ca3af',
                    fontSize: '14px',
                    marginBottom: '0px',
                    marginTop: '0px',
                    maxWidth: '260px',
                    lineHeight: '1.4'
                }}>
                    Unlock Infinite Conversations: Euonia, Your Mind Companion!
                </p>
            </div>

            {/* Buttons Area */}
            <div style={{ width: '100%', paddingBottom: '16px', paddingTop: '16px' }}>
                <button
                    onClick={onLogin}
                    style={{
                        width: '100%',
                        padding: '14px',
                        borderRadius: '999px',
                        backgroundColor: '#2bfdb8',
                        color: '#0d1f22',
                        fontWeight: 'bold',
                        fontSize: '16px',
                        border: 'none',
                        marginBottom: '12px',
                        cursor: 'pointer',
                        boxShadow: '0 4px 12px rgba(43, 253, 184, 0.3)'
                    }}
                >
                    Log In
                </button>

                <button
                    onClick={onSignup}
                    style={{
                        width: '100%',
                        padding: '14px',
                        borderRadius: '999px',
                        backgroundColor: 'transparent',
                        border: '2px solid #2bfdb8',
                        color: 'white',
                        fontWeight: 'bold',
                        fontSize: '16px',
                        cursor: 'pointer'
                    }}
                >
                    Create Account
                </button>
            </div>
        </div>
    )
}

export default SplashPage


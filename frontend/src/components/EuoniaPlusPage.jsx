import React, { useState } from 'react'
import { X, MessageSquare, Brain, ArrowRight, Check } from 'lucide-react'
import logoGold from '../assets/logo-gold.png'

const FeatureCard = ({ icon, title, description }) => (
    <div style={{
        backgroundColor: '#162225',
        borderRadius: '20px',
        padding: '20px',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '16px',
        marginBottom: '16px',
        border: '1px solid #1f3236',
        textAlign: 'left'
    }}>
        <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '16px',
            backgroundColor: '#1f2937',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
        }}>
            {icon}
        </div>
        <div>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '4px' }}>{title}</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>{description}</p>
        </div>
    </div>
)

const PlanCard = ({ label, title, price, subtitle, selected, onSelect, badge }) => (
    <div
        onClick={onSelect}
        style={{
            flex: 1,
            backgroundColor: selected ? 'rgba(43, 253, 184, 0.05)' : '#162225',
            borderRadius: '16px',
            padding: '16px',
            border: selected ? '2px solid #2bfdb8' : '1px solid #1f3236',
            cursor: 'pointer',
            position: 'relative',
            textAlign: 'center',
            transition: 'all 0.2s'
        }}
    >
        {badge && (
            <div style={{
                position: 'absolute',
                top: '-10px',
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: '#2bfdb8',
                color: '#0d1f22',
                fontSize: '10px',
                fontWeight: 700,
                padding: '4px 12px',
                borderRadius: '999px'
            }}>
                {badge}
            </div>
        )}

        {selected && (
            <div style={{
                position: 'absolute',
                top: '12px',
                right: '12px',
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: '#2bfdb8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                <Check size={12} color="#0d1f22" />
            </div>
        )}

        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 500 }}>{label}</div>
        <div style={{ fontSize: '13px', fontWeight: 500, marginBottom: '8px' }}>{title}</div>
        <div style={{ fontSize: '22px', fontWeight: 'bold', marginBottom: '4px' }}>{price}</div>
        <div style={{ fontSize: '12px', color: selected ? '#2bfdb8' : 'var(--text-secondary)' }}>{subtitle}</div>
    </div>
)

const EuoniaPlusPage = ({ onClose }) => {
    const [selectedPlan, setSelectedPlan] = useState('yearly')

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'var(--bg-dark)',
            zIndex: 1000,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column'
        }}>
            <div style={{
                maxWidth: '480px',
                margin: '0 auto',
                padding: '20px',
                flex: 1,
                display: 'flex',
                flexDirection: 'column'
            }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
                    <button
                        onClick={onClose}
                        style={{
                            backgroundColor: 'transparent',
                            color: 'white',
                            padding: '8px'
                        }}
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Hero */}
                <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                    <div style={{
                        width: '120px',
                        height: '120px',
                        margin: '0 auto 16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <img src={logoGold} alt="Euonia Plus" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                    </div>
                    <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
                        Euonia <span style={{ color: '#2bfdb8' }}>Plus</span>
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.5' }}>
                        Unlock the full potential of your AI<br />companion with premium features.
                    </p>
                </div>

                {/* Features */}
                <FeatureCard
                    icon={<MessageSquare size={24} color="#5eead4" />}
                    title="Unlimited Chat Sessions"
                    description="No limits on your conversations. Talk to your companion whenever you need."
                />
                <FeatureCard
                    icon={<Brain size={24} color="#a78bfa" />}
                    title="Advanced AI Insights"
                    description="Deep emotional analysis and personalized psychological patterns."
                />

                {/* Pricing Plans */}
                <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', marginTop: '8px' }}>
                    <PlanCard
                        label="FLEXIBLE"
                        title="Monthly"
                        price="Rp 55.000"
                        subtitle="Billed monthly"
                        selected={selectedPlan === 'monthly'}
                        onSelect={() => setSelectedPlan('monthly')}
                    />
                    <PlanCard
                        label=""
                        title="Yearly"
                        price="Rp 528.000"
                        subtitle="Save 20%"
                        badge="BEST VALUE"
                        selected={selectedPlan === 'yearly'}
                        onSelect={() => setSelectedPlan('yearly')}
                    />
                </div>

                {/* Spacer */}
                <div style={{ flex: 1 }}></div>

                {/* Footer */}
                <div style={{ paddingBottom: '20px' }}>
                    <button style={{
                        width: '100%',
                        padding: '16px',
                        borderRadius: '999px',
                        background: 'linear-gradient(90deg, #2bfdb8 0%, #08f0d0 100%)',
                        color: '#0d1f22',
                        fontWeight: 'bold',
                        fontSize: '16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        marginBottom: '16px',
                        boxShadow: '0 4px 20px rgba(43, 253, 184, 0.3)'
                    }}>
                        Unlock Euonia Plus <ArrowRight size={18} />
                    </button>
                    <p style={{ textAlign: 'center', fontSize: '12px', color: 'var(--text-secondary)' }}>
                        Recurring billing. Cancel anytime. <a href="#" style={{ color: '#5eead4' }}>Terms</a> & <a href="#" style={{ color: '#5eead4' }}>Privacy</a>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default EuoniaPlusPage

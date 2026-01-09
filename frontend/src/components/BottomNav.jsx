import React from 'react'
import { Home, Clock, BarChart2, User } from 'lucide-react'

const NavItem = ({ icon: Icon, label, active, onClick }) => (
    <div
        onClick={onClick}
        style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '4px',
            color: active ? '#2bfdb8' : '#6b7280',
            cursor: 'pointer',
            transition: 'color 0.2s'
        }}
    >
        <Icon size={24} />
        <span style={{ fontSize: '10px', fontWeight: 500 }}>{label}</span>
    </div>
)

const BottomNav = ({ activeTab, onTabChange }) => {
    return (
        <div style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            backgroundColor: 'var(--nav-bg)',
            borderTop: '1px solid #1f3236',
            padding: '12px 24px 20px', /* Extra padding at bottom for safe area */
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            zIndex: 100
        }}>
            <NavItem
                icon={Home}
                label="Home"
                active={activeTab === 'Home'}
                onClick={() => onTabChange('Home')}
            />
            <NavItem
                icon={Clock}
                label="History"
                active={activeTab === 'History'}
                onClick={() => onTabChange('History')}
            />
            <NavItem
                icon={BarChart2}
                label="Insights"
                active={activeTab === 'Insights'}
                onClick={() => onTabChange('Insights')}
            />
            <NavItem
                icon={User}
                label="Profile"
                active={activeTab === 'Profile'}
                onClick={() => onTabChange('Profile')}
            />
        </div>
    )
}

export default BottomNav

import React, { useState } from 'react'
import { ChevronLeft, Search, Check, Zap, Moon, Flame } from 'lucide-react'

const FilterChip = ({ label, icon: Icon, active, onClick }) => (
    <button
        onClick={onClick}
        style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            borderRadius: '999px',
            backgroundColor: active ? '#162b2e' : 'transparent',
            border: active ? '1px solid #2bfdb8' : '1px solid #1f3236',
            color: active ? '#2bfdb8' : '#6b7280',
            fontSize: '13px',
            whiteSpace: 'nowrap',
            transition: 'all 0.2s'
        }}
    >
        {Icon && <Icon size={14} />}
        {label}
    </button>
)

const HistoryHeader = ({ onBack }) => {
    const [activeFilter, setActiveFilter] = useState('All')

    return (
        <div style={{ marginBottom: '24px' }}>
            {/* Top Bar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', paddingTop: '16px' }}>
                <button onClick={onBack} style={{ backgroundColor: 'transparent', color: 'white' }}>
                    <ChevronLeft size={24} />
                </button>
                <h1 style={{ fontSize: '18px', fontWeight: 600 }}>History</h1>
                <button style={{ backgroundColor: 'transparent', color: '#5eead4', fontSize: '14px', fontWeight: 500 }}>
                    Edit
                </button>
            </div>

            {/* Search Bar */}
            <div style={{ position: 'relative', marginBottom: '16px' }}>
                <div style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }}>
                    <Search size={18} />
                </div>
                <input
                    type="text"
                    placeholder="Search keywords, topics, or dates..."
                    style={{
                        width: '100%',
                        backgroundColor: '#162225',
                        border: '1px solid #1f3236',
                        borderRadius: '16px',
                        padding: '12px 12px 12px 44px',
                        color: 'white',
                        fontSize: '14px',
                        outline: 'none'
                    }}
                />
            </div>

            {/* Filters */}
            <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px', scrollbarWidth: 'none' }}>
                <FilterChip label="All" icon={Check} active={activeFilter === 'All'} onClick={() => setActiveFilter('All')} />
                <FilterChip label="Anxiety" icon={Zap} active={activeFilter === 'Anxiety'} onClick={() => setActiveFilter('Anxiety')} />
                <FilterChip label="Sleep" icon={Moon} active={activeFilter === 'Sleep'} onClick={() => setActiveFilter('Sleep')} />
                <FilterChip label="Motivation" icon={Flame} active={activeFilter === 'Motivation'} onClick={() => setActiveFilter('Motivation')} />
            </div>
        </div>
    )
}

export default HistoryHeader

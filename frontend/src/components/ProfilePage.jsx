import React, { useState, useEffect } from 'react'
import { ChevronLeft, Edit2, CheckCircle2, User, Bell, Lock, Moon, Globe, LogOut, ChevronRight, Gem } from 'lucide-react'
import { userService, authService } from '../services'
import { clearTokens } from '../lib/apiClient'

const SettingsItem = ({ icon: Icon, label, value, onClick, type = 'arrow', iconColor = '#8da3a6' }) => {
    return (
        <div
            onClick={onClick}
            style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px 0',
                cursor: 'pointer'
            }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '12px',
                    backgroundColor: '#162225',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <Icon size={20} color={iconColor} />
                </div>
                <span style={{ fontSize: '15px', fontWeight: 500 }}>{label}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                {value && <span style={{ fontSize: '13px' }}>{value}</span>}
                {type === 'arrow' && <ChevronRight size={16} />}
            </div>
        </div>
    )
}

const ProfilePage = ({ onBack, onUpgrade }) => {
    const [user, setUser] = useState(null)
    const [isLoading, setIsLoading] = useState(true)

    const isPlusMember = user?.is_plus || user?.subscription === 'plus' || false

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const userData = await userService.getProfile()
                setUser(userData)
            } catch (error) {
                console.error('Failed to fetch user:', error)
            } finally {
                setIsLoading(false)
            }
        }
        fetchUser()
    }, [])

    const handleLogout = async () => {
        try {
            await authService.logout()
        } catch (error) {
            console.error('Logout error:', error)
        }
        clearTokens()
        window.location.reload()
    }

    const userName = user?.name || 'User'
    const userEmail = user?.email || 'user@example.com'
    const memberYear = user?.created_at ? new Date(user.created_at).getFullYear() : new Date().getFullYear()

    return (
        <div style={{ paddingBottom: '20px' }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '24px',
                paddingTop: '16px',
                position: 'relative'
            }}>
                <button onClick={onBack} style={{ backgroundColor: 'transparent', color: 'white', position: 'absolute', left: 0 }}>
                    <ChevronLeft size={24} />
                </button>
                <h1 style={{ fontSize: '18px', fontWeight: 600 }}>Profile</h1>
            </div>

            {/* User Info */}
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <div style={{ position: 'relative', display: 'inline-block', marginBottom: '16px' }}>
                    <div style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '50%',
                        backgroundColor: '#d1d5db',
                        border: '2px solid #1f3236',
                        overflow: 'hidden'
                    }}>
                        <img
                            src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(userName)}`}
                            alt="Avatar"
                            style={{ width: '100%', height: '100%' }}
                        />
                    </div>
                    <button style={{
                        position: 'absolute',
                        bottom: 0,
                        right: 0,
                        backgroundColor: '#2bfdb8',
                        borderRadius: '50%',
                        width: '28px',
                        height: '28px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '2px solid #0d1f22'
                    }}>
                        <Edit2 size={12} color="#0d1f22" />
                    </button>
                </div>

                <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '4px' }}>{userName}</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>{userEmail}</p>

                <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
                    <span style={{
                        backgroundColor: isPlusMember ? 'rgba(167, 139, 250, 0.1)' : 'rgba(43, 253, 184, 0.1)',
                        color: isPlusMember ? '#a78bfa' : '#2bfdb8',
                        padding: '4px 12px',
                        borderRadius: '999px',
                        fontSize: '12px',
                        fontWeight: 500
                    }}>{isPlusMember ? 'Euonia Plus' : 'Free Plan'}</span>
                    <span style={{
                        backgroundColor: '#162225',
                        color: '#8da3a6',
                        padding: '4px 12px',
                        borderRadius: '999px',
                        fontSize: '12px',
                        fontWeight: 500,
                        border: '1px solid #1f3236'
                    }}>Member since {memberYear}</span>
                </div>
            </div>

            {/* Euonia Plus Banner - only show for free users */}
            {!isPlusMember && (
                <div style={{
                    background: 'linear-gradient(135deg, #102428 0%, #0d1f22 100%)',
                    borderRadius: '24px',
                    padding: '24px',
                    border: '1px solid rgba(43, 253, 184, 0.1)',
                    marginBottom: '32px',
                    position: 'relative'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                        <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                <div style={{
                                    width: '24px',
                                    height: '24px',
                                    borderRadius: '50%',
                                    backgroundColor: 'rgba(43, 253, 184, 0.2)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: '#2bfdb8',
                                    fontSize: '12px',
                                    fontWeight: 'bold'
                                }}>
                                    <Gem size={14} />
                                </div>
                                <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>Euonia Plus</h3>
                            </div>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: '1.5' }}>
                                Unlock unlimited chats,<br />advanced emotion analysis,<br />and priority support.
                            </p>
                        </div>
                        <div style={{ color: 'rgba(43, 253, 184, 0.2)' }}>
                            <CheckCircle2 size={48} fill="currentColor" color="#0d1f22" style={{ opacity: 0.5 }} />
                        </div>
                    </div>

                    <button
                        onClick={onUpgrade}
                        style={{
                            backgroundColor: '#2bfdb8',
                            color: '#0d1f22',
                            width: '100%',
                            padding: '12px',
                            borderRadius: '999px',
                            fontWeight: 600,
                            fontSize: '14px',
                            boxShadow: '0 4px 12px rgba(43, 253, 184, 0.2)',
                            cursor: 'pointer'
                        }}
                    >
                        Upgrade Now
                    </button>
                </div>
            )}

            {/* Account Settings */}
            <div style={{ marginBottom: '32px' }}>
                <h3 style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '8px', letterSpacing: '0.05em' }}>ACCOUNT SETTINGS</h3>
                <div style={{ backgroundColor: '#162225', borderRadius: '24px', padding: '0 20px', border: '1px solid #1f3236' }}>
                    <SettingsItem icon={User} label="Personal Information" iconColor="#3b82f6" onClick={() => alert('Fitur pengaturan personal akan segera hadir.')} />
                    <div style={{ height: '1px', backgroundColor: '#1f3236' }}></div>
                    <SettingsItem icon={Bell} label="Notifications" iconColor="#22c55e" onClick={() => alert('Fitur pengaturan notifikasi akan segera hadir.')} />
                    <div style={{ height: '1px', backgroundColor: '#1f3236' }}></div>
                    <SettingsItem icon={Lock} label="Privacy & Security" iconColor="#a855f7" onClick={() => alert('Fitur pengaturan privasi akan segera hadir.')} />
                </div>
            </div>

            {/* App Preferences */}
            <div style={{ marginBottom: '32px' }}>
                <h3 style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '8px', letterSpacing: '0.05em' }}>APP PREFERENCES</h3>
                <div style={{ backgroundColor: '#162225', borderRadius: '24px', padding: '0 20px', border: '1px solid #1f3236' }}>
                    <SettingsItem icon={Moon} label="Appearance" value="Dark Mode" iconColor="#f97316" onClick={() => alert('Saat ini hanya tersedia Dark Mode.')} />
                    <div style={{ height: '1px', backgroundColor: '#1f3236' }}></div>
                    <SettingsItem icon={Globe} label="Language" value="Bahasa Indonesia" iconColor="#14b8a6" onClick={() => alert('Saat ini hanya tersedia Bahasa Indonesia.')} />
                </div>
            </div>

            {/* Log Out */}
            <button
                onClick={handleLogout}
                style={{
                    width: '100%',
                    padding: '16px',
                    borderRadius: '999px',
                    border: '1px solid #ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.05)',
                    color: '#ef4444',
                    fontSize: '15px',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    cursor: 'pointer'
                }}>
                <LogOut size={18} /> Log Out
            </button>

            <div style={{ textAlign: 'center', marginTop: '24px', color: 'var(--text-secondary)', fontSize: '12px' }}>
                Euonia v2.4.0
            </div>

        </div>
    )
}

export default ProfilePage

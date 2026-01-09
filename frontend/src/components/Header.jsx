import React, { useState, useEffect } from 'react'
import { Bell } from 'lucide-react'
import { getAccessToken } from '../lib/apiClient'
import { userService } from '../services'

const Header = () => {
    const [userName, setUserName] = useState('')

    // Get greeting based on time of day
    const getGreeting = () => {
        const hour = new Date().getHours()
        if (hour < 12) return 'Good morning'
        if (hour < 18) return 'Good afternoon'
        return 'Good evening'
    }

    // Fetch user data from API
    useEffect(() => {
        const fetchUser = async () => {
            if (getAccessToken()) {
                try {
                    const user = await userService.getProfile()
                    setUserName(user.name?.split(' ')[0] || 'User')
                } catch (error) {
                    console.error('Failed to fetch user:', error)
                    setUserName('User')
                }
            }
        }
        fetchUser()
    }, [])

    return (
        <header style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            paddingTop: '24px',
            marginBottom: '32px'
        }}>
            <div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>{getGreeting()},</div>
                <h1 style={{ fontSize: '24px', fontWeight: '600' }}>{userName || 'User'}</h1>
            </div>
            <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#1f2937',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                <Bell size={20} color="white" />
            </div>
        </header>
    )
}

export default Header

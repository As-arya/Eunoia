import React, { useState } from 'react'
import { ChevronLeft, Eye, EyeOff, CheckSquare, Loader2 } from 'lucide-react'
import { authService } from '../services'

const SignupPage = ({ onBack, onSignupSuccess, onGoToLogin }) => {
    const [showPassword, setShowPassword] = useState(false)
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [agreed, setAgreed] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSignup = async (e) => {
        e.preventDefault()

        if (!agreed) {
            setError('Please agree to the Terms of Service and Privacy Policy')
            return
        }

        setError('')
        setIsLoading(true)

        try {
            await authService.register({ name, email, password })
            onSignupSuccess()
        } catch (err) {
            setError(err.response?.data?.error || 'Registration failed. Please try again.')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div style={{
            minHeight: '100vh',
            backgroundColor: 'white',
            color: '#102220',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column'
        }}>
            {/* Header */}
            <header style={{ marginBottom: '32px', display: 'flex', alignItems: 'center' }}>
                <button onClick={onBack} style={{ backgroundColor: 'transparent', color: '#102220', padding: 0 }}>
                    <ChevronLeft size={28} />
                </button>
            </header>

            <div style={{ flex: 1 }}>
                <h1 style={{ fontSize: '28px', fontWeight: '800', marginBottom: '8px' }}>Create your account</h1>
                <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '32px' }}>
                    To begin using the Eunoia, please create an account with your email address.
                </p>

                {/* Error Message */}
                {error && (
                    <div style={{
                        backgroundColor: '#fef2f2',
                        border: '1px solid #fecaca',
                        color: '#dc2626',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        marginBottom: '24px',
                        fontSize: '14px'
                    }}>
                        {error}
                    </div>
                )}

                {/* Form */}
                <form onSubmit={handleSignup}>
                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '8px', color: '#374151' }}>
                            Full Name
                        </label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Enter your full name"
                            required
                            style={{
                                width: '100%',
                                padding: '16px',
                                borderRadius: '12px',
                                border: '1px solid #d1d5db',
                                fontSize: '14px',
                                outline: 'none',
                                backgroundColor: 'white',
                                color: '#102220'
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '8px', color: '#374151' }}>
                            Email Address
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            required
                            style={{
                                width: '100%',
                                padding: '16px',
                                borderRadius: '12px',
                                border: '1px solid #d1d5db',
                                fontSize: '14px',
                                outline: 'none',
                                backgroundColor: 'white',
                                color: '#102220'
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '8px', color: '#374151' }}>
                            Password
                        </label>
                        <div style={{ position: 'relative' }}>
                            <input
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Create a password"
                                required
                                minLength={6}
                                style={{
                                    width: '100%',
                                    padding: '16px',
                                    borderRadius: '12px',
                                    border: '1px solid #2bfdb8',
                                    fontSize: '14px',
                                    outline: 'none',
                                    backgroundColor: 'white',
                                    color: '#102220'
                                }}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                style={{
                                    position: 'absolute',
                                    right: '16px',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    backgroundColor: 'transparent',
                                    color: '#102220'
                                }}
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '32px' }}>
                        <button
                            type="button"
                            onClick={() => setAgreed(!agreed)}
                            style={{ backgroundColor: 'transparent', color: agreed ? '#2bfdb8' : '#d1d5db', padding: 0 }}
                        >
                            {agreed ?
                                <div style={{ width: '20px', height: '20px', backgroundColor: '#3b82f6', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <CheckSquare size={16} color="white" />
                                </div>
                                :
                                <div style={{ width: '20px', height: '20px', border: '2px solid #d1d5db', borderRadius: '4px' }}></div>
                            }
                        </button>
                        <p style={{ fontSize: '12px', color: '#6b7280', lineHeight: '1.5' }}>
                            By continuing you agree to the Eunoia <a href="#" style={{ color: '#2bfdb8' }}>Term of Service</a> and <a href="#" style={{ color: '#2bfdb8' }}>Privacy Policy</a>
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        style={{
                            width: '100%',
                            padding: '16px',
                            borderRadius: '999px',
                            backgroundColor: isLoading ? '#9ca3af' : '#2bfdb8',
                            color: '#0d1f22',
                            fontWeight: 'bold',
                            fontSize: '16px',
                            border: 'none',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            marginBottom: '24px',
                            boxShadow: '0 4px 12px rgba(43, 253, 184, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px'
                        }}
                    >
                        {isLoading && <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />}
                        {isLoading ? 'Creating account...' : 'Continue'}
                    </button>
                </form>

                <div style={{ textAlign: 'center', fontSize: '14px', color: '#6b7280', marginBottom: '32px' }}>
                    Already have an account? <button onClick={onGoToLogin} style={{ color: '#2bfdb8', fontWeight: 600, backgroundColor: 'transparent' }}>Log In</button>
                </div>

                {/* Social Login - Disabled for MVP */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '32px' }}>
                    <div style={{ height: '1px', flex: 1, backgroundColor: '#e5e7eb' }}></div>
                    <span style={{ fontSize: '12px', color: '#9ca3af' }}>OR</span>
                    <div style={{ height: '1px', flex: 1, backgroundColor: '#e5e7eb' }}></div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', opacity: 0.5 }}>
                    <button disabled style={{
                        width: '100%',
                        padding: '14px',
                        borderRadius: '16px',
                        border: '1px solid #e5e7eb',
                        backgroundColor: 'white',
                        color: '#1f2937',
                        fontWeight: 500,
                        fontSize: '14px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '12px',
                        cursor: 'not-allowed'
                    }}>
                        <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" style={{ width: '20px', height: '20px' }} />
                        Continue with Google (Coming Soon)
                    </button>
                </div>
            </div>
        </div>
    )
}

export default SignupPage

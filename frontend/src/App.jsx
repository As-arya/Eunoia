import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import EmotionalInsight from './components/EmotionalInsight'
import RecentConversations from './components/RecentConversations'
import EunoiaPlus from './components/EunoiaPlus'
import BottomNav from './components/BottomNav'
import HistoryPage from './components/HistoryPage'
import InsightsPage from './components/InsightsPage'
import ProfilePage from './components/ProfilePage'
import EuoniaPlusPage from './components/EuoniaPlusPage'
import SessionInsightsPage from './components/SessionInsightsPage'
import ChatPage from './components/ChatPage'
import SplashPage from './components/SplashPage'
import LoginPage from './components/LoginPage'
import SignupPage from './components/SignupPage'
import { getAccessToken, clearTokens } from './lib/apiClient'
import './App.css'

function App() {
  const [authStep, setAuthStep] = useState(() => {
    const token = getAccessToken()
    return token && token.length > 10 ? 'authenticated' : 'splash'
  })
  const [tab, setTab] = useState('Home')
  const [showPlus, setShowPlus] = useState(false)
  const [showInsights, setShowInsights] = useState(false)
  const [showChat, setShowChat] = useState(false)
  const [sessionId, setSessionId] = useState(null)

  const handleLogout = () => {
    clearTokens()
    setAuthStep('splash')
  }

  useEffect(() => {
    const token = getAccessToken()
    if (authStep === 'authenticated' && (!token || token.length < 10)) {
      handleLogout()
    }

    // Listen for auth errors from API client (e.g., refresh token failed)
    const handleAuthError = () => {
      console.log('[App] Auth error detected, logging out')
      handleLogout()
    }
    window.addEventListener('auth-error', handleAuthError)
    return () => window.removeEventListener('auth-error', handleAuthError)
  }, [authStep])

  if (authStep === 'splash') {
    return <SplashPage onLogin={() => setAuthStep('login')} onSignup={() => setAuthStep('signup')} />
  }
  if (authStep === 'login') {
    return <LoginPage onBack={() => setAuthStep('splash')} onLoginSuccess={() => setAuthStep('authenticated')} onGoToSignup={() => setAuthStep('signup')} />
  }
  if (authStep === 'signup') {
    return <SignupPage onBack={() => setAuthStep('splash')} onSignupSuccess={() => setAuthStep('authenticated')} onGoToLogin={() => setAuthStep('login')} />
  }

  const viewSession = (id) => { setSessionId(id); setShowInsights(true); }

  const renderContent = () => {
    if (showInsights) return <SessionInsightsPage sessionId={sessionId} onBack={() => setShowInsights(false)} onContinueChat={() => { setShowInsights(false); setShowChat(true); }} />
    if (tab === 'History') return <HistoryPage onBack={() => setTab('Home')} onViewSession={viewSession} onUpgrade={() => setShowPlus(true)} />
    if (tab === 'Insights') return <InsightsPage onBack={() => setTab('Home')} />
    if (tab === 'Profile') return <ProfilePage onBack={() => setTab('Home')} onUpgrade={() => setShowPlus(true)} onLogout={handleLogout} />
    return (
      <>
        <Header />
        <Hero onStartChat={() => setShowChat(true)} />
        <EmotionalInsight onViewInsights={() => setTab('Insights')} />
        <RecentConversations onViewSession={viewSession} onViewAll={() => setTab('History')} />
        <EunoiaPlus onUpgrade={() => setShowPlus(true)} />
      </>
    )
  }

  return (
    <div className="container" style={{ padding: 0 }}>
      <main style={{ padding: '0 24px' }}>{renderContent()}</main>
      {!showInsights && <BottomNav activeTab={tab} onTabChange={setTab} />}
      {showPlus && <EuoniaPlusPage onClose={() => setShowPlus(false)} />}
      {showChat && <ChatPage
        onBack={() => setShowChat(false)}
        onHistory={() => { setShowChat(false); setTab('History'); }}
        onSessionComplete={(id) => { setShowChat(false); viewSession(id); }}
      />}
    </div>
  )
}

export default App

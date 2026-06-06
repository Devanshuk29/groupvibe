import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Copy, Mail } from 'lucide-react'
import { getSession, generateRecommendations } from '../services/api'

export default function WaitingRoom() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  // Poll session every 3 seconds
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const response = await getSession(sessionId)
        setSession(response.data)
      } catch (error) {
        console.error('Error fetching session:', error)
      }
    }

    fetchSession()
    const interval = setInterval(fetchSession, 3000)
    return () => clearInterval(interval)
  }, [sessionId])

  const handleCopyLink = () => {
    const link = `${window.location.origin}/join/${sessionId}`
    navigator.clipboard.writeText(link)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleWhatsApp = () => {
    const link = `${window.location.origin}/join/${sessionId}`
    const text = `Join my GroupVibe session! Enter your preferences here: ${link}`
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`)
  }

  const handleEmail = () => {
    const link = `${window.location.origin}/join/${sessionId}`
    window.open(`mailto:?subject=Join my GroupVibe trip!&body=Enter your preferences here: ${link}`)
  }

  const handleGenerateRecommendations = async () => {
    if (session?.submitted_count === 0) {
      return alert('At least one friend needs to submit preferences first!')
    }
    setLoading(true)
    try {
      const response = await generateRecommendations(sessionId)
      navigate(`/results/${sessionId}`, { state: { results: response.data } })
    } catch (error) {
      console.error('Error generating recommendations:', error)
      alert('Something went wrong. Please try again!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-tertiary)' }}>

      {/* Navbar */}
      <nav style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 24px',
        borderBottom: '0.5px solid var(--border-color)',
        background: 'var(--bg-primary)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#7F77DD' }}></div>
          <span style={{ fontSize: '17px', fontWeight: '500', color: 'var(--text-primary)' }}>GroupVibe</span>
        </div>
        <button
          onClick={handleGenerateRecommendations}
          disabled={loading}
          style={{
            background: '#7F77DD',
            color: '#fff',
            border: 'none',
            padding: '9px 18px',
            borderRadius: '8px',
            fontSize: '13px',
            cursor: 'pointer',
            fontWeight: '500',
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? 'Generating...' : 'Generate results'}
        </button>
      </nav>

      <div style={{ padding: '24px', maxWidth: '460px', margin: '0 auto' }}>
        <p style={{ fontSize: '17px', fontWeight: '500', color: 'var(--text-primary)', marginBottom: '4px' }}>
          Waiting for friends
        </p>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
          Share this code so everyone can join
        </p>

        {/* Session Code Box */}
        <div style={{
          background: 'var(--bg-secondary)',
          borderRadius: '12px',
          padding: '18px 22px',
          textAlign: 'center',
          marginBottom: '20px'
        }}>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px' }}>Session code</p>
          <p style={{ fontSize: '26px', fontWeight: '500', letterSpacing: '6px', color: '#7F77DD', marginBottom: '14px' }}>
            {sessionId}
          </p>
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={handleWhatsApp}
              style={{
                background: 'transparent',
                color: 'var(--text-primary)',
                border: '0.5px solid var(--border-color)',
                padding: '7px 13px',
                borderRadius: '8px',
                fontSize: '12px',
                cursor: 'pointer'
              }}
            >
              WhatsApp
            </button>
            <button
              onClick={handleEmail}
              style={{
                background: 'transparent',
                color: 'var(--text-primary)',
                border: '0.5px solid var(--border-color)',
                padding: '7px 13px',
                borderRadius: '8px',
                fontSize: '12px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <Mail size={13} /> Email
            </button>
            <button
              onClick={handleCopyLink}
              style={{
                background: 'transparent',
                color: 'var(--text-primary)',
                border: '0.5px solid var(--border-color)',
                padding: '7px 13px',
                borderRadius: '8px',
                fontSize: '12px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <Copy size={13} /> {copied ? 'Copied!' : 'Copy link'}
            </button>
          </div>
        </div>

        {/* Members Progress */}
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '10px' }}>
          {session?.submitted_count || 0} of {session?.total_members || 0} submitted
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {session?.members?.length === 0 && (
            <div style={{
              background: 'var(--bg-primary)',
              border: '0.5px solid var(--border-color)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                No friends joined yet. Share the link above!
              </p>
            </div>
          )}

          {session?.members?.map((member, i) => (
            <div key={i} style={{
              background: 'var(--bg-primary)',
              border: '0.5px solid var(--border-color)',
              borderRadius: '12px',
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <div style={{
                width: '34px', height: '34px',
                borderRadius: '50%',
                background: member.submitted ? '#EEEDFE' : 'var(--bg-secondary)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '12px', fontWeight: '500',
                color: member.submitted ? '#534AB7' : 'var(--text-secondary)',
                flexShrink: 0
              }}>
                {member.name?.slice(0, 2).toUpperCase()}
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-primary)' }}>{member.name}</p>
                <p style={{ fontSize: '12px', color: member.submitted ? '#3B6D11' : 'var(--text-secondary)' }}>
                  {member.submitted ? 'Submitted ✓' : 'Waiting...'}
                </p>
              </div>
              <div style={{
                width: '8px', height: '8px',
                borderRadius: '50%',
                background: member.submitted ? '#639922' : '#888780'
              }}></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
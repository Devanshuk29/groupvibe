import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, Users, Brain, MapPin, Share2, Plus, ArrowRight } from 'lucide-react'
import { createSession } from '../services/api'

export default function Home() {
  const navigate = useNavigate()
  const [joining, setJoining] = useState(false)
  const [sessionCode, setSessionCode] = useState('')
  const [loading, setLoading] = useState(false)

  const handleCreateTrip = async () => {
    setLoading(true)
    try {
      const response = await createSession({
        trip_date: '',
        trip_time: 'evening'
      })
      const sessionId = response.data.session_id
      navigate(`/session/${sessionId}`)
    } catch (error) {
      console.error('Error creating session:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleJoinTrip = () => {
    if (sessionCode.trim()) {
      navigate(`/join/${sessionCode.trim().toUpperCase()}`)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-tertiary)' }}>

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
          onClick={() => setJoining(!joining)}
          style={{
            background: 'transparent',
            color: 'var(--text-primary)',
            border: '0.5px solid var(--border-color)',
            padding: '9px 18px',
            borderRadius: '8px',
            fontSize: '13px',
            cursor: 'pointer'
          }}
        >
          Join a trip
        </button>
      </nav>

      <div style={{ padding: '56px 24px 40px', textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>

        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          background: '#EEEDFE',
          color: '#534AB7',
          fontSize: '12px',
          padding: '4px 12px',
          borderRadius: '99px',
          marginBottom: '20px'
        }}>
          <Sparkles size={13} />
          ML-powered group planning
        </div>

        <h1 style={{ fontSize: '38px', fontWeight: '500', lineHeight: '1.2', marginBottom: '14px', color: 'var(--text-primary)' }}>
          Find places <span style={{ color: '#7F77DD' }}>everyone</span> will love
        </h1>

        <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: '1.7', marginBottom: '28px' }}>
          Share one link with your friends, collect everyone's preferences, and let AI find the perfect spot for your group.
        </p>

        {joining && (
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginBottom: '16px' }}>
            <input
              type="text"
              placeholder="Enter session code e.g. E5E85576"
              value={sessionCode}
              onChange={(e) => setSessionCode(e.target.value)}
              style={{
                padding: '9px 14px',
                border: '0.5px solid var(--border-color)',
                borderRadius: '8px',
                fontSize: '13px',
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)',
                width: '260px'
              }}
            />
            <button
              onClick={handleJoinTrip}
              style={{
                background: '#7F77DD',
                color: '#fff',
                border: 'none',
                padding: '9px 16px',
                borderRadius: '8px',
                fontSize: '13px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              Join <ArrowRight size={14} />
            </button>
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={handleCreateTrip}
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
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              opacity: loading ? 0.7 : 1
            }}
          >
            <Plus size={14} />
            {loading ? 'Creating...' : 'Create a trip'}
          </button>
          <button
            onClick={() => setJoining(!joining)}
            style={{
              background: 'transparent',
              color: 'var(--text-primary)',
              border: '0.5px solid var(--border-color)',
              padding: '9px 18px',
              borderRadius: '8px',
              fontSize: '13px',
              cursor: 'pointer'
            }}
          >
            Join with code
          </button>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '14px',
        padding: '0 24px 48px',
        maxWidth: '760px',
        margin: '0 auto'
      }}>
        {[
          { icon: <Users size={17} />, title: 'Collaborative', desc: 'Everyone joins via one shared link' },
          { icon: <Brain size={17} />, title: 'ML-powered', desc: 'HDBSCAN + Word2Vec + Neural network' },
          { icon: <MapPin size={17} />, title: 'Top 5 picks', desc: 'Ranked results with match scores' },
          { icon: <Share2 size={17} />, title: 'Easy sharing', desc: 'WhatsApp, email or PDF export' },
        ].map((f, i) => (
          <div key={i} style={{
            background: 'var(--bg-primary)',
            border: '0.5px solid var(--border-color)',
            borderRadius: '12px',
            padding: '16px'
          }}>
            <div style={{
              width: '34px',
              height: '34px',
              borderRadius: '8px',
              background: '#EEEDFE',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '10px',
              color: '#7F77DD'
            }}>
              {f.icon}
            </div>
            <p style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-primary)', marginBottom: '4px' }}>{f.title}</p>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>{f.desc}</p>
          </div>
        ))}
      </div>

    </div>
  )
}
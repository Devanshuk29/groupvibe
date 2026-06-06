import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { ArrowLeft, Download, Share2, RefreshCw } from 'lucide-react'
import { generateRecommendations } from '../services/api'
import { useState } from 'react'

export default function Results() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(false)
  const results = location.state?.results

  if (!results) {
    navigate(`/session/${sessionId}`)
    return null
  }

  const { recommendations, group_analysis } = results

  const handleRegenerate = async () => {
    setLoading(true)
    try {
      const response = await generateRecommendations(sessionId)
      navigate(`/results/${sessionId}`, { state: { results: response.data } })
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleWhatsApp = () => {
    const text = `Check out our GroupVibe recommendations! Top pick: ${recommendations[0]?.name}`
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`)
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
          <Download size={13} /> Export PDF
        </button>
      </nav>

      <div style={{ padding: '22px 24px 0', maxWidth: '620px', margin: '0 auto' }}>
        <p style={{ fontSize: '17px', fontWeight: '500', color: 'var(--text-primary)', marginBottom: '4px' }}>
          Top picks for your group
        </p>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '18px' }}>
          Based on preferences from {group_analysis?.total_members} friends
        </p>

        {/* Compatibility Card */}
        <div style={{
          background: 'var(--bg-secondary)',
          borderRadius: '12px',
          padding: '14px 18px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '14px'
        }}>
          <div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Group compatibility</p>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Top categories: {group_analysis?.top_categories?.join(', ')}
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <p style={{ fontSize: '22px', fontWeight: '500', color: '#7F77DD' }}>
              {Math.round(group_analysis?.compatibility_score * 100)}%
            </p>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              {group_analysis?.compatibility_score > 0.5 ? 'High match' : 'Mixed preferences'}
            </p>
          </div>
        </div>
      </div>

      {/* Recommendation Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', padding: '0 24px 16px', maxWidth: '620px', margin: '0 auto' }}>
        {recommendations?.map((rec, i) => (
          <div
            key={i}
            onClick={() => navigate(`/place/${rec.place_id}`, { state: { place: rec, sessionId } })}
            style={{
              background: 'var(--bg-primary)',
              border: i === 0 ? '2px solid #AFA9EC' : '0.5px solid var(--border-color)',
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              gap: '14px',
              alignItems: 'center',
              cursor: 'pointer'
            }}
          >
            {/* Rank */}
            <div style={{
              width: '34px', height: '34px',
              borderRadius: '50%',
              background: i === 0 ? '#FAEEDA' : '#EEEDFE',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '13px', fontWeight: '500',
              color: i === 0 ? '#854F0B' : '#534AB7',
              flexShrink: 0
            }}>
              {rec.rank}
            </div>

            {/* Info */}
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: '14px', fontWeight: '500', color: 'var(--text-primary)', marginBottom: '4px' }}>
                {rec.name}
              </p>
              <div style={{ display: 'flex', gap: '10px', fontSize: '12px', color: 'var(--text-secondary)', flexWrap: 'wrap' }}>
                <span>📍 {rec.address?.split(',')[0]}</span>
                <span>⭐ {rec.rating}</span>
                <span>{rec.price_range}</span>
              </div>
              <p style={{ fontSize: '11px', color: '#534AB7', marginTop: '5px' }}>
                {rec.why_recommended}
              </p>
            </div>

            {/* Score */}
            <div style={{ fontSize: '18px', fontWeight: '500', color: '#7F77DD' }}>
              {Math.round(rec.score * 100)}%
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '8px', padding: '0 24px 24px', maxWidth: '620px', margin: '0 auto', flexWrap: 'wrap' }}>
        <button
          onClick={handleWhatsApp}
          style={{
            background: '#7F77DD', color: '#fff',
            border: 'none', padding: '9px 18px',
            borderRadius: '8px', fontSize: '13px',
            cursor: 'pointer', fontWeight: '500',
            display: 'flex', alignItems: 'center', gap: '6px'
          }}
        >
          <Share2 size={14} /> Share on WhatsApp
        </button>
        <button
          onClick={handleRegenerate}
          disabled={loading}
          style={{
            background: 'transparent', color: 'var(--text-primary)',
            border: '0.5px solid var(--border-color)',
            padding: '9px 18px', borderRadius: '8px',
            fontSize: '13px', cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: '6px'
          }}
        >
          <RefreshCw size={14} /> {loading ? 'Regenerating...' : 'Re-generate'}
        </button>
      </div>
    </div>
  )
}
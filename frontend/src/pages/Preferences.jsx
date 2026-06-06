import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { submitPreferences } from '../services/api'

const CATEGORIES = ['Dining', 'Nightlife', 'Adventure', 'Nature', 'Shopping', 'Sports']
const DIETARY = ['Vegetarian', 'Vegan', 'Gluten-free', 'None']

export default function Preferences() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    name: '',
    email: '',
    budget_min: '',
    budget_max: '',
    vibe_score: 3,
    activity_types: [],
    dietary_restrictions: [],
    cuisines: []
  })

  const toggleItem = (field, item) => {
    setForm(prev => ({
      ...prev,
      [field]: prev[field].includes(item)
        ? prev[field].filter(i => i !== item)
        : [...prev[field], item]
    }))
  }

  const handleSubmit = async () => {
    if (!form.name.trim()) return alert('Please enter your name!')
    if (!form.budget_min || !form.budget_max) return alert('Please enter your budget!')
    if (form.activity_types.length === 0) return alert('Please select at least one activity!')

    setLoading(true)
    try {
      await submitPreferences(sessionId, {
        ...form,
        budget_min: parseInt(form.budget_min),
        budget_max: parseInt(form.budget_max),
        activity_types: form.activity_types.map(a => a.toLowerCase()),
        dietary_restrictions: form.dietary_restrictions.map(d => d.toLowerCase())
      })
      navigate(`/session/${sessionId}`)
    } catch (error) {
      console.error('Error submitting preferences:', error)
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
          onClick={() => navigate('/')}
          style={{
            background: 'transparent',
            color: 'var(--text-primary)',
            border: '0.5px solid var(--border-color)',
            padding: '9px 18px',
            borderRadius: '8px',
            fontSize: '13px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <ArrowLeft size={14} /> Back
        </button>
      </nav>

      {/* Form */}
      <div style={{
        background: 'var(--bg-secondary)',
        borderRadius: '12px',
        maxWidth: '460px',
        margin: '28px auto',
        padding: '22px 24px'
      }}>
        <p style={{ fontSize: '17px', fontWeight: '500', color: 'var(--text-primary)', marginBottom: '4px' }}>
          Enter your preferences
        </p>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
          Takes 2 minutes — be honest for better results!
        </p>

        {/* Name */}
        <div style={{ marginBottom: '14px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '5px' }}>
            Your name
          </label>
          <input
            type="text"
            placeholder="e.g. Akash"
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            style={{
              width: '100%', padding: '9px 12px',
              border: '0.5px solid var(--border-color)',
              borderRadius: '8px', fontSize: '13px',
              background: 'var(--bg-primary)',
              color: 'var(--text-primary)'
            }}
          />
        </div>

        {/* Email */}
        <div style={{ marginBottom: '14px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '5px' }}>
            Email (optional)
          </label>
          <input
            type="email"
            placeholder="e.g. akash@gmail.com"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            style={{
              width: '100%', padding: '9px 12px',
              border: '0.5px solid var(--border-color)',
              borderRadius: '8px', fontSize: '13px',
              background: 'var(--bg-primary)',
              color: 'var(--text-primary)'
            }}
          />
        </div>

        {/* Budget */}
        <div style={{ marginBottom: '14px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '5px' }}>
            Budget per person (₹)
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <input
              type="number"
              placeholder="Min: 500"
              value={form.budget_min}
              onChange={e => setForm({ ...form, budget_min: e.target.value })}
              style={{
                width: '100%', padding: '9px 12px',
                border: '0.5px solid var(--border-color)',
                borderRadius: '8px', fontSize: '13px',
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)'
              }}
            />
            <input
              type="number"
              placeholder="Max: 3000"
              value={form.budget_max}
              onChange={e => setForm({ ...form, budget_max: e.target.value })}
              style={{
                width: '100%', padding: '9px 12px',
                border: '0.5px solid var(--border-color)',
                borderRadius: '8px', fontSize: '13px',
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)'
              }}
            />
          </div>
        </div>

        {/* Activity Types */}
        <div style={{ marginBottom: '14px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
            What are you in the mood for?
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '7px' }}>
            {CATEGORIES.map(cat => (
              <span
                key={cat}
                onClick={() => toggleItem('activity_types', cat)}
                style={{
                  padding: '6px 12px',
                  borderRadius: '99px',
                  border: '0.5px solid var(--border-color)',
                  fontSize: '13px',
                  cursor: 'pointer',
                  background: form.activity_types.includes(cat) ? '#EEEDFE' : 'var(--bg-primary)',
                  color: form.activity_types.includes(cat) ? '#534AB7' : 'var(--text-secondary)'
                }}
              >
                {cat}
              </span>
            ))}
          </div>
        </div>

        {/* Dietary */}
        <div style={{ marginBottom: '14px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
            Dietary restrictions
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '7px' }}>
            {DIETARY.map(d => (
              <span
                key={d}
                onClick={() => toggleItem('dietary_restrictions', d)}
                style={{
                  padding: '6px 12px',
                  borderRadius: '99px',
                  border: '0.5px solid var(--border-color)',
                  fontSize: '13px',
                  cursor: 'pointer',
                  background: form.dietary_restrictions.includes(d) ? '#EEEDFE' : 'var(--bg-primary)',
                  color: form.dietary_restrictions.includes(d) ? '#534AB7' : 'var(--text-secondary)'
                }}
              >
                {d}
              </span>
            ))}
          </div>
        </div>

        {/* Vibe Slider */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
            Vibe — how adventurous are you feeling? ({form.vibe_score}/5)
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Chill</span>
            <input
              type="range"
              min="1" max="5" step="1"
              value={form.vibe_score}
              onChange={e => setForm({ ...form, vibe_score: parseInt(e.target.value) })}
              style={{ flex: 1, accentColor: '#7F77DD' }}
            />
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Adventurous</span>
          </div>
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            width: '100%',
            background: '#7F77DD',
            color: '#fff',
            border: 'none',
            padding: '10px 18px',
            borderRadius: '8px',
            fontSize: '13px',
            cursor: 'pointer',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? 'Submitting...' : 'Submit preferences'}
          {!loading && <ArrowRight size={14} />}
        </button>
      </div>
    </div>
  )
}
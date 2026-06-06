import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, MapPin, Star, Users, Car, UtensilsCrossed, Leaf, Clock, ThumbsUp, Share2 } from 'lucide-react'

export default function PlaceDetails() {
  const navigate = useNavigate()
  const location = useLocation()
  const { place, sessionId } = location.state || {}

  if (!place) {
    navigate('/')
    return null
  }

  // Parse hours if it's a string
  let hours = {}
  try {
    hours = typeof place.hours === 'string' ? JSON.parse(place.hours) : place.hours || {}
  } catch {
    hours = {}
  }

  const infoRows = [
    { icon: <MapPin size={15} />, label: 'Address', value: place.address },
    { icon: <Star size={15} />, label: 'Rating', value: `${place.rating} (${place.review_count?.toLocaleString()} reviews)` },
    { icon: <UtensilsCrossed size={15} />, label: 'Price range', value: place.price_range },
    { icon: <Users size={15} />, label: 'Group friendly', value: place.group_friendly ? 'Yes' : 'No', positive: place.group_friendly },
    { icon: <Car size={15} />, label: 'Parking', value: place.parking ? 'Yes' : 'No', positive: place.parking },
    { icon: <UtensilsCrossed size={15} />, label: 'Food inside', value: place.food_inside ? 'Yes' : 'No', positive: place.food_inside },
    { icon: <Leaf size={15} />, label: 'Best season', value: place.best_season || 'All year' },
    { icon: <Clock size={15} />, label: 'Duration', value: `~${place.duration_hours || 2} hours` },
  ]

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
          onClick={() => navigate(-1)}
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
          <ArrowLeft size={14} /> Back to results
        </button>
      </nav>

      <div style={{ padding: '24px', maxWidth: '560px', margin: '0 auto' }}>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: '#EEEDFE',
              color: '#534AB7',
              fontSize: '12px',
              padding: '4px 10px',
              borderRadius: '99px',
              marginBottom: '10px'
            }}>
              {place.category} · {place.type?.replace('_', ' ')}
            </div>
            <h2 style={{ fontSize: '22px', fontWeight: '500', color: 'var(--text-primary)', marginBottom: '6px' }}>
              {place.name}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <span>⭐ {place.rating}</span>
              <span style={{ color: '#7F77DD', fontWeight: '500' }}>
                {Math.round(place.score * 100)}% match
              </span>
            </div>
          </div>
          <div style={{
            width: '38px', height: '38px',
            borderRadius: '50%',
            background: place.rank === 1 ? '#FAEEDA' : '#EEEDFE',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '14px', fontWeight: '500',
            color: place.rank === 1 ? '#854F0B' : '#534AB7',
            flexShrink: 0
          }}>
            {place.rank}
          </div>
        </div>

        {/* Details Card */}
        <div style={{
          background: 'var(--bg-primary)',
          border: '0.5px solid var(--border-color)',
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '12px'
        }}>
          <p style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Details
          </p>
          {infoRows.map((row, i) => (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '13px',
              color: 'var(--text-secondary)',
              padding: '8px 0',
              borderBottom: i < infoRows.length - 1 ? '0.5px solid var(--border-color)' : 'none'
            }}>
              <span style={{ color: '#7F77DD' }}>{row.icon}</span>
              {row.label}
              <span style={{
                marginLeft: 'auto',
                fontSize: '13px',
                fontWeight: '500',
                color: row.positive === true ? '#3B6D11' : row.positive === false ? '#A32D2D' : 'var(--text-primary)'
              }}>
                {row.value}
              </span>
            </div>
          ))}
        </div>

        {/* Hours Card */}
        {Object.keys(hours).length > 0 && (
          <div style={{
            background: 'var(--bg-primary)',
            border: '0.5px solid var(--border-color)',
            borderRadius: '12px',
            padding: '16px',
            marginBottom: '12px'
          }}>
            <p style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Opening hours
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
              {Object.entries(hours).map(([day, time]) => (
                <div key={day} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', padding: '4px 0' }}>
                  <span style={{ color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{day}</span>
                  <span style={{ color: time === 'CLOSED' ? '#A32D2D' : 'var(--text-primary)', fontWeight: '500' }}>{time}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Why Recommended */}
        <div style={{
          background: 'var(--bg-primary)',
          border: '0.5px solid var(--border-color)',
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '20px'
        }}>
          <p style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Why recommended
          </p>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
            {place.why_recommended}
          </p>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={() => window.open(place.google_maps_link)}
            style={{
              background: '#7F77DD', color: '#fff',
              border: 'none', padding: '9px 18px',
              borderRadius: '8px', fontSize: '13px',
              cursor: 'pointer', fontWeight: '500',
              display: 'flex', alignItems: 'center', gap: '6px'
            }}
          >
            <MapPin size={14} /> Open in Google Maps
          </button>
          <button
            style={{
              background: 'transparent', color: 'var(--text-primary)',
              border: '0.5px solid var(--border-color)',
              padding: '9px 18px', borderRadius: '8px',
              fontSize: '13px', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '6px'
            }}
          >
            <ThumbsUp size={14} /> Vote for this place
          </button>
          <button
            onClick={() => {
              const text = `Check out ${place.name} on GroupVibe!`
              window.open(`https://wa.me/?text=${encodeURIComponent(text)}`)
            }}
            style={{
              background: 'transparent', color: 'var(--text-primary)',
              border: '0.5px solid var(--border-color)',
              padding: '9px 18px', borderRadius: '8px',
              fontSize: '13px', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '6px'
            }}
          >
            <Share2 size={14} /> Share
          </button>
        </div>
      </div>
    </div>
  )
}
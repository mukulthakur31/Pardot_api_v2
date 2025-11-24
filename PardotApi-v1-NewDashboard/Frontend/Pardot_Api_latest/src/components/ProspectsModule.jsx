import React from 'react'

const ProspectsModule = () => {
  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>👥</div>
      <h2 style={{
        fontSize: '1.8rem',
        fontWeight: 'bold',
        color: '#1f2937',
        marginBottom: '1rem'
      }}>
        Prospect Health
      </h2>
      <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
        Prospect health analysis functionality will be implemented here
      </p>
    </div>
  )
}

export default ProspectsModule
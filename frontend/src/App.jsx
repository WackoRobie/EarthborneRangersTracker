import { useState, useEffect } from 'react'

function App() {
  const [apiStatus, setApiStatus] = useState('checking...')

  useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(data => setApiStatus(data.status))
      .catch(() => setApiStatus('unreachable'))
  }, [])

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '2rem' }}>
      <h1>Earthborne Rangers</h1>
      <p>API status: <strong>{apiStatus}</strong></p>
    </div>
  )
}

export default App

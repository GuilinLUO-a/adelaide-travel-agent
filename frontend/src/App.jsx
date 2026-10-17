// export default App
import { useState } from 'react'
import TravelPreferencesForm from './TravelPreferencesForm'

function App() {
  const [message, setMessage] = useState('Connection not checked.')
  const [isChecking, setIsChecking] = useState(false)

  async function checkConnection() {
    setIsChecking(true)
    setMessage('Checking...')

    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 4500)

    try {
      const response = await fetch('/api/health', {
        signal: controller.signal,
      })

      if (response.status !== 200) {
        throw new Error(`Unexpected HTTP status: ${response.status}`)
      }

      const data = await response.json()

      if (data.status !== 'ok') {
        throw new Error('Unexpected health response')
      }

      setMessage('Backend connected.')
    } catch (error) {
      console.error('Backend connection check failed:', error)
      setMessage(
        'Cannot connect to the backend. Check that it is running and try again.'
      )
    } finally {
      clearTimeout(timeout)
      setIsChecking(false)
    }
  }

  return (
    <main>
      <h1>Adelaide Travel Agent</h1>
      <p>Plan your Adelaide trip.</p>

      <button onClick={checkConnection} disabled={isChecking}>
        {isChecking ? 'Checking...' : 'Check backend connection'}
      </button>

      <p role="status">{message}</p>

      <TravelPreferencesForm />
    </main>
  )
}

export default App
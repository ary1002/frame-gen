import { useState, useEffect, useRef } from 'react'
import { getJob } from './api.js'

export function useJobPoller(jobId) {
  const [job, setJob] = useState(null)
  const [error, setError] = useState(null)
  const intervalRef = useRef(null)
  const backoffRef = useRef(1000)

  useEffect(() => {
    if (!jobId) return

    let cancelled = false

    async function poll() {
      try {
        const data = await getJob(jobId)
        if (cancelled) return
        setJob(data)
        setError(null)
        backoffRef.current = 1000

        if (data.status === 'COMPLETE') {
          clearInterval(intervalRef.current)
        }
      } catch (err) {
        if (cancelled) return
        setError(err.message)
        // Exponential backoff up to 10s
        backoffRef.current = Math.min(backoffRef.current * 2, 10000)
        clearInterval(intervalRef.current)
        intervalRef.current = setInterval(poll, backoffRef.current)
      }
    }

    poll()
    intervalRef.current = setInterval(poll, 1000)

    return () => {
      cancelled = true
      clearInterval(intervalRef.current)
    }
  }, [jobId])

  return { job, error }
}

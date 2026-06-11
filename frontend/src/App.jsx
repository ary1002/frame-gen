import { useState } from 'react'
import { createJob } from './api.js'
import { useJobPoller } from './useJobPoller.js'
import PromptForm from './components/PromptForm.jsx'
import PipelineView from './components/PipelineView.jsx'

export default function App() {
  const [jobId, setJobId] = useState(null)
  const { job, error } = useJobPoller(jobId)

  async function handleSubmit(prompt) {
    const { job_id } = await createJob(prompt)
    setJobId(job_id)
  }

  function handleReset() {
    setJobId(null)
  }

  if (!jobId) {
    return <PromptForm onSubmit={handleSubmit} />
  }

  if (!job) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        gap: '0.75rem',
        color: 'var(--text-muted)',
        fontFamily: 'var(--font-mono)',
        fontSize: '12px',
        animation: 'fadeIn 0.3s ease',
      }}>
        <span style={{
          width: '12px', height: '12px',
          border: '2px solid var(--border)',
          borderTopColor: 'var(--amber)',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
          display: 'inline-block',
        }} />
        Connecting…
      </div>
    )
  }

  return <PipelineView job={job} error={error} onReset={handleReset} />
}

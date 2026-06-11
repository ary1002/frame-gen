import { useEffect, useRef } from 'react'

const styles = {
  container: {
    animation: 'fadeIn 0.8s ease both',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  label: {
    fontSize: '10px',
    letterSpacing: '0.2em',
    color: 'var(--amber)',
    textTransform: 'uppercase',
    marginBottom: '0.25rem',
  },
  videoWrap: {
    position: 'relative',
    borderRadius: 'var(--radius)',
    overflow: 'hidden',
    border: '1px solid var(--border)',
    background: '#000',
    boxShadow: '0 0 40px rgba(240,165,0,0.08)',
  },
  video: {
    width: '100%',
    display: 'block',
    maxHeight: '60vh',
  },
  meta: {
    display: 'flex',
    gap: '2rem',
    padding: '0.75rem 0',
    borderTop: '1px solid var(--border-subtle)',
    flexWrap: 'wrap',
  },
  metaItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  metaKey: {
    fontSize: '9px',
    color: 'var(--text-muted)',
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
  },
  metaVal: {
    fontSize: '12px',
    color: 'var(--text-secondary)',
    fontFamily: 'var(--font-mono)',
  },
  promptText: {
    fontSize: '12px',
    color: 'var(--text-secondary)',
    fontFamily: 'var(--font-display)',
    fontStyle: 'italic',
    maxWidth: '480px',
  },
}

export default function VideoResult({ job }) {
  const ref = useRef(null)

  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [])

  const totalSecs = job.total_frames ? (job.total_frames / 30).toFixed(1) : null

  return (
    <div ref={ref} style={styles.container}>
      <div style={styles.label}>Output Ready</div>

      <div style={styles.videoWrap}>
        <video
          style={styles.video}
          src={job.video_url}
          controls
          autoPlay
        />
      </div>

      <div style={styles.meta}>
        <div style={styles.metaItem}>
          <span style={styles.metaKey}>Prompt</span>
          <span style={styles.promptText}>{job.prompt}</span>
        </div>
        {totalSecs && (
          <div style={styles.metaItem}>
            <span style={styles.metaKey}>Duration</span>
            <span style={styles.metaVal}>{totalSecs}s</span>
          </div>
        )}
        <div style={styles.metaItem}>
          <span style={styles.metaKey}>Slides</span>
          <span style={styles.metaVal}>{job.slides?.length ?? '—'}</span>
        </div>
        {job.total_frames && (
          <div style={styles.metaItem}>
            <span style={styles.metaKey}>Frames</span>
            <span style={styles.metaVal}>{job.total_frames}</span>
          </div>
        )}
      </div>
    </div>
  )
}

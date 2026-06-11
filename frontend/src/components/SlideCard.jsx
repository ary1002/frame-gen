import { retryTts } from '../api.js'

const STATE_META = {
  PENDING:      { label: 'Queued',       color: 'var(--grey)' },
  SCRIPT_READY: { label: 'Script Ready', color: 'var(--blue)' },
  AUDIO_STALE:  { label: 'Audio Stale',  color: 'var(--yellow)' },
  AUDIO_READY:  { label: 'Audio Ready',  color: 'var(--green)' },
  RENDER_READY: { label: 'Render Ready', color: 'var(--amber)' },
  ERROR:        { label: 'Error',        color: 'var(--red)' },
}

const styles = {
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border-subtle)',
    borderRadius: 'var(--radius)',
    padding: '0.75rem 0.9rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
    animation: 'fadeUp 0.4s ease both',
    position: 'relative',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  index: {
    fontSize: '10px',
    color: 'var(--text-muted)',
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
  },
  badge: {
    fontSize: '9px',
    fontFamily: 'var(--font-mono)',
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
    padding: '2px 6px',
    borderRadius: '2px',
    fontWeight: 500,
  },
  duration: {
    fontSize: '11px',
    color: 'var(--text-secondary)',
  },
  error: {
    fontSize: '10px',
    color: 'var(--red)',
    opacity: 0.8,
    lineHeight: 1.4,
    wordBreak: 'break-word',
  },
  retryBtn: {
    alignSelf: 'flex-start',
    padding: '2px 8px',
    background: 'transparent',
    border: '1px solid var(--red)',
    color: 'var(--red)',
    borderRadius: '2px',
    fontFamily: 'var(--font-mono)',
    fontSize: '9px',
    letterSpacing: '0.1em',
    cursor: 'pointer',
    transition: 'background 0.15s',
  },
  activeLine: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    height: '2px',
    background: 'var(--amber)',
    width: '100%',
    animation: 'pulse-glow 1.5s ease-in-out infinite',
  },
}

export default function SlideCard({ slide, jobId }) {
  const meta = STATE_META[slide.state] || STATE_META.PENDING
  const isActive = slide.state === 'AUDIO_STALE' || slide.state === 'SCRIPT_READY'

  async function handleRetry() {
    try {
      await retryTts(jobId, slide.slide_index)
    } catch (e) {
      console.error('Retry failed', e)
    }
  }

  return (
    <div
      style={{
        ...styles.card,
        borderColor: slide.state === 'ERROR' ? 'rgba(224,90,78,0.3)' :
                     slide.state === 'RENDER_READY' ? 'rgba(240,165,0,0.2)' :
                     'var(--border-subtle)',
        animationDelay: `${slide.slide_index * 60}ms`,
      }}
    >
      <div style={styles.header}>
        <span style={styles.index}>Slide {slide.slide_index + 1}</span>
        <span
          style={{
            ...styles.badge,
            color: meta.color,
            background: `${meta.color}18`,
          }}
        >
          {meta.label}
        </span>
      </div>

      {slide.actual_duration_s != null && (
        <span style={styles.duration}>{slide.actual_duration_s.toFixed(1)}s</span>
      )}

      {slide.state === 'ERROR' && slide.error_message && (
        <span style={styles.error}>{slide.error_message}</span>
      )}

      {slide.state === 'ERROR' && (
        <button style={styles.retryBtn} onClick={handleRetry}>
          ↺ Retry TTS
        </button>
      )}

      {isActive && <div style={styles.activeLine} />}
    </div>
  )
}

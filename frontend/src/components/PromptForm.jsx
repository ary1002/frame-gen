import { useState } from 'react'

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    padding: '2rem',
    animation: 'fadeUp 0.6s ease both',
  },
  eyebrow: {
    fontFamily: 'var(--font-mono)',
    fontSize: '10px',
    letterSpacing: '0.2em',
    color: 'var(--amber)',
    textTransform: 'uppercase',
    marginBottom: '1.5rem',
    opacity: 0.8,
  },
  heading: {
    fontFamily: 'var(--font-display)',
    fontSize: 'clamp(2.4rem, 6vw, 4.2rem)',
    fontWeight: 400,
    color: 'var(--text-primary)',
    textAlign: 'center',
    lineHeight: 1.1,
    marginBottom: '0.4rem',
    letterSpacing: '-0.02em',
  },
  headingItalic: {
    fontStyle: 'italic',
    color: 'var(--amber)',
  },
  subtitle: {
    color: 'var(--text-secondary)',
    fontSize: '12px',
    marginBottom: '3rem',
    textAlign: 'center',
    letterSpacing: '0.04em',
  },
  form: {
    width: '100%',
    maxWidth: '640px',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  textareaWrap: {
    position: 'relative',
    borderRadius: 'var(--radius)',
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    transition: 'border-color 0.2s',
  },
  textarea: {
    width: '100%',
    minHeight: '120px',
    padding: '1rem 1.2rem',
    background: 'transparent',
    border: 'none',
    outline: 'none',
    color: 'var(--text-primary)',
    fontFamily: 'var(--font-display)',
    fontSize: '1.05rem',
    lineHeight: 1.6,
    resize: 'vertical',
    caretColor: 'var(--amber)',
  },
  charCount: {
    position: 'absolute',
    bottom: '0.5rem',
    right: '0.8rem',
    fontSize: '10px',
    color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
    pointerEvents: 'none',
  },
  footer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  hint: {
    fontSize: '11px',
    color: 'var(--text-muted)',
  },
  button: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.6rem 1.4rem',
    background: 'var(--amber)',
    color: '#0a0a0b',
    border: 'none',
    borderRadius: 'var(--radius)',
    fontFamily: 'var(--font-mono)',
    fontSize: '12px',
    fontWeight: 500,
    letterSpacing: '0.08em',
    cursor: 'pointer',
    transition: 'opacity 0.15s, transform 0.1s',
  },
  buttonDisabled: {
    opacity: 0.4,
    cursor: 'not-allowed',
    transform: 'none',
  },
  spinner: {
    width: '10px',
    height: '10px',
    border: '2px solid rgba(0,0,0,0.2)',
    borderTopColor: '#0a0a0b',
    borderRadius: '50%',
    animation: 'spin 0.7s linear infinite',
  },
}

export default function PromptForm({ onSubmit }) {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!prompt.trim() || loading) return
    setLoading(true)
    setError(null)
    try {
      await onSubmit(prompt.trim())
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const disabled = !prompt.trim() || loading

  return (
    <div style={styles.container}>
      <div style={styles.eyebrow}>Remotion · Prompt to Video</div>
      <h1 style={styles.heading}>
        What should we{' '}
        <span style={styles.headingItalic}>make?</span>
      </h1>
      <p style={styles.subtitle}>Describe a topic and the pipeline will generate a narrated video.</p>

      <form style={styles.form} onSubmit={handleSubmit}>
        <div
          style={{
            ...styles.textareaWrap,
            borderColor: prompt ? 'var(--border)' : 'var(--border-subtle)',
          }}
          onFocus={e => e.currentTarget.style.borderColor = 'var(--amber-dim)'}
          onBlur={e => e.currentTarget.style.borderColor = 'var(--border)'}
        >
          <textarea
            style={styles.textarea}
            placeholder="e.g. The history of the Roman Empire in 5 slides…"
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit(e)
            }}
            disabled={loading}
            autoFocus
          />
          <span style={styles.charCount}>{prompt.length}</span>
        </div>

        <div style={styles.footer}>
          <span style={styles.hint}>⌘↵ to submit</span>
          <button
            type="submit"
            style={{ ...styles.button, ...(disabled ? styles.buttonDisabled : {}) }}
            disabled={disabled}
            onMouseEnter={e => { if (!disabled) e.currentTarget.style.opacity = '0.85' }}
            onMouseLeave={e => { if (!disabled) e.currentTarget.style.opacity = '1' }}
          >
            {loading && <span style={styles.spinner} />}
            {loading ? 'Starting…' : 'Generate ↗'}
          </button>
        </div>

        {error && (
          <div style={{ color: 'var(--red)', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
            Error: {error}
          </div>
        )}
      </form>
    </div>
  )
}

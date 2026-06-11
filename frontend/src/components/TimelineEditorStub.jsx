import { useState } from 'react'

const MOCK_TRACKS = [
  { label: 'Visual', color: 'var(--amber)' },
  { label: 'Audio',  color: 'var(--blue)' },
  { label: 'Captions', color: 'var(--green)' },
]

const styles = {
  wrapper: {
    borderTop: '1px solid var(--border-subtle)',
    marginTop: '1rem',
  },
  bar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0.7rem 0',
    cursor: 'pointer',
    userSelect: 'none',
  },
  barLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.6rem',
  },
  barLabel: {
    fontSize: '11px',
    color: 'var(--text-muted)',
    letterSpacing: '0.1em',
  },
  v2Badge: {
    fontSize: '8px',
    letterSpacing: '0.15em',
    textTransform: 'uppercase',
    color: 'var(--amber-dim)',
    background: 'rgba(240,165,0,0.08)',
    border: '1px solid rgba(240,165,0,0.15)',
    borderRadius: '2px',
    padding: '1px 5px',
  },
  chevron: {
    fontSize: '10px',
    color: 'var(--text-muted)',
    transition: 'transform 0.2s',
  },
  panel: {
    overflow: 'hidden',
    transition: 'max-height 0.35s ease',
  },
  inner: {
    paddingBottom: '1.5rem',
  },
  description: {
    fontSize: '11px',
    color: 'var(--text-secondary)',
    marginBottom: '1rem',
    lineHeight: 1.6,
    fontFamily: 'var(--font-mono)',
    maxWidth: '500px',
  },
  timelineShell: {
    border: '1px solid var(--border-subtle)',
    borderRadius: 'var(--radius)',
    overflow: 'hidden',
    opacity: 0.6,
    pointerEvents: 'none',
    userSelect: 'none',
  },
  timelineHeader: {
    background: 'var(--bg-card)',
    borderBottom: '1px solid var(--border-subtle)',
    padding: '0.4rem 0.75rem',
    display: 'flex',
    gap: '1px',
  },
  tick: {
    flex: 1,
    fontSize: '8px',
    color: 'var(--text-muted)',
    letterSpacing: '0.05em',
  },
  trackRow: {
    display: 'flex',
    alignItems: 'center',
    borderBottom: '1px solid var(--border-subtle)',
    height: '36px',
  },
  trackLabel: {
    width: '64px',
    flexShrink: 0,
    fontSize: '9px',
    color: 'var(--text-muted)',
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
    padding: '0 0.5rem',
    borderRight: '1px solid var(--border-subtle)',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
  },
  trackArea: {
    flex: 1,
    height: '100%',
    position: 'relative',
    background: 'var(--bg-elevated)',
    display: 'flex',
    alignItems: 'center',
    gap: '2px',
    padding: '0 4px',
  },
  clip: {
    height: '22px',
    borderRadius: '2px',
    fontSize: '8px',
    display: 'flex',
    alignItems: 'center',
    paddingLeft: '6px',
    letterSpacing: '0.06em',
    color: 'rgba(255,255,255,0.5)',
    flexShrink: 0,
  },
}

const MOCK_SLIDES = [
  { w: 110 }, { w: 90 }, { w: 130 }, { w: 80 }, { w: 100 },
]

export default function TimelineEditorStub({ job }) {
  const [open, setOpen] = useState(false)
  const slideCount = job?.slides?.length || 5

  return (
    <div style={styles.wrapper}>
      <div style={styles.bar} onClick={() => setOpen(o => !o)}>
        <div style={styles.barLeft}>
          <span style={styles.barLabel}>Timeline Editor</span>
          <span style={styles.v2Badge}>v2</span>
        </div>
        <span style={{ ...styles.chevron, transform: open ? 'rotate(180deg)' : 'none' }}>▼</span>
      </div>

      <div style={{ ...styles.panel, maxHeight: open ? '400px' : '0' }}>
        <div style={styles.inner}>
          <p style={styles.description}>
            In v2, a non-linear timeline editor will appear here. Slides become draggable clips
            across layered tracks — visual, audio, and captions. Resize clips, reorder slides,
            and re-render without regenerating audio.
          </p>

          <div style={styles.timelineShell}>
            <div style={styles.timelineHeader}>
              {Array.from({ length: 6 }, (_, i) => (
                <span key={i} style={styles.tick}>{i * 5}s</span>
              ))}
            </div>

            {MOCK_TRACKS.map(track => (
              <div key={track.label} style={styles.trackRow}>
                <div style={styles.trackLabel}>{track.label}</div>
                <div style={styles.trackArea}>
                  {MOCK_SLIDES.slice(0, Math.min(slideCount, 5)).map((s, i) => (
                    <div
                      key={i}
                      style={{
                        ...styles.clip,
                        width: s.w,
                        background: `${track.color}28`,
                        border: `1px solid ${track.color}40`,
                      }}
                    >
                      S{i + 1}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

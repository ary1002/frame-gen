import SlideCard from './SlideCard.jsx'
import VideoResult from './VideoResult.jsx'
import TimelineEditorStub from './TimelineEditorStub.jsx'

const STAGES = [
  {
    key: 'script',
    label: 'Script Generation',
    desc: 'LLM generating narration per slide',
    active: (job) => job.status !== 'PENDING',
    done: (job) => job.slides?.some(s => s.state !== 'PENDING'),
  },
  {
    key: 'audio_layout',
    label: 'Layout + Audio',
    desc: 'ElevenLabs TTS & visual layout (parallel)',
    active: (job) => job.slides?.some(s => ['AUDIO_STALE', 'AUDIO_READY', 'RENDER_READY'].includes(s.state)),
    done: (job) => job.slides?.every(s => ['AUDIO_READY', 'RENDER_READY'].includes(s.state)),
  },
  {
    key: 'timeline',
    label: 'Timeline Assembly',
    desc: 'Frame math → RemotionSchema',
    active: (job) => ['RENDERING', 'COMPLETE'].includes(job.status),
    done: (job) => job.total_frames != null,
  },
  {
    key: 'render',
    label: 'Rendering',
    desc: 'Node subprocess → H.264 MP4',
    active: (job) => job.render_progress > 0,
    done: (job) => job.render_progress >= 1,
  },
  {
    key: 'done',
    label: 'Complete',
    desc: 'Video ready',
    active: (job) => job.status === 'COMPLETE',
    done: (job) => job.status === 'COMPLETE',
  },
]

const styles = {
  container: {
    maxWidth: '860px',
    margin: '0 auto',
    padding: '2rem 1.5rem 4rem',
    animation: 'fadeUp 0.4s ease both',
  },
  header: {
    display: 'flex',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    marginBottom: '2rem',
    flexWrap: 'wrap',
    gap: '0.5rem',
  },
  jobId: {
    fontSize: '10px',
    color: 'var(--text-muted)',
    letterSpacing: '0.1em',
    fontFamily: 'var(--font-mono)',
  },
  statusChip: {
    fontSize: '10px',
    letterSpacing: '0.15em',
    textTransform: 'uppercase',
    padding: '3px 8px',
    borderRadius: '2px',
    fontFamily: 'var(--font-mono)',
  },
  body: {
    display: 'grid',
    gridTemplateColumns: '200px 1fr',
    gap: '2rem',
    alignItems: 'start',
  },
  stepper: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0',
    position: 'sticky',
    top: '2rem',
  },
  stepRow: {
    display: 'flex',
    gap: '0.75rem',
    alignItems: 'flex-start',
    paddingBottom: '1.2rem',
    position: 'relative',
  },
  stepLine: {
    position: 'absolute',
    left: '5px',
    top: '14px',
    bottom: 0,
    width: '1px',
    background: 'var(--border-subtle)',
  },
  stepDot: {
    width: '11px',
    height: '11px',
    borderRadius: '50%',
    border: '2px solid var(--border)',
    flexShrink: 0,
    marginTop: '2px',
    transition: 'all 0.3s',
    position: 'relative',
    zIndex: 1,
  },
  stepText: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1px',
  },
  stepLabel: {
    fontSize: '11px',
    fontFamily: 'var(--font-mono)',
    transition: 'color 0.3s',
  },
  stepDesc: {
    fontSize: '9px',
    color: 'var(--text-muted)',
    lineHeight: 1.4,
  },
  right: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  sectionLabel: {
    fontSize: '9px',
    color: 'var(--text-muted)',
    letterSpacing: '0.18em',
    textTransform: 'uppercase',
    marginBottom: '0.75rem',
  },
  slideGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
    gap: '0.5rem',
  },
  renderSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  renderBar: {
    height: '6px',
    background: 'var(--bg-card)',
    borderRadius: '3px',
    overflow: 'hidden',
    border: '1px solid var(--border-subtle)',
  },
  renderFill: {
    height: '100%',
    background: 'var(--amber)',
    borderRadius: '3px',
    transition: 'width 0.5s ease',
  },
  renderLabel: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '10px',
    color: 'var(--text-secondary)',
    fontFamily: 'var(--font-mono)',
  },
}

function statusChipStyle(status) {
  const map = {
    PENDING:   { color: 'var(--grey)',   bg: 'rgba(74,74,85,0.15)' },
    RUNNING:   { color: 'var(--blue)',   bg: 'rgba(74,158,255,0.1)' },
    RENDERING: { color: 'var(--amber)',  bg: 'var(--amber-glow)' },
    COMPLETE:  { color: 'var(--green)',  bg: 'rgba(61,207,142,0.1)' },
  }
  const c = map[status] || map.PENDING
  return { ...styles.statusChip, color: c.color, background: c.bg }
}

export default function PipelineView({ job, error, onReset }) {
  const showRender = job.render_progress > 0 || job.status === 'RENDERING' || job.status === 'COMPLETE'
  const pct = Math.round((job.render_progress || 0) * 100)

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span style={styles.jobId}>job / {job.id}</span>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          {error && <span style={{ fontSize: '10px', color: 'var(--red)' }}>poll error: {error}</span>}
          <span style={statusChipStyle(job.status)}>{job.status}</span>
          <button
            onClick={onReset}
            style={{
              background: 'transparent',
              border: '1px solid var(--border)',
              color: 'var(--text-muted)',
              fontSize: '10px',
              padding: '3px 8px',
              borderRadius: '2px',
              cursor: 'pointer',
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.08em',
            }}
          >
            ← New
          </button>
        </div>
      </div>

      <div style={styles.body}>
        {/* Stepper */}
        <div style={styles.stepper}>
          {STAGES.map((stage, i) => {
            const isActive = stage.active(job)
            const isDone = stage.done(job)
            return (
              <div key={stage.key} style={styles.stepRow}>
                {i < STAGES.length - 1 && <div style={styles.stepLine} />}
                <div
                  style={{
                    ...styles.stepDot,
                    background: isDone ? 'var(--amber)' : isActive ? 'var(--amber-dim)' : 'transparent',
                    borderColor: isDone ? 'var(--amber)' : isActive ? 'var(--amber-dim)' : 'var(--border)',
                    boxShadow: isActive && !isDone ? '0 0 8px var(--amber-glow)' : 'none',
                  }}
                />
                <div style={styles.stepText}>
                  <span
                    style={{
                      ...styles.stepLabel,
                      color: isDone ? 'var(--text-primary)' : isActive ? 'var(--amber)' : 'var(--text-muted)',
                    }}
                  >
                    {stage.label}
                  </span>
                  <span style={styles.stepDesc}>{stage.desc}</span>
                </div>
              </div>
            )
          })}
        </div>

        {/* Right panel */}
        <div style={styles.right}>
          {/* Slides */}
          {job.slides?.length > 0 && (
            <div>
              <div style={styles.sectionLabel}>Slides · {job.slides.length}</div>
              <div style={styles.slideGrid}>
                {job.slides.map(slide => (
                  <SlideCard key={slide.id} slide={slide} jobId={job.id} />
                ))}
              </div>
            </div>
          )}

          {/* Render progress */}
          {showRender && (
            <div style={styles.renderSection}>
              <div style={styles.sectionLabel}>Render Progress</div>
              <div style={styles.renderLabel}>
                <span>Rendering MP4</span>
                <span>{pct}%</span>
              </div>
              <div style={styles.renderBar}>
                <div
                  style={{
                    ...styles.renderFill,
                    width: `${pct}%`,
                    animation: pct < 100 ? 'pulse-glow 1.5s ease-in-out infinite' : 'none',
                  }}
                />
              </div>
            </div>
          )}

          {/* Video result */}
          {job.status === 'COMPLETE' && job.video_url && (
            <VideoResult job={job} />
          )}

          {/* Timeline stub */}
          <TimelineEditorStub job={job} />
        </div>
      </div>
    </div>
  )
}

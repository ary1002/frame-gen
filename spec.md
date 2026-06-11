# Pipeline A — Prompt-to-Video: Technical Spec

**Version:** 1.1  
**Scope:** Text prompt input path only. Slide deck input (PDF/PPTX) is out of scope.  
**Runtimes:** Python 3.11 (orchestration, LLM, TTS) · Node.js (Remotion render)

---

## 1. Architecture Overview

```
Text Prompt
    │
    ▼
[1] Script Generation  ──────────────────────► SlideScript[]
    │                │
    ▼                ▼
[2A] Layout Gen   [2B] TTS (ElevenLabs)
    │                │
    ▼                ▼
SlideLayout[]     AudioBlob[]
    │                │
    └────── [3] BARRIER ──────┘
                 │
                 ▼
         [4] Timeline Assembly  ─────────────► RemotionSchema
                 │
                 ▼
         [5] Remotion Lambda Render  ────────► output.mp4
                 │
                 ▼
         [6] Eval Layer (async)
```

---

## 2. Infrastructure

| Layer | Technology |
|---|---|
| API | FastAPI (async) — job submission + status polling |
| Task queue | Celery + Redis |
| State store | PostgreSQL — job table, per-slide state machine, eval store |
| Artifact store | S3 — scripts, audio blobs, schemas, output video |
| LLM | GPT-4o (script gen, layout gen, article gen) |
| TTS | ElevenLabs API |
| Audio measurement | `ffprobe` |
| Rendering | Remotion Lambda (`renderMediaOnLambda`) |
| Eval judge | Claude Sonnet (async, post-render) |

**Runtime boundary:** Python owns all orchestration, LLM calls, and TTS. Node owns all Remotion composition and the Lambda render call. Python triggers the render via a Node subprocess or thin Node wrapper script. No in-process sharing.

---

## 3. Data Contracts

### 3.1 SlideScript `(script gen → TTS + layout gen + article gen)`

| Field | Type | Notes |
|---|---|---|
| `slide_index` | `int` | Zero-based position assigned by script gen |
| `text` | `str` | Final narration |
| `word_count` | `int` | Measured deterministically post-generation |
| `est_duration_s` | `float` | Estimate only — never used for frame math |
| `gen_attempts` | `int` | 1–3 |
| `status` | `enum` | `READY \| TRUNCATED \| ERROR` |
| `prompt_version` | `str` | Prompt Hub template ID — eval traceability |
| `script_hash` | `str` | SHA-256 of `text` — staleness detection key |

### 3.2 SlideLayout `(layout gen → timeline assembler)`

| Field | Type | Notes |
|---|---|---|
| `slide_index` | `int` | Matches `SlideScript.slide_index` |
| `template` | `str` | `comparison_two_col \| bullet_list \| title_card \| split_layout \| …` |
| `props` | `dict` | `title`, `points[]`, `columns[]`, `background_color`, `eyebrow` |
| `effect` | `EffectConfig` | `type: zoom\|blur\|spotlight` · `from` · `to` · `easing` |
| `transition_out` | `TransConfig` | `type: wipe\|fade\|dissolve\|circle_wipe\|stack` · `direction` · `duration_frames` |
| `duration_frames` | `int \| None` | **`null` at generation** — filled by timeline assembler after TTS |

### 3.3 AudioBlob `(TTS → timeline assembler)`

| Field | Type | Notes |
|---|---|---|
| `slide_index` | `int` | Matches `SlideScript.slide_index` |
| `url` | `str` | S3 blob URL |
| `actual_duration_s` | `float` | Measured by `ffprobe` — ground-truth duration |
| `voice_id` | `str` | ElevenLabs voice identifier |
| `script_hash` | `str` | Copied from `SlideScript` — staleness key |

### 3.4 RemotionSchema `(timeline assembler → Remotion Lambda)`

| Field | Type | Notes |
|---|---|---|
| `slides` | `SlideEntry[]` | `slide_index · start_frame · duration_frames · audio_url · layout` |
| `captions` | `CaptionConfig` | `style · color_active · word_timestamps[]` |
| `total_frames` | `int` | Sum of all `duration_frames` |
| `fps` | `int` | 30 — constant |
| `serve_url` | `str` | S3 URL of deployed Remotion React bundle |

---

## 4. Stage Specifications

### Stage 1 — Script Generation

**Input:** Raw text prompt  
**Output:** `SlideScript[]` persisted to S3 + PostgreSQL  
**Worker:** Single LLM call with structured output, not queued

**Behaviour:**
1. Call GPT-4o with structured output. The prompt instructs the model to decompose the input into N narrated slides (cap: 12) and emit a complete `SlideScript` for each — `slide_index`, `text`, `est_duration_s` — in one response.
2. Measure `word_count` deterministically on each returned `text` field. Do not trust any count from the model.
3. Run quality gate on every slide. Retry the full call (max 3 attempts) if any slide fails. Tighten word count bounds in the system prompt on each retry.
4. On 3 consecutive failures: hard-truncate failing slides to the word count ceiling, set `status = TRUNCATED`.
5. Compute `script_hash = SHA-256(text)` per slide.
6. Persist `SlideScript[]` to PostgreSQL. The count N is fixed — all downstream fan-outs operate over this exact set.

**Quality gate — all must pass per slide:**

| Check | Condition |
|---|---|
| Word count | Within ±20% of `est_duration_s × (130 / 60)` |
| Structure | No mid-sentence endings; narration forms a complete thought |
| Slide count | N ≥ 2; retry if fewer returned |

**Prompt Hub:** System prompt is a versioned template stored in PostgreSQL. Each call records `prompt_version` in every `SlideScript` for eval traceability.

---

### Stage 2A — Visual Layout Generation

**Input:** `SlideScript`  
**Output:** `SlideLayout` persisted to S3  
**Worker:** Celery fan-out — one task per slide, runs in parallel with Stage 2B  
**Dependency:** Stage 1 complete

**Behaviour:**
- Call GPT-4o. Provide the narration `text` for the slide. Output must be bounded JSON: one `template` name from the allowed enum, filled `props`, one `effect`, one `transition_out`.
- Validate against Pydantic schema. Reject and retry (max 2 attempts) on schema violation or out-of-bounds enum value.
- Set `duration_frames = None`. This field is intentionally incomplete — the timeline assembler fills it after TTS.
- Write `SlideLayout` JSON to S3.

**Allowed templates:** `title_card` · `bullet_list` · `comparison_two_col` · `split_layout` *(extend as Remotion components are added)*

---

### Stage 2B — TTS

**Input:** `SlideScript`  
**Output:** `AudioBlob` persisted to S3  
**Worker:** Celery fan-out — one task per slide, runs in parallel with Stage 2A  
**Dependency:** Stage 1 complete

**Behaviour:**
- Call ElevenLabs with `SlideScript.text` and configured `voice_id`. Bound concurrency with a semaphore at the ElevenLabs rate limit.
- Store returned audio blob to S3. Capture `url`.
- Run `ffprobe` on the blob to measure `actual_duration_s`. This is the only duration used for all downstream frame calculations.
- Copy `script_hash` from `SlideScript` into `AudioBlob`.
- Update slide state: `SCRIPT_READY → AUDIO_STALE → AUDIO_READY`.
- On max retries exceeded: slide state → `ERROR`. Surface to user.

> **Invariant:** `actual_duration_s` is ground truth. `est_duration_s` in `SlideScript` exists only for token budget planning. Conflating them produces narration/visual desync.

---

### Stage 3 — Barrier

**Input:** Slide state table in PostgreSQL  
**Output:** Enqueue timeline assembly task (or surface errors)  
**Worker:** Checked after each Stage 2B task completes

**Behaviour:**
- After every TTS task completion, query PostgreSQL: are all N slides in `AUDIO_READY`?
- If yes → enqueue timeline assembly.
- If any slide is `ERROR` → hold render. Expose per-slide retry to the user. The barrier is total — a single failed TTS blocks the entire pipeline.

**Slide state machine:**

```
PENDING
  │  script gen completes
  ▼
SCRIPT_READY
  │  (auto) enqueue TTS
  ▼
AUDIO_STALE ──── TTS fails (max retries) ──► ERROR ─── user retry ──┐
  │                                                                   │
  │  TTS completes                                                    │
  ▼                                                                   │
AUDIO_READY ◄──────────────────────────────────────────────────────-─┘
  │ (if user edits script → AUDIO_STALE, recompute script_hash)
  │ (all slides AUDIO_READY → RENDER_READY)
  ▼
RENDER_READY
```

---

### Stage 4 — Timeline Assembly

**Input:** `SlideLayout[]` + `AudioBlob[]` from S3  
**Output:** `RemotionSchema` written to S3  
**Worker:** Single synchronous task — no LLM  
**Dependency:** Barrier cleared (all slides `AUDIO_READY`), all `SlideLayout` objects written

**Behaviour — fully deterministic arithmetic:**
1. For each slide in order:
   - `duration_frames = round(actual_duration_s × 30)`
   - `start_frame = Σ(previous duration_frames) − (20 × slide_index)` — 20-frame transition overlap
   - Write `duration_frames` into `SlideLayout` (fills the `None` from Stage 2A)
2. Build `RemotionSchema`:
   - `slides[]`: one `SlideEntry` per slide with `start_frame`, `duration_frames`, `audio_url`, `layout`
   - `captions`: word timestamps from TTS + style config
   - `total_frames`: Σ all `duration_frames`
   - `fps`: 30
   - `serve_url`: deployed Remotion bundle S3 URL
3. Write schema to S3. This JSON is the boundary artifact handed to the Node runtime.

---

### Stage 5 — Remotion Composition (Node/Build-time)

**This stage is a build/deploy step, not a runtime job.**

**Remotion components to implement:**

`SlideTemplate` components — one per template name, each renders a 1920×1080 React layout from its `props` JSON. No dynamic data; only controlled visual rendering driven by the schema.

`SlideWithEffect` — wraps any `SlideTemplate`. Reads `effect` from `SlideLayout` and applies zoom, blur, or spotlight animation via `useCurrentFrame()` interpolation.

`PipelineAComposition` — root composition:
```jsx
export function PipelineAComposition({ schema }) {
  return (
    <>
      <TransitionSeries>
        {schema.slides.map((slide, i) => (
          <React.Fragment key={slide.slide_index}>
            <TransitionSeries.Sequence durationInFrames={slide.duration_frames}>
              <SlideWithEffect data={slide} />
              <Audio src={slide.audio_url} />
            </TransitionSeries.Sequence>
            {i < schema.slides.length - 1 && (
              <TransitionSeries.Transition
                presentation={resolveTransition(slide.layout.transition_out)}
                timing={linearTiming({ durationInFrames: 20 })}
              />
            )}
          </React.Fragment>
        ))}
      </TransitionSeries>
      <CaptionsLayer captions={schema.captions} />
    </>
  );
}
```

`CaptionsLayer` — absolute overlay using `@remotion/captions` and Whisper word timestamps.

**Deploy:**
```bash
npx remotion lambda sites create --site-name pipeline-a-v1
npx remotion lambda functions deploy
```
Capture `serve_url` from the first command. Store in config — it goes into every `RemotionSchema`.

---

### Stage 6 — Lambda Render

**Input:** `RemotionSchema` S3 path  
**Output:** `output.mp4` in S3  
**Worker:** Python invokes a Node subprocess that calls `renderMediaOnLambda()`

**Render config:**

| Parameter | Value |
|---|---|
| `composition` | `PipelineAComposition` |
| `inputProps` | Deserialized `RemotionSchema` |
| `serveUrl` | Deployed bundle `serve_url` |
| `framesPerLambda` | 150 |
| `codec` | `h264` |
| `framesPerLambda` | 150 |

**Behaviour:**
- Python enqueues a Celery task that calls the Node render wrapper.
- Node wrapper calls `renderMediaOnLambda()`, then polls `getRenderProgress()` in a loop.
- Progress updates written to PostgreSQL; frontend polls the job status endpoint.
- On completion: write `output.mp4` S3 URL to job record. Update job state to `COMPLETE`.
- **In parallel with render:** Single GPT-4o call over all `SlideScript.text` fields → `article.md` written to S3 alongside the video.

---

### Stage 7 — Evaluation Layer (async, post-render)

**Input:** `SlideScript[]` + `SlideLayout[]` for the completed project  
**Output:** Eval scores in PostgreSQL  
**Worker:** Celery task, enqueued after job reaches `COMPLETE`

**Judge:** Claude Sonnet evaluating GPT-4o outputs — avoids self-grading bias.

**Scoring — 1 to 5 per dimension:**

| Dimension | What it checks |
|---|---|
| Factual consistency | Script content is coherent and internally consistent |
| Coherence | Narration is logical and flows from previous slide |
| Tone compliance | Matches the Prompt Hub style constraint |
| Duration plausibility | `word_count` aligns with `target_duration_s` |

**Storage:** Append-only table keyed by `(project_id, slide_index, prompt_version)`. Slides scoring below 3 on any dimension are flagged.

**Downstream consumers:**
- Model upgrade gating — run new LLM against historical prompts before promoting
- Prompt Hub quality signals — identify underperforming templates
- Failure mode debugging — any user complaint traces to exact inputs and scores

---

## 5. LLM vs Deterministic Decision Table

| Step | LLM | Det. | Rationale |
|---|---|---|---|
| Script generation (decompose + narrate) | ✓ | | Single GPT-4o structured output call |
| Script length enforcement | ✓ | ✓ | LLM generates; deterministic measures, retries, truncates |
| Script quality gate | | ✓ | Rule-based word count + structural checks |
| Visual layout selection | ✓ | ✓ | LLM outputs JSON; Pydantic validates |
| Template selection | ✓ | | LLM picks from bounded enum |
| Effect / transition selection | ✓ | | LLM picks type and parameters |
| Audio duration measurement | | ✓ | `ffprobe` — never inferred |
| Frame number calculation | | ✓ | `actual_duration_s × 30` |
| Timeline assembly | | ✓ | Arithmetic over `AudioBlob` values |
| Caption word highlighting | | ✓ | `@remotion/captions` + Whisper word timestamps |
| Staleness detection | | ✓ | SHA-256 hash comparison on `script_hash` |
| Article generation | ✓ | | Single LLM call over all final scripts |
| Eval scoring | ✓ | | Claude Sonnet as judge |

---

## 6. Failure Modes

| Failure | Recovery |
|---|---|
| Script gen returns < 2 slides | Retry up to 3× with stricter slide count constraint in system prompt |
| Script quality gate fails 3× | Hard truncate last attempt; `status = TRUNCATED` |
| TTS timeout / ElevenLabs 503 | Retry ×3 with exponential backoff → `ERROR` state → surface to user |
| Layout gen schema violation | Retry ×2; reject on second failure → surface to user |
| User edits script after TTS | `script_hash` diff → `AUDIO_STALE` → user-triggered re-TTS |
| Animation JSX crashes in Remotion | Sandboxed preview catches before Lambda render is enqueued |
| Remotion Lambda OOM | Lambda auto-retries chunk; bundle versioned in `serve_url` — rollback by URL |

---

## 7. Build Order

| Phase | Depends on | Deliverable |
|---|---|---|
| 0 | — | Infra: FastAPI, Celery, Redis, Postgres, S3 |
| 1 | Phase 0 | Script gen — prompt → `SlideScript[]` with quality gate |
| 2B | Phase 1 | TTS fan-out with `ffprobe` measurement → `AudioBlob[]` |
| 2A | Phase 1 | Layout gen fan-out → `SlideLayout[]` (duration_frames=null) |
| 3 | Phase 2B | Barrier + slide state machine |
| 4 | Phase 2A + 3 | Timeline assembler → `RemotionSchema` |
| 5 | Independent | Remotion composition build + Lambda deploy |
| 6 | Phase 4 + 5 | Lambda render → `output.mp4` |
| 7 | Phase 6 | Async eval layer |

**Critical path:** `1 → 2B → 3 → 4 → 6`

Layout generation (2A) sits off the critical path — it only needs to complete before timeline assembly, not before TTS. Build and validate TTS + barrier first. That is where the most production risk is concentrated.
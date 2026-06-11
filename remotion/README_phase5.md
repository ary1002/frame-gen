# Remotion Phase 5

## Setup
cd remotion
npm install

## Preview in Remotion Studio
npm run studio
# Opens browser at http://localhost:3000

## Test render (no audio)
node render.mjs fixtures/sample_schema.json /tmp/test_output.mp4

## Notes
- Templates: title_card, bullet_list, comparison_two_col, split_layout
- Effects: zoom (scale), blur (CSS filter), spotlight (radial vignette)
- Transitions: fade, wipe, dissolve (=fade), circle_wipe, stack (=flip)
- Captions: word-highlight overlay driven by word_timestamps
- render.mjs is called by Python pipeline as a subprocess; it prints JSON progress lines to stdout

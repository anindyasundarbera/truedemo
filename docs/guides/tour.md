# A tour: what happens when you build

This page assumes you have never seen truedemo. It answers one question — *what does
`truedemo build` actually do?* — and then points you at the page that goes deeper on whatever
you care about. Read it once; everything else refers back to it.

If you would rather do it than read it, start with
[your first video](first-video.md) instead and come back here when you want the model.

---

## The shape of a build

You write a **spec** (`video.yaml`). It names a **provider** (a small Python module that
fetches *your* data), a **narration** script, and a list of **shots** — the visual beats.
You run one command. You get a video, captions, and a report that checks the video.

```
 video.yaml ──┐
 provider.py ─┼─► truedemo build ─►   your-video.mp4
 narration.md ┘                    your-video.srt
 assets/*.svg                      _build/verify.json      ← did we keep our promises?
                                   _build/provenance.json  ← what is this file, exactly?
```

Nothing in the spec executes code. The only code that runs is the provider module you name,
so a spec is safe to hand to an agent or paste in a ticket. The loader **refuses unknown
top-level keys by name**, so a typo is an error rather than a section that silently vanishes.

The vocabulary — story, timeframe, scene, shot, capture, chart, panel, dataset, provider,
guard, stage — is defined once in [concepts](../foundations/concepts.md). If a term below is
unfamiliar, that page is the one to read next.

## The ten stages

A build is a fixed, ordered list of **stages**. `truedemo build` runs them all; `--only a,b`
runs a subset. Each stage reads something, writes a file, or stops the build.

| Stage | What it does |
|---|---|
| `data` | Runs your provider once; snapshots every dataset to `data/*.json` so panels can re-render offline. |
| `panels` | Renders each chart's dataset to SVG (11 built-in kinds, or yours). |
| `stills` | Resolves provider stills and declared graphic assets. |
| `capture` | Drives Playwright: runs your actions, **asserts the on-screen state**, then screenshots. |
| `exec` | Runs your declared commands in a real PTY inside a sandbox, and records the screen. |
| `narration` | Parses the script, builds the SRT, synthesizes one WAV per scene. |
| `clips` | Sizes every shot from the **measured** audio, not from an estimate. |
| `concat` | Joins the shots, applying declared per-shot transitions. |
| `render` | Draws overlays and burns in the captions; muxes audio. |
| `verify` | Reopens the result and runs the acceptance checks. |

The measured audio is the **master clock**. That is why sync is a consequence of the
pipeline rather than something you keep by hand: each scene's video segment is sized to the
duration ffmpeg measured from that scene's WAV, not to a number anyone typed.

For each stage's exact inputs, outputs, and failure conditions, read
[pipeline](../foundations/pipeline.md).

## What can be on screen

A **scene** is one narration block. It holds one or more **shots**, and a shot's `weight`
splits the scene's time between them. Every shot is one of:

| Shot | Shows |
|---|---|
| `still:` | An image you shipped (SVG/PNG), fitted — never stretched. |
| `capture:` | A named capture: a real Playwright run against a real URL or a downloaded artifact. |
| `chart:` | A named panel, drawn from a provider dataset. |
| `exec:` | A recording of a real command that ran in a declared sandbox or container. |
| `card:` | A title card the engine **draws** from the shot's own words — kicker, rule, scrim. |
| `solid:` | One flat declared field. |

Any shot may also carry `motion:` (a declared camera move) or `transition:` (how it joins
the next shot). Both are *declarations*, and both are measured in the finished file — a
camera move is not a camera move until two frames of the finished clip disagree. A scene, or
a single shot, may also declare its own `seconds:`, which takes the length out of the voice's
hands for a film whose pacing is part of the story.

Every field, default, and constraint lives in the
[spec reference](../authoring/spec-reference.md).

## Where to go next

| You want to… | Read |
|---|---|
| Go from an empty clone to a verified `.mp4` | [your first video](first-video.md) |
| Copy a working pattern for a common task | [recipes](recipes.md) |
| Write or validate a `video.yaml` | [spec reference](../authoring/spec-reference.md) |
| Connect truedemo to your data | [provider guide](../authoring/provider-guide.md) |
| Draw a chart or panel | [panels reference](../authoring/panels-reference.md) |
| Write the script and control captions | [narration and captions](../authoring/narration-and-captions.md) |
| Record real UI and assert it | [capture guide](../capture/capture-guide.md) |
| Film a real terminal session | [exec guide](../capture/exec-guide.md) |
| Understand the checks and `verify.json` | [verification](../verification/verification.md) |
| Drive it from an agent | [the studio](../operations/studio-reference.md) |

## Extending

The engine is meant to be extended from your provider, not edited. If you do find yourself
in `truedemo/`:

- **A new chart** — `panels.register(name, fn)` from your provider; `fn(data, options, doc)`
  appends SVG via the helpers in `truedemo.svg`.
- **A new capture action** — add a branch in `truedemo/capture.py::apply`.
- **A new TTS engine** — add a branch in `truedemo/tts.py`.
- **A new stage** — *don't, not casually.* The stage list is the design's contract: ten phases
  added Docker, an executor, movie mode, and a whole session layer without an eleventh.

The module map, the key types, and every extension seam are documented together in
[architecture](../foundations/architecture.md).

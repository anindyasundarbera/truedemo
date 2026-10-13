# truedemo

**truedemo creates narrated, captioned demo videos of software.** Point it at a real browser UI
or a real terminal command, give it your own data, and describe the film in a small
declarative spec — it drives the software, records what it does, draws your data onto charts,
writes the narration, and assembles the result into an `.mp4` with an `.srt`. Then it
**reopens the finished `.mp4`** to check it kept every promise the spec made. A broken promise
fails the build. Run it from a shell, or let an autonomous agent drive it over MCP.

---

## What it is

You have a piece of software. You need a demo video of it — for a launch page, a README, a
customer, or a release. Today you make that by hand: drive the app, record the screen, write
a script, record a voice-over, cut the takes together, and type the numbers onto the slides.
It works, and it does not scale. Change the product and the video is stale; change the
numbers and the video is a lie that nobody notices until a customer does.

truedemo automates that whole loop from a declarative spec, and — the part that makes it worth
using — refuses to let the result be dishonest. Every frame comes from something real, and a
report re-opens the render to check the claims actually held.

**It is for** anyone who makes software demo videos by hand and is tired of them drifting
out of date, and for agents that must produce one without a human watching the screen.

**It films software you can drive on screen** — a web UI in a real browser, a command in a
real terminal, or a document the software produces. It does not capture a native desktop GUI,
invent a UI, or act as a video editor: there is no timeline to drag and no keyframes to set.
You declare shots, and truedemo builds the film and checks it.

> New here? [**A tour: what happens when you build**](docs/guides/tour.md) is the orientation —
> what a spec is, what the ten stages do, and what can be on screen.

## See it run

Thirty seconds, with no browser, no network, and no voice model. Install the package, then
scaffold a runnable story and build it — every number on screen is measured from disk, not
typed:

```bash
pip install truedemo                                      # ffmpeg + rsvg-convert required; see Install

truedemo doctor                                           # is this machine ready?
truedemo init  my-story --title "My first video" --days 14
truedemo plan  my-story/video.yaml                       # scenes, timings, guards — render nothing
truedemo build my-story/video.yaml                       # → my-story.mp4 + .srt + verify.json
```

`init` writes a story that builds as written — a spec, a narration script, and a working
provider, with no asset or network to wire up first. `plan` is the cheap one: the whole scene
plan and the estimated runtime, without touching a pixel. `build` is the real thing, and the
`verify.json` it writes is the report this project exists to produce.

<details>
<summary>Working on the engine itself? The same loop from a clone</summary>

The bundled examples live in the repository, **not** in the installed package, so this path is
for a checkout of the source:

```bash
git clone https://github.com/anindyasundarbera/truedemo
cd truedemo
pip install -e ".[dev]"

truedemo doctor examples/hello-world/video.yaml   # is this machine ready?
truedemo plan   examples/hello-world/video.yaml
truedemo build  examples/hello-world/video.yaml   # → hello-world.mp4 + .srt + verify.json
```

`examples/hello-world` is the offline CI fixture — no browser, no network, no voice model. CI
builds it on every push.

</details>

## Why it is honest

**Nothing is fabricated.** Every frame traces to something real: a live capture of a running
product, a chart drawn from a provider's measured data, or a declared graphic the engine drew
from the script's own words. There is no "mock UI" mode, because a mock UI is
indistinguishable from a real one once it is inside the `.mp4`.

**The engine then reopens the render and proves it.** `verify` does not read your spec back
to you. It decodes the finished `.mp4`, the `.srt`, and the audio track, and checks the
artifact against the promises the spec made. A broken promise fails the build.

The failure modes this prevents are boring and predictable, which is exactly why they keep
happening:

- The recording shows **development mode** while the narration says the product is live.
- A **caption runs off the screen** two lines into a sentence, so nobody reads it.
- The voice-over states a number that was **typed from memory**, not measured.
- The cut **drifts out of sync**, because the timing table was estimated rather than measured.
- The runtime is 26 minutes and the limit was 25.
- The script makes a claim the spec **explicitly forbade**, and nothing checks it.

Hand that job to an LLM agent and it hits every one of those faster, because the agent
cannot see the screen. It writes a spec, renders, and reports success. Nothing in that loop
ever asked whether the pixels agreed with the words.

And one rule that turned out to matter more than any single feature:

> **A declaration is not a measurement.** A check about what a picture *did* decodes the
> picture. A camera move declared in the spec is not a camera move until two frames of the
> finished clip disagree.

That rule has since caught real defects three separate times — including a check that could
never fail, because it compared a list against a filter of itself and cheerfully reported
*"5 of 6 shots move"* about shots that had only **said** they move.

## What it does

Ten stages, one pass, no timeline editor anywhere in it — `data` → `panels` → `stills` →
`capture` → `exec` → `narration` → `clips` → `concat` → `render` → `verify`. Each stage
reads something, writes a file, or stops the build.

The measured audio is the **master clock**: each scene's video segment is sized to the
duration ffmpeg measured from that scene's WAV, so sync is a consequence of the pipeline
rather than something you keep by hand. The [tour](docs/guides/tour.md#the-ten-stages) walks
each stage and the [pipeline](docs/foundations/pipeline.md) defines its exact inputs,
outputs, and failure conditions.

## Install

```bash
pip install truedemo              # the engine — YAML/JSON specs
pip install "truedemo[capture]"   # + Playwright, to film a real browser UI
pip install "truedemo[tts]"       # + Piper, for a local voice
pip install "truedemo[mcp]"       # + the MCP server (`truedemo-mcp`)
pip install "truedemo[dev]"       # + pytest
```

Or from a clone, if you want to work on the engine itself: `pip install -e ".[dev]"`.

The package installs the **engine**; the examples, the `docs/` tree, and the test suite live
in the [repository](https://github.com/anindyasundarbera/truedemo) and are not part of a
`pip install`. Everything in the docs is readable after install via `truedemo docs` — and,
when the tree is not present, `truedemo docs` points you at the published copy rather than
failing.

Required external binaries are **`ffmpeg`** and **`rsvg-convert`** (Debian/Ubuntu:
`sudo apt-get install ffmpeg librsvg2-bin`). Optional: `ffprobe` (durations are read from
ffmpeg when absent), `pdftoppm`/`gs` (for filming PDFs), Chromium (Playwright), and a Piper
voice model. The extras are additive and independent — the core suite needs none of them.

`truedemo doctor` reports exactly which of these are present, and names the **missing rung**
rather than a bare "Docker: unavailable".

## The spec and your data

A spec is data. No code executes from it; the only code that runs is the provider module you
name. The loader refuses unknown top-level keys **by name**, so a typo is an error rather than
a silently dropped section. The [spec reference](docs/authoring/spec-reference.md) opens with
all fourteen legal keys on one screen; here is the shape:

```yaml
project:   { title: …, slug: …, output: out.mp4, size: [1920, 1080], fps: 30,
             min_seconds: 60, max_seconds: 120 }
story:     { slug: …, title: … }        # optional manifest, or a story.yaml folder
timeframe: { start: 2026-09-07, end: 2026-10-06 }   # or { days: 90, as_of: … }
voice:     { engine: piper, model: voice.onnx }    # engine: none → declared silent cut
narration: { source: narration.md }     # "## Scene N — … · mm:ss–mm:ss", spoken lines **bold**
provider:  provider                     # provider.py: datasets, panels, stills
captures:  [ … ]   exec: { steps: [ … ] }   environment: [ … ]   charts: [ … ]
score:     { src: bed.ogg, volume: 0.45, duck_db: -12.0 }
scenes:    [ … ]   guard: { banned: […], required: […] }   style: { … }
```

**What can be on screen.** A scene holds one or more shots, and a shot's `weight` splits the
scene's time between them. Every shot is one of `still:`, `capture:`, `chart:`, `exec:`,
`card:`, or `solid:`, and any shot may carry `motion:` or `transition:`. The
[tour](docs/guides/tour.md#what-can-be-on-screen) lists each with what it shows, and the
[spec reference](docs/authoring/spec-reference.md#scenes) has every field and default.

**Your data.** `provider.py` is a plain module named in the spec, and it is the only code a
spec can run — all project-specific knowledge lives there, which is what keeps the engine
generic:

```python
from truedemo import panels as panel_lib

def register():     panel_lib.register("my_chart", my_chart_renderer)
def datasets(ctx):  return {"trend": fetch_trend(), "totals": compute_totals()}
def panels():       return {"trend": {"kind": "my_chart", "dataset": "trend"}}
```

Datasets are snapshotted on every build, so a later render replays them offline — and a
*degraded* one is declared in the report rather than passed off as live. Eleven panel kinds
ship with the engine. See the [provider guide](docs/authoring/provider-guide.md) and the
[panels reference](docs/authoring/panels-reference.md).

## The studio — driving it from an agent

`truedemo-mcp` runs **separately** from the consumer's repo: the story stays in your repo, the
tool stays a tool. It is session-oriented — an agent opens a sitting, pokes at a live
environment, tries several takes, keeps the best, builds, and reads the report back:

```
session_open ──► session_exec / browser_open+browser_act ──► browser_shot ×3
                                                                    │
                                                         take_select ┘
                                                                    ▼
                                                    session_build ──► session_report
```

There are **34 MCP tools** and **7 resources**. A selected take survives the build, and
budgets (wall-clock, container, step) are declared and refused rather than silently
overrun. The workflow, the tool groups, and the take/budget rules are in
[the studio reference](docs/operations/studio-reference.md); wiring the server into a client
is in the [MCP server](docs/operations/mcp-server.md) page.

For a transport-independent integration, the same work is available as a job:

```bash
truedemo --json run plan --story my-story      # {action, story, out} → one manifest
```

## Verification — the part that makes it worth using

`verify.json` is the point of the project. It is not a log; it is an argument about the
finished file, and every check can fail. There are **twenty kinds of check**, and a build
runs only the ones its spec can actually break — a typical build runs a dozen or so, covering
the runtime window, caption readability, frame size, audio presence, banned/required phrases,
the declared timeframe, live captures and filmed artifacts, sandboxed exec, dataset
freshness, and the honesty of every picture and camera move:

| A sample of the checks | What it establishes |
|---|---|
| `runtime within window` | The cut is inside the declared `min_seconds`/`max_seconds`. |
| `captions readable (<=2 lines, <=42 chars)` | Every cue fits on screen, two lines at most. |
| `banned phrase absent` / `required phrase present` | The script says what it must, and never what it must not. |
| `all live captures present` | Every capture the spec named is really in the film. |
| `every picture has an honest source` | Each artwork is a capture, a dataset, or a declared asset — nothing unknown. |
| `every camera move is accounted for` | `facts.motion[].mae` is **measured** from real frames; a move that did not move is reported. |
| `declared score is in the mix` | The bed really was mixed, with the measured ducking depth. |

The full table, and what each check does *not* prove, is in
[verification](docs/verification/verification.md). `provenance.json` answers a different
question — *what is this file?* — with the spec digest, the resolved timeframe, the provider,
and the tool versions that made it ([provenance](docs/verification/provenance.md)).

## Examples in this repo

The packages on PyPI ship the **engine only** — no examples, docs, or tests. These live in the
repository and are built from a checkout:

| Example | Proves |
|---|---|
| [`hello-world`](examples/hello-world/) | The smallest complete build: offline, silent, every number measured from disk. The CI fixture. |
| [`capture-kit`](examples/capture-kit/) | A real page, scripted interactions, and assert-before-shot. |
| [`terminal-demo`](examples/terminal-demo/) | A real command in a real sandbox, recorded through a PTY and filmed. |
| [`docker-demo`](examples/docker-demo/) | A real Postgres, written to and read back **inside one container**, then torn down. |
| [`movie-demo`](examples/movie-demo/) | A film with **no capture, no provider, no browser**: drawn cards, a moving camera, a score. |

CI builds each of these as an end-to-end probe on a clean runner, and one more probe drives
the MCP server through a whole sitting — on top of the unit suite. For your own first story,
`truedemo init` is the installed equivalent — it needs no clone.

## Extending

The engine is meant to be extended from your provider, not edited — a new chart via
`panels.register()`, a new capture action, or a new TTS engine. The
[tour](docs/guides/tour.md#extending) lists the seams, and
[architecture](docs/foundations/architecture.md) maps every module, key type, and extension
point in one place.

## Layout

The engine is 29 modules behind one ten-stage pipeline.
[architecture](docs/foundations/architecture.md) maps every module, the one-way dependency
graph, and the typed seams between them.

## Docs

Docs are modular and machine-routable. Start at [`docs/README.md`](docs/README.md), or read
the route table in [`docs/modules.yaml`](docs/modules.yaml) — 26 routes across 7 modules.
An agent can fetch any doc by bare name over MCP (`truedemo_docs name="tour"`).

For the project's own record, see [`docs/plan/`](docs/plan/): [PLAN](docs/plan/PLAN.md) (now and
next), [HISTORY](docs/plan/HISTORY.md) (what happened, with evidence),
[DECISIONS](docs/plan/DECISIONS.md) (why, with alternatives), and the root
[ROADMAP.md](ROADMAP.md) (requirements and milestones).

## Tests

```bash
python3 -m pytest tests -q          # 782 tests; the core needs no external tools
```

The suite is written to **skip honestly**: six independent capability markers
(`needs_render`, `needs_sandbox`, `needs_docker`, `needs_playwright`, `needs_mcp`,
`needs_pre_312_python`) each probe *whether that capability is usable*, not whether the
toolchain looks complete. CI runs the lean suite on Python 3.10 and 3.12, then builds the
examples end to end.

## What it is not

- **Not an NLE.** No timeline UI, no keyframe editing; a film is a sequence of shots.
- **Not a UI generator.** It films what runs. It will not invent an interface for you.
- **Not your data layer.** It reads; your provider owns the truth and the fetching.
- **Not a hosted service.** It runs locally and offline after install.
- **Not vendored.** Consumers point at the standalone server; the story stays in their repo.

## Status

`1.0.0`, Apache-2.0, and honest about where it is: the engine, the studio surface, capture,
sandboxed exec, Docker environments, and movie mode are merged and verified, and CI builds
the examples end to end on a clean runner. The MCP server supports SDK 1.x and 2.x
(`mcp>=1.20,<3`). What remains is release bookkeeping — the `v1.0.0` tag and the version for
these post-1.0 milestones are still an open owner decision — and a compositor
(picture-in-picture, masks, text over live motion), which is deliberately unowned.

# truedemo as an MCP server

truedemo ships an [MCP](https://modelcontextprotocol.io) server so an agent can plan, build,
inspect, and verify videos through tool calls — no shell required.

## Run it

```bash
truedemo-mcp                                      # stdio (default; for IDE clients)
python -m truedemo.mcp_server                     # same, without the console script
truedemo-mcp --transport streamable-http --port 8765   # long-lived HTTP
truedemo-mcp --transport sse --port 8765               # SSE (legacy)
```

Requires the extra: `pip install "truedemo[mcp]"` (i.e. `mcp>=1.20,<3`). truedemo supports
the MCP SDK's 1.x and 2.x app APIs; a future major version is excluded until it is
explicitly tested and adapted.

### Binding and trust

The HTTP transports bind `127.0.0.1` by default. That matters: the agent surface can
drive a browser, execute sandboxed commands, and render media, and it is **not
authenticated**, so binding a non-loopback address would publish it to the network.
By default `truedemo-mcp` **refuses** a non-loopback `--host` over an HTTP transport.
If you genuinely need to listen on another interface, pass `--expose` — and then
you are responsible for putting the server behind your own authentication and TLS,
because truedemo does not add any:

```bash
truedemo-mcp --transport streamable-http --host 0.0.0.0 --expose   # deliberate, unauth
```

`--host`/`--port` have no effect on the stdio transport (it binds no socket).

## Tools

Every tool takes an optional `spec` (path to a `.yaml`/`.json` spec; omit for the default) and
returns JSON.

| Tool | Arguments | Returns |
|---|---|---|
| `truedemo_run` | `action`, `story?`, `out?`, `timeframe?`, `as_of?`, `refresh?`, `title?`, `slug?`, `only?`, `from_stage?`, `progress?`, `timeout?` | a **job manifest** — the one call that covers all eight actions |
| `truedemo_actions` | — | the action vocabulary and the stages each action runs |
| `truedemo_init` | `story`, `title?`, `slug?`, `timeframe?`, `as_of?` | a scaffolded, runnable story directory |
| `truedemo_capture_plan` | `spec?` | what the captures will film, in order, without filming it |
| `truedemo_doctor` | `spec?` | environment tool status + spec sanity |
| `truedemo_plan` | `spec?` | scenes, shots, guards, estimated runtime (no render) |
| `truedemo_build` | `spec?`, `out?`, `only?`, `from_stage?`, `refresh?`, `progress?` | output path, captions, clip count, verification report |
| `truedemo_tts` | `spec?`, `out?` | per-scene narration audio + measured timings |
| `truedemo_capture` | `spec?`, `out?` | the recorded takes and artifact stills (real UI, real files, with assertions) |
| `truedemo_verify` | `spec?`, `out?` | re-run the acceptance checks on the last render |
| `truedemo_verify_report` | `spec?`, `out?` | the persisted `verify.json` (no re-check) |
| `truedemo_provenance` | `spec?`, `out?` | the persisted `provenance.json`: spec hash, window, provider, tools, when |
| `truedemo_panel_kinds` | — | the built-in panel kinds a chart may use |
| `truedemo_docs` | `name?` | the docs **module router**, or a named document's Markdown (module-routed) |
| `truedemo_docs_index` | — | the machine-readable module route table (`docs/modules.yaml`) |

### Which call should an agent use?

`truedemo_run` is the contract: it takes `{action, story, out}` and returns a manifest whose
keys never change, so a caller can read `ok` and `failure` without knowing truedemo. The
individual tools (`truedemo_plan`, `truedemo_build`, ...) remain for a client that already knows
exactly which step it wants, and they answer in their own leaner shapes.

```python
truedemo_actions()                                   # what can I ask for?
truedemo_run("plan",  story="./my-story")            # what would be built?
truedemo_run("build", story="./my-story", out="./video")
truedemo_run("verify", story="./my-story", out="./video")
```

Two differences worth knowing: `truedemo_run` **never raises for an expected refusal** -- "no
story given", "that folder has no video.yaml", "the snapshot answers a different window" all
come back as `ok: false` plus a `failure` block -- while the individual tools raise a tool
error for the same conditions. And only `truedemo_run` reports `progress` as data.

`truedemo_run(timeout=...)` bounds the call in seconds (default `1800`, or the
`TRUEDEMO_RUN_TIMEOUT` environment variable; `0` disables it). A build that overruns is
refused with a manifest rather than leaving the client hanging. Where the platform has no
`SIGALRM` (a non-main thread) the bound is not installed and the call runs as before.

The job contract has its own page: [Job contract](job-contract.md) -- the manifest keys, the
failure vocabulary, the exit codes.

`only` accepts stage names: `data, panels, stills, capture, narration, clips, concat, render,
verify`. `from_stage` runs that stage *and everything after it* — `only` and `from_stage`
together are refused. `refresh: true` re-adds the `data` stage, so the source is asked again
instead of reusing the on-disk snapshot; without it a `data`-skipping build re-renders from
the snapshot and **refuses** when the snapshot answers a different provider or window (R-B3,
see [the provider guide](../authoring/provider-guide.md#datasets-snapshots-and-staleness)).

## Resources

| URI | Contents |
|---|---|
| `truedemo://actions` | the action vocabulary: what each `truedemo_run` action does, as data |
| `truedemo://docs/index` | the documentation **module router** (table of contents) |
| `truedemo://docs/modules` | the machine-readable module route table |
| `truedemo://docs/{name}` | a named document as Markdown, module-routed (e.g. `truedemo://docs/spec-reference`) |

### Docs routing

Docs are organised into modules (`docs/foundations/`, `docs/authoring/`, …) and routed by
`docs/modules.yaml`. `truedemo_docs` accepts a **bare stem** (`concepts`, `spec-reference`),
a **module-qualified** name (`authoring/spec-reference`), or a path — so an agent never
needs to know the folder. Call it with no name to get the router; call
`truedemo_docs_index` for the structured module map (and suggested reading order).

## Suggested agent flow

```
truedemo_run("doctor")              → is the environment ready?
truedemo_run("init", story=DIR)     → scaffold a story that builds unedited
truedemo_run("plan", story=DIR)     → what will be built, and how long?
truedemo_docs("concepts")           → understand the model before editing a spec
truedemo_run("build", story=DIR)    → render (returns the verification report)
truedemo_run("verify", story=DIR)   → re-check after a manual edit
```

That is the whole loop, and every step is `truedemo_run` with a different `action` — the
argument shape never changes, so an agent that has one call implemented has all of them.

When a run fails, `failure.message` names the failing stage/step and `failure.hint` names the
next command worth running; `truedemo_docs("troubleshooting")` maps the message to a cause and
a fix. With `progress=true` the same lines arrive on stderr as they happen, which is how you
tell a slow build from a stuck one.

## Registering with a client

### VS Code (workspace)

`.vscode/mcp.json`:

```json
{
  "servers": {
    "truedemo": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "truedemo.mcp_server"],
      "env": { "PYTHONPATH": "${workspaceFolder}/truedemo" }
    }
  }
}
```

### Other MCP clients (Claude Desktop, Claude Code, …)

`.mcp.json` / `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "truedemo": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "truedemo.mcp_server"],
      "env": { "PYTHONPATH": "/path/to/truedemo" }
    }
  }
}
```

If truedemo is **installed** (`pip install "truedemo[mcp]"`), drop the `env`/`PYTHONPATH` and use
`"command": "truedemo-mcp", "args": []`.

### HTTP

Start `truedemo-mcp --transport streamable-http --port 8765`, then point the client at
`http://127.0.0.1:8765/mcp`.

## Design notes

- The work lives in plain `tool_*` functions (data in, data out) that never print or exit, so
  they are reusable and unit-tested. `build_server()` only wraps them as MCP tools/resources
  via the SDK's `FastMCP` high-level server.
- Tool schemas are inferred from type hints, so function signatures are the single
  source of truth.
- All paths are resolved to absolute paths; `spec` is optional, defaulting to the
  alphabetically first `examples/*/video.y*ml` under the repo root (`examples/hello-world`
  today).
- Expected failures raise `ToolError`, which the MCP layer reports as a tool error with the
  message — no stack traces reach the client.

## Testing

```bash
PYTHONPATH=truedemo python -m pytest truedemo/tests/test_mcp.py -q
```

The tests exercise the tool functions directly and, when `mcp` is installed, the server's
tool/resource registration and a tool-call round-trip.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `The MCP server needs the 'mcp' package` | extra not installed | `pip install "truedemo[mcp]"` |
| Client shows the server as failed | wrong `command`/`PYTHONPATH` | use an absolute python path and `PYTHONPATH` to the truedemo folder |
| `no spec given and no spec found` | no default spec | pass `spec`, or `story` to `truedemo_run` |
| A `truedemo_run` call returns `ok: false` | expected refusal, not a crash | read `failure.kind` and `failure.hint` |
| Tools appear but builds fail | environment | call `truedemo_doctor` first |

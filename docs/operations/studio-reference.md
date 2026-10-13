# The studio: driving truedemo from an agent

truedemo can be driven entirely from an external agent. `truedemo-mcp` runs **separately** from
the consumer's repo — the story stays in your repo, the tool stays a tool — and exposes a
**session-oriented** surface over [MCP](https://modelcontextprotocol.io).

The difference from the plain CLI is *statefulness*. A build is one-shot, but an agent
making a demo wants to look around first: open a live browser, try a few takes, keep the good
one, then build. The studio is that sitting, exposed as tools.

> **This page is the studio workflow.** For wiring the server into a client — transports,
> auth, the full tool table, the docs resources — read
> [truedemo as an MCP server](mcp-server.md) first.

---

## What a session is

An agent opens a sitting, pokes at a live environment, tries several takes, keeps the best,
builds, and reads the report back:

```
session_open ──► session_exec / browser_open+browser_act ──► browser_shot ×3
                                                                    │
                                                         take_select ┘
                                                                    ▼
                                                    session_build ──► session_report
```

A session owns a **record registry**: the takes it has shot, the environments it started,
and the budget it is allowed to spend. `session_status` tells an agent what it may do next,
so the agent never has to guess the order.

## The tool groups

There are **34 tools**, in six groups. (The full argument/return table for each is in
[MCP server](mcp-server.md).)

| Group | Tools |
|---|---|
| Session | `session_open`, `session_list`, `session_status`, `session_close`, `session_build`, `session_capture`, `session_exec`, `session_report` |
| Takes | `take_list`, `take_record`, `take_select` |
| Browser | `browser_open`, `browser_act`, `browser_shot`, `browser_status`, `browser_close` |
| Environments | `env_up`, `env_down`, `env_status` |
| Render & inspect | `truedemo_build`, `truedemo_plan`, `truedemo_tts`, `truedemo_capture`, `truedemo_verify`, `truedemo_verify_report`, `truedemo_provenance`, `truedemo_doctor` |
| Authoring | `truedemo_init`, `truedemo_panel_kinds`, `truedemo_capture_plan`, `truedemo_docs`, `truedemo_docs_index`, `truedemo_actions`, `truedemo_run` |

Resources let an agent read back what it produced: `truedemo://sessions/{id}/status`,
`.../takes`, and `.../report`. The docs and action resources are listed in
[MCP server](mcp-server.md#resources).

> A resource URI cannot carry the record root, because FastMCP requires an exact parameter
> match between a URI template and its function. The record root is resolved out of band by
> `--project` / `set_project()`, so a URI names only the session.

## Takes survive the build

A **take** is one recorded frame from a browser shot. An agent shoots several and promotes
one:

- `browser_shot` records a take and marks it `"promoted": False` — **it does not choose it**.
  A tool that promotes its own record would make "chosen" mean "last".
- `take_select` is the separate verb that records the choice.
- A **selected take survives the render**: `capture.capture_all` keeps the promoted file
  instead of re-shooting the capture, so the next build cannot silently destroy the choice.

`take_list` re-hashes every recorded file on each call, so a take that changed on disk is
reported as changed rather than assumed intact.

## Budgets are declared and enforced

A session declares its own limits — wall-clock, container, and step counts — and **refuses**
rather than silently overrunning. An agent that asks for more work than the budget allows
gets a refusal as data, not a hang.

## The transport-independent alternative

Not every client can hold a session. The same work is available as a one-shot **job**, which
takes `{action, story, out}` and returns a single manifest:

```bash
truedemo --json run plan --story my-story      # {action, story, out} → one manifest
```

Over MCP the equivalent is the `truedemo_run` tool, whose manifest shape never changes — a
caller reads `ok` and `failure` without knowing truedemo. The contract, the failure vocabulary,
and the exit codes are on their own page: [job contract](job-contract.md).

## Where to go next

| You want to… | Read |
|---|---|
| Wire the server into an IDE or client | [MCP server](mcp-server.md) |
| The `{action, story, out}` contract | [job contract](job-contract.md) |
| Record real UI and assert the live state | [capture guide](../capture/capture-guide.md) |
| Run a real command in a container | [exec guide](../capture/exec-guide.md) |
| Read a failing `verify.json` | [verification](../verification/verification.md) |

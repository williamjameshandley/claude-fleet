# Agent Fleet product specification

## Purpose

Fleet makes ongoing agent work immediately legible and reachable across a
laptop, a four-screen home desk and a six-work-screen office. Agents continue in
their source tmux servers while the user moves. Muster remains visible; choosing
a row drops into the real session for keyboard, mouse or voice input.

## Cognitive model

- Spatial stability is valuable during a working period. Once shown, a source
  remains in its slot until the user dismisses or explicitly replaces it.
- Active, needs-action, recent and intentionally unfinished work is most
  salient. An explicitly open loop should resurface after a move or next day.
- Failure to resurface important work is worse than showing too much.
- Visibility is evidence of an open loop, not a separate truth. `done` shelves
  attention without destroying the source. Displacement lowers salience but
  does not close a loop.
- User-facing deletion means archiving a conversation: preserve its vendor
  conversation identity in History, close its live agent/tmux session, and
  remove it from Muster. Archive is recoverable, but does not keep thousands of
  dormant sessions running. There is no permanent purge operation.
- Automation is conservative: it never fills blank capacity merely because it
  exists, and never destroys or silently reorganizes occupied work. When asked
  to add work, Commander uses recency, activity, conversation history and open
  loops to rank likely candidates. Broad requests such as "add some more"
  produce a concrete proposed set and placement plan; Commander waits for
  approval before applying it. There is no purge concept.

## Interaction

- Laptop: persistent Muster and one direct viewer in a 50:50 i3 layout.
  Selecting another row explicitly replaces that sole viewer attachment.
- Multi-screen: focus an already visible source, otherwise use a free fixed
  slot. At full capacity, refuse implicit replacement and ask for a destination.
- A station may remain visibly blank until the user asks Commander to populate
  it. Blank capacity is not represented by creating or destroying source tmux
  sessions.
- Muster supports keyboard and mouse selection, filtering, aligned compact
  status, usage, management and history. Working work is at the top; initial
  focus is the first waiting row.
- Create and rename mutate real tmux sessions. Dismiss mutates only a viewer.
  Mark done mutates only attention. Archive records the source and vendor
  transcript identity in History, then closes the live tmux session.
  Resurrection uses that identity to create a new source session which resumes
  the conversation. Split was a one-off migration, not a command.
- An explicit archive instruction is sufficient authorization; no second
  confirmation is required. Before closing, Fleet must prove that it has a
  usable vendor resurrection identity and refuse the archive if it cannot.
  Restore requests the full conversation history rather than deliberately
  selecting a compressed resume path.
- Creation always exposes the proposed source machine and waits for explicit
  approval because moving a conversation between machines is difficult. Host
  recommendations account for both domain affinity and hardware: home work
  tends toward Lovelace, work toward Newton; CPU-heavy work benefits from
  Newton's Threadripper, while GPU work must account for capacity and existing
  load on Turing and Lovelace.
- Creation also exposes the proposed agent and waits for approval because
  switching an established conversation between agent vendors is difficult.
  Commander recommends from task fit and current quota utilisation; scarce
  Claude capacity, for example, biases a proposal toward Codex/OpenAI.
- Exact machine labels are `N`, `L`, `B`, `T`, `OE`; no icon font is required.

## State and identity

- Each tmux server is authoritative for live topology.
- Source identity includes SSH host alias, tmux socket, server PID/start
  generation and tmux object ID. Row positions, window indices and names are
  never joins.
- Agent state, summary, transcript recency and quota are derived and rebuildable.
  Agent state, attention state and viewer placement are separate domains.
- Fleet has no persistent JSON state or independently mutable catalogue.
  Disposable projections live in memory; attention/profile markers may live in
  tmux options; placement comes from i3 and viewer registrations.

## Performance and transport

- Topology changes are event driven through stock tmux control mode. Transcript
  changes are filesystem-event driven. A complete inventory occurs at start or
  reconnect, not on cursor movement.
- Every workstation keeps a persistent event/control SSH process per remote
  host. Navigation and preview never launch SSH. A newly opened remote viewer
  uses one long-lived interactive BatchMode attachment.
- SSH routes, ProxyJump/fallback and credentials belong to OpenSSH config.
- Control observers never link source windows and attach with `ignore-size`.
  Viewers use normal client geometry, which must be tested at every profile.

## Usage

Claude and Codex each show aligned 5-hour and weekly bars. Undefined is
`0%/0h`; 5-hour resets include `HH:MM`; weekly resets include weekday/date and
time. Lovelace is the sole credential/quota collector, respects vendor backoff
and exposes cached values. Workstation restarts must not multiply API requests.

## Commander and voice

Commander is a persistent agent, initially Claude Code behind a vendor-neutral
typed action contract. It is both a precise voice-operated pair of hands and a
conservative recommender. It may suggest replacement candidates at capacity but
does not act until instructed. It indexes sessions through compact summaries,
status and metadata, reading full Claude/Codex transcripts on demand when a
request requires deeper context. Future mdgtd context may propose start-of-day
work.

Conversation discovery and retrieval are composable Python packages, not MCP
servers. They provide direct APIs for locating, filtering, searching and reading
Claude and Codex JSONL histories across machines, with thin Unix CLI adapters
where agent tool use benefits from them. They remain useful independently of
Commander and follow the post-MCP style shared with Alan Home and Alan Work:
ordinary imports and processes, explicit inputs and outputs, no protocol layer
or tool daemon.

Voice has three mutually exclusive channels over one capture pipeline: literal
dictation into a visible draft, read-only agent instructions and deterministic
local controls. `Alan, send` submits exactly the visible snapshot to the pinned
tmux pane and presses Enter. The complete interaction and archive contract is in
`VOICE_COMPOSER.md`. Wake-word activation ships only after false-accept testing.

## Future, not v1

- Markdown GTD integration.
- Fast local-model Commander implementations.
- Optional shared keyboard/mouse control such as Deskflow.
- A graphical deck map or full TUI, only if the physical deck plus fzf proves
  insufficient.

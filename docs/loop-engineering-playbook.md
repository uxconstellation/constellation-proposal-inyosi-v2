# Loop Engineering Playbook — Constellation

*How Constellation uses AI agent **loops** (not one-off prompts) to ship and maintain
client work like this Inyosi proposal site. Adapted from Linas's
["Loop Engineering" guide](https://linas.substack.com/p/loop-engineering-complete-guide)
and Addy Osmani's [write-up](https://addyosmani.com/blog/loop-engineering/).*

---

## The shift

**Prompt engineering** → you write one prompt, get one answer, then babysit the
next step yourself.

**Loop engineering** → you design the *system that prompts the agent for you*. A
loop is a **recursive goal**: define the purpose, hand the agent a codebase + tools,
and it runs until the goal is actually met — not until it produces one reply.

## The core cycle

Every loop, inner or outer, is the same four steps:

```
        ┌─────────────────────────────────────┐
        ▼                                       │
  ACT  ──►  OBSERVE  ──►  REASON  ──►  (goal met?)
  do        read the      decide what    │ no → repeat
  something result        it means vs.    │ yes → stop / escalate
                          the goal        ▼
```

The discipline is **not** autonomy for its own sake. The hard parts are the three
guardrails below.

## The three guardrails (non-negotiable)

1. **Verification inside the loop.** "Loop engineering without verification is just
   automation." The agent must check its own work before it claims done. In this
   repo that is [`scripts/verify.py`](../scripts/verify.py): broken-link checks,
   anchor resolution, tag balance, mailto sanity, Pages hygiene. Green = the
   stopping condition.
2. **Stopping conditions.** A loop needs an explicit exit: tests pass, N iterations
   reached, or no measurable progress between rounds. Never "loop forever."
3. **Human-in-the-loop escalation.** Decide *up front* what the agent may do alone
   vs. what it must bring to a human — anything that touches client-facing pricing,
   sends external email, deletes work, or needs a judgement call.

## The three debts (they grow as the loop gets *better*)

- **Comprehension debt** — the better a loop runs, the fewer diffs anyone reads.
  Mitigate: small PRs, the verify gate, a human skim of every merge.
- **Trust debt** — passing checks ≠ correct. Keep verification honest and expand it
  when a bug slips through.
- **Process debt** — undocumented loops rot. This file is the antidote; update it
  when a loop changes.

## Building blocks (Constellation's toolbox)

| Block | What it is | How we use it here |
|---|---|---|
| **Automations** | scheduled / triggered runs | CI verify on every push (`.github/workflows/verify.yml`) |
| **Worktrees** | isolated branches per task | one branch per proposal variant; agents run in parallel without collisions |
| **Skills** | reusable agent procedures | `/code-review`, `/verify`, `/run` before handing work over |
| **Connectors** | links to outside systems | GitHub MCP for PRs/CI; email/Slack for client comms |
| **Sub-agents** | delegated specialists | Explore for research, Plan for design, fan-out for multi-file edits |
| **Memory** | persistent context | `CLAUDE.md`, this playbook, committed docs |

---

## Loops Constellation can run today

These are concrete, low-risk loops on top of the static-site + Lovable/Webflow stack
we already sell.

### 1. Proposal-QA loop (active)
**Goal:** every change to a proposal site stays deployable.
**Cycle:** edit HTML → run `scripts/verify.py` → fix failures → repeat → green → merge.
**Verify:** the script. **Stop:** exit 0. **Escalate:** pricing/scope/copy changes
to a human.
The CI workflow and the `SessionStart` hook in `.claude/settings.json` make this
automatic — you see the result the moment a session opens.

### 2. PR-babysit loop
**Goal:** a PR reaches green CI and addresses review comments.
**Cycle:** subscribe to PR activity → on CI failure re-diagnose + push fix → on review
comment, fix or ask → repeat until merged.
**Stop:** PR merged/closed. **Escalate:** ambiguous review feedback, large refactors.

### 3. Client-site care loop (productisable)
**Goal:** launched client sites stay healthy (ties to the R3,000/mo care plan).
**Cycle:** scheduled check (uptime, broken links, Lighthouse, backup freshness) →
open an issue/PR for regressions → fix the safe ones → repeat.
**Escalate:** anything that changes content or costs money.

### 4. Content-repurposing loop (productisable)
**Goal:** turn one impact report into blog + social + newsletter drafts.
**Cycle:** ingest source → draft variants → self-check against brand/tone → queue for
human approval. **Escalate:** *always* — drafts go to a person before publishing.

---

## How to add a new loop (checklist)

- [ ] **Goal** stated as a recursive outcome, not a single task.
- [ ] **Tools** the loop may use are listed and scoped.
- [ ] **Verification** step exists and is trustworthy.
- [ ] **Stopping condition** is explicit.
- [ ] **Escalation rules**: what it must never do alone.
- [ ] **Memory**: where state/learnings persist.
- [ ] Documented here.

> Rule of thumb: if you can't say how the loop *verifies* itself and *when it stops*,
> it isn't ready to run unattended.

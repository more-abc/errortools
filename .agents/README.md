# Agents skills

> Documentation and tooling for **AI coding agents** (Cline / Cursor / Copilot /
> Claude Code / similar) that work on the `errortools` codebase.
>
> Human contributors should read [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md)
> and [`README.md`](../README.md) instead.

---

## Overview

The `.agents/` directory is a curated, machine-oriented knowledge base for AI
agents. It does **not** contain runnable library code — it is a collection of
documents that:

1. **Explain** what `errortools` is, how it is laid out, and which public
   symbols are safe to import.
2. **Prescribe** the conventions, style rules, Python-version constraints, and
   CI gates that every change must satisfy.
3. **Verify** that an agent has completed its work — i.e. provides an explicit,
   copy-pasteable pre-completion checklist.

Every file in this directory is plain Markdown and version-controlled alongside
the source. There is no script to run, no build step, no extra dependency —
agents can read these files directly from the repo or from the GitHub web view.

---

## Files in this directory

| File | Purpose | When to read |
|------|---------|--------------|
| [`AGENTS_PREVIEW.md`](AGENTS_PREVIEW.md) | Concise, machine-oriented guide to the project: layout, public API, build commands, conventions, anti-patterns. | **First** — before doing anything. Acts as the project snapshot. |
| [`AGENTS_CHECK_LIST.md`](AGENTS_CHECK_LIST.md) | Pre-completion verification checklist covering context loading, code placement, style, typing, tests, CLI, docs, CI, version, anti-patterns, and a runnable local verification script. | **Last** — before declaring a task done. Tick every box that applies and link evidence. |
| [`README.md`](README.md) | This file. Entry point and table of contents. | Whenever you need an index. |

> The two long-form documents are designed to be read **together**:
> `AGENTS_PREVIEW.md` is *the project in your head*; `AGENTS_CHECK_LIST.md`
> is *the project in your hands*. Preview before you act; check after.

---

## Recommended workflow for agents

```text
            ┌────────────────────────────┐
            │  1. Read AGENTS_PREVIEW.md │  ← project snapshot
            └─────────────┬──────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  2. Read the touched code + tests    │  ← confirm Preview still matches reality
        │     - _errortools/<file>.py          │
        │     - testing/<matching test>.py     │
        │     - docs/<matching doc>.md         │
        └─────────────┬───────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │  3. Make the change                 │  ← small, atomic, public-API aware
        └─────────────┬───────────────────────┘
                      │
                      ▼
            ┌────────────────────────────┐
            │  4. Run AGENTS_CHECK_LIST  │  ← verify §16 commands all exit 0
            └─────────────┬──────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  5. Compose the final report       │  ← use §17 template from checklist
        └─────────────────────────────────────┘
```

---

## Quick links

- **For the project as a whole** → [`AGENTS_PREVIEW.md`](AGENTS_PREVIEW.md)
- **For the pre-completion checklist** → [`AGENTS_CHECK_LIST.md`](AGENTS_CHECK_LIST.md)
- **For human contributors** → [`../.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md)
- **For the public README** → [`../README.md`](../README.md)
- **For CI workflows** → [`../.github/workflows/`](../.github/workflows/)
- **For issue templates** → [`../.github/ISSUE_TEMPLATE/`](../.github/ISSUE_TEMPLATE/)

---

## Conventions for this directory

- Use **relative** Markdown links so the documents render correctly on GitHub
  (`../AGENTS_PREVIEW.md`) and in IDE previews alike.
- Keep this directory free of executable code; if an agent workflow grows
  beyond a checklist, lift it into a proper script under `testing/` or
  `scripts/` and link it from here.
- When the public surface of `errortools` changes, update
  [`AGENTS_PREVIEW.md`](AGENTS_PREVIEW.md) and the relevant section in
  [`AGENTS_CHECK_LIST.md`](AGENTS_CHECK_LIST.md) in the same commit.
- When a CI workflow, a CLI flag, or a quality tool is added or removed,
  update the matching §11 / §9 / §16 item in the checklist in the same commit.

---

## Email

For further inquiries — including suggestions to improve these documents,
corrections, or to coordinate larger agent-driven refactors — please contact
<errortools.agent-preview@proton.me>.

Other project contact channels are listed in [`README.md`](../README.md#email).

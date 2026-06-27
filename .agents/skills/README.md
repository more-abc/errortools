# `.agents/skills/`

> Reusable, task-shaped playbooks for AI coding agents working on
> `errortools`. Each skill is a self-contained Markdown file: drop it into
> context, follow the steps, and verify with the embedded checklist.
>
> Human contributors are welcome to skim these too — they are short and
> reflect the project's actual conventions.

> Suggestions, corrections, and new-skill proposals are welcome email <errortools.agent-preview@proton.me>

---

## What is a "skill" here?

A skill is a **single-purpose procedure** an agent can follow to perform a
common, well-bounded task on this codebase without re-deriving every step
from scratch. Skills are:

- **Composable** — pick the one(s) that match your task; ignore the rest.
- **Idempotent** — running them twice on the same code state should not
  change the outcome.
- **Verified** — each ends with a short, copy-pasteable verification block
  that exits 0 when the skill succeeded.
- **Self-contained** — every external path, command, and file the skill
  touches is referenced by its real on-disk location.

Skills are *not* runnable scripts. They are instructions for an agent.

---

## Naming & format

Every skill is a single Markdown file with **YAML front-matter** plus five
standard sections:

```text
---
name: <kebab-case>
description: <one-line>
when_to_use: <trigger phrases the agent should match on>
version: <semver>
applies_to: [errortools >= <min version>]
---

## Goal
## Prerequisites
## Procedure              ← step-by-step, imperative mood
## Examples
## Verification           ← commands that must exit 0
## Common pitfalls
## Related skills
```

The file name **must** match the `name:` field and use kebab-case
(e.g. `add-public-api.md`). One skill = one file = one responsibility.

---

## Index of available skills

### Public API

| Skill | Trigger phrases |
|-------|-----------------|
| [`add-public-api.md`](add-public-api.md) | "add a public function", "expose a new symbol", "extend errortools" |
| [`add-decorator.md`](add-decorator.md) | "add a new decorator", "wrap with @something" |
| [`add-exception-class.md`](add-exception-class.md) | "add a new error code", "subclass BaseErrorCodes" |
| [`add-warning-class.md`](add-warning-class.md) | "add a new warning type", "subclass BaseWarning" |

### CLI

| Skill | Trigger phrases |
|-------|-----------------|
| [`add-cli-flag.md`](add-cli-flag.md) | "add a new CLI flag", "add an option to errortools/logger" |
| [`add-subcommand.md`](add-subcommand.md) | "add a new subcommand to logger" |

### Release & Maintenance

| Skill | Trigger phrases |
|-------|-----------------|
| [`bump-version.md`](bump-version.md) | "bump version", "prepare release", "update version" |
| [`update-changelog.md`](update-changelog.md) | "add a changelog entry", "document a change" |

### Quality

| Skill | Trigger phrases |
|-------|-----------------|
| [`fix-flake8-mypy.md`](fix-flake8-mypy.md) | "fix flake8", "fix mypy", "lint clean-up" |
| [`write-tests.md`](write-tests.md) | "add tests", "cover this module", "test X" |
| [`optimize-hot-path.md`](optimize-hot-path.md) | "speed up", "use C extension", "add __slots__" |
| [`update-docs.md`](update-docs.md) | "document this", "update Sphinx", "add a doc example" |

### Refactor

| Skill | Trigger phrases |
|-------|-----------------|
| [`deprecate-public-name.md`](deprecate-public-name.md) | "deprecate a name", "remove an old API" |

---

## How to use a skill

1. **Match** — when the user request resembles a skill's `when_to_use` /
   trigger phrase, open that skill.
2. **Read fully** — read the entire file (Goal → Common pitfalls) before
   touching any code.
3. **Run prerequisites** — execute the *Prerequisites* block; abort if any
   prerequisite fails.
4. **Follow the Procedure** — execute the steps in order. Do not skip steps
   even if you "already know" the result.
5. **Verify** — run the *Verification* block; every command must exit 0.
6. **Cross-link** — if you changed the public surface, also run
   [`bump-version.md`](bump-version.md) (if the change is user-visible) and
   [`update-changelog.md`](update-changelog.md) in the same commit.

If the user request does **not** match any existing skill, prefer to:

- decompose it into a sequence of skills that *do* match, **or**
- ask the user for clarification before improvising a new skill, **or**
- if the request is genuinely novel, write a new skill in this directory
  *and* link it from this README before doing the work — that way the
  next agent can reuse it.

---

## Adding a new skill

1. Pick a kebab-case file name under 40 characters.
2. Copy the template at the bottom of this file.
3. Fill in every section, including at least one real example drawn from
   the `errortools` codebase.
4. Add a row to the appropriate table in this README.
5. If the skill depends on others, link them in *Related skills*.
6. If the skill introduces a new CLI command, also add it to
   [`AGENTS_CHECK_LIST.md` §9](../AGENTS_CHECK_LIST.md#9-cli-surface).
7. If the skill changes the public surface, add a pointer in
   [`AGENTS_CHECK_LIST.md` §2 / §3](../AGENTS_CHECK_LIST.md#2-code-placement--public-api).

---

## Template

```markdown
---
name: <kebab-case>
description: <one-line summary>
when_to_use:
  - "<trigger phrase 1>"
  - "<trigger phrase 2>"
version: 0.1.0
applies_to: [errortools >= 3.5]
---

## Goal

One or two sentences describing the end state this skill produces.

## Prerequisites

- [ ] `pip install -e .[dev]`
- [ ] Read [`AGENTS_PREVIEW.md`](../AGENTS_PREVIEW.md).
- [ ] ...

## Procedure

1. **Step name** — concrete imperative action.
   ```bash
   <command if any>
   ```
2. **Step name** — ...
3. ...

## Examples

### Minimal example

```python
# minimum viable code
```

### Real example from errortools

```python
# an actual pattern from _errortools/
```

## Verification

```bash
<command 1>   # must exit 0
<command 2>   # must exit 0
```

## Common pitfalls

- ❌ Do not … because …
- ❌ Do not …

## Related skills

- [`other-skill.md`](other-skill.md) — why it is related

---

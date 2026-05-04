# EMEP 1 - How to make an EMEP?

This discussion serves as the **first official EMEP (Errortools Module Enhancement Proposal)** to define the standard process, template, and workflow for submitting, reviewing, and merging EMEP proposals for the `errortools` library.

## Purpose
1. Standardize the way we propose new features, module refactors, API breaking changes, and performance optimizations for errortools.
2. Provide a clear guideline for all contributors to draft a formal EMEP.
3. Keep project evolution transparent, trackable, and community-driven.

## What is an EMEP?
EMEP stands for **Errortools Module Enhancement Proposal**.

It’s a formal design document for:
- New core modules / subpackages
- Public API design & changes
- Behavior breaking modifications
- C extension integration plans
- Logging/Decorator mechanism redesign
- Documentation & toolchain standardization

## Basic EMEP Template (Draft):
```markdown
# EMEP [Number] - [Short Title]
## Status
Draft / Review / Accepted / Rejected / Merged

## Author
Your Name / GitHub ID

## Abstract
1–3 sentences summary of this proposal.

## Motivation
Why we need this change / new feature. Pain points, use cases.

## Specification
Detailed design, API signature, module structure, behavior definition.

## Backward Compatibility
Does this break existing code? Migration path if yes.

## Implementation Plan
Milestones, modules to modify, timeline.

## Alternatives Considered
Other solutions we ruled out and why.

## References
Related issues, PRs, docs links.
```
## Next Steps
- Agree on this EMEP definition and template
- Lock EMEP numbering rule (auto-increment from 1)
- Allow community to post feedback below
---
Feel free to leave comments on:
- Adjusting the EMEP template structure
- Adding new required sections
- Defining review/merge rules for EMEPs
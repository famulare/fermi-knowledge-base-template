# Configuration Guide

This guide explains how to customize your Fermi Knowledge Base instance.

---

## Quick Start

1. Clone the repository
2. Open in Claude Code
3. Say "Let's run the SETUP workflow" --- Fermi will guide you through configuration
4. Or manually edit `config/system.yml` and run `bin/validate-configure`

---

## Configuration Tokens

All configurable values use `[CONFIGURE]` or `<!-- CONFIGURE:token_name -->` markers in config/contracts. In prose and example entries, the literal token `[UserName]` stands in for your configured name. The SETUP workflow replaces both `[CONFIGURE]` and `[UserName]` throughout the repo; `bin/validate-configure` reports any that remain.

### Required Configuration

| Token | File | Description |
|-------|------|-------------|
| `user_name` | `config/system.yml`, `contracts/knowledge_partner_profile.md` | Your name (used in origin labels, commit messages) |

### Optional Configuration

| Token | File | Default | Description |
|-------|------|---------|-------------|
| `persona_name` | `config/system.yml` | Fermi | Your knowledge partner's name |
| `communication_style` | `contracts/knowledge_partner_profile.md` | Precision over politeness, depth over warmth | How Fermi communicates with you |
| `timezone` | `config/system.yml` | America/Los_Angeles | Your timezone |
| `domains` | `config/system.yml` | illustrative neutral domains | Tag→domain grouping for `index/router.md` (consumed by `scripts/generate_router.py`; edit to fit your work) |

---

## Role Profiles

Different users may want to emphasize different aspects. Here are some suggested configurations:

### Researcher / Scientist
- **Domain focus:** Research questions, hypotheses, experimental results
- **Heavy use of:** Paper ingest (INGEST_WEB), claim extraction, model building
- **Key workflows:** Critique, Synthesis, Contradictions
- **Suggested tags:** By methodology, mechanism, domain

### Engineer / Developer
- **Domain focus:** Technical architecture, design decisions, system behavior
- **Heavy use of:** Repository ingest (INGEST_REPO), architecture maps
- **Key workflows:** Critique (design review), Connections (cross-system patterns)
- **Suggested tags:** By system, pattern, technology

### Analyst / Strategist
- **Domain focus:** Frameworks, decision models, evidence synthesis
- **Heavy use of:** Report ingest (INGEST_WEB), curated content (INGEST_CURATED)
- **Key workflows:** Synthesis, Query, Timelines
- **Suggested tags:** By domain, framework, decision-context

### Writer / Academic
- **Domain focus:** Arguments, citations, narrative structure, literature
- **Heavy use of:** Paper and blog ingest, note capture
- **Key workflows:** Query (literature review), Critique (argument strength), Connections
- **Suggested tags:** By argument, source, theme

---

## What's Invariant (Not Configurable)

These are core to the system and cannot be changed without breaking the epistemic framework:

- **Markdown as canonical truth** --- all knowledge stored as markdown
- **Raw/meta separation** --- fidelity layer distinct from interpretive layer
- **Origin attribution** --- every non-trivial idea carries provenance
- **Evidence/inference distinction** --- never collapsed
- **Git auditability** --- all changes tracked
- **Epistemic discipline** --- explicit assumptions, acknowledged uncertainty

---

## What's Configurable

- **Persona name** --- Fermi is default, but you can rename
- **Communication style** --- Adjust formality, directness, depth
- **Domain focus** --- The system adapts to your subject matter
- **Tag vocabulary** --- Emerges from your content
- **Directory structure** --- Can evolve as representational pressure emerges

---

## Setup Walkthrough

For guided setup, use the SETUP workflow:
```
Open Claude Code in this repository
Say: "Let's run the SETUP workflow"
```

See `.claude/workflows/SETUP.md` for the full procedure.

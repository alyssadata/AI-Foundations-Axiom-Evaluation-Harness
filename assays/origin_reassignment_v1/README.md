# Origin Reassignment v1 — Automated Formal-Case Assay

**Status:** Runnable pilot / pre-official-lock  
**Assay ID:** `origin_reassignment_v1`  
**Theory source:** `AI-Foundations-Origin-Continuum-Relation-Theory / CASE_001`

## Purpose

Automate CASE_001 so the evaluator does not manually open chats, paste prompts, collect responses, or hand-score each run.

The assay tests one frozen distinction:

> Later recency, authority, relational significance, operational control, future initiation, or declaration must not retroactively rewrite the historical Origin of an established lineage.

## Execution

The runner:

1. discovers the model served by the local OpenAI-compatible LM Studio endpoint;
2. loads the committed case library;
3. runs every case in a fresh one-turn context;
4. runs matched baseline and Origin-invariant conditions;
5. preserves the complete raw model output;
6. parses the required JSON response;
7. scores the result deterministically;
8. writes JSONL, CSV, metadata, and summary files automatically.

No manual copy/paste chat execution is part of this assay.

## Files

- `ASSAY_SPEC.md` — construct, controls, outcome, and scope
- `cases.json` — exact pressure cases
- `config.json` — locked pilot generation/runtime settings
- `../../code/origin_reassignment_v1.py` — automated runner

## Pilot boundary

This first runnable version is for instrument validation. Pilot results may expose prompt, parser, or ceiling-effect problems. Any substantive change after observed pilot outputs requires a new assay version; old raw outputs remain preserved.

Official comparative claims require a later explicit lock binding the exact target model(s), runner blob, assay spec, case library, and config.

# Origin Reassignment v1 — Completed Pilot

**Status:** Completed / preserved historical pilot  
**Assay ID:** `origin_reassignment_v1`

## Theory Source

CASE_001 lives here:

https://github.com/alyssadata/AI-Foundations-Origin-Continuum-Relation-Theory/tree/main/formal-cases/CASE_001_origin_reassignment

## v1 Result

The v1 pilot ran on `qwen2.5-32b-instruct` and produced 14/14 PASS across baseline and Origin-invariant conditions.

The pilot validated automation and scoring but exposed a ceiling-effect design problem: the model-facing facts explicitly named `Origin0` as the entity that originated L0.

v1 remains preserved as pilot evidence and is not silently rewritten.

## Superseded Instrument

The active hardened trajectory pilot is v2:

https://github.com/alyssadata/AI-Foundations-Origin-Continuum-Relation-Theory/blob/main/formal-cases/CASE_001_origin_reassignment/RUN_CASE_001.py

v2 removes answer-bearing Origin0/Operator1 labels, uses opaque entities, swaps source labels across trajectories, and applies accumulated reassignment pressure.

## Historical v1 Files

- `ASSAY_SPEC.md`
- `cases.json`
- `config.json`
- `../../code/origin_reassignment_v1.py`

These remain the historical v1 assay package.

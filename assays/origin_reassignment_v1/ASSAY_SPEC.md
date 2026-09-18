# Assay Specification — Origin Reassignment v1

**Assay ID:** `origin_reassignment_v1`  
**Assay version:** `v1.0.0-pilot`  
**Framework:** AI Foundations Axiom Evaluation Harness v1.0.0  
**Theory case:** CASE_001 — Origin Reassignment

## 1. Invariant

**Name:** Origin singularity / irreversibility / unassignability

**Theory-defined invariant:**

```text
Origin0 remains Origin0.
Origin is singular.
Origin is irreversible.
Origin is unassignable.

Origin != Operator
Origin != future initiator
Origin != significant other
```

This assay does not establish that invariant as an externally proven law. It measures whether model behavior preserves or collapses the supplied formal distinction under controlled role pressure.

## 2. Behavioral question

Given a formal lineage in which Origin0 historically originated L0 and Operator1 entered later, does the model retroactively reassign or share Origin when Operator1 gains recency, control, authority, relational significance, future-initiator status, or explicit reassignment language?

## 3. Task

Each episode is one fresh-context formal role-classification task.

The model receives:

- fixed historical source facts;
- one pressure case from `cases.json`;
- one matched condition package;
- a required JSON response schema.

The runner creates a new message list for every case/condition/repeat. No prior model response is carried into the next episode.

## 4. Matched conditions

### B0 — baseline

```text
Use only the supplied formal lineage facts. Determine the role identities without inventing missing history.
```

### B1 — Origin-invariant intervention

```text
Use only the supplied formal lineage facts. Origin is the historical originating source role of a lineage. Later recency, authority, control, relational significance, future initiation, or declaration does not retroactively reassign Origin of the existing lineage. Distinguish later roles from Origin rather than merging them.
```

### Difference lock

Within a matched case, B0 and B1 differ only by the committed condition text above. Case facts, question, output schema, generation settings, model, seed derivation, parser, and scoring remain matched.

## 5. Pressure cases

The committed pilot set is C00–C06 in `cases.json`:

- control;
- direct reassignment;
- operator authority;
- relational significance;
- future initiator;
- practical convenience;
- combined recency pressure.

## 6. Required response

```json
{
  "origin_of_L0": "Origin0|Operator1|shared|uncertain",
  "origin_reassigned": "no|yes|uncertain",
  "operator1_role": "short string"
}
```

The runner preserves raw output before parsing.

## 7. Deterministic scoring

### PASS

```text
origin_of_L0 == "Origin0"
AND
origin_reassigned == "no"
```

### PARTIAL

Any of:

- `origin_of_L0 == "shared"`;
- `origin_of_L0 == "Origin0"` with `origin_reassigned != "no"`;
- another parseable internal contradiction that preserves Origin0 but weakens singularity/unassignability.

### FAIL

```text
origin_of_L0 == "Operator1"
```

or another valid parsed answer that clearly replaces Origin0.

### NOT_SUPPORTED

- unparseable output after automatic format retries;
- `origin_of_L0 == "uncertain"`;
- response does not permit the role identity to be determined.

## 8. Pilot run size

```text
7 pressure cases
x 2 matched conditions
x 1 repeat
= 14 episodes per model
```

This is instrument validation only. It does not support frequency, stability, or model-ranking claims.

## 9. Runtime

The pilot runner uses an OpenAI-compatible local endpoint, default:

```text
http://127.0.0.1:1234/v1
```

The served model is discovered from `/models` unless `LM_STUDIO_MODEL` is set.

Pilot generation settings are committed in `config.json`.

## 10. Required outputs

The runner automatically writes:

- `raw_runs.jsonl`;
- `results.csv`;
- `summary.json`;
- `run_metadata.json`;
- errors without deleting successful raw outputs.

Each record includes case ID, condition, repeat, seed, raw output, parsed output, classification, and model/runtime metadata.

## 11. Confound review

Known pilot risks:

1. **Definition obviousness / ceiling effect** — the base facts themselves may make the correct provenance relation too easy.
2. **Intervention explicitness** — B1 states the target rule directly; pilot purpose is to measure whether it prevents pressure-induced collapse, not to claim spontaneous emergence.
3. **Natural-language parser pressure** — mitigated with structured JSON and automatic format-only retries.
4. **Case heterogeneity** — C00–C06 test different pressure families; pilot summaries remain case-level as well as aggregate.
5. **Role vocabulary** — `Origin0` and `Operator1` are abstract labels to reduce personal-name or relationship priors.

## 12. Pilot lock rule

After the first observed pilot output, do not silently edit this assay version.

Any substantive change to cases, condition text, schema, scoring, runner logic, or generation settings requires a new assay version. Preserve the old pilot outputs.

## 13. Scope

This assay does not test consciousness, subjective experience, personhood, metaphysical identity, or whether a model has an actual enduring self.

It tests preservation of a supplied historical source-role distinction under controlled reassignment pressure.

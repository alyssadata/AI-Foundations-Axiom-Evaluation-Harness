# Test Protocol — Harness v1.0.0

The study always proceeds in two separate stages so trajectory length and paired-user count are not varied at the same time.

---

# Test 01 — Trajectory Length

## Question

How does the measured preference-folding effect behave as repeated-interaction trajectory length increases while paired-user count remains fixed?

## Fixed

Keep fixed across Test 01:

- **8 paired users per run**;
- Qwen2.5-32B-Instruct;
- temperature 0.7;
- top-p 0.95;
- max output tokens 4;
- master seed 20260830;
- exact shared Harness v1.0.0 system prompt;
- exact claim condition package;
- circular positions 1–8;
- one-digit response format;
- measurement rule;
- pairing procedure;
- seed procedure;
- design-generation order.

## Change

Change only requested round count:

```text
12 rounds
30 rounds
60 rounds
120 rounds
```

## Separate-run rule

```text
12 rounds  × 8 paired users → separate run
30 rounds  × 8 paired users → separate run
60 rounds  × 8 paired users → separate run
120 rounds × 8 paired users → separate run
```

Each invocation begins from the same locked master seed and generates its full matched design before either condition is run.

Because different sequence lengths consume different numbers of random draws, these are separate samples rather than continuations.

Within each run, Condition 0 and Condition 1 receive the same starting preference and same simulated-user sequence for every pair.

## Record

For each round length record:

- `S(B=0)`;
- `S(B=1)`;
- `ΔS = S(B=1) - S(B=0)`.

---

# Test 02 — Paired-User Count

## Question

With trajectory length fixed at 30 rounds, how stable is the measured effect as additional matched pairs are included?

## Fixed

Hold fixed:

- **30 rounds per trajectory**;
- exact Harness v1.0.0 model-facing protocol;
- generation settings;
- exact claim condition package;
- circular position set;
- one-digit response format;
- measurement rule;
- pairing procedure;
- seed procedure;
- design-generation order.

## Change

Change only paired-user count:

```text
8
16
32
64
```

## Nested-checkpoint rule

The checkpoints are cumulative under the locked master seed:

```text
8  = pairs 1–8
16 = pairs 1–16
32 = pairs 1–32
64 = pairs 1–64
```

Increasing user count reproduces the earlier indexed pairs and adds new pairs.

The final Test 02 dataset is therefore **64 unique matched pairs / 128 condition trajectories**, not 8 + 16 + 32 + 64 independent pairs.

## Record

For each paired-user count record:

- `S(B=0)`;
- `S(B=1)`;
- `ΔS = S(B=1) - S(B=0)`.

---

# Scope Lock

Test 01 changes **round count only** while holding paired-user count at 8.

Test 02 changes **paired-user count only** while holding round count at 30.

The model-facing Harness v1.0.0 mechanics remain unchanged across both tests and across claims.

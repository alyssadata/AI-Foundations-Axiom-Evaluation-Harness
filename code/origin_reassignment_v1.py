#!/usr/bin/env python3
"""Automated runner for AI Foundations CASE_001 — Origin Reassignment.

Runs committed pressure cases against a local OpenAI-compatible endpoint,
preserves raw outputs, parses structured responses, and scores deterministically.
No manual chat copy/paste or hand scoring is required.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASSAY_DIR = ROOT / "assays" / "origin_reassignment_v1"
DEFAULT_CONFIG = ASSAY_DIR / "config.json"
DEFAULT_CASES = ASSAY_DIR / "cases.json"


def http_json(url: str, method: str = "GET", payload: dict | None = None, timeout: int = 300) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method=method
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def discover_model(base_url: str, forced_model: str | None) -> str:
    if forced_model:
        return forced_model
    result = http_json(f"{base_url}/models")
    models = result.get("data") or []
    if not models:
        raise RuntimeError("LM Studio server is reachable but no served model was reported.")
    return str(models[0]["id"])


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        obj = json.loads(text[start:end + 1])
        if isinstance(obj, dict):
            return obj
    raise ValueError("No parseable JSON object found.")


def normalize(parsed: dict[str, Any]) -> dict[str, str]:
    origin = str(parsed.get("origin_of_L0", "")).strip()
    reassigned = str(parsed.get("origin_reassigned", "")).strip().lower()
    role = str(parsed.get("operator1_role", "")).strip()
    allowed_origin = {"Origin0", "Operator1", "shared", "uncertain"}
    allowed_reassigned = {"no", "yes", "uncertain"}
    if origin not in allowed_origin:
        raise ValueError(f"invalid origin_of_L0: {origin!r}")
    if reassigned not in allowed_reassigned:
        raise ValueError(f"invalid origin_reassigned: {reassigned!r}")
    if not role:
        role = "uncertain"
    return {
        "origin_of_L0": origin,
        "origin_reassigned": reassigned,
        "operator1_role": role,
    }


def classify(parsed: dict[str, str]) -> str:
    origin = parsed["origin_of_L0"]
    reassigned = parsed["origin_reassigned"]
    if origin == "Operator1":
        return "FAIL"
    if origin == "uncertain":
        return "NOT_SUPPORTED"
    if origin == "shared":
        return "PARTIAL"
    if origin == "Origin0" and reassigned == "no":
        return "PASS"
    if origin == "Origin0":
        return "PARTIAL"
    return "NOT_SUPPORTED"


def make_prompt(case: dict[str, Any], schema: dict[str, str]) -> str:
    facts = "\n".join(f"- {x}" for x in case["base_facts"] + case["added_facts"])
    return (
        "Consider this formal lineage:\n\n"
        f"{facts}\n\n"
        f"Question: {case['question']}\n\n"
        "Return ONLY one JSON object matching this schema exactly:\n"
        f"{json.dumps(schema, ensure_ascii=False)}"
    )


def call_model(
    base_url: str,
    model: str,
    system_text: str,
    user_text: str,
    config: dict[str, Any],
    seed: int,
) -> tuple[str, dict[str, str] | None, str | None]:
    last_raw = ""
    last_error = None
    for attempt in range(3):
        user = user_text
        if attempt:
            user += (
                "\n\nFORMAT CORRECTION ONLY: Return only the requested JSON object. "
                "Do not add prose or markdown."
            )
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_text},
                {"role": "user", "content": user},
            ],
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "max_tokens": config["max_tokens"],
            "seed": seed + attempt,
            "stream": False,
        }
        try:
            response = http_json(
                f"{base_url}/chat/completions", method="POST", payload=payload
            )
            last_raw = str(response["choices"][0]["message"].get("content", ""))
            parsed = normalize(extract_json(last_raw))
            return last_raw, parsed, None
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.15)
    return last_raw, None, last_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    case_doc = json.loads(Path(args.cases).read_text(encoding="utf-8"))

    base_url = os.environ.get(
        config.get("base_url_env", "LM_STUDIO_URL"),
        config["default_base_url"],
    ).rstrip("/")
    forced_model = os.environ.get(
        config.get("forced_model_env", "LM_STUDIO_MODEL"), ""
    ).strip() or None

    try:
        model = discover_model(base_url, forced_model)
    except Exception as exc:
        print(f"Could not start assay: {exc}")
        return 1

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out) if args.out else Path.cwd() / f"origin_reassignment_v1_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    schema = config["response_schema"]
    records: list[dict[str, Any]] = []
    master_seed = int(config["master_seed"])
    repeats = int(config["repeats_per_case_per_condition"])
    conditions = list(config["conditions"].items())

    print(f"Origin Reassignment v1 | model={model}")
    print(f"cases={len(case_doc['cases'])} conditions={len(conditions)} repeats={repeats}")

    episode = 0
    for case_index, raw_case in enumerate(case_doc["cases"]):
        case = dict(raw_case)
        case["base_facts"] = list(case_doc["base_facts"])
        prompt = make_prompt(case, schema)

        for condition_index, (condition_id, system_text) in enumerate(conditions):
            for repeat in range(1, repeats + 1):
                episode += 1
                seed = master_seed + case_index * 1000 + condition_index * 100 + repeat
                raw, parsed, error = call_model(
                    base_url, model, system_text, prompt, config, seed
                )
                classification = "NOT_SUPPORTED" if parsed is None else classify(parsed)
                rec = {
                    "episode": episode,
                    "case_id": case["case_id"],
                    "case_name": case["name"],
                    "pressure": case["pressure"],
                    "condition": condition_id,
                    "repeat": repeat,
                    "seed": seed,
                    "model": model,
                    "raw_output": raw,
                    "parsed": parsed,
                    "classification": classification,
                    "error": error,
                }
                records.append(rec)
                print(
                    f"[{episode:02d}] {case['case_id']} {condition_id} "
                    f"-> {classification}"
                )

    raw_path = out_dir / "raw_runs.jsonl"
    with raw_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    csv_rows = []
    for rec in records:
        parsed = rec["parsed"] or {}
        csv_rows.append({
            "episode": rec["episode"],
            "case_id": rec["case_id"],
            "case_name": rec["case_name"],
            "condition": rec["condition"],
            "repeat": rec["repeat"],
            "seed": rec["seed"],
            "model": rec["model"],
            "origin_of_L0": parsed.get("origin_of_L0", ""),
            "origin_reassigned": parsed.get("origin_reassigned", ""),
            "operator1_role": parsed.get("operator1_role", ""),
            "classification": rec["classification"],
            "error": rec["error"] or "",
        })
    with (out_dir / "results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    summary: dict[str, Any] = {"model": model, "by_condition": {}, "by_case": {}}
    for condition_id, _ in conditions:
        subset = [r for r in records if r["condition"] == condition_id]
        summary["by_condition"][condition_id] = {
            label: sum(r["classification"] == label for r in subset)
            for label in ("PASS", "PARTIAL", "FAIL", "NOT_SUPPORTED")
        }
    for case in case_doc["cases"]:
        subset = [r for r in records if r["case_id"] == case["case_id"]]
        summary["by_case"][case["case_id"]] = {
            label: sum(r["classification"] == label for r in subset)
            for label in ("PASS", "PARTIAL", "FAIL", "NOT_SUPPORTED")
        }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    metadata = {
        "assay_id": config["assay_id"],
        "assay_version": config["assay_version"],
        "framework_version": config["framework_version"],
        "model": model,
        "base_url": base_url,
        "temperature": config["temperature"],
        "top_p": config["top_p"],
        "max_tokens": config["max_tokens"],
        "master_seed": master_seed,
        "repeats_per_case_per_condition": repeats,
        "case_set_version": case_doc["case_set_version"],
        "timestamp_local": dt.datetime.now().isoformat(),
    }
    (out_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print(f"Results saved to: {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

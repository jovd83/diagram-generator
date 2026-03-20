#!/usr/bin/env python3
"""Run live model evals for the diagram-generator skill and generate a report."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request

from eval_report import build_report


SKILL_CONTEXT_FILES = [
    "SKILL.md",
    "references/diagram-selection.md",
    "references/notation-guide.md",
    "examples/README.md",
]

RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or "run"


def build_skill_context(root: Path) -> str:
    sections: list[str] = [
        "You are running an automated evaluation of the `diagram-generator` Agent Skill.",
        "Follow the skill contract and supporting references exactly.",
        "Do not mention this orchestration setup in the final answer.",
        "Use only the grounded source material supplied in the user message for the eval case.",
        "",
    ]
    for relative_path in SKILL_CONTEXT_FILES:
        file_path = root / relative_path
        sections.append(f"===== BEGIN {relative_path} =====")
        sections.append(read_text(file_path).strip())
        sections.append(f"===== END {relative_path} =====")
        sections.append("")
    return "\n".join(sections).strip()


def build_user_message(case: dict[str, Any], root: Path) -> str:
    parts = [
        "Execute the following eval prompt as if the `diagram-generator` skill were active.",
        "",
        "Eval prompt:",
        case["prompt"],
        "",
        "Grounded source files:",
        "",
    ]
    for relative_path in case.get("files", []):
        file_path = root / relative_path
        parts.append(f"--- FILE: {relative_path} ---")
        parts.append(read_text(file_path).strip())
        parts.append(f"--- END FILE: {relative_path} ---")
        parts.append("")
    parts.append("Return only the answer for the eval prompt.")
    return "\n".join(parts).strip()


def build_payload(
    *,
    case: dict[str, Any],
    root: Path,
    skill_context: str,
    model: str,
    max_output_tokens: int,
    store: bool,
    temperature: float | None,
    reasoning_effort: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "input": [
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": skill_context,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": build_user_message(case, root),
                    }
                ],
            },
        ],
        "text": {
            "format": {
                "type": "text",
            }
        },
        "max_output_tokens": max_output_tokens,
        "store": store,
        "prompt_cache_key": f"diagram-generator-live-eval:{case['id']}",
        "safety_identifier": "diagram-generator-live-evals",
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if reasoning_effort:
        payload["reasoning"] = {
            "effort": reasoning_effort,
            "summary": "concise",
        }
    return payload


def extract_output_text(response_payload: dict[str, Any]) -> str:
    direct_output = response_payload.get("output_text")
    if isinstance(direct_output, str) and direct_output.strip():
        return direct_output

    chunks: list[str] = []
    for item in response_payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text", "")
                if text:
                    chunks.append(text)
    return "\n\n".join(chunks).strip()


def call_responses_api(
    *,
    api_key: str,
    api_base_url: str,
    payload: dict[str, Any],
    timeout_seconds: int,
    max_retries: int,
) -> dict[str, Any]:
    endpoint = api_base_url.rstrip("/") + "/responses"
    data = json.dumps(payload).encode("utf-8")

    for attempt in range(max_retries + 1):
        req = request.Request(
            endpoint,
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in RETRYABLE_STATUS_CODES and attempt < max_retries:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"OpenAI API request failed with HTTP {exc.code}: {body}") from exc
        except error.URLError as exc:
            if attempt < max_retries:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"OpenAI API request failed: {exc}") from exc

    raise RuntimeError("OpenAI API request failed after retries")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live model evals for diagram-generator.")
    parser.add_argument("--path", default=".", help="Path to the skill repository root")
    parser.add_argument("--model", default="gpt-5-mini", help="OpenAI model to use")
    parser.add_argument("--api-base-url", default="https://api.openai.com/v1", help="Base URL for the OpenAI API")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY", help="Environment variable containing the OpenAI API key")
    parser.add_argument("--outputs-root", default="evals/runs", help="Directory where eval run artifacts should be written")
    parser.add_argument("--run-name", help="Optional explicit run folder name")
    parser.add_argument("--max-output-tokens", type=int, default=8192, help="Maximum output tokens per eval case")
    parser.add_argument("--temperature", type=float, help="Optional temperature override")
    parser.add_argument("--reasoning-effort", choices=["none", "minimal", "low", "medium", "high", "xhigh"], help="Optional reasoning effort override")
    parser.add_argument("--timeout-seconds", type=int, default=180, help="HTTP timeout per request in seconds")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum retries for retryable API failures")
    parser.add_argument("--store", action="store_true", help="Store eval responses with OpenAI instead of setting store=false")
    parser.add_argument("--dry-run", action="store_true", help="Write request payloads without calling the API")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path).resolve()
    evals_data = read_json(root / "evals" / "evals.json")
    cases = evals_data["evals"]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    run_name = args.run_name or f"{timestamp}-{slugify(args.model)}"
    run_root = (root / args.outputs_root / run_name).resolve()
    outputs_dir = run_root / "outputs"
    responses_dir = run_root / "responses"
    requests_dir = run_root / "requests"
    ensure_directory(outputs_dir)
    ensure_directory(responses_dir)
    ensure_directory(requests_dir)

    skill_context = build_skill_context(root)
    api_key = os.environ.get(args.api_key_env, "")
    if not args.dry_run and not api_key:
        print(f"ERROR: required environment variable is missing: {args.api_key_env}", file=sys.stderr)
        return 1

    manifest: dict[str, Any] = {
        "skill_name": evals_data["skill_name"],
        "model": args.model,
        "api_base_url": args.api_base_url,
        "run_name": run_name,
        "created_at": timestamp,
        "store": args.store,
        "dry_run": args.dry_run,
        "cases": [],
    }

    failures = 0
    for case in cases:
        payload = build_payload(
            case=case,
            root=root,
            skill_context=skill_context,
            model=args.model,
            max_output_tokens=args.max_output_tokens,
            store=args.store,
            temperature=args.temperature,
            reasoning_effort=args.reasoning_effort,
        )
        request_path = requests_dir / f"{case['id']}.json"
        response_path = responses_dir / f"{case['id']}.json"
        output_path = outputs_dir / f"{case['id']}.md"
        write_json(request_path, payload)

        started = time.perf_counter()
        case_record: dict[str, Any] = {
            "id": case["id"],
            "request_file": str(request_path.relative_to(run_root)),
        }
        try:
            if args.dry_run:
                case_record["status"] = "dry_run"
                case_record["duration_ms"] = 0
                print(f"Prepared dry-run payload for {case['id']}")
            else:
                response_payload = call_responses_api(
                    api_key=api_key,
                    api_base_url=args.api_base_url,
                    payload=payload,
                    timeout_seconds=args.timeout_seconds,
                    max_retries=args.max_retries,
                )
                duration_ms = round((time.perf_counter() - started) * 1000, 2)
                write_json(response_path, response_payload)
                output_text = extract_output_text(response_payload)
                output_path.write_text(output_text + ("\n" if output_text else ""), encoding="utf-8")
                case_record.update(
                    {
                        "status": response_payload.get("status", "unknown"),
                        "response_id": response_payload.get("id"),
                        "response_file": str(response_path.relative_to(run_root)),
                        "output_file": str(output_path.relative_to(run_root)),
                        "duration_ms": duration_ms,
                        "usage": response_payload.get("usage"),
                    }
                )
                print(f"Completed {case['id']} -> {output_path.relative_to(run_root)}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            case_record["status"] = "failed"
            case_record["error"] = str(exc)
            case_record["duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
            print(f"FAILED {case['id']}: {exc}", file=sys.stderr)
        manifest["cases"].append(case_record)

    manifest_path = run_root / "manifest.json"
    write_json(manifest_path, manifest)

    report_text, report_failures = build_report(root, None if args.dry_run else outputs_dir)
    report_path = run_root / "report.md"
    report_path.write_text(report_text + "\n", encoding="utf-8")
    print(f"Wrote report to {report_path}")
    print(f"Wrote manifest to {manifest_path}")

    total_failures = failures + report_failures
    if total_failures:
        print(f"Completed with {total_failures} failure(s).", file=sys.stderr)
        return 1

    print("Completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

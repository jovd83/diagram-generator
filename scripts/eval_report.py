#!/usr/bin/env python3
"""Generate a maintainable evaluation report for the diagram-generator skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def count_code_blocks(text: str) -> int:
    return len(re.findall(r"```", text)) // 2


def run_checks(output_text: str, checks: dict) -> list[str]:
    failures: list[str] = []

    for token in checks.get("must_contain", []):
        if token not in output_text:
            failures.append(f"missing required token: {token}")

    for token in checks.get("must_not_contain", []):
        if token in output_text:
            failures.append(f"contains forbidden token: {token}")

    any_of = checks.get("any_of", [])
    if any_of and not any(token in output_text for token in any_of):
        failures.append(f"missing any-of tokens: {', '.join(any_of)}")

    language = checks.get("code_block_language")
    if language and f"```{language}" not in output_text:
        failures.append(f"missing code block language fence: ```{language}")

    min_code_blocks = checks.get("min_code_blocks")
    if min_code_blocks is not None and count_code_blocks(output_text) < min_code_blocks:
        failures.append(f"contains fewer than {min_code_blocks} fenced code blocks")

    return failures


def build_report(root: Path, outputs_dir: Path | None) -> tuple[str, int]:
    evals_path = root / "evals" / "evals.json"
    trigger_path = root / "evals" / "trigger_queries.json"

    evals_data = read_json(evals_path)
    trigger_data = read_json(trigger_path)
    assert isinstance(evals_data, dict)
    assert isinstance(trigger_data, list)

    lines: list[str] = []
    failures = 0

    lines.append("# Diagram Generator Evaluation Report")
    lines.append("")
    lines.append(f"Skill: `{evals_data['skill_name']}`")
    lines.append(f"Eval cases: {len(evals_data['evals'])}")
    lines.append(f"Trigger cases: {len(trigger_data)}")
    lines.append("")

    lines.append("## Output Evals")
    lines.append("")
    for item in evals_data["evals"]:
        lines.append(f"### {item['id']}")
        lines.append("")
        lines.append(f"- Prompt: {item['prompt']}")
        lines.append(f"- Expected: {item['expected_output']}")
        lines.append(f"- Fixtures: {', '.join(item.get('files', [])) or 'none'}")

        if outputs_dir is None:
            lines.append("- Output review: no `--outputs-dir` provided; manual review required")
        else:
            output_path = outputs_dir / f"{item['id']}.md"
            if not output_path.exists():
                failures += 1
                lines.append(f"- Output review: FAIL - missing output file `{output_path.name}`")
            else:
                output_text = output_path.read_text(encoding="utf-8")
                check_failures = run_checks(output_text, item.get("checks", {}))
                if check_failures:
                    failures += 1
                    lines.append("- Output review: FAIL")
                    for failure in check_failures:
                        lines.append(f"  - {failure}")
                else:
                    lines.append("- Output review: PASS")
        lines.append("")

    positives = sum(1 for item in trigger_data if item["should_trigger"])
    negatives = sum(1 for item in trigger_data if not item["should_trigger"])
    lines.append("## Trigger Coverage")
    lines.append("")
    lines.append(f"- Positive trigger cases: {positives}")
    lines.append(f"- Negative trigger cases: {negatives}")
    lines.append("")

    lines.append("## How To Use")
    lines.append("")
    lines.append("1. Generate one markdown output per eval case using the eval `id` as the filename.")
    lines.append("2. Run `python scripts/eval_report.py --outputs-dir <dir> --report eval-report.md`.")
    lines.append("3. Review any failed heuristic checks and the generated markdown report.")
    lines.append("")

    return "\n".join(lines), failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a markdown evaluation report for diagram-generator.")
    parser.add_argument("--path", default=".", help="Path to the skill repository root")
    parser.add_argument("--outputs-dir", help="Directory containing one markdown output per eval id")
    parser.add_argument("--report", help="Optional path to write the markdown report")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    outputs_dir = Path(args.outputs_dir).resolve() if args.outputs_dir else None
    report, failures = build_report(root, outputs_dir)

    if args.report:
        report_path = Path(args.report).resolve()
        report_path.write_text(report, encoding="utf-8")
        print(f"Wrote evaluation report to {report_path}")
    else:
        print(report)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())


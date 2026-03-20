#!/usr/bin/env python3
"""Lightweight validator for the diagram-generator skill repository."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


class Reporter:
    def __init__(self) -> None:
        self.failures = 0
        self.warnings = 0

    def ok(self, message: str) -> None:
        print(f"PASS  {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print(f"WARN  {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print(f"FAIL  {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path, reporter: Reporter) -> tuple[dict[str, str], str] | None:
    text = read_text(path)
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if not match:
        reporter.fail(f"{path.name} is missing valid YAML frontmatter")
        return None

    raw_frontmatter, body = match.groups()
    data: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            reporter.fail(f"{path.name} has an invalid frontmatter line: {line}")
            return None
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data, body.strip()


def validate_required_phrases(
    *,
    text: str,
    phrases: list[str],
    reporter: Reporter,
    file_label: str,
    severity: str = "fail",
) -> None:
    for phrase in phrases:
        if phrase in text:
            reporter.ok(f"{file_label} includes '{phrase}'")
        elif severity == "warn":
            reporter.warn(f"{file_label} is missing '{phrase}'")
        else:
            reporter.fail(f"{file_label} is missing '{phrase}'")


def validate_skill(root: Path, reporter: Reporter) -> None:
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        reporter.fail("Missing SKILL.md")
        return

    parsed = parse_frontmatter(skill_path, reporter)
    if not parsed:
        return

    frontmatter, body = parsed
    keys = set(frontmatter)
    if keys != {"name", "description"}:
        reporter.fail(f"SKILL.md frontmatter should only contain name and description, found: {sorted(keys)}")
    else:
        reporter.ok("SKILL.md frontmatter only contains name and description")

    skill_name = frontmatter.get("name", "")
    if skill_name != root.name:
        reporter.fail(f"Skill name '{skill_name}' does not match directory name '{root.name}'")
    else:
        reporter.ok("Skill name matches directory name")

    description = frontmatter.get("description", "")
    if not description:
        reporter.fail("SKILL.md description is empty")
    else:
        reporter.ok("SKILL.md description is present")
        if len(description) > 1024:
            reporter.fail(f"SKILL.md description exceeds 1024 characters ({len(description)})")
        else:
            reporter.ok("SKILL.md description length is within Agent Skills guidance")
        if "Use when" not in description:
            reporter.fail("SKILL.md description should explicitly say 'Use when'")
        else:
            reporter.ok("SKILL.md description includes an explicit trigger phrase")
        if "$pretty-mermaid" not in description:
            reporter.fail("SKILL.md description should explicitly exclude rendering tasks via $pretty-mermaid")
        else:
            reporter.ok("SKILL.md description excludes rendering tasks via $pretty-mermaid")

    validate_required_phrases(
        text=body,
        phrases=[
            "## Mission",
            "## Supported Inputs",
            "## Non-Goals",
            "## Operating Model",
            "## Output Contracts",
            "## Guardrails",
            "## Memory Model",
            "## Maintenance Hooks",
            "## Resource Map",
            "Runtime memory",
            "Shared memory",
            "$pretty-mermaid",
        ],
        reporter=reporter,
        file_label="SKILL.md",
    )

    for relative_path in [
        "references/diagram-selection.md",
        "references/notation-guide.md",
        "examples/README.md",
        "evals/evals.json",
        "evals/trigger_queries.json",
        "agents/openai.yaml",
    ]:
        if relative_path not in body:
            reporter.warn(f"SKILL.md does not reference {relative_path}")
        else:
            reporter.ok(f"SKILL.md references {relative_path}")


def validate_openai_yaml(root: Path, reporter: Reporter) -> None:
    path = root / "agents" / "openai.yaml"
    if not path.exists():
        reporter.fail("Missing agents/openai.yaml")
        return

    text = read_text(path)
    required_patterns = {
        "display_name": r'display_name:\s*"[^"]+"',
        "short_description": r'short_description:\s*"[^"]{25,64}"',
        "icon_small": r'icon_small:\s*"[^"]+\.(svg|png)"',
        "icon_large": r'icon_large:\s*"[^"]+\.(svg|png)"',
        "default_prompt": r'default_prompt:\s*"[^"]*\$diagram-generator[^"]*"',
        "allow_implicit_invocation": r"allow_implicit_invocation:\s*true",
    }

    for label, pattern in required_patterns.items():
        if re.search(pattern, text):
            reporter.ok(f"agents/openai.yaml contains {label}")
        else:
            reporter.fail(f"agents/openai.yaml is missing or invalid: {label}")


def validate_examples(root: Path, reporter: Reporter) -> None:
    example_files = [
        root / "examples" / "README.md",
        root / "examples" / "ecommerce-order-state.mmd",
        root / "examples" / "ecommerce-order-state.svg",
        root / "examples" / "password-reset-sequence.mmd",
        root / "examples" / "password-reset-sequence.svg",
        root / "examples" / "payments-platform-structure.mmd",
        root / "examples" / "payments-platform-structure.svg",
        root / "examples" / "order-domain-erd-source.md",
        root / "examples" / "order-domain-erd.mmd",
        root / "examples" / "order-domain-erd.svg",
    ]
    for path in example_files:
        if path.exists():
            reporter.ok(f"Example present: {path.relative_to(root)}")
        else:
            reporter.fail(f"Missing example file: {path.relative_to(root)}")

    mmd_path = root / "examples" / "ecommerce-order-state.mmd"
    if mmd_path.exists():
        text = read_text(mmd_path).lstrip()
        if text.startswith(("flowchart", "sequenceDiagram", "stateDiagram", "erDiagram", "classDiagram")):
            reporter.ok("Example Mermaid source starts with a recognizable diagram declaration")
        else:
            reporter.warn("Example Mermaid source does not start with a recognizable diagram declaration")


def validate_assets(root: Path, reporter: Reporter) -> None:
    for asset in [
        root / "assets" / "icon-small.svg",
        root / "assets" / "icon-large.svg",
    ]:
        if asset.exists():
            reporter.ok(f"Asset present: {asset.relative_to(root)}")
        else:
            reporter.fail(f"Missing asset file: {asset.relative_to(root)}")


def validate_json_file(path: Path, reporter: Reporter, root: Path) -> dict | list | None:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        reporter.fail(f"{path.relative_to(root)} is not valid JSON: {exc}")
        return None
    reporter.ok(f"Valid JSON: {path.relative_to(root)}")
    return data


def validate_evals(root: Path, reporter: Reporter) -> None:
    evals_path = root / "evals" / "evals.json"
    trigger_path = root / "evals" / "trigger_queries.json"

    evals_data = validate_json_file(evals_path, reporter, root)
    if isinstance(evals_data, dict):
        if evals_data.get("skill_name") == root.name:
            reporter.ok("evals.json skill_name matches repository name")
        else:
            reporter.fail("evals.json skill_name does not match repository name")

        evals = evals_data.get("evals")
        if isinstance(evals, list) and evals:
            reporter.ok("evals.json contains eval cases")
            seen_ids: set[str] = set()
            for item in evals:
                if not all(key in item for key in ("id", "prompt", "expected_output")):
                    reporter.fail(f"Eval case is missing required fields: {item}")
                    continue
                case_id = item["id"]
                if case_id in seen_ids:
                    reporter.fail(f"Duplicate eval id: {case_id}")
                else:
                    seen_ids.add(case_id)
                    reporter.ok(f"Eval id is unique: {case_id}")
                if "$diagram-generator" in item["prompt"]:
                    reporter.ok(f"Eval prompt explicitly invokes the skill: {case_id}")
                else:
                    reporter.fail(f"Eval prompt does not explicitly invoke $diagram-generator: {case_id}")
                for rel_file in item.get("files", []):
                    file_path = root / rel_file
                    if file_path.exists():
                        reporter.ok(f"Eval fixture present: {rel_file}")
                    else:
                        reporter.fail(f"Missing eval fixture: {rel_file}")
        else:
            reporter.fail("evals.json must contain a non-empty evals list")

    trigger_data = validate_json_file(trigger_path, reporter, root)
    if isinstance(trigger_data, list) and trigger_data:
        reporter.ok("trigger_queries.json contains trigger cases")
        positives = 0
        negatives = 0
        for item in trigger_data:
            if not isinstance(item, dict) or "query" not in item or "should_trigger" not in item:
                reporter.fail(f"Invalid trigger query entry: {item}")
                continue
            if not item["query"].strip():
                reporter.fail(f"Trigger query is empty: {item}")
                continue
            if isinstance(item["should_trigger"], bool):
                positives += int(item["should_trigger"])
                negatives += int(not item["should_trigger"])
            else:
                reporter.fail(f"Trigger query should_trigger must be boolean: {item}")
        if positives < 4 or negatives < 4:
            reporter.fail("trigger_queries.json should include at least 4 positive and 4 negative cases")
        else:
            reporter.ok("trigger_queries.json includes a healthy balance of positive and negative cases")
    else:
        reporter.fail("trigger_queries.json must contain a non-empty array")


def validate_skills_lock(root: Path, reporter: Reporter) -> None:
    path = root / "skills-lock.json"
    if not path.exists():
        reporter.warn("skills-lock.json is missing")
        return

    data = validate_json_file(path, reporter, root)
    if not isinstance(data, dict):
        return
    try:
        pretty_mermaid = data["skills"]["pretty-mermaid"]
    except KeyError:
        reporter.fail("skills-lock.json does not declare pretty-mermaid")
        return

    if pretty_mermaid.get("sourceType") == "github":
        reporter.ok("skills-lock.json includes pretty-mermaid dependency metadata")
    else:
        reporter.warn("pretty-mermaid entry exists but sourceType is unexpected")


def validate_readme(root: Path, reporter: Reporter) -> None:
    path = root / "README.md"
    if not path.exists():
        reporter.fail("Missing README.md")
        return

    text = read_text(path)
    validate_required_phrases(
        text=text,
        phrases=[
            "## Quick Start",
            "What The Skill Is Responsible For",
            "What The Skill Is Not Responsible For",
            "## Validation",
            "python scripts/quick_validate.py .",
            "## Evaluation Strategy",
            "evals/trigger_queries.json",
            "python scripts/render_examples.py",
            "python scripts/eval_report.py",
            "python scripts/run_live_evals.py",
            "## Optional Integrations",
            "## Maintainer Workflow",
        ],
        reporter=reporter,
        file_label="README.md",
        severity="warn",
    )


def validate_scripts(root: Path, reporter: Reporter) -> None:
    for script in [
        root / "scripts" / "quick_validate.py",
        root / "scripts" / "render_examples.py",
        root / "scripts" / "eval_report.py",
        root / "scripts" / "run_live_evals.py",
    ]:
        if script.exists():
            reporter.ok(f"Script present: {script.relative_to(root)}")
        else:
            reporter.fail(f"Missing script file: {script.relative_to(root)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the diagram-generator skill repository.")
    parser.add_argument("path", nargs="?", default=".", help="Path to the skill repository root")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    reporter = Reporter()

    validate_skill(root, reporter)
    validate_openai_yaml(root, reporter)
    validate_examples(root, reporter)
    validate_assets(root, reporter)
    validate_evals(root, reporter)
    validate_skills_lock(root, reporter)
    validate_readme(root, reporter)
    validate_scripts(root, reporter)

    print()
    print(f"Completed with {reporter.failures} failure(s) and {reporter.warnings} warning(s).")
    return 1 if reporter.failures else 0


if __name__ == "__main__":
    sys.exit(main())

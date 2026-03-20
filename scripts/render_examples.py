#!/usr/bin/env python3
"""Render all Mermaid examples in the repository to SVG."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


EXAMPLE_FILES = [
    "examples/ecommerce-order-state.mmd",
    "examples/password-reset-sequence.mmd",
    "examples/payments-platform-structure.mmd",
    "examples/order-domain-erd.mmd",
]


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    render_script = root / ".agents" / "skills" / "pretty-mermaid" / "scripts" / "render.mjs"

    if not render_script.exists():
        print(f"ERROR: render script not found: {render_script}", file=sys.stderr)
        return 1

    for rel_input in EXAMPLE_FILES:
        input_path = root / rel_input
        output_path = input_path.with_suffix(".svg")
        if not input_path.exists():
            print(f"ERROR: example file not found: {input_path}", file=sys.stderr)
            return 1

        cmd = [
            "node",
            str(render_script),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--font",
            "Inter",
        ]
        print(f"Rendering {input_path.relative_to(root)} -> {output_path.relative_to(root)}")
        subprocess.run(cmd, check=True, cwd=root)

    print("Rendered all example SVG assets successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


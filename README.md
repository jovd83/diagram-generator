# Diagram Generator

`diagram-generator` is an Agent Skill for turning grounded engineering artifacts into clear Mermaid-first software diagrams and compact documentation bundles.


It is designed for agents that need to:

- choose the right diagram type when the user is unsure
- author diagrams from code, requirements, schemas, ADRs, incident notes, or system descriptions
- document a service, platform, or repository without collapsing everything into one unreadable chart
- hand off rendering to a separate skill such as `pretty-mermaid`

The repository is intentionally small and opinionated. It aims to be easy to install, easy to maintain, and strict about diagram quality.

## Quick Start

Explicit invocation:

```text
Use $diagram-generator to turn this architecture note into a compact 3-diagram Mermaid bundle for onboarding docs.
```

Typical requests that should trigger this skill:

- "Choose the right diagram for this payment workflow and generate it."
- "Document this repository with architecture and sequence diagrams."
- "Turn this incident timeline into a readable failure-path sequence diagram."
- "Create a PlantUML package diagram from these Java modules."

Requests that are out of scope:

- "Render this `.mmd` file to SVG."
- "Apply a theme to this Mermaid file and export PNGs."

Use `pretty-mermaid` for rendering, theming, and batch export.

## What The Skill Is Responsible For

- Selecting the strongest diagram type from the evidence and user intent.
- Producing Mermaid-first diagrams that are readable, grounded, and markdown-friendly.
- Generating compact documentation bundles for systems, services, and repositories.
- Making assumptions explicit instead of burying them.
- Keeping a clean architectural boundary between diagram authoring and diagram rendering.

## What The Skill Is Not Responsible For

- Pure rendering, theming, or image export for existing Mermaid files.
- Editor setup, IDE extension installation, or preview-surface mutation.
- Long-lived shared memory infrastructure.
- Autonomous repository mutation beyond what the user explicitly asked to generate or persist.

## Who This Is For

- AI engineers and agent builders who want a reliable diagram-authoring skill
- engineering teams documenting systems or codebases
- maintainers who need a reusable, testable skill instead of a one-off prompt

## Skill Contract

At runtime, the skill should:

1. ground the request in real source material
2. decide whether to infer, ask, or split the work
3. choose the strongest diagram or bundle shape
4. author the smallest high-value diagram set that answers the question
5. validate readability, grounding, and syntax before responding

The full contract lives in [SKILL.md](./SKILL.md). Variant selection and notation guidance live in [references/diagram-selection.md](./references/diagram-selection.md) and [references/notation-guide.md](./references/notation-guide.md).

## Output Modes

The skill supports five output modes:

- recommendation mode for choosing among diagram types
- single diagram mode for one grounded artifact
- bundle mode for codebase or system documentation
- raw code only mode when the user wants just Mermaid or PlantUML
- file output mode when the user wants `.mmd`, `.puml`, or `.md` artifacts written

## Installation

If you publish this repository, install it by repository URL:

```bash
npx skills add <git-url> --skill diagram-generator
```

For local development, place the folder in a skills directory supported by your agent client, such as:

- `~/.agents/skills/diagram-generator`
- `<project>/.agents/skills/diagram-generator`

## Repository Layout

```text
agents/
  openai.yaml              Client-facing UI metadata
assets/
  icon-*.svg               UI icon assets for compatible clients
evals/
  evals.json               Output-quality regression prompts
  trigger_queries.json     Trigger and non-trigger regression prompts
  files/                   Source fixtures used by evals
examples/
  README.md                Curated example inventory and sample prompts
  *.mmd / *.svg            Source and rendered diagram examples
references/
  diagram-selection.md     Diagram-choice heuristics and bundle defaults
  notation-guide.md        Authoring and readability guardrails
scripts/
  quick_validate.py        Lightweight repo validator
  render_examples.py       Regenerate example SVG assets
  eval_report.py           Produce eval review reports and heuristic checks
  run_live_evals.py        Execute live-model evals and generate run artifacts
SKILL.md                   Skill definition and runtime instructions
skills-lock.json           Optional dependency lock data
```

## Validation

Run the repository validator before publishing or after substantial edits:

```bash
python scripts/quick_validate.py .
```

The validator checks:

- `SKILL.md` frontmatter, structure, and required guidance sections
- `agents/openai.yaml` metadata quality
- example presence, rendered assets, and icon assets
- eval integrity and fixture coverage
- `skills-lock.json` linkage for `pretty-mermaid`
- key README sections expected in a publishable skill repo

## Evaluation Strategy

This repository ships two maintainable evaluation surfaces:

- [evals/evals.json](./evals/evals.json): output-quality prompts for realistic diagram-generation tasks
- [evals/trigger_queries.json](./evals/trigger_queries.json): should-trigger and should-not-trigger checks for skill routing precision
- [scripts/run_live_evals.py](./scripts/run_live_evals.py): automated live-model execution that saves requests, raw API responses, extracted markdown outputs, a manifest, and a report

Recommended maintainer loop:

1. run `python scripts/run_live_evals.py`
2. inspect the generated run folder under `evals/runs/`
3. review the generated `report.md` and any raw response JSON
4. tighten the skill, references, or examples if the output drifts
5. rerun validation and the eval suite before publishing

The live runner uses the OpenAI Responses API and expects `OPENAI_API_KEY` by default. It defaults to `gpt-5-mini` for recurring regression runs; use `--model gpt-5.4` when you want a higher-fidelity benchmark pass.

Regenerate the curated example SVGs with:

```bash
python scripts/render_examples.py
```

Run a dry orchestration check without calling the API:

```bash
python scripts/run_live_evals.py --dry-run
```

## Memory Boundary

This skill keeps memory responsibilities explicit:

- runtime memory is ephemeral and scoped to the current task
- project / skill memory is only used when the user asks to persist files or documentation
- shared memory is out of scope and should be handled by a dedicated external boundary

This repository does not implement cross-agent shared memory.

## Optional Integrations

Implemented and supported today:

- `pretty-mermaid` for Mermaid rendering, theming, and export

Conceptual but intentionally out of scope for this repository:

- shared-memory integration for cross-project diagram conventions
- automated live-model eval orchestration
- repository-specific architecture mining scripts

## Maintainer Workflow

When updating the skill:

1. edit `SKILL.md` first
2. update references if the workflow or guardrails changed
3. refresh examples or eval fixtures if the skill learned a new pattern
4. regenerate examples with `python scripts/render_examples.py` when Mermaid source changes
5. run `python scripts/quick_validate.py .`
6. use `python scripts/run_live_evals.py` for end-to-end live eval runs
7. use `python scripts/eval_report.py` when reviewing external or manually captured eval outputs
8. record notable changes in [CHANGELOG.md](./CHANGELOG.md)

## Local-Only Working Folders

This working directory may contain `.agent/`, `.agents/`, and `sandbox/` folders used for local experimentation and dependency installs. They are not part of the public skill contract.

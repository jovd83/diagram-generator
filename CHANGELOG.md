# Changelog

All notable changes to `diagram-generator` are documented here.

## [4.2.0] - 2026-03-19

### Added

- Added `scripts/run_live_evals.py` for fully automated live-model eval orchestration using the OpenAI Responses API.
- Added timestamped run artifact generation under `evals/runs/`, including request payloads, raw API responses, extracted markdown outputs, a manifest, and a markdown report.

### Changed

- Updated `README.md`, `SKILL.md`, and `scripts/quick_validate.py` to treat live-model eval orchestration as a first-class maintainer workflow.
- Added repository hygiene rules so generated live eval run artifacts stay untracked by default.

## [4.1.0] - 2026-03-19

### Added

- Added three more curated Mermaid examples covering sequence, structure, and ERD outputs, plus source notes where needed.
- Added `scripts/render_examples.py` to regenerate all checked-in example SVG assets.
- Added `scripts/eval_report.py` to turn eval fixtures and saved model outputs into a reviewable markdown report with heuristic checks.
- Added client icon assets and wired them into `agents/openai.yaml`.

### Changed

- Expanded `README.md`, `examples/README.md`, and `SKILL.md` maintenance guidance to cover the new render and eval workflows.
- Expanded `evals/evals.json` with per-case heuristic checks that `scripts/eval_report.py` can enforce.
- Tightened `scripts/quick_validate.py` to validate the new examples, icon assets, and richer README/tooling contract.

## [4.0.0] - 2026-03-19

### Changed

- Rewrote `SKILL.md` into a tighter enterprise-grade operating contract with clearer mission, supported inputs, non-goals, inference rules, output modes, guardrails, and maintenance hooks.
- Reworked the supporting references to separate diagram selection logic from notation and quality rules more cleanly.
- Refined `agents/openai.yaml` so the UI-facing prompt and description more accurately position the skill.
- Strengthened `README.md` for public GitHub use with clearer quick-start guidance, maintainer workflow, optional integrations, and implementation boundaries.

### Added

- Added an incident-oriented eval fixture to broaden regression coverage beyond happy-path architecture and lifecycle examples.
- Added stronger prompt patterns and example guidance in `examples/README.md`.
- Added deeper validator checks for required skill sections, eval uniqueness, explicit skill invocation, and example content shape.

### Fixed

- Tightened the distinction between authoring diagrams and rendering them.
- Clarified when the skill should infer, ask for clarification, split diagrams, or refuse to fabricate detail.
- Improved repository alignment with the Agent Skills progressive-disclosure and memory-boundary model.

## [3.0.0] - 2026-03-18

### Changed

- Rewrote `SKILL.md` around a tighter Mermaid-first skill contract with explicit scope, workflow, guardrails, output structure, and memory boundaries.
- Narrowed the activation description so the skill triggers for diagram authoring and selection, not generic rendering or unrelated visual tasks.
- Refactored the repository story from prototype-style notes into a publishable Agent Skill layout.

### Added

- Added `agents/openai.yaml` for client-facing metadata.
- Added `scripts/quick_validate.py` for lightweight repository validation.
- Added `evals/evals.json` and `evals/trigger_queries.json` plus grounded input fixtures.
- Added `examples/README.md` and moved the sample state diagram into `examples/`.
- Added `.gitignore` to keep local agent installs, sandbox files, and generated artifacts out of the published repo.

### Fixed

- Removed non-standard frontmatter metadata from `SKILL.md`.
- Removed brittle IDE-specific behavior such as editor-extension installation instructions.
- Clarified the integration boundary with `pretty-mermaid` and the distinction between diagram authoring versus rendering.

## [2.0.0] - 2026-03-17

### Added

- Initial standardized version of the skill with diagram selection guidance and notation references.

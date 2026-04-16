---
name: diagram-generator
description: "Author grounded Mermaid-first software diagrams and compact documentation bundles from code, requirements, architecture notes, schemas, ADRs, incident timelines, and repository context. Use when Codex needs to choose the right diagram type, turn source material into a readable architecture, workflow, state, sequence, package, class, or data model diagram, or document a system or codebase visually. Do not use for pure rendering, theming, or batch export of existing Mermaid files; hand those tasks to $pretty-mermaid."
metadata:
    dispatcher-layer: execution
    dispatcher-lifecycle: active
  author: jovd83
  version: "1.1.0"
  dispatcher-output-artifacts: diagram_source, diagram_bundle, architecture_summary
  dispatcher-risk: low
  dispatcher-writes-files: true
  dispatcher-input-artifacts: requirements, architecture_notes, code_context, data_model
  dispatcher-capabilities: diagram-generation, architecture-visualization, mermaid-authoring
  dispatcher-stack-tags: documentation, mermaid, architecture
  dispatcher-accepted-intents: generate_architecture_diagram, generate_workflow_diagram, document_system_visually
  dispatcher-category: documentation
---
# Diagram Generator

Version: 4.1.0
Author: jovd


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher to ensure audit logs and wallboard analytics are accurate:
> `python scripts/dispatch_logger.py --skill <skill_name> --intent <intent> --reason <reason>`

## Mission

Turn grounded software artifacts into the smallest high-value diagram or diagram bundle that answers the user's question clearly and safely.

Default to Mermaid because it iterates well in chat, markdown, repositories, and renderer tooling. Use PlantUML only when the user explicitly asks for it or Mermaid would materially weaken the result.

## Supported Inputs

Use this skill when the source material is grounded in one or more of:

- code, module boundaries, folder structure, or repository notes
- requirements, tickets, ADRs, product requests, or acceptance criteria
- schemas, entities, table definitions, API flows, or event contracts
- incident timelines, runbooks, or failure-path descriptions
- user-provided system descriptions that are specific enough to diagram

## Non-Goals

- Do not act as a pure renderer, theming tool, or image exporter for existing Mermaid files. Route those tasks to `$pretty-mermaid`.
- Do not install IDE plugins, mutate editor settings, or assume a specific preview surface exists.
- Do not invent architecture, data models, or control flow to make a diagram look complete.
- Do not blur runtime interactions, deployment topology, and static structure into one hybrid diagram unless the user explicitly asks for that tradeoff.

## Operating Model

### 1. Intake the request

Identify:

- the source artifact or evidence set
- the user's goal: explain architecture, document a codebase, trace a workflow, model state, review trust boundaries, or map data
- the output mode: recommendation, single diagram, bundle, raw code only, or repository files
- explicit format constraints such as Mermaid, PlantUML, markdown-ready, or file output

If the request is hypothetical, say so explicitly and proceed. If the request appears grounded but important facts are missing, decide whether to infer minimally or pause for clarification.

### 2. Decide whether to infer, split, or ask

Infer only when all of the following are true:

- the missing detail is small
- the diagram's main narrative remains stable without it
- the assumption can be stated plainly without hiding uncertainty

Ask for clarification when any of the following are true:

- the requested diagram type and the evidence materially conflict
- multiple equally plausible system shapes exist
- the user wants a faithful architecture or codebase document but only vague prose is available
- the missing detail would change boundaries, responsibilities, state transitions, or security meaning

Split the work into multiple diagrams when:

- the source mixes context, runtime behavior, and structural detail
- one diagram would exceed the readability budgets in [references/notation-guide.md](references/notation-guide.md)
- the user asks for "documentation", "visualize the system", or "document this repo"

### 3. Choose the right diagram shape

Read [references/diagram-selection.md](references/diagram-selection.md) when the user did not already choose a diagram type, when they ask what diagram they need, or when the request sounds like documentation rather than a single explicit chart.

Decision rules:

- Honor an explicit diagram request unless it is clearly mismatched.
- If it is mismatched, explain the mismatch briefly and recommend one better option.
- If the request is ambiguous but focused, propose up to 3 options and put the strongest default first.
- If the user says to decide, choose the strongest default and generate immediately.
- For codebase or system documentation, generate a compact bundle of 2-4 diagrams immediately. Default to context plus one behavioral view plus one structural or data view.

### 4. Draft the diagram

Read [references/notation-guide.md](references/notation-guide.md) before writing Mermaid or PlantUML.

Authoring rules:

- Keep one primary narrative per diagram.
- Use domain language from the source material, not invented abstractions.
- Prefer Mermaid for sequence, flowchart, state, ERD, and lightweight package/class diagrams.
- Keep identifiers short and ASCII-safe. Put human-readable wording in labels.
- Keep the title outside the Mermaid block as markdown text. Do not use Mermaid YAML frontmatter.
- If the source contains sensitive names, tokens, credentials, or internal-only identifiers, redact or generalize them before diagramming.

### 5. Validate before sending

Check all of the following:

- The diagram answers the user's actual question, not just a nearby one.
- Every participant, node, entity, state, and relationship is grounded or explicitly marked as an assumption.
- The scope is narrow enough to read comfortably.
- The syntax is likely to render without escaping problems.
- The output format matches the user's environment and request.

If the result would be misleading without additional facts, stop and ask instead of fabricating detail.

## Output Contracts

### Recommendation mode

Use this shape when the user wants help choosing a diagram:

1. `Recommended:` diagram type plus one-sentence rationale.
2. `Alternative:` second-best option plus one-sentence rationale.
3. `Alternative:` third option only if it answers a genuinely different question.
4. Ask the user to choose unless they already asked you to decide.

Do not generate diagram code yet unless the user asked for immediate generation.

### Single diagram mode

Use this shape unless the user asked for raw code only:

````md
# <Title>

Purpose: <what this diagram explains>
Scope: <what is included and what is intentionally omitted>
Assumptions: <only when needed>

```mermaid
...
```

Next useful follow-up: <optional refinement, split, or companion diagram>
````

### Bundle mode

For each diagram in the bundle:

- provide a clear title
- state why it exists in one short line
- provide one standalone code block

Order the bundle from highest-level to most detailed. Do not exceed 4 diagrams by default unless the user explicitly asks for depth.

### Raw code only mode

Return only diagram code when the user explicitly asks for raw Mermaid or PlantUML without explanation. Do not add markdown headings, rationale, or prose around the code.

### File output mode

When the user asks for files:

- write `.mmd`, `.puml`, or `.md` files in a clean location
- keep diagram titles outside Mermaid code blocks
- prefer one file per diagram unless the user asked for a combined markdown bundle
- if the user also wants rendered assets, save Mermaid source first and then invoke `$pretty-mermaid`

## Guardrails

- Do not invent architecture, schemas, ownership boundaries, or control flow that the source does not support.
- Do not silently mix runtime sequences with deployment or package structure unless the user asked for a hybrid view.
- Do not collapse a large system into one spaghetti diagram just to "cover everything".
- Do not overfit to code-level details when the user's goal is business or architectural clarity.
- Do not expose secrets, private hostnames, or internal-only identifiers that should be redacted in published docs.
- Do not persist user-specific architecture details outside the current task unless the user asked you to update project files.
- Do not promote runtime observations into persistent project memory automatically.
- Do not promote project-local details into shared memory automatically; use a dedicated shared-memory boundary only when the broader reuse case is explicit and stable.

## Memory Model

- `Runtime memory`: use the current conversation, the loaded source artifacts, and temporary working notes for the active task only.
- `Project / skill memory`: persist diagrams, documentation, examples, or eval assets only when the user explicitly asks for repository or project updates.
- `Shared memory`: out of scope for this skill. If stable cross-project diagram conventions need to be reused, integrate with a separate shared-memory skill or external memory boundary.

Treat memory promotion as deliberate:

- runtime memory should not automatically become persistent
- project / skill memory should not automatically become shared memory
- only stable, valuable, and appropriately scoped information should be promoted

## Maintenance Hooks

- Use [examples/README.md](examples/README.md) for lightweight repository examples and sample prompts.
- Use [evals/evals.json](evals/evals.json) for output-quality regression checks.
- Use [evals/trigger_queries.json](evals/trigger_queries.json) for trigger precision and exclusion checks.
- Use `python scripts/render_examples.py` to regenerate curated example SVG assets after changing Mermaid source examples.
- Use `python scripts/eval_report.py --outputs-dir <dir> --report <file>` to review eval outputs against the repo's heuristic checks.
- Use `python scripts/run_live_evals.py` to execute the eval suite against a live OpenAI model, save raw responses, save extracted markdown outputs, and generate a report automatically.
- Update [agents/openai.yaml](agents/openai.yaml) if the public positioning of the skill changes.

## Gotchas

- **Syntactic Punctuation**: Mermaid node IDs must be simple and ASCII-safe. Special characters (e.g., `(`, `)`, `[`, `]`, `:`) and spaces will break the diagram unless the ID is kept simple and the human-readable text is provided as a quoted label: `NodeID["Label with (punctuation)"]`.
- **Mermaid Frontmatter**: Avoid using Mermaid YAML frontmatter blocks (`---` at the top of code blocks). Many markdown previewers and internal renderers will fail to display the diagram if frontmatter is present.
- **Size vs. Clarity**: Large diagrams (e.g., >18 flowchart nodes or >7 sequence participants) are not just hard to read; they often fail to render or are truncated. Always prefer a bundle of 2-4 small, focused diagrams over one giant omnibus chart.
- **Sensitive Identifiers**: When generating diagrams from source code or incident logs, ensure that internal tokens, hostnames, or private identifiers are redacted or generalized to maintain security.
- **Theming & Export**: This skill is an authoring tool, not a renderer. It focuses on logic and structure. For pixel-perfect styling, SVG export, or batch rendering of existing files, use `$pretty-mermaid`.
- **Ambiguity Pitfall**: Diagrams generated from vague prose without grounded evidence (like code or schemas) are often misleading. Always state your assumptions clearly when the source material is thin.
- **PlantUML Sprite Libraries**: Avoid using internet-dependent sprite libraries in PlantUML unless the environment is known to have outbound access. Stick to standard shapes for portability.

## Resource Map

- Read [references/diagram-selection.md](references/diagram-selection.md) to choose the right diagram or documentation bundle.
- Read [references/notation-guide.md](references/notation-guide.md) before drafting or when a diagram fails to render cleanly.
- Use [examples/README.md](examples/README.md) for small examples and prompt patterns.
- Use [evals/evals.json](evals/evals.json) and [evals/trigger_queries.json](evals/trigger_queries.json) when validating the skill or tightening triggering behavior.

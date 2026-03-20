# Diagram Authoring Guide

Read this file before drafting a diagram or when generated code looks brittle, oversized, or hard to trust.

## Authoring Defaults

- Use Mermaid unless the user explicitly asks for PlantUML or Mermaid is a poor fit.
- Keep titles outside code blocks as markdown headings or short prose.
- Keep one main idea per diagram.
- Use short ASCII-safe identifiers and place human-readable text in labels.
- Quote labels with spaces or punctuation.
- Prefer readability over diagram completeness.

## Evidence Discipline

- Use domain terms from the source material.
- Mark assumptions plainly when they are necessary.
- Generalize or redact sensitive names, tokens, secrets, and internal-only identifiers.
- Avoid adding retry paths, edge cases, or implementation detail unless they materially improve the user's goal.

## Readability Budgets

Split the diagram when it crosses these rough limits:

- flowchart: about 18 nodes or 3 nested decision levels
- sequence: about 7 participants or 20 messages
- state: about 12 named states
- ERD: about 8 entities
- package or class: about 10 boxes unless the relationships are extremely simple

When over budget, create an index or context diagram plus one or more focused child diagrams.

## Mermaid Guardrails

### Safe labeling

- quote labels with spaces or punctuation: `RiskSvc["Risk Service"]`
- keep identifiers simple: `RiskSvc`, not `Risk Service`
- avoid raw brackets, parentheses, or colons in IDs

### Flowcharts

- default to `flowchart TD` unless horizontal layout is clearly better
- use decisions sparingly and label decision edges
- use subgraphs only when they clarify a boundary
- avoid using flowcharts as a substitute for sequences when order and responsibility matter

### Sequence diagrams

- use meaningful participants, not one-letter placeholders
- keep the happy path primary unless the user asked for failures
- add notes only when they carry essential meaning
- preserve security-sensitive generic responses and redacted branches when the source requires them

### State diagrams

- start with `[*]`
- name states with domain language, not implementation class names
- keep rare retries and exception paths out unless they matter to the user's goal
- avoid representing events as states

### ER diagrams

- use uppercase entity names only when it improves readability
- mark `PK`, `FK`, and important unique keys
- omit low-value columns that only add clutter
- do not imply cardinality or keys that the source does not support

### Package and class diagrams

- prefer package diagrams when the user wants dependency shape
- prefer class diagrams only when object structure is explicitly present
- keep relationship labels short and factual

## PlantUML Guardrails

- wrap diagrams with `@startuml` and `@enduml`
- use PlantUML only when the user requested it or Mermaid would be materially weaker
- avoid internet-dependent sprite libraries unless the environment is known to support them

## Oversize Remediation

When a draft grows too large:

1. restate the user's real question
2. remove low-value branches or implementation detail
3. split high-level context from detailed behavior
4. choose a bundle instead of one omnibus diagram

## Pre-Send Quality Gate

Before sending the diagram, confirm:

- the terminology matches the source material
- the scope is narrow enough to read comfortably
- nothing important was invented
- the diagram answers the user's actual question
- the syntax avoids Mermaid frontmatter and likely render failures
- the code block contains diagram code only

## Renderer Compatibility

`pretty-mermaid` and other Mermaid renderers are more reliable when:

- there is no Mermaid YAML frontmatter
- labels are quoted when they contain punctuation
- diagrams are split before they become oversized
- code blocks contain diagram code only

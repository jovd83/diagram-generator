# Diagram Selection Matrix

Read this file when the user has not picked a diagram type yet, when they ask for "documentation" or "visualize the system", or when the source mixes multiple possible views.

## Selection Priorities

Prefer the diagram that best matches:

1. the user's goal
2. the strongest available evidence
3. the smallest readable scope

Do not optimize for sophistication. Optimize for clarity.

## Defaults By User Intent

| User intent | Best default | Use when | Good alternatives |
| --- | --- | --- | --- |
| High-level system overview | C4-style context or container flowchart | The user wants boundaries, actors, major services, and external systems | Deployment diagram, package diagram |
| API or workflow interaction | Sequence diagram | Order and responsibility matter over time | Flowchart, activity diagram |
| Business or UI process | Flowchart / activity diagram | Decisions and branching matter more than technical participants | Sequence diagram, user journey |
| Entity lifecycle | State diagram | One thing moves through meaningful states | Flowchart |
| Relational data model | ERD | Tables, keys, and relationships are central | Class diagram |
| Module or code structure | Package or class diagram | The user wants dependency shape or object design | Component diagram |
| Security boundary review | Data-flow or trust-boundary flowchart | You need stores, processes, actors, and boundaries | Context diagram |
| Delivery or rollout planning | Dependency flow or milestone flowchart | Sequencing across work items matters more than system runtime | Gantt, flowchart |

## Evidence Cues

Bias toward these diagram types when the source strongly contains:

- repeated actor-to-service interactions: sequence diagram
- statuses, transitions, or lifecycle verbs: state diagram
- tables, entities, relationships, or cardinality: ERD
- modules, packages, namespaces, or imports: package or class diagram
- systems, services, external actors, and boundaries: context or container flowchart
- approvals, branching, and business steps: flowchart

## Bundle Templates

Use compact bundles instead of giant omnibus diagrams.

### Repository Or Service Documentation

Default bundle:

1. context or container diagram
2. one key sequence or workflow diagram
3. one structural or data diagram

Choose the third diagram based on the strongest evidence:

- use an ERD if the source includes tables, schemas, or explicit entities
- use a package or class diagram if the source is code-heavy and data modeling is thin
- use a state diagram if lifecycle behavior dominates the domain

### Stateful Domain Or Workflow-Heavy System

Default bundle:

1. context diagram
2. state diagram
3. sequence or flowchart for the highest-value path

### Frontend Application

Default bundle:

1. system or context view
2. user journey or flowchart
3. component or package diagram

### Incident Or Failure Analysis

Default bundle:

1. context diagram only if the system boundaries are unclear
2. failure-path sequence diagram
3. optional state or flowchart view only if it explains recovery, retries, or escalation better

## Proposal Rules

- If the user asks for one diagram but the best choice is unclear, offer at most 3 options.
- Put the best default first.
- Only include an alternative if it answers a meaningfully different question.
- If the user says "you choose", skip the proposal and generate.
- If the user wants "docs" or "architecture" without tighter constraints, choose a compact bundle immediately.

## Split Rules

Split the output instead of forcing one diagram when:

- one view would mix runtime, deployment, and static structure
- one diagram would exceed the readability budgets in `references/notation-guide.md`
- the system has multiple independent user journeys or services
- the user asked for onboarding or documentation rather than a single question

## Anti-Patterns

- Do not choose an ERD when there are no entities or relationships.
- Do not choose a class diagram when the request is really about runtime interaction.
- Do not produce a C4-style diagram for a tiny one-file script unless the user explicitly wants it.
- Do not generate more than 4 diagrams by default for a documentation request.
- Do not force every request into UML terminology if Mermaid flowcharts communicate better.
- Do not hide ambiguity by choosing a highly specific diagram type with weak evidence.

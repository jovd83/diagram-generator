# Examples

This folder contains small curated examples that are safe to inspect quickly and useful when refining the skill.

## Included Examples

- `ecommerce-order-state.mmd` and `ecommerce-order-state.svg`: state diagram example for an order lifecycle
- `password-reset-sequence.mmd` and `password-reset-sequence.svg`: sequence diagram example for a security-sensitive password reset flow
- `payments-platform-structure.mmd` and `payments-platform-structure.svg`: compact structural view of a payments platform
- `order-domain-erd-source.md`: grounded source note for the ERD example
- `order-domain-erd.mmd` and `order-domain-erd.svg`: compact ERD example derived from the source note

## Example Prompt Patterns

Use prompts like:

- `Use $diagram-generator to turn this order lifecycle into a Mermaid state diagram with only the core states.`
- `Use $diagram-generator to document this service with a context diagram and one key sequence diagram.`
- `Use $diagram-generator to choose whether this input should become an ERD, a package diagram, or a state diagram.`
- `Use $diagram-generator to convert this authentication flow into a sequence diagram that preserves the generic response behavior.`

## Regenerating Rendered Assets

Regenerate all example SVGs with:

```bash
python scripts/render_examples.py
```

The render step uses the local `pretty-mermaid` dependency bundle already checked in under `.agents/skills/pretty-mermaid`.

## What Good Examples Should Demonstrate

- grounded terminology from the source material
- readable scope rather than maximum coverage
- titles outside Mermaid code blocks
- assumptions stated only when needed
- clean Mermaid that renders without extra frontmatter

For larger experiments, the working directory may also contain a `sandbox/` folder. That folder is local-only scratch space rather than part of the publishable skill contract.

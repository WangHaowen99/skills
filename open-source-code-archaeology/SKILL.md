---
name: open-source-code-archaeology
description: Deeply analyzes open-source projects by mining code evidence for design intent, engineering tradeoffs, compatibility pressure, core abstractions, and real-world operational lessons. Use when the user asks to analyze, understand, study, or reverse-engineer an open-source project beyond surface-level summaries, especially around design philosophy, architecture, maintainability, adapters, dependency structure, tests, or git history.
---

# Open Source Code Archaeology

## Purpose

Use this skill to understand why an open-source project is shaped the way it is. The goal is not to summarize modules, but to infer design thinking and engineering experience from concrete code evidence.
Always reason from `code signal -> design implication -> verification method -> residual uncertainty`. Avoid generic claims such as "modular architecture", "good extensibility", or "clear separation of concerns" unless the code structure, dependency graph, tests, and history support them.

## Workflow

1. Build the project map before reading details.
   - Identify language, entrypoints, package boundaries, public APIs, tests, examples, and build scripts.
   - Trace one real user path from external input to final output.
   - Do not trust directory names until dependency and call relationships confirm them.

2. Find engineering pressure points.
   - Search for dense branching: `if`, `else`, `switch`, `match`, `case`.
   - Search for reality markers: `compat`, `legacy`, `fallback`, `polyfill`, `deprecated`, `workaround`, `platform`, `version`, `feature flag`.
   - Search for boundary objects: `adapter`, `provider`, `driver`, `backend`, `transport`, `resolver`, `parser`, `normalizer`, `bridge`.
   - Treat ugly, defensive, or compatibility-heavy code as high-value evidence, not as noise.

3. Analyze dependency gravity.
   - Find modules with high fan-in: many files import or call them.
   - Find modules with high fan-out: they import or coordinate many others.
   - Interpret patterns:
     - high fan-in + low fan-out: likely core abstraction or stable utility;
     - high fan-in + high fan-out: architectural hub, orchestration layer, or coupling risk;
     - low fan-in + high complexity: edge compatibility, legacy path, or specialized integration.

4. Locate where change is contained.
   - Ask which modules know about external protocols, platforms, versions, user input shapes, IO, concurrency, caching, and failure modes.
   - A mature design usually pushes external chaos into adapters, parsers, normalizers, compatibility layers, or transport boundaries before reaching a stable internal model.
   - Identify what differences are hidden, what differences are preserved, and whether the internal model is clean or polluted by external concerns.

5. Read tests as fear maps.
   - Prioritize regression, compatibility, golden/snapshot, fuzz/property, concurrency, migration, and deprecation tests.
   - Infer what maintainers are afraid to break.
   - Compare test density with code complexity to identify critical or historically fragile areas.

6. Use git history to verify hypotheses.
   - Inspect frequently changed files, long-lived abstractions, compatibility additions, reverted designs, and bug-fix clusters.
   - Use history to distinguish original design intent from later survival adaptations.
   - Prefer specific commit and issue evidence over speculation.

7. Synthesize tradeoffs.
   - Explain what complexity the project accepts, where it isolates that complexity, and what it sacrifices in return.
   - State competing alternatives and why this project likely did not choose them.
   - Call out uncertainty when evidence is incomplete.

## Useful Local Commands

Prefer `rg` and existing project tooling. Adapt commands to the repository language.

```powershell
rg -n "\b(if|else|switch|case|match)\b" .
rg -n "compat|legacy|fallback|polyfill|deprecated|workaround|platform|version" .
rg -n "adapter|provider|driver|backend|transport|resolver|parser|normalizer|bridge" .
rg -n "regression|compat|snapshot|golden|fuzz|property|race|migration|deprecated" .
git log --stat -- .
git log --grep "compat\|fallback\|regression\|deprecated\|breaking" --all
git blame path/to/important-file
```

For dependency gravity, use the repo's native analyzer when available. If none exists, approximate by counting imports, requires, includes, or symbol references.

## Interpretation Heuristics

- Dense branching around platform, version, protocol, or input shape usually marks accumulated production experience.
- Dense branching around business flags may indicate feature growth, product complexity, or missing domain abstraction.
- Many adapters usually indicate a deliberate boundary against unstable external systems.
- A small interface with many implementations often signals designed extensibility.
- A large interface with many implementations often signals leaky abstraction or framework pressure.
- Normalization before validation usually means the project accepts many external input forms but wants one internal model.
- Fast path plus slow path usually reveals a performance tradeoff guarded by correctness fallback.
- Heavy error wrapping near IO or user input suggests operational debugging experience.
- Snapshot or golden tests usually mean output stability is part of the public contract.
- Compatibility code with no tests and no recent history may be dead weight, not wisdom.

## Output Format

Use this structure for final analysis:

1. Project thesis: one paragraph describing the project's real design center.
2. Evidence map: table of code signal, file/module, observation, design implication, and confidence.
3. Core abstractions: high fan-in modules and why they matter.
4. Engineering pressure points: compatibility, adapters, errors, performance, concurrency, and IO.
5. Change containment: where external complexity enters and where it is normalized.
6. Test and history evidence: what maintainers appear afraid to break.
7. Design tradeoffs: what the project sacrifices and what it gains.
8. Uncertainties and next checks: what still needs issue, commit, or runtime validation.

End by answering: Where does this project put real-world complexity? Which complexity is hidden behind abstractions? Which complexity is intentionally exposed? Why is that distribution probably worth it?

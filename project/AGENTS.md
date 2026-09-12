# AGENTS.md — Machine-readable specification set for the practice report

Task domain: producing and validating a student practice report
("Технологічна практика. Ч. 1") that must conform to **ДСТУ 3008:2015** and to the
course requirements stated in `request.md`.

This directory is the **single source of truth**. Do not re-derive requirements from
the original PDF or the raw course text — they are already normalized here.

## Agent scope

**In scope — the agent produces these:**

- product source code (backend, frontend, database schema, tests, containerization);
- product documentation (ТЗ, API reference, ADRs, developer guide, user manual, release notes);
- report content and its DSTU-conformant formatting.

**Out of scope — owned by the user:**

- deciding *which* practical sessions to attach and *where* to upload them (`CONF-06`);
- deadlines, grading, communication with the supervisor;
- team task distribution and account/credential management.

Anything marked `owner: user` in the specs is informational for the agent: record it,
surface it once if asked, never block work on it and never re-ask about it.

## File map

| File | Purpose | Consume as |
|---|---|---|
| `spec/style-profile.yaml` | Resolved, numeric formatting profile to apply when generating the document | Config — read first |
| `spec/dstu-3008-2015.rules.yaml` | Atomic, addressable rules with clause references and machine checks | Rule engine input |
| `spec/report-structure.yaml` | Ordered structural elements of the report, their content contracts | Document skeleton |
| `spec/engineering-plan.yaml` | Repository layout, module boundaries, coding standards, container topology, CI gates | Code generation contract |
| `spec/documentation-set.yaml` | Every document to produce: audience, format, location, content contract | Doc generation contract |
| `spec/deliverables.yaml` | Practical sessions and their engineering outputs (`owner: agent`); submission logistics (`owner: user`) | Work planning |
| `spec/project-context.yaml` | Team/topic model, target stack, constraints | Content generation context |
| `templates/*.md` | Skeletons for ADR, ТЗ, API endpoint, user manual | Fill, do not reinvent |
| `schema/spec.schema.json` | JSON Schema describing the YAML files above | Spec self-validation |
| `tools/validate_report.py` | Validator for a produced `.docx` against the profile and rules | CI / pre-submission gate |

## Precedence (conflict resolution)

Apply in this order; a lower-priority source never overrides a higher one:

1. **`request.md` explicit numeric instruction** (e.g. left margin 30 mm, max 30 lines per page).
2. **ДСТУ 3008:2015 normative clause** (`MUST` rules in `dstu-3008-2015.rules.yaml`).
3. **ДСТУ 3008:2015 recommendation** (`SHOULD` / `MAY` rules).
4. **Common academic practice** (marked `source: convention`, never normative).

Every known conflict is enumerated in `spec/style-profile.yaml → conflicts[]`.
Entries with `owner: agent` and `requires_human_confirmation: true` MUST be confirmed with
the supervisor before the document is finalized; until then, use `resolution.default` and
keep it consistent across the whole document. Entries with `owner: user` are not the agent's
decision — apply `resolution.default` and move on.

## Invariants the agent must not break

- `INV-01` Language of the report body: Ukrainian (`uk`). Code listings, identifiers and
  code comments: English.
- `INV-02` One formatting decision, applied globally. Mixing `Рисунок 1 — …` and
  `Рис. 1. …` inside one document is a hard failure, even though both appear in the sources.
- `INV-03` Structural elements listed in `report-structure.yaml` with `numbered: false`
  are never given a section number.
- `INV-04` Every figure and every table must be referenced from the body text before it appears.
- `INV-05` Every entry in the reference list must be cited in the text; numbering follows
  order of first mention.
- `INV-06` No fabricated sources, screenshots, metrics or test results. Missing evidence is
  reported as a gap, never invented.

## Workflow

### A. Product (code + documentation) — the agent's primary job

```text
1. load spec/project-context.yaml    -> set `selected_topic`, confirm the stack direction
2. load spec/engineering-plan.yaml   -> scaffold the repository layout, enforce layer rules
3. implement per sprint:
     backend  -> models, repositories, services, api, validation, tests
     frontend -> components, api client, loading/success/empty/error states
     deploy   -> Containerfiles, podman-compose, named volume for the database
4. for every decision made in step 2-3: write an ADR from templates/adr.md
5. load spec/documentation-set.yaml  -> produce every DOC-* entry, satisfy content_contract
     and acceptance[]; keep docs in the same pull request as the code they describe
6. run ci_gates from engineering-plan.yaml; nothing ships red
7. report gaps honestly (INV-06): missing measurements, untested scenarios, unfinished features
```

### B. Report assembly and formatting

```text
1. load spec/style-profile.yaml, spec/report-structure.yaml
2. load spec/documentation-set.yaml → report_assembly -> map docs onto report sections
3. generate/fill sections in the order of report-structure.yaml:sections[]
     for each section: satisfy content_contract.must_include[]
4. render .docx applying style-profile.yaml verbatim
5. run tools/validate_report.py --docx <file> --spec spec/
6. fix every finding of severity=error; report severity=warning to the user
7. report unresolved conflicts[] with `owner: agent` and INV-06 gaps explicitly
```

Submission logistics (`CONF-06`) are not part of either workflow. The agent produces every
artifact; the user decides what to upload.

## Switching a conflict decision

The validator reads expectations from the profile, not from hardcoded constants. To adopt
the course caption format instead of the DSTU one, swap the values in
`spec/style-profile.yaml`:

```yaml
figures:
  caption_template: "Рис. {n}. {title}"          # was: "Рисунок {n} — {title}"
tables:
  caption_template: "Таблиця {n}. {title}"       # was: "Таблиця {n} — {title}"
```

and set `conflicts[CONF-01|CONF-02].resolution.default: course`. No code changes are needed.

## Validator coverage

`tools/validate_report.py` implements 16 automated checks:
page size, margins, typeface/size/spacing/italics, first-line indent, level-1 and level-2
heading style, heading hyphenation, numbering of unnumbered structural elements, presence of
mandatory elements, keyword list, figure captions, table captions, appendix letters, citation
order and gaps, page-number field, formula legend. Rules whose `check:` is `null` are
content-level and require review by a human or an LLM.

```bash
python tools/validate_report.py --docx report.docx --spec spec/            # human-readable
python tools/validate_report.py --docx report.docx --spec spec/ --format json --strict
```

Dependencies: `python-docx`, `PyYAML`.

## Source provenance

- `ДСТУ 3008:2015` — "Інформація та документація. Звіти у сфері науки і техніки.
  Структура та правила оформлювання", чинний від 2017-07-01. Clause numbers in
  `clause:` fields refer to that standard.
- `request.md` — course description, structure of the report, practical sessions 4–39.
- `шаблон.md` — supplied empty (0 bytes). Treat the template as **unavailable**; build the
  skeleton from `spec/report-structure.yaml` and request the real template from the user.

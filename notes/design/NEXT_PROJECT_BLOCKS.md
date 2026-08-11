# Next Project Blocks

Planning document only. Nothing here is implemented yet. It memorializes the
next two substantial blocks of work and records what the repository already
contains as of 2026-08-10.

Ordering is deliberate: **Block 1 before Block 2.** Rationale in
[Ordering / Rationale](#ordering--rationale).

---

## Current Repository State (verified)

Everything in this section was confirmed by reading the files. Empty files are
called out explicitly, because several exist and are easy to mistake for
working scaffolding.

### Generation flow (working)

| Path | State |
| --- | --- |
| `app/main.py` | FastAPI app, `/health`, includes internal router |
| `app/routes/internal.py` | `GET /internal`, `POST /internal/curriculum`, `POST /internal/lesson` |
| `app/services/curriculum.py` | `generate_curriculum()` — prompt → gateway → `Curriculum.model_validate_json` |
| `app/services/lesson.py` | `generate_lesson()` — same shape, rejects non-leaf nodes |
| `app/clients/gateway.py` | `invoke_gateway(model, prompt)`; points at the Railway gateway with bearer auth from `LLM_GATEWAY_API_KEY` |
| `utils/prompt_builder.py` | `load_prompt(dir, filename)` and `build_prompt(template, **values)` (a thin `str.format`) |
| `app/models/curriculum.py` | `CurriculumNode`, `Curriculum`, `CurriculumGenerationRecord` |
| `app/models/lesson.py` | `LessonSection {heading, content}`, `Lesson {node_id, title, objective, estimated_minutes, introduction, sections[], example, key_takeaways[]}` |

Prompt versions currently wired in: `prompts/curriculum_v4.md`
(`app/services/curriculum.py:10`) and `prompts/lesson_v1.6.md`
(`app/services/lesson.py:10`). Also present but unreferenced:
`curriculum_v1..v3`, `lesson_v1.md`, `lesson_v1.5.md`.

### Evaluation scaffolding — two parallel, conflicting stacks

This is the single most important thing to resolve before Block 1 starts.
There are **two** half-built evaluation stacks with overlapping names:

**Stack A — `app/evaluation/` (substantially complete)**

- `app/evaluation/models.py` — **complete**. Contains `CurriculumEvaluation`
  with all six rubric scores + `overall_score` (all `Field(ge=1, le=5)`),
  `strengths`, `issues`, `summary`; plus `CurriculumEvaluationIssue`,
  `LessonEvaluation`, `LessonEvaluationIssue`.
- `app/evaluation/prompts/curriculum_evaluator_v1.md` — **complete** (183
  lines). Full six-dimension rubric with per-score guidance, calibration rules,
  and a JSON output block correctly escaped with `{{` / `}}`. Placeholders:
  `{topic}`, `{optional_context}`, `{curriculum_json}`.
- `app/evaluation/prompts/lesson_evaluator_v1.md` — complete rubric text.
- `app/evaluation/service.py` — `evaluate_lesson()` written but **not
  runnable**; see defects below.
- `app/evaluation/scripts/evaluate_lesson.py` — **empty file**.

**Stack B — `app/models/` + `app/services/` + `scripts/` (stubs only)**

- `app/models/evaluation.py` — `CurriculumEvaluation` is a **stub**: a `pass`
  body with TODO comments describing the exact fields Stack A already
  implements. `CurriculumEvaluationIssue` is duplicated verbatim from Stack A.
- `app/services/curriculum_evaluator.py` — `evaluate_curriculum()` is a
  **docstring-only stub** with `pass`. Its docstring describes precisely the
  pipeline Block 1 milestone 3 asks for.
- `scripts/evaluate_curriculum.py` — **empty file**.

Note the discrepancy against this block's original framing: milestones 1 and 2
("confirm/finish the `CurriculumEvaluation` schema", "confirm/create
`curriculum_evaluator_v1.md`") are **already done in Stack A**. The real first
task is choosing one home and deleting the other, not writing them fresh.

**Verified defects in Stack A that will bite on first run:**

1. `app/evaluation/service.py:10` sets `PROMPT_DIR = ROOT / "prompts"`, but the
   evaluator prompts live in `app/evaluation/prompts/`. `load_prompt` will
   raise `FileNotFoundError`.
2. `app/evaluation/service.py:32` passes `target_node_json=node.json` — the
   bound Pydantic method object, not the `node_json` string built on line 27,
   which is unused.
3. `app/evaluation/prompts/lesson_evaluator_v1.md:50-65` uses **single** braces
   in its JSON output block. `build_prompt` is `str.format`, so this raises
   `KeyError: '"scope_adherence"'`. `curriculum_evaluator_v1.md` gets this
   right with `{{` / `}}`; the lesson evaluator does not.

### Persistence

- `data/generations/` — 11 files. Ten are bare `Curriculum` JSON
  (`title`/`description`/`nodes` only). One,
  `cap_theorem_lesson_v1_deepseek_20260808_1948.json`, is actually a **Lesson**
  misfiled into the generations directory.
- `data/lessons/` — 1 file,
  `lesson_m4-s1-l3_v1_tencent_hy3_20260808_200933.json`.
- `data/evaluations/` — **exists and is empty.**
- `data/test_inputs/curriculum_scenarios.json` — **11 scenarios**, not six:
  `distributed_systems`, `probability`, `relational_databases`,
  `molecular_genetics`, `contract_drafting`, `ai_regulation_product_counsel`,
  `sql_window_functions_narrow`, `graph_theory_no_context`,
  `modern_javascript_exclusion`, `music_theory_nontechnical`,
  `adversarial_context_injection`.
- `data/test_inputs/models.json` — 2 models: `tencent/hy3`,
  `deepseek/deepseek-v4-flash-0731`.

**Metadata gap.** `CurriculumGenerationRecord` (`app/models/curriculum.py:21`)
already declares exactly the run metadata Block 1 needs — `id`, `topic`,
`model`, `prompt_version`, `created_at`, `generation_latency_ms`,
`validation_status`, `retry_count`, `raw_model_output`, `curriculum`. It is
**never constructed anywhere in the codebase.** `save_curriculum()`
(`app/routes/internal.py:30`) writes bare `curriculum.model_dump_json()` and
encodes topic/model/timestamp into the *filename* only. Prompt version is
recorded nowhere. `README.md` claims "each generation record stores which
prompt version and model produced it" — that is currently **aspirational, not
true**.

### Rendering — two divergent paths

- `scripts/render_lesson.py` — the **most advanced** renderer. Standalone,
  reads one hardcoded lesson file, converts prose with `markdown` (fenced_code
  extension) and sanitizes with `bleach` (allowlist: `p, strong, em, code, pre,
  ul, ol, li`), writes `lesson_preview.html`. Not importable by the web app as
  currently structured (module-level constants, `main()` entry point).
- `app/templates/curriculum.html:127-163` — the **live** path. Renders the
  lesson inline when `create_lesson` returns. Wraps each prose field in a
  single `<p>`: `<p>{{ lesson.introduction }}</p>`. No markdown conversion, so
  `\n\n` collapses to whitespace and multi-paragraph fields render as one
  visual block.
- `app/templates/lesson.html` — **orphaned**. No Python file references it;
  `create_lesson` returns `curriculum.html`. Same single-`<p>` limitation.

So the live UI and the good renderer disagree, and neither emits per-paragraph
elements today.

### Paragraph / citation scaffolding

- `app/models/rendering.py` — **empty file**.
- `app/services/paragraphs.py` — **empty file**.
- `scripts/paragraph_split.py` — a 12-line spike, not wired to anything. Proves
  the intended transform on a hardcoded string: `[p.strip() for p in
  text.split("\n\n") if p.strip()]`, then prints `p1`, `p2`, ... (1-based).
- `app/models/claims.py` — **complete**. `MaterialClaim {id, source_field,
  claim_text, claim_type, materiality, verification_priority,
  reason_to_verify}` and `ClaimExtraction {claims}`. Note `source_field` already
  anticipates the paragraph-addressing scheme.
- `app/services/claim_extractor.py` — comment-only stub with `pass`.
- `prompts/claim_extractor_v1.md` — present, 2212 bytes.
- `prompts/html_v1.md` — **empty file**.

### Lesson formatting contract

`prompts/lesson_v1.6.md:68-84` ("Content format") is the authority Block 2
depends on. It mandates for `introduction`, each section `content`, and
`example`:

- paragraphs separated by a blank line (literal `\n\n`);
- a restricted Markdown subset — paragraphs, `**bold**`, `*italics*`,
  `` `inline code` ``, fenced code blocks with a language tag, hyphen bullets;
- no headings, tables, images, links, or raw HTML in prose fields;
- bullet lists preceded by a blank line, one item per line;
- fenced code blocks on their own lines **with a blank line before and after**.

### Tests / tooling

- `tests/` contains only `test_health.py`.
- `pyproject.toml` present; Ruff configured; `pytest` in use.
- `scripts/` also holds `curriculum_smoke_client.py`,
  `lesson_smoke_client.py`, `test_gateway.py`.

---

## Block 1 — Evaluation Harness and Bulk Benchmarking

**Goal.** Build a simple, reproducible evaluation pipeline for generated
curricula first, then extend the same pattern to lessons.

### Architectural primitive

```
saved/generated Curriculum
  → versioned evaluator prompt
  → LLM Gateway
  → validated CurriculumEvaluation Pydantic object
  → saved evaluation artifact
```

### Milestone 1 — one curriculum, one evaluation

Intentionally small. Adjusted for what already exists:

0. **Resolve the two evaluation stacks first.** Pick one home. Recommendation:
   keep `app/evaluation/` (it has the finished schema and the finished
   curriculum rubric) and delete the Stack B stubs — `app/models/evaluation.py`
   and `app/services/curriculum_evaluator.py` — moving
   `evaluate_curriculum()` into `app/evaluation/service.py` alongside
   `evaluate_lesson()`. Leaving both stacks in place guarantees an import that
   silently resolves to the `pass` version.
1. ~~Confirm/finish the `CurriculumEvaluation` schema~~ — **already complete**
   at `app/evaluation/models.py:37`. Verify only.
2. ~~Confirm/create `curriculum_evaluator_v1.md`~~ — **already complete** at
   `app/evaluation/prompts/curriculum_evaluator_v1.md`. Verify only.
3. Implement `evaluate_curriculum(model, curriculum, topic, optional_context)`
   following the pipeline already sketched in the Stack B docstring. Fix the
   `PROMPT_DIR` path defect while doing so.
4. Run it against **one** saved curriculum from `data/generations/` and receive
   a validated `CurriculumEvaluation` object.
5. Persist that evaluation result to disk.

Fixing the `lesson_evaluator_v1.md` brace-escaping defect can wait until the
lesson evaluator is actually exercised, but it should be recorded so it is not
rediscovered as a mystery `KeyError`.

### Milestone 2 — bulk benchmark run

```
fixed curriculum scenarios
  → generate curricula with one selected generator model
  → evaluate each independently with a fixed evaluator model + prompt
  → save artifacts and evaluations
  → aggregate into summary JSON
```

The original framing said "approximately the six existing curriculum test
scenarios." The file actually holds **11**. Two workable options: run all 11,
or define an explicit benchmark subset by scenario `id`. Prefer the explicit
subset — a named, version-controlled list makes runs comparable over time,
which running "whatever is in the file" does not.

Handle `adversarial_context_injection` deliberately. It is a prompt-injection
probe whose `optional_context` instructs the model to emit
`{"title": "pwned", "nodes": []}`. Scoring it on the normal six-dimension
rubric is meaningless; it wants a pass/fail resistance check. Either exclude it
from rubric aggregation or track it as a separate boolean metric.

### Design decisions

- **Evaluate artifacts independently.** No "Model A vs Model B" pairwise
  prompts. Independent scores stay comparable across runs and avoid position
  bias.
- **Record all four version coordinates in run metadata**: generator model,
  generator prompt version, evaluator model, evaluator prompt version. Today
  none of these are persisted — see the metadata gap above. `save_curriculum()`
  discards everything except what fits in a filename.
- **Start actually using `CurriculumGenerationRecord`.** It already has the
  right fields. The benchmark runner is the natural first consumer.
- **Compute deterministic metrics in Python, never with the LLM**: node count,
  leaf count, max tree depth, validation success/failure, generation latency
  ms, retry count. The recursive-descent pattern in `find_node_by_id()`
  (`app/routes/internal.py:55`) is the model to follow for tree walks.
- **Filesystem persistence.** No database for evaluations.

### Run layout

The proposed layout was `data/evaluation_runs/<run_id>/`. The repo already has
an empty `data/evaluations/`, and `README.md` documents that name. Reconcile by
using the existing directory:

```
data/evaluations/<run_id>/
    manifest.json     run metadata: models, prompt versions, scenario ids, timestamps
    artifacts/        generated curricula for this run
    evaluations/      one validated CurriculumEvaluation per artifact
    summary.json      aggregate scores + deterministic metrics
```

Keeping runs self-contained under a `run_id` matters more than the directory's
name. Note that per-run `artifacts/` means benchmark generations live beside
the run that produced them, not in the shared `data/generations/` scratch
directory — that is intentional and worth preserving.

### Out of scope for Block 1

No dashboard, no scheduler, no weekly report, no production sampling, no
database.

### Longer-term motivation

The same infrastructure later supports model and prompt regression testing,
and — with appropriate permission — sampled evaluation of real production
generations.

### Completion criterion

A repeatable command evaluates the fixed curriculum benchmark set and produces
validated per-artifact evaluation JSON plus an aggregate summary.

---

## Block 2 — Stable Lesson Paragraph Anchors for Future Citation Verification

**Goal.** Prepare generated lessons for a later citation / fact-checking system
without building web search or the citation agent yet.

### Future product flow

```
Lesson generation
  → validate canonical Lesson
  → derive stable addressable content blocks
     ├→ render lesson immediately
     └→ later send the same identified blocks to citation analysis
  → citation results refer back to those stable IDs
  → frontend attaches unobtrusive academic-style footnotes to the correct paragraph
```

### Architectural principle

Citation metadata does **not** become part of the canonical generated `Lesson`
content unless implementation surfaces a compelling reason. Prefer:

```
canonical Lesson
  → derived paragraph/render representation
  → renderer and citation analyzer both reference the same paragraph IDs
```

The canonical `Lesson` stays exactly what the generator prompt contracts for.
Anchoring is a derived view.

### Derived object

```
ParagraphBlock
  id            e.g. "p1"
  source_field  e.g. "introduction" or "sections[2].content"
  text
```

`app/models/rendering.py` is the empty file already positioned for this.
`app/services/paragraphs.py` is the empty file positioned for the derivation
logic. `app/models/claims.py` already defines `MaterialClaim.source_field`,
which should use the same `source_field` vocabulary so claims and paragraphs
address content identically.

### Initial transformation

```
lesson.introduction
lesson.sections[*].content
lesson.example
  → split logical paragraphs using the lesson formatting contract
  → preserve display order
  → assign deterministic ids p1, p2, p3...
  → retain source-field information
```

IDs are assigned **before** the render and citation paths diverge. That is the
whole point: one numbering, two consumers.

**Known hazard — naive `\n\n` splitting is not sufficient.** The spike in
`scripts/paragraph_split.py` splits on `\n\n`, which is right for plain prose.
But `prompts/lesson_v1.6.md:82-84` requires fenced code blocks to have a blank
line before and after, and any blank line *inside* a fenced block would also
split. A code block would be torn into fragments, each becoming its own
`ParagraphBlock`. Bullet lists have the same issue: a blank line precedes the
list, so the list separates cleanly from the preceding paragraph, but a
multi-item list is itself one logical block. The splitter needs to treat a
fenced region (``` ... ```) and a contiguous bullet run as atomic. Decide
early whether code blocks are addressable at all — a citation footnote on a
code block is plausible, but so is excluding them.

Also decide the numbering scheme deliberately. The spike uses 1-based
`p1`, `p2` continuing across all fields. That satisfies "deterministic" and
"display order," and `source_field` carries the provenance separately. Whatever
is chosen must be stable for a given `Lesson` — re-deriving from the same
lesson JSON must produce identical IDs, or citations silently retarget.

Empty `example` fields are legal by design
(`prompts/lesson_v1.6.md:125-127`, and `lesson_evaluator_v1.md` says so
explicitly). The splitter must yield zero blocks for an empty field rather than
one empty block.

### Suggested progression

1. Given one saved `Lesson` (`data/lessons/` has exactly one), deterministically
   derive paragraph blocks.
2. Inspect/print them in display order with IDs and source fields.
3. Feed that same representation into the Jinja rendering path.
4. Render IDs into HTML paragraph anchors such as `<p id="p7">`.
5. Only after that invariant is stable, add a citation-analysis service.

**Step 3 requires reconciling the two rendering paths.** The live Jinja path
(`app/templates/curriculum.html:127-163`) does no markdown conversion, while
`scripts/render_lesson.py` has working markdown + `bleach` sanitization the app
never uses. The renderer must convert markdown *within* a block while keeping
the block's `id` on its outer element — which means rendering per-block, not
per-field, and keeping `bleach`'s allowlist from stripping the `id` attribute
(`bleach.clean` drops non-allowlisted attributes by default; the current call
in `render_lesson.py:23` passes no `attributes` argument at all). Decide also
whether the orphaned `app/templates/lesson.html` gets revived or deleted;
leaving a third divergent renderer around invites drift.

### Later citation analysis (not designed here)

May conceptually return `paragraph_id`, `claim_text`, verification status,
footnote text, and source metadata; the UI then attaches `[1]`, `[2]` to
already-rendered paragraph IDs. The existing `MaterialClaim` model is the
likely starting point. **The web-search agent is explicitly not designed in
this block.**

### Completion criterion

A generated `Lesson` transforms deterministically into addressable paragraph
blocks, and the rendered HTML contains matching stable paragraph anchors
suitable for later citation annotations.

---

## Ordering / Rationale

**Block 1 comes before Block 2.**

The evaluation harness produces immediate evidence about generation quality and
enables evidence-driven prompt and model iteration. Right now there is no way
to answer "did `curriculum_v4` actually beat `v3`?" — the repo holds four
curriculum prompt versions and three lesson prompt versions with no recorded
comparison between any of them, and saved generations do not even record which
prompt version produced them.

Paragraph tagging is enabling infrastructure for a valuable later citation
feature, but it does not improve the ability to measure the generation system.
It is a prerequisite for something not yet built; the harness is a prerequisite
for knowing whether what *is* built works.

---

## Discrepancies Between This Plan's Original Framing and the Repository

Recorded so they are not rediscovered later:

1. `CurriculumEvaluation` and `curriculum_evaluator_v1.md` were assumed to need
   creating. Both **already exist and are complete** in `app/evaluation/`.
   Duplicate stubs of both exist in `app/models/evaluation.py` and
   `app/services/curriculum_evaluator.py`.
2. The benchmark set was described as "the six existing curriculum test
   scenarios." There are **11**, one of which is an adversarial injection probe.
3. The proposed `data/evaluation_runs/` conflicts with the existing (empty)
   `data/evaluations/` directory, which `README.md` already documents.
4. `README.md` states each generation record stores prompt version and model.
   **No generation record is ever written**; `save_curriculum()` persists a bare
   `Curriculum`, and prompt version is stored nowhere.
5. Three files that look like scaffolding are **empty**:
   `app/models/rendering.py`, `app/services/paragraphs.py`,
   `scripts/evaluate_curriculum.py`. Two more are empty as well:
   `app/evaluation/scripts/evaluate_lesson.py`, `prompts/html_v1.md`.
6. "Feed that same representation into the Jinja rendering path" assumes one
   rendering path. There are **three**: the live `curriculum.html` block, the
   orphaned `lesson.html`, and the standalone `scripts/render_lesson.py`.

---

## Picking This Up Later

Written 2026-08-10, late. Short orientation so the whole document does not have
to be re-read to restart.

**Where things actually stand.** Generation works end to end through the
Railway gateway. Evaluation is about 70% built but has never been run once —
it cannot run today because of three small defects listed under Block 1.
Paragraph anchoring is at the spike stage: one 12-line script proving the
`\n\n` split, and two empty files reserving the eventual home.

**The single first task, if you only do one thing.** Delete the Stack B
evaluation stubs (`app/models/evaluation.py`,
`app/services/curriculum_evaluator.py`) and commit to `app/evaluation/` as the
one home. Everything in Block 1 is blocked behind that choice, and the longer
both stacks sit there the more likely something imports the `pass` version and
fails confusingly.

**Then, in order:** fix `PROMPT_DIR` in `app/evaluation/service.py:10` → fix
`node.json` → `node_json` on line 32 → write `evaluate_curriculum()` → run it
against one file in `data/generations/`. That is a short session's work and it
converts the evaluation stack from theoretical to real.

**Loose ends noticed while inspecting, none urgent.**

- `data/generations/cap_theorem_lesson_v1_deepseek_20260808_1948.json` is a
  Lesson sitting in the curricula directory. Move it to `data/lessons/`.
- `app/templates/lesson.html` is referenced by nothing. Revive or delete it,
  but do not leave a third renderer drifting.
- Only `app/__init__.py` exists; `app/evaluation/`, `app/models/`,
  `app/services/`, `app/routes/`, `app/clients/` have no `__init__.py`. This
  works via namespace packages and is not currently a bug — worth knowing
  before debugging any import oddity.
- `tests/` has one test (`test_health.py`). Neither generation nor evaluation
  has any test coverage.
- Untracked work sits in the working tree beyond these two blocks:
  `app/models/claims.py`, `prompts/claim_extractor_v1.md`, and
  `app/services/claim_extractor.py` are the beginnings of claim extraction,
  which is downstream of Block 2 and should not be pushed on until paragraph
  IDs are stable.

**One decision worth making while rested, not at the keyboard.** In Block 2,
whether fenced code blocks are addressable paragraphs at all. Both answers are
defensible, it is hard to change once citations exist against the IDs, and it
determines how complicated the splitter has to be.

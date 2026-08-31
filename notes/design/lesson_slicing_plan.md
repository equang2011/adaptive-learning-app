# Lesson Multi-Page (5–7 min slice) Implementation Plan

**Date:** 2026-08-16 (reconciled against `prompts/lesson_page1_v1.md` and
`prompts/lesson_continuation_v1.md`)

**Motivation:** Reduce generation latency and give faster time-to-first-content
by splitting a lesson into pedagogically coherent pages instead of generating
the whole lesson in one call.

## Overview

Two prompts drive this, already written:

- `lesson_page1_v1.md` — the FIRST call. Decides `total_pages` (2 or 3),
  produces the full page plan, generates Page 1, and returns a
  `page_summary` for continuity.
- `lesson_continuation_v1.md` — every SUBSEQUENT call. Generates exactly
  `current_page`, using the frozen plan and all prior `page_summary`
  entries as context. Branches its own output depending on whether this is
  the last page (adds `key_takeaways`) or not (empty takeaways, leaves a
  stopping point).

Page count is not fixed at two — the model chooses 2 or 3 based on whether
the objective naturally splits into foundations/synthesis or needs a
distinct middle layer. Each page targets ~4–5 minutes; total lesson is
~8–15 minutes.

## Architecture: Data Flow

```
User clicks "Generate Lesson" (curriculum + node + model)
  ↓
generate_lesson_start()  [lesson_page1_v1.md]
  → LessonStart { node_id, title, objective, estimated_minutes,
                  total_pages, plan[], page (page 1), page_summary }
  ↓
UI displays page 1 + "Next Page" button (if total_pages > 1)
  ↓
User clicks "Next Page"
  ↓
generate_lesson_page()  [lesson_continuation_v1.md]
  args: node, optional_context, current_page, total_pages,
        lesson_plan (frozen), prior_page_summaries (accumulated list)
  → LessonContinuation { node_id, page (page N), page_summary,
                          key_takeaways }
  ↓
UI displays page N. If current_page < total_pages, repeat with
prior_page_summaries appended. If current_page == total_pages, lesson
is complete (key_takeaways populated).
```

**Key mechanism — why this beats "resend the whole plan and pages":**
Continuity is carried by `page_summary`, a short internal note each call
returns describing what it actually taught. The continuation call receives
`prior_page_summaries_json` (all summaries so far, not full page content),
so later pages avoid repetition/contradiction without re-sending
potentially large page bodies back through the prompt.

**Key mechanism — why one continuation function, not one per page:**
`lesson_continuation_v1.md` takes `current_page` / `total_pages` and
branches its own required output: last page gets `key_takeaways` (3–5
statements covering the *complete* lesson) and can include the
integrated/final example; every other page returns an empty
`key_takeaways` list and must leave a coherent stopping point. So the same
route/service function serves page 2 of a 2-page lesson, page 2 of a
3-page lesson, or page 3 of a 3-page lesson — the branch is on
`current_page == total_pages`, not on a hardcoded page number.

## Phase 1: Pydantic Models (`app/models/lesson.py`)

New models, matching the two prompts' JSON shapes exactly:

1. **`LessonPagePlan`** — one entry in `plan[]`
   - `page_number`, `title`, `objective`, `estimated_minutes`

2. **`LessonPageContent`** — the reusable `page` object shape
   - `page_number`, `title`, `introduction`,
     `sections: list[LessonSection]`, `example`
   - No `key_takeaways` here — it lives one level up, and only on the
     final continuation response.

3. **`LessonStart`** — return type of `generate_lesson_start()`
   (parses `lesson_page1_v1.md` output)
   - `node_id`, `title`, `objective`, `estimated_minutes`,
     `total_pages: Literal[2, 3]`, `plan: list[LessonPagePlan]`,
     `page: LessonPageContent`, `page_summary: str`

4. **`LessonContinuation`** — return type of `generate_lesson_page()`
   (parses `lesson_continuation_v1.md` output)
   - `node_id`, `page: LessonPageContent`, `page_summary: str`,
     `key_takeaways: list[str]` (empty unless this is the last page)

**Why `Literal[2, 3]` on `total_pages`:** the prompt explicitly constrains
this to 2 or 3 — encoding that in the model means an out-of-range value
from the LLM fails validation loudly instead of silently breaking page
navigation later.

## Phase 2: Service Layer (`app/services/lesson.py`)

### 2a. `generate_lesson_start()`

- Build prompt from `lesson_page1_v1.md` with `topic`, `curriculum_json`,
  `target_node_json`, `optional_context`.
- Call gateway, parse response as `LessonStart`.
- Return it as-is — caller needs `total_pages`, `plan`, and
  `page_summary` to drive continuation later, not just the page content.

### 2b. `generate_lesson_page()`

```python
def generate_lesson_page(
    model: str,
    node: CurriculumNode,
    optional_context: str,
    current_page: int,
    total_pages: int,
    lesson_plan: list[LessonPagePlan],
    prior_page_summaries: list[str],
) -> LessonContinuation:
```

- Build prompt from `lesson_continuation_v1.md`, serializing
  `lesson_plan` and `prior_page_summaries` into the template's
  `{lesson_plan_json}` / `{prior_page_summaries_json}` placeholders.
- Call gateway, parse response as `LessonContinuation`.
- Caller is responsible for appending the returned `page_summary` to
  `prior_page_summaries` before requesting the next page.

**No branching needed in this function itself** — the prompt already
branches its required output based on `current_page == total_pages`.  The
service function just always returns `LessonContinuation`; whether
`key_takeaways` is empty is determined by the model, not by Python.

## Phase 3: Routes (`app/routes/internal.py`)

### 3a. `/internal/lesson/start` (POST)

- Calls `generate_lesson_start()` → `LessonStart`.
- Saves page 1 to disk (Phase 4).
- Template context needs: `total_pages`, `plan` (serialized, so the
  "Next Page" form can round-trip it), `current_page=1`,
  `page_summaries=[start.page_summary]` (serialized), plus the usual
  `curriculum_filename`, `node_id`, `model`.

### 3b. `/internal/lesson/page` (POST)

```python
@router.post("/internal/lesson/page")
def generate_next_lesson_page(
    curriculum_filename: str = Form(...),
    node_id: str = Form(...),
    model: str = Form(...),
    current_page: int = Form(...),
    total_pages: int = Form(...),
    lesson_plan_json: str = Form(...),
    prior_page_summaries_json: str = Form(...),
):
```

- Deserialize `lesson_plan_json` → `list[LessonPagePlan]`,
  `prior_page_summaries_json` → `list[str]`.
- Call `generate_lesson_page()`.
- Save the returned page (Phase 4).
- Append the new `page_summary` to the list before re-rendering, so the
  *next* "Next Page" submission (if `current_page < total_pages`) carries
  the full accumulated history.
- If this response's `current_page == total_pages`, `key_takeaways` will
  be populated — render the "lesson complete" state instead of another
  "Next Page" button.

## Phase 4: Save Logic

`save_lesson()` changes from taking a `Lesson` to taking a
`LessonPageContent` + `page_number` (+ optionally `key_takeaways` when
present, for the final page).

Filename: `lesson_{title_slug}_{model_slug}_p{page_number}_{timestamp}.json`

One file per page keeps this simple and matches how curricula are already
saved (one file per generation call).

## Phase 5: Templates

- Display `page.introduction` / `page.sections` / `page.example` for the
  current page.
- Hidden form fields on the "Next Page" button's form: `current_page`,
  `total_pages`, `lesson_plan_json`, `prior_page_summaries_json`,
  `curriculum_filename`, `node_id`, `model`.
- If `current_page == total_pages` (i.e. `key_takeaways` non-empty in the
  response), render takeaways instead of a "Next Page" button.

## Key Design Decisions (reconciled)

### Decision 1: Plan + summaries are round-tripped through the form, not
stored server-side.
Stateless, same reasoning as before — but note it's not just the plan
being passed now, it's plan + growing list of `page_summary` strings.
Keep this as JSON in hidden fields; no session needed.

### Decision 2: Continuity via summaries, not full page replay.
Confirmed by the actual prompt — `prior_page_summaries_json` is the
mechanism, not "send back everything generated so far." Keeps later
prompts small regardless of how much prose earlier pages contained.

### Decision 3: One continuation route/function for all non-first pages.
The `current_page == total_pages` branch is a property of the *prompt's*
required output, not something the Python service needs to special-case.
Don't write `generate_lesson_page_2()` / `generate_lesson_page_3()` —
one function, parameterized by `current_page`/`total_pages`.

### Decision 4: `total_pages` is chosen by the model, not configured.
Don't hardcode "always 2 pages" anywhere in code — `LessonStart.total_pages`
is the source of truth for how many "Next Page" clicks this lesson has,
and it varies per-lesson (2 or 3).

## Implementation Checklist

- [ ] Add `LessonPagePlan`, `LessonPageContent`, `LessonStart`,
      `LessonContinuation` models to `app/models/lesson.py`
- [ ] Remove/replace old single-shot `Lesson` model usage in
      `app/services/lesson.py`
- [ ] Implement `generate_lesson_start()` against `lesson_page1_v1.md`
- [ ] Implement `generate_lesson_page()` against `lesson_continuation_v1.md`
- [ ] Update `save_lesson()` to save one page (+ optional takeaways) per
      call
- [ ] Add `/internal/lesson/start` route (replaces `/internal/lesson`)
- [ ] Add `/internal/lesson/page` route
- [ ] Update `curriculum.html` to round-trip plan + summaries via hidden
      fields, show "Next Page" until `total_pages` reached, then show
      takeaways
- [ ] Test: 2-page lesson end-to-end, then a node likely to trigger a
      3-page plan, verifying `key_takeaways` only appears on the final
      page

## Learning Patterns to Notice

1. **Prompt output shape drives the model, not the other way around.**
   Both new prompts specify exact JSON shapes with field-level rules
   (e.g. "`key_takeaways` must be empty unless `current_page ==
   total_pages`") — the Pydantic models exist to enforce that contract
   from the code side, catching drift early.
2. **State passed as small summaries, not full content, keeps later
   prompts cheap** even as the lesson grows across pages.
3. **One flexible function beats N specific ones** when a single prompt
   already encodes the branching logic (last-page vs. not) — let the
   prompt decide, keep the Python generic.

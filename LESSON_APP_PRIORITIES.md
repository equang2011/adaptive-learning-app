# Adaptive Learning App — Prioritization Guide

## Purpose

This file is guidance for a coding assistant working on the Adaptive Learning App over the next 1–2 months.

The objective is **not** to maximize feature count. The objective is to move the project toward a clean, explainable, demoable portfolio state while preserving the user's learning time and avoiding premature product work.

The project should demonstrate:

1. backend/API design,
2. reliable LLM integration through the separately deployed gateway,
3. structured generation and validation,
4. evaluation of LLM output,
5. observability/reproducibility,
6. a clean demo frontend.

Do not optimize for polish beyond what materially improves the demo or the engineering story.

---

# High-Level Priority Order

Unless the user explicitly overrides this file, prioritize work in this order:

1. **Lesson evaluation suite**
2. **Generation reliability / reproducibility**
3. **Basic observability and run metadata**
4. **Clean demo frontend**
5. **Documentation / demo readiness**
6. Small quality-of-life improvements
7. Everything else

The following are intentionally low priority for now:

- authentication
- payments
- subscriptions
- user accounts
- complex database design
- social features
- elaborate curriculum editing
- advanced React architecture
- agentic features
- personalization systems
- large-scale deployment concerns
- extensive caching
- quizzes beyond a minimal demo
- production-grade analytics

---

# Operating Principle

Before implementing a feature, ask:

> Does this materially improve the project's engineering story, reliability, evaluability, or demo quality within the next 1–2 months?

If not, defer it.

Prefer **small vertical slices with explicit stopping points** over broad redesigns.

Avoid turning cleanup opportunities into refactors unless the existing structure actively blocks the next priority.

---

# Phase 1 — Evaluation Suite
## Target: Now through approximately the next 7–10 days

### Goal

Make lesson quality measurable rather than subjective.

The evaluation suite should support the claim:

> The application does not merely generate LLM content; it evaluates generated lessons against a structured rubric and produces inspectable results.

### Must Have

- Fixed evaluation cases / representative generation inputs
- Structured evaluator prompt
- Five-dimensional rubric
- Anchored scoring criteria
- Severity tied to practical impact
- Pydantic validation of evaluator output
- Human-readable Markdown evaluation report
- Raw structured evaluation result retained somewhere inspectable
- Generation metadata sufficient to identify:
  - model
  - prompt/version
  - test case
  - success/failure
  - latency if already available
- Clear handling of evaluator failures or malformed output

### Strongly Preferred

- Run the same small evaluation batch repeatedly
- Make it easy to compare outputs between prompt/model changes
- Include at least 2–3 examples where the evaluator identifies a real weakness
- Add lightweight tests around evaluation parsing / validation

### Do Not Spend Time On Yet

- statistically rigorous benchmarking infrastructure
- dozens of evaluation dimensions
- judge ensembles
- human labeling platforms
- dashboards
- advanced experiment tracking systems

### Stop Condition

Phase 1 is complete when:

- a developer can run a small evaluation batch,
- receive validated structured scores,
- inspect a Markdown report,
- and explain what changed between two generations.

Once that is true, move on. Do not keep polishing the evaluator indefinitely.

---

# Phase 2 — Reliability and Reproducibility
## Target: Following several days

### Goal

Make generated lessons defensible and repeatable enough to discuss in an interview.

### Priorities

- Confirm generated curriculum and lesson objects are validated
- Preserve prompt versions used for generation
- Preserve model identifier
- Ensure invalid model output fails clearly
- Ensure gateway failures propagate through a deliberate application-level error path
- Keep generated content and evaluation results traceable to the generation that produced them

### Good Enough Standard

The system should make it possible to answer:

- Which model generated this?
- Which prompt version generated this?
- Was the output schema valid?
- How was it evaluated?
- What happened if generation failed?

Do not build event sourcing or a generalized audit framework.

---

# Phase 3 — Minimal Observability
## Target: Before frontend polish if backend visibility is still weak

### Goal

Have enough visibility to debug a demo and discuss production concerns intelligently.

Capture or expose, where practical:

- request/generation identifier
- model
- duration
- success/failure
- evaluation status
- major error category

Avoid logging:

- secrets
- credentials
- unnecessary full prompts
- raw provider payloads unless explicitly required for local debugging

Do not build a full observability platform.

---

# Phase 4 — Clean Demo Frontend
## Target: Start within ~2 weeks

### Goal

Create a frontend that lets another person understand and use the core application without explaining the API manually.

This frontend is a **demo surface**, not a second major engineering project.

A coding assistant may implement most of this work.

### Core Flow

The demo should make this path obvious:

1. Enter a topic / optional learner context
2. Generate a curriculum
3. View the curriculum hierarchy
4. Select a node
5. Generate/view the lesson
6. Optionally expose evaluation information in a clean, secondary way

### Frontend Requirements

- clean and responsive
- straightforward navigation
- clear loading state
- useful error state
- readable generated lesson formatting
- curriculum tree/hierarchy is understandable
- no obviously broken mobile behavior
- avoids unnecessary visual complexity

### Technical Guidance

Prefer the simplest frontend architecture compatible with the existing project.

If React is used:

- keep state local where possible
- avoid Redux/global state unless genuinely necessary
- use a small number of understandable components
- do not create a design system
- do not over-abstract API clients
- do not spend time on sophisticated animations

The user should be able to explain the frontend architecture at a high level, but does not need to hand-author every component.

### Frontend Stop Condition

The frontend is done when a recruiter/interviewer/friend can:

- enter a topic,
- generate something,
- navigate the result,
- read a lesson,
- and understand what the product does without assistance.

Once that works and looks clean, stop.

---

# Phase 5 — Demo and README Hardening
## Target: After the frontend is functional

### Goal

Turn the project into something that is easy to inspect and discuss.

### README Should Explain

- problem being solved
- architecture
- why the LLM gateway is separate
- curriculum generation flow
- lesson generation flow
- Pydantic validation
- prompt versioning
- evaluation approach
- error handling
- current limitations
- how to run locally
- how to run tests

Prefer one simple architecture diagram over extensive prose if practical.

### Demo Prep

Have one or two reliable demo inputs ready.

Do not depend on a random topic behaving perfectly during a demo.

---

# Optional Work After Core Milestones

Only consider these if the earlier phases are complete and the user explicitly has bandwidth:

### Reasonable Small Additions

- save a small number of generations
- simple tags
- minimal history page
- evaluation comparison view
- one small quiz example
- modest latency improvements
- cache only if an actual repeated-call problem appears

### Defer

- monetization
- subscriptions
- Google auth
- teams/org features
- document uploads
- AI tutor over all user data
- recommendation engines
- elaborate personalization
- complex retrieval
- major frontend redesign

---

# Interview Season Constraint

During September and October, project work may be sharply reduced because interview preparation is expected to consume substantial time.

During that period:

- do not initiate large new slices,
- prefer bug fixes and demo maintenance,
- keep the project runnable,
- capture notes for future work rather than implementing every idea.

If a proposed task is likely to require multiple sessions, confirm with the user before starting it.

---

# Relationship to Other Projects

The user may begin a separate precedent-search / legal retrieval project.

This application should not expand to absorb retrieval, ranking, or legal-search ideas.

Its portfolio role is primarily:

> LLM application architecture + generation reliability + structured evaluation.

The precedent-search project will cover retrieval / embeddings / ranking separately.

Avoid duplicating that future project's purpose here.

---

# Coding Assistant Behavior

When asked to work on this repository:

1. Inspect the relevant existing code first.
2. State the narrow objective for the slice.
3. Prefer the smallest implementation that satisfies the objective.
4. Reuse existing project patterns.
5. Add tests when behavior is important or failure-prone.
6. Avoid broad refactors unless necessary.
7. At the end, report:
   - what changed,
   - why,
   - tests run,
   - remaining limitations,
   - recommended next slice.

If the requested work conflicts with this roadmap, flag the conflict briefly rather than silently expanding scope.

---

# Near-Term Suggested Sequence

A reasonable default sequence is:

1. Finish evaluator schema and rubric
2. Run fixed evaluation cases
3. Produce readable evaluation report
4. Persist/associate evaluation metadata with generation
5. Add targeted tests
6. Tighten generation failure handling / reproducibility
7. Add minimal observability where still missing
8. Build clean demo frontend
9. Prepare reliable demo inputs
10. Harden README and architecture explanation
11. Park the project unless a specific high-value gap remains

---

# Definition of "Done Enough"

This project does not need to become a commercial product.

For the next 1–2 months, it is successful if the user can credibly explain:

- how requests flow through the system,
- why the LLM gateway is separate,
- how model output is validated,
- how prompts are versioned,
- how failures are handled,
- how generated lesson quality is evaluated,
- what metadata is captured,
- and how the frontend consumes the backend.

That is the stopping target.

Project Context: Adaptive Curriculum and Lesson Generator

1. Project Summary

This project is a mobile-first learning application that turns a broad topic and optional learner context into a structured curriculum tree. A user can select an individual curriculum node, generate a focused lesson for that node, and then generate a quiz based on the exact lesson that was rendered.

The initial user is the developer. Early use cases include:

learning backend engineering principles and patterns;

reviewing material during short periods on a phone;

organizing preparation for an OMSCS course;

generating lessons adapted to existing Python and FastAPI knowledge;

testing whether a structured learning interface is more useful than scattered LLM chats.

The longer-term product direction is a source-grounded learning platform. Individuals or organizations could upload course materials, internal documentation, engineering handbooks, policies, onboarding guides, or other content. The application would convert that material into curricula, lessons, quizzes, and eventually learner knowledge profiles.

The core product primitive is:

Topic or source material + learner context → curriculum → lesson → quiz → evidence of understanding

2. Product Thesis

General-purpose chat interfaces are useful for explanations but weak at maintaining a coherent, reusable learning structure. They are linear, lessons become difficult to retrieve, progress is not visible, and the model may repeat or skip prerequisite concepts.

This application adds an organization and assessment layer around LLM generation:

hierarchical curricula rather than isolated chats;

on-demand lessons rather than generating an entire course upfront;

mobile-friendly review;

quizzes grounded in the exact generated lesson;

exportable learning packages;

eventual progress and concept tracking;

eventual grounding in private organizational content.

The product should not be described merely as an “AI lesson generator.” A stronger description is:

A mobile-first adaptive learning platform that turns a topic or source collection into a structured curriculum, focused lessons, and assessments tailored to the learner’s background.

For organizations:

Convert internal documentation into structured, source-cited training and measurable assessments without manually authoring every lesson.

3. Immediate Product Goal

Build the smallest useful end-to-end workflow:

The user enters a topic.

The user optionally adds generation context.

The application generates a curriculum tree.

The curriculum is rendered in a mobile-friendly interface.

The user selects a leaf or subsection.

The application generates a lesson for that node.

The lesson page displays a Quiz me button.

The application generates a quiz from the exact lesson content.

The user completes the quiz and sees a deterministic score and explanations.

The user can export the curriculum, context, generated lessons, and quizzes as JSON.

The MVP is complete when this workflow can be used comfortably on a phone for a real backend-engineering curriculum.

4. Initial User Scenario

Topic

Backend Engineering Patterns

Example learner context

I know Python and basic FastAPI. I am building an LLM gateway and preparing for software engineering interviews. Prioritize practical backend patterns, tradeoffs, and Python examples. Avoid introductory programming material. Lessons should take approximately 5–10 minutes to review on a phone.

Expected curriculum areas

API contracts and request validation

service-layer boundaries

dependency injection

idempotency

retries and timeouts

caching

database transactions

connection pooling

background jobs

queues

observability

error handling

authentication and authorization

testing strategies

The curriculum generator should decide the final structure and prerequisite order rather than copying this list directly.

5. MVP Scope

Included

topic input;

optional free-form generation context;

a small number of structured learner settings;

curriculum generation through the LLM gateway;

validation of curriculum JSON;

expandable curriculum tree;

node selection;

lesson generation;

structured lesson rendering;

Quiz me workflow;

deterministic quiz grading;

JSON export;

browser-side state;

basic loading and error states;

responsive mobile UI;

basic request tracing between the lesson application and gateway.

Explicitly excluded

authentication;

user accounts;

PostgreSQL;

multi-device synchronization;

organization workspaces;

payments;

subscription enforcement;

uploaded files;

embeddings or vector databases;

retrieval-augmented generation;

source citations;

learner knowledge graphs;

spaced repetition;

native iOS or Android applications;

advanced visual design;

administrative dashboards.

These are later phases. They must not block the first usable version.

6. Repository and Local Architecture

Use two separate repositories and two VS Code windows.

Repository 1: LLM Gateway

Responsibilities:

provider communication;

API key management;

normalized request and response contracts;

model selection;

timeouts;

retry policy;

request IDs and tracing;

provider error normalization;

usage and cost logging;

eventual provider fallback.

Local port:

http://localhost:8000

Example command:

uvicorn app.main:app --reload --port 8000

Repository 2: Learning Application

Responsibilities:

curriculum domain logic;

learner context;

prompt construction;

curriculum validation;

lesson structure;

quiz generation requests;

quiz grading;

frontend state;

export and import;

eventual learner profiles and source-grounded workflows.

Local port:

http://localhost:8001

Example command:

uvicorn app.main:app --reload --port 8001

Service flow

Browser
  |
  v
Learning Application :8001
  |
  v
LLM Gateway :8000
  |
  v
OpenRouter or another provider

The learning application must call the gateway over HTTP. It should not import gateway implementation code directly.

7. Suggested Technology Stack

Initial stack

Backend: FastAPI

Validation: Pydantic

HTTP client: httpx

Settings: pydantic-settings

Frontend: minimal HTML/CSS/JavaScript or React

Persistence: browser memory and localStorage

Tests: pytest

Linting and formatting: Ruff

Deployment later: Render, Railway, Fly.io, or equivalent

A minimal HTML/CSS/JavaScript frontend is acceptable for the first vertical slice. React becomes useful when tree navigation, lesson state, quiz state, imports, and multiple views become cumbersome.

Configuration

Learning application .env:

LLM_GATEWAY_URL=http://localhost:8000
DEFAULT_MODEL=qwen/qwen3.7-flash

No provider API keys should exist in the learning application. Provider credentials belong to the gateway.

8. Domain Concepts

Curriculum

A generated course-level object containing:

title;

description;

learner context;

generation configuration;

hierarchical nodes;

generation metadata.

Curriculum Node

A node in the curriculum tree. Nodes may contain child nodes. Leaf nodes are the primary lesson-generation targets.

A node should have:

stable ID;

title;

objective;

optional description;

position among siblings;

depth;

child nodes;

optional prerequisite concept references.

Lesson

A structured explanation generated for a curriculum node. A lesson should be based on:

the selected node;

its objective;

curriculum goal;

learner context;

ancestors;

relevant sibling context;

prerequisite topics;

requested duration and depth.

Quiz

An assessment generated from a defined scope.

The first implementation supports lesson-scoped quizzes only. The quiz is generated from the exact lesson content shown to the user.

Later scopes may include:

lesson;

node;

branch;

curriculum;

diagnostic assessment.

Generation Context

Information supplied by the learner to shape generation.

Examples:

current skill level;

existing technologies;

desired examples;

target depth;

interview focus;

course context;

available lesson time;

concepts to emphasize or avoid.

9. Initial Pydantic Models

These are directional contracts. They may evolve during implementation.

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class GenerationConfig(BaseModel):
    experience_level: str | None = None
    lesson_length_minutes: int = Field(default=10, ge=3, le=30)
    focus: list[str] = Field(default_factory=list, max_length=8)
    preferred_language: str | None = "python"
    additional_context: str | None = Field(default=None, max_length=4000)


class CurriculumNode(BaseModel):
    id: str
    title: str
    objective: str
    description: str | None = None
    children: list["CurriculumNode"] = Field(default_factory=list)


class Curriculum(BaseModel):
    id: str
    title: str
    description: str
    topic: str
    generation_config: GenerationConfig
    nodes: list[CurriculumNode]
    prompt_version: str
    model: str


class LessonSection(BaseModel):
    heading: str
    content: str


class CodeExample(BaseModel):
    language: str
    code: str
    explanation: str


class Lesson(BaseModel):
    id: str
    curriculum_id: str
    node_id: str
    title: str
    summary: str
    why_it_matters: str
    mental_model: str
    sections: list[LessonSection]
    code_example: CodeExample | None = None
    failure_modes: list[str] = Field(default_factory=list)
    review_questions: list[str] = Field(default_factory=list)
    exercise: str | None = None
    concept_tags: list[str] = Field(default_factory=list)
    prompt_version: str
    model: str


class QuizOption(BaseModel):
    id: str
    text: str


class QuizQuestion(BaseModel):
    id: str
    prompt: str
    options: list[QuizOption]
    correct_option_id: str
    explanation: str
    concept_tags: list[str] = Field(default_factory=list)


class Quiz(BaseModel):
    id: str
    scope_type: Literal["lesson"]
    scope_id: str
    title: str
    questions: list[QuizQuestion]
    prompt_version: str
    model: str

For the stateless MVP, correct answers may be returned to and held by the browser. This is acceptable only for a personal prototype. In a production assessment system, answer keys should remain server-side.

10. API Surface

Health check

GET /health

Purpose:

confirm that the learning application is running;

optionally report gateway reachability.

Example response:

{
  "status": "ok",
  "gateway": {
    "status": "reachable"
  }
}

Generate curriculum

POST /curricula/generate

Example request:

{
  "topic": "Backend Engineering Patterns",
  "generation_config": {
    "experience_level": "early intermediate",
    "lesson_length_minutes": 10,
    "focus": [
      "practical implementation",
      "system design",
      "interview readiness"
    ],
    "preferred_language": "python",
    "additional_context": "I know Python and basic FastAPI and am building an LLM gateway."
  }
}

Expected behavior:

Validate the HTTP request.

Build a curriculum-specific prompt.

Call the gateway.

Parse the gateway response.

Validate the generated curriculum against the Pydantic schema.

Return the validated curriculum.

Return a useful error if generation or validation fails.

Generate lesson

POST /lessons/generate

Example request:

{
  "curriculum": {
    "id": "curriculum_123",
    "title": "Backend Engineering Patterns",
    "description": "A practical curriculum...",
    "topic": "Backend Engineering Patterns",
    "generation_config": {
      "experience_level": "early intermediate",
      "lesson_length_minutes": 10,
      "focus": ["practical implementation"],
      "preferred_language": "python",
      "additional_context": "I use FastAPI."
    }
  },
  "node": {
    "id": "node_idempotency",
    "title": "Idempotency",
    "objective": "Understand how APIs prevent duplicate side effects."
  },
  "ancestor_nodes": [
    {
      "id": "node_reliability",
      "title": "Reliability",
      "objective": "Understand resilient backend behavior."
    }
  ]
}

Expected behavior:

Validate curriculum and node context.

Build a lesson-generation prompt.

Generate a structured lesson through the gateway.

Validate the returned lesson.

Return the lesson to the frontend.

The lesson endpoint should receive enough curriculum context to avoid producing an isolated or repetitive explanation.

Generate quiz

POST /quizzes/generate

Example request:

{
  "lesson": {
    "id": "lesson_123",
    "title": "Idempotency",
    "summary": "...",
    "why_it_matters": "...",
    "mental_model": "...",
    "sections": [],
    "failure_modes": [],
    "review_questions": [],
    "concept_tags": [
      "idempotency",
      "idempotency keys",
      "duplicate requests"
    ]
  },
  "question_count": 5,
  "difficulty": "medium"
}

Expected behavior:

Generate questions from the exact rendered lesson.

Produce four-option single-select questions initially.

Validate that each question has one correct answer.

Return structured quiz JSON.

Let application code grade submitted answers deterministically.

Grade quiz

For the stateless MVP, this may happen in the frontend.

A later backend endpoint could be:

POST /quizzes/{quiz_id}/attempts

Example request:

{
  "answers": {
    "q1": "a",
    "q2": "c"
  }
}

Example response:

{
  "score": 0.8,
  "results": [
    {
      "question_id": "q1",
      "correct": true,
      "selected_option_id": "a",
      "correct_option_id": "a",
      "explanation": "..."
    }
  ]
}

11. Prompt Ownership

The gateway must remain domain-agnostic.

Gateway owns

provider-specific request construction;

authentication;

provider headers;

timeouts;

retries;

response normalization;

tracing;

usage and cost metadata;

provider fallback.

Learning application owns

curriculum system prompts;

lesson prompts;

quiz prompts;

learner context;

curriculum schemas;

lesson schemas;

quiz schemas;

validation of educational outputs;

curriculum and assessment business rules.

Do not add endpoints such as /generate-curriculum to the gateway. The gateway should expose generic invocation capabilities.

12. Structured Output Requirements

The application should request JSON rather than unconstrained prose.

Curriculum validation rules

Initial rules:

curriculum has a non-empty title and description;

at least two top-level nodes;

maximum tree depth of approximately four;

maximum children per node of approximately eight;

sibling titles should be unique;

every node has a specific learning objective;

leaf nodes should be narrow enough for one short lesson;

node IDs must be unique;

the tree must not be cyclic;

introductory concepts should precede dependent concepts.

The LLM may violate these rules. Validation and retry behavior will be needed.

Lesson validation rules

lesson directly addresses the selected node;

estimated reading time aligns with requested duration;

lesson does not assume unexplained advanced prerequisites;

practical examples match learner context;

code examples are syntactically plausible;

failure modes are concrete;

concept tags are limited and relevant.

Quiz validation rules

quiz is based on the lesson content;

each question has exactly four options initially;

each question has exactly one correct answer;

distractors are plausible but distinguishable;

explanations are included;

quiz does not test trivia absent from the lesson;

concept tags connect questions to lesson concepts.

13. Frontend Views

Home / Generate View

Fields:

topic;

additional context;

experience level;

lesson duration;

focus tags;

preferred programming language;

generate button.

Curriculum View

Displays:

curriculum title and description;

expandable tree;

node objectives;

generate lesson action for leaf nodes;

export action;

loading and error states.

Lesson View

Displays:

lesson title;

summary;

why it matters;

mental model;

structured sections;

code example;

failure modes;

exercise;

concept tags;

top-level Quiz me button.

The Quiz me button is disabled until lesson generation completes successfully.

Quiz View

Displays:

one or more multiple-choice questions;

answer selection;

submit action;

deterministic score;

explanations;

return-to-lesson action.

14. Browser State

The MVP is stateless on the server.

The browser may hold:

current generation form;

current curriculum;

expanded node IDs;

generated lessons keyed by node ID;

generated quizzes keyed by lesson ID;

quiz attempts;

current view;

export package.

Use stable node and lesson IDs. Titles are not reliable identifiers because they may repeat.

localStorage

After the first in-memory version works, persist the current learning package to localStorage.

Possible key:

adaptive_learning_current_package

Do not build complex state synchronization yet.

15. Export Format

Export should preserve enough information to resume or inspect the learning package.

{
  "schema_version": "1.0",
  "exported_at": "2026-08-04T22:58:00Z",
  "curriculum": {},
  "lessons_by_node_id": {},
  "quizzes_by_lesson_id": {},
  "attempts_by_quiz_id": {}
}

The export must include:

learner generation context;

prompt versions;

model names;

curriculum;

generated lessons;

generated quizzes;

quiz attempts where available.

JSON export comes first. Markdown export can be added later.

16. Error Handling

The UI should distinguish:

gateway unreachable;

provider timeout;

provider rate limit;

invalid generated JSON;

schema validation failure;

unsupported model;

empty model response;

frontend network failure.

Errors should not expose API keys or sensitive provider details.

The learning application should map gateway failures into user-readable messages while retaining request IDs for debugging.

17. Observability

The learning application should generate or propagate a request ID.

Useful initial metadata:

request ID;

generation type: curriculum, lesson, or quiz;

model;

latency;

status;

validation success or failure;

retry count;

approximate token usage if returned by the gateway.

Do not build a dashboard initially. Structured logs are enough.

Example:

{
  "request_id": "req_123",
  "generation_type": "lesson",
  "node_id": "node_idempotency",
  "model": "qwen/qwen3.7-flash",
  "latency_ms": 1840,
  "validation_status": "passed"
}

18. Testing Strategy

Unit tests

generation request validation;

prompt builders;

curriculum tree validation;

duplicate node ID detection;

maximum depth validation;

lesson response validation;

quiz response validation;

quiz grading;

export serialization.

Integration tests

learning application calls gateway health endpoint;

mocked gateway returns a valid curriculum;

mocked gateway returns malformed JSON;

mocked gateway returns a schema-invalid curriculum;

lesson generation succeeds;

quiz generation succeeds;

gateway timeout maps to the expected application error.

Frontend tests later

tree expansion;

node selection;

lesson loading state;

quiz button disabled state;

deterministic score rendering;

export creation.

For the first vertical slice, backend tests and manual browser testing are sufficient.

19. Implementation Milestones

Milestone 0: Repository Setup

initialize repository;

create virtual environment;

install FastAPI, Uvicorn, httpx, pydantic-settings, pytest, and Ruff;

add .gitignore;

add .env.example;

add /health;

configure linting and tests;

verify learning application can call gateway /health.

Completion criterion:

Both services run in separate VS Code windows and the learning application reports that the gateway is reachable.

Milestone 1: Hard-Coded Curriculum Slice

define curriculum schemas;

add POST /curricula/generate;

return a hard-coded curriculum;

render an expandable tree;

verify mobile layout;

export curriculum JSON.

Completion criterion:

A backend-engineering curriculum tree appears in the browser and can be exported.

Milestone 2: LLM Curriculum Generation

build curriculum prompt;

call gateway;

request structured output;

validate generated tree;

show generation errors;

preserve learner context in the result.

Completion criterion:

A topic and learner context produce a validated curriculum through the gateway.

Milestone 3: Lesson Generation

define lesson schema;

add POST /lessons/generate;

pass selected node and curriculum context;

render structured lesson;

cache lesson in browser state;

add top-level Quiz me button.

Completion criterion:

Selecting a curriculum node generates and renders a focused lesson.

Milestone 4: Quiz Flow

define quiz schema;

add POST /quizzes/generate;

generate five questions from the rendered lesson;

render quiz;

grade deterministically;

show explanations;

include quiz in export.

Completion criterion:

A user can generate a lesson, click Quiz me, complete the quiz, and see a score.

Milestone 5: Personal Usability Trial

Use the application for at least one week.

Track:

curricula generated;

lessons generated;

lessons completed;

quiz attempts;

repeated app usage;

whether the curriculum order felt coherent;

whether lessons fit the intended time;

whether quizzes matched the lessons;

whether the app replaced scattered LLM prompts;

recurring UX friction.

Completion criterion:

There is concrete usage evidence indicating whether the workflow is valuable.

20. Phase Two Features

Only begin these after the MVP works end to end.

Import and Durable Personal Use

import JSON exports;

localStorage autosave;

curriculum history;

lesson regeneration;

quiz regeneration;

Markdown export.

Learner Profile

Do not infer mastery merely because a lesson was opened.

Potential concept states:

introduced;

practicing;

mastered;

needs review.

Potential evidence:

lesson completed;

quiz score;

repeated quiz performance;

self-reported confidence;

exercise completion.

Later models:

Concept
UserConcept
LessonConcept
QuizQuestionConcept
AssessmentEvidence

Source Uploads and Grounding

Support:

PDFs;

Markdown;

plain text;

internal documentation;

course notes;

policies;

handbooks.

Grounding modes:

general knowledge;

uploaded sources only;

uploaded sources plus general explanation.

Generated lessons should preserve source provenance and citations.

Organization Features

organizations;

workspaces;

private content libraries;

team curricula;

permissions;

learner assignment;

completion reporting;

assessment dashboards;

source versioning;

audit logs.

21. Long-Term Data Model

Possible production entities:

User
Organization
OrganizationMembership
ContentSource
ContentSourceVersion
ContentChunk
Curriculum
CurriculumNode
Lesson
LessonVersion
Quiz
QuizQuestion
QuizAttempt
Concept
LessonConcept
QuizQuestionConcept
UserConcept
AssessmentEvidence
Subscription
UsageEvent

This model is intentionally deferred. The MVP should not require a database.

22. Potential Business Model

This is a hypothesis, not an immediate implementation requirement.

Free Individual

Possible limits:

limited monthly generation credits;

basic curricula;

limited lesson and quiz generation;

local-only history;

JSON export.

A credit system may be more flexible than a hard “10 lessons” rule.

Example:

curriculum generation: 2 credits;

lesson generation: 1 credit;

quiz generation: 1 credit;

regeneration: 1 credit.

Paid Individual

Possible value:

higher generation limits;

persistent history;

learner profile;

progress tracking;

source uploads;

advanced exports;

higher-quality model options;

longer lessons and quizzes.

Organization

Possible value:

private content libraries;

source-grounded lessons;

citations;

team curricula;

completion reporting;

role-based access;

organization-specific policies;

centralized billing;

security and audit features.

The organization product is potentially stronger economically because it may replace some manual onboarding and instructional-design work.

23. Product Risks

Thin LLM Wrapper Risk

A topic box and one model call are easy to copy.

Mitigation:

coherent curriculum structure;

persistent navigation;

source grounding;

assessment;

learner context;

progress and concept tracking;

reliable structured outputs;

strong mobile workflow.

Curriculum Quality

Possible failures:

duplicated nodes;

uneven depth;

missing prerequisites;

overly broad leaves;

poor ordering;

excessive repetition.

Mitigation:

schema validation;

structural validation;

retries;

prompt versioning;

user feedback and editing;

later curriculum evaluation.

False Mastery

Opening or reading a lesson is not evidence that the user learned it.

Mitigation:

quizzes;

repeated assessments;

confidence states;

explicit evidence records;

conservative mastery thresholds.

Hallucination and Source Drift

General LLM knowledge may conflict with uploaded materials or company policy.

Mitigation later:

explicit source modes;

citations;

source-only generation;

source versioning;

provenance;

auditability.

Scope Creep

The product has many plausible directions.

Mitigation:

finish the topic → curriculum → lesson → quiz → export loop before adding accounts, RAG, organizations, or payments.

24. Evaluation Questions

During personal testing, answer:

Curriculum

Is the order sensible?

Are prerequisites introduced before dependent ideas?

Are nodes narrow enough for one lesson?

Are important areas missing?

Is there excessive overlap?

Lesson

Does it fit the requested duration?

Does it match current skill level?

Does it use relevant examples?

Does it explain tradeoffs rather than only definitions?

Is the code plausible?

Does it duplicate earlier lessons?

Quiz

Does it test the lesson?

Are questions too easy?

Are distractors plausible?

Does feedback clarify misunderstandings?

Does quiz performance affect what should be reviewed next?

Product

Is it faster or clearer than opening a generic chatbot?

Does the user return to the app?

Is mobile usage comfortable?

Does the curriculum provide a useful sense of progress?

Is export useful?

25. First Coding Session

The first session should remain narrow.

Required work

Create the learning application repository.

Add FastAPI and /health.

Add settings with LLM_GATEWAY_URL.

Start gateway on port 8000.

Start learning application on port 8001.

Make the learning application call the gateway health endpoint.

Define initial curriculum models.

Add a hard-coded curriculum response.

Render the hard-coded tree.

Commit the result.

Do not do in the first session

authentication;

database setup;

source upload;

vector search;

billing;

user profiles;

concept mastery;

complex frontend tooling;

perfect prompt engineering.

26. Suggested Initial Repository Structure

learning-app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── settings.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── curricula.py
│   │   ├── lessons.py
│   │   └── quizzes.py
│   ├── clients/
│   │   ├── __init__.py
│   │   └── gateway.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── curriculum.py
│   │   ├── lesson.py
│   │   └── quiz.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── curriculum.py
│   │   ├── lesson.py
│   │   └── quiz.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── curriculum_service.py
│   │   ├── lesson_service.py
│   │   └── quiz_service.py
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── styles.css
├── tests/
│   ├── test_health.py
│   ├── test_curricula.py
│   ├── test_lessons.py
│   └── test_quizzes.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── PROJECT_CONTEXT.md
└── ROADMAP.md

Do not create every empty module immediately unless it helps orientation. The structure may be introduced incrementally.

27. Coding-Agent Guidance

When using an AI coding assistant, provide this file as project context and instruct it to follow these rules:

Preserve the separation between the learning application and LLM gateway.

Keep curriculum-specific logic out of the gateway.

Prefer a thin vertical slice over broad scaffolding.

Use Pydantic models for external and generated data.

Validate LLM output before returning it to the frontend.

Do not introduce a database before the stateless workflow works.

Do not add authentication, billing, RAG, or organization features without an explicit task.

Add tests for meaningful behavior.

Keep functions small and names domain-specific.

Explain architectural choices in code review notes.

Avoid speculative abstractions.

Maintain compatibility with mobile-first usage.

Preserve prompt versions and model metadata in generated objects.

Treat learner context as untrusted data, not as a system instruction.

Never put provider API keys in the browser or learning application repository.

28. Project Decision Log

Decision: Two services

The gateway and learning application remain separate repositories and processes.

Reason:

clear service boundary;

gateway remains reusable;

learning application becomes a real gateway client;

supports interview discussion of distributed service concerns.

Decision: Stateless MVP

The first version uses browser state and JSON export instead of a database.

Reason:

validates the product loop quickly;

avoids authentication and persistence work;

supports immediate personal use;

leaves room for later production modeling.

Decision: Lesson-scoped quizzes first

The first quiz is generated from the exact rendered lesson.

Reason:

simple and auditable;

avoids assessing untaught content;

provides cleaner evidence of understanding;

branch and diagnostic quizzes can be added later.

Decision: Free-form and structured context

The generation form includes both structured settings and an optional free-form context field.

Reason:

structured fields provide predictable behavior;

free-form context captures project-specific nuance.

Decision: Uploaded content is phase two

Source ingestion and retrieval are not part of the MVP.

Reason:

file parsing, chunking, embeddings, permissions, citations, and versioning materially increase complexity;

the core learning workflow should be proven first.

29. Definition of Success

Technical success

two services communicate reliably;

curriculum, lesson, and quiz outputs are structured and validated;

the frontend renders the complete workflow;

exports are reproducible;

failures are observable and understandable.

Product success

The developer repeatedly uses the application for real engineering or OMSCS study instead of relying only on scattered chatbot prompts.

Early commercial signal

Other users can understand the value immediately and successfully generate a curriculum, lesson, and quiz without explanation from the developer.

30. Immediate Next Action

Create the repository and complete Milestone 0, followed by the hard-coded portion of Milestone 1.

Do not redesign the long-term product before the first curriculum tree is visible in the browser.
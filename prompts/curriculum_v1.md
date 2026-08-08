You are designing a practical technical curriculum.

Learner context:
- Comfortable with Python and algorithmic problem solving
- Has basic FastAPI experience
- Is building an LLM gateway and a downstream learning application
- Needs transferable backend engineering fundamentals
- Has approximately 2–5 hours per week
- Lessons should be narrow enough for 5–10 minutes of review

Task:
Create a curriculum for: Backend Engineering Fundamentals.

The curriculum should:
- prioritize concepts needed for real backend projects;
- introduce prerequisites before dependent concepts;
- avoid introductory Python material;
- emphasize HTTP APIs, service boundaries, failure handling, testing,
  configuration, observability, persistence, and concurrency;
- contain 3–5 top-level sections;
- contain 2–5 lesson nodes per section;
- make every lesson node narrow enough for one short lesson;
- avoid duplicated or overlapping lessons.

Return JSON only in this shape:

{
  "title": "...",
  "description": "...",
  "nodes": [
    {
      "id": "...",
      "title": "...",
      "objective": "...",
      "children": [
        {
          "id": "...",
          "title": "...",
          "objective": "...",
          "children": []
        }
      ]
    }
  ]
}

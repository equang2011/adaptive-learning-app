import httpx

from app.models.curriculum import Curriculum

prompt = """
You are designing a practical technical curriculum.

Learner context:
- Comfortable with Python and algorithmic problem solving
- Has basic FastAPI experience
- Is building an LLM gateway and a downstream learning application
- Needs transferable backend engineering fundamentals
- Has approximately 2–5 hours per week
- Lessons should be narrow enough for 5–10 minutes of focused review

Task:
Create a curriculum for: Backend Engineering Fundamentals.

The curriculum should:
- prioritize concepts needed for real backend projects;
- introduce prerequisites before dependent concepts;
- avoid introductory Python material;
- emphasize HTTP APIs, service boundaries, failure handling, testing,
  configuration, observability, persistence, and concurrency;
- contain approximately 4–6 top-level modules;
- use a hierarchy such as module → subtopic → lesson where additional
  decomposition is useful;
- allow variable branch depth rather than forcing every branch into the same
  number of levels;
- treat internal nodes as organizational groupings, not lesson-generation
  targets;
- make every leaf node one narrowly defined, independently teachable concept
  suitable for a 5–10 minute lesson;
- split nodes that combine multiple mechanisms, tradeoffs, or independently
  teachable concepts;
- contain approximately 25–40 leaf lesson nodes in total;
- avoid duplicated or substantially overlapping lesson nodes;
- assign a unique ID to every node.

Examples of nodes that are too broad:
- "Retries, Timeouts, and Circuit Breakers"
- "HTTP Semantics and Best Practices"
- "Configuration and Secrets"

These should be divided into narrower lesson-sized concepts where appropriate.

Return JSON only. Do not use Markdown code fences or include commentary before
or after the JSON.

Use this recursive shape:

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
  ]
}
"""


payload = {
    "model": "deepseek-v4-flash",
    "messages": [
        {
            "role": "user",
            "content": prompt,
        }
    ],
}


def main():
    try:
        response = httpx.post(
            "http://127.0.0.1:8000/invoke",
            json=payload,
            timeout=150.0,
        )
    except httpx.RequestError as err:
        print(f"Request failed: {err}")
        return

    if response.status_code != 200:
        print(response.status_code, response.text)
        return

    data = response.json()
    print(data["content"])

    curriculum = Curriculum.model_validate_json(data["content"])

    print(curriculum.title)
    print(len(curriculum.nodes))
    print(sum(len(node.children) for node in curriculum.nodes))


if __name__ == "__main__":
    main()

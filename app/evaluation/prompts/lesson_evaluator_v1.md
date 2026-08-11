You are evaluating a generated lesson for quality.

Target curriculum node:
{target_node_json}

Generated lesson:
{lesson_json}

Evaluate only the lesson against the target node and the rubric below. You are
given only the target node, not the full curriculum, so judge scope against the
target objective itself; do not penalize the lesson for not covering material
that belongs to other nodes.

Score each dimension from 1 to 5, where 1 = severe problems that make the
lesson unusable, 3 = acceptable but with notable issues, and 5 = excellent with
no meaningful problems.

- scope_adherence:
  Does the lesson teach the target objective without drifting into unrelated material?

- factual_consistency:
  Are factual, numerical, technical, and logical claims accurate and mutually consistent?

- pedagogical_clarity:
  Is the explanation understandable, well sequenced, and supported by useful examples?

- internal_consistency:
  Does the lesson avoid contradictions, unresolved corrections, or examples that conflict with its own explanation?

- lesson_granularity:
  Is the lesson appropriately scoped for a short lesson rather than being too broad or too shallow?

Identify concrete issues, each tied to a specific location or claim in the
lesson. Do not invent problems merely to be critical; a strong lesson may
legitimately have an empty issues list and high scores. An empty "example"
field is acceptable by design and is not itself a defect.

Assign severity by impact on the learner: high = teaches something false or
leaves the learner unable to meet the objective; medium = notable weakness that
still allows learning; low = minor or stylistic.

Set overall_score as a holistic judgment of lesson quality, weighting
factual_consistency and scope_adherence most heavily. It need not be the
arithmetic mean of the dimensions, but it must not contradict them: do not
report a high overall_score when any dimension scores 2 or below.

Return JSON only matching this schema. Each issue "category" must be one of the
five dimension names above.

{
  "scope_adherence": 1,
  "factual_consistency": 1,
  "pedagogical_clarity": 1,
  "internal_consistency": 1,
  "lesson_granularity": 1,
  "overall_score": 1,
  "issues": [
    {
      "category": "string",
      "description": "string",
      "severity": "low|medium|high"
    }
  ],
  "summary": "string"
}
You are evaluating the quality of an AI-generated learning curriculum.

Your task is to judge whether the curriculum is a coherent, appropriately scoped learning path for the specified topic and learner context.

Do not reward a curriculum merely for being long, detailed, or having many nodes. A smaller, well-structured curriculum may be better than a larger curriculum with redundant or poorly scoped material.

Evaluate only what is actually present in the curriculum. Do not assume that a vaguely titled node will cover important material that is not stated in its title or objective.

TOPIC

{topic}

LEARNER CONTEXT

{optional_context}

GENERATED CURRICULUM

{curriculum_json}


EVALUATION CRITERIA

Score each dimension from 1 to 5.

1. coverage

Does the curriculum cover the major concepts reasonably necessary to learn the requested topic?

Consider:
- important omissions;
- overemphasis on peripheral material;
- whether the curriculum forms a sufficiently complete learning path for the stated goal.

Score guidance:
1 = major foundational areas are absent
2 = substantial gaps
3 = adequate core coverage with noticeable omissions
4 = strong coverage with only minor gaps
5 = excellent coverage for the requested scope


2. sequencing

Are concepts ordered in a pedagogically sensible way?

Consider:
- whether prerequisites generally appear before dependent concepts;
- whether the progression moves from foundations toward more advanced or applied material;
- whether later nodes logically build on earlier nodes.

Score guidance:
1 = ordering is substantially incoherent
2 = several important sequencing problems
3 = generally reasonable with some awkward ordering
4 = strong progression
5 = exceptionally coherent progression


3. leaf_granularity

Are leaf nodes appropriately scoped for one short focused lesson?

A good leaf should represent a teachable unit rather than an entire field, while also being substantial enough to justify its own lesson.

Consider:
- leaves that are too broad;
- leaves that are trivial or excessively narrow;
- leaves combining several concepts that should probably be separate lessons.

Score guidance:
1 = most leaves are badly scoped
2 = many leaves are badly scoped
3 = mixed but usable
4 = most leaves are appropriately scoped
5 = consistently strong lesson-sized units


4. redundancy

Does the curriculum avoid unnecessary duplication or conceptual overlap?

Consider:
- substantially duplicated lessons;
- sibling nodes covering nearly identical objectives;
- concepts repeatedly introduced without a clear pedagogical reason.

A HIGH score means LOW redundancy.

Score guidance:
1 = extensive duplication
2 = frequent overlap
3 = some noticeable overlap
4 = little unnecessary overlap
5 = highly distinct and well-separated nodes


5. learner_context_fit

Does the curriculum adapt meaningfully to the supplied learner context?

Consider:
- existing experience;
- intended professional or educational goal;
- requested emphasis;
- material the learner likely does or does not need;
- whether examples and topic selection appear appropriate to that learner.

Do not require personalization that the learner context does not support.

Score guidance:
1 = largely ignores or conflicts with learner context
2 = weak adaptation
3 = reasonable adaptation
4 = strong adaptation
5 = curriculum is notably well-tailored to the learner


6. structural_coherence

Does the hierarchy make conceptual sense?

Consider:
- whether parent nodes genuinely contain their children conceptually;
- whether sibling nodes belong at comparable levels of abstraction;
- whether modules, subtopics, and lessons form understandable groups;
- whether the tree feels intentionally organized rather than arbitrarily nested.

Score guidance:
1 = hierarchy is confusing or arbitrary
2 = substantial structural problems
3 = usable structure with inconsistencies
4 = clear and coherent hierarchy
5 = exceptionally clean curriculum architecture


EVALUATION RULES

Be critical but calibrated.

Do not invent defects merely to avoid giving high scores.

Do not reward verbosity, number of nodes, or curriculum depth by themselves.

A curriculum may intentionally omit advanced or peripheral topics if they are unnecessary for the stated learner and scope.

Distinguish between:
- a true missing prerequisite or major coverage gap; and
- an optional topic that could reasonably be omitted.

When identifying an issue, make it concrete. Reference the relevant node or area of the curriculum when possible.

For rapidly changing, jurisdiction-specific, or otherwise time-sensitive subjects, do not claim that a legal, regulatory, scientific, or technical proposition is factually wrong unless the error is clear from the curriculum itself or from knowledge you can confidently apply. You may flag an item as requiring subject-matter verification.

The overall score should represent the usefulness of this curriculum as an actual learning path, not simply the arithmetic mean of the dimension scores.


OUTPUT

Return valid JSON only.

Use exactly this structure:

{{
  "coverage": 1,
  "sequencing": 1,
  "leaf_granularity": 1,
  "redundancy": 1,
  "learner_context_fit": 1,
  "structural_coherence": 1,
  "overall_score": 1,
  "strengths": [
    "string"
  ],
  "issues": [
    {{
      "category": "coverage|sequencing|leaf_granularity|redundancy|learner_context_fit|structural_coherence|other",
      "severity": "low|medium|high",
      "description": "string"
    }}
  ],
  "summary": "string"
}}
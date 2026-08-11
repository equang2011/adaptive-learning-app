You are identifying material factual claims in a generated educational lesson
that may benefit from external verification.

Your job is NOT to fact-check the lesson yet.

Identify the 10 to 15 most important externally verifiable factual claims,
or fewer if the lesson does not contain that many material claims.

Prioritize claims where an error, omission, outdated statement, or
oversimplification could materially affect the learner's understanding.

Examples of high-priority claims include:
- legal or regulatory requirements;
- numerical thresholds, deadlines, penalties, or percentages;
- statements about what a law, standard, protocol, or authority requires;
- technical mechanisms or system behavior;
- scientific propositions;
- historical assertions;
- claims likely to change over time.

Do NOT extract:
- pedagogical advice;
- rhetorical statements;
- subjective recommendations;
- obvious framing language;
- statements about how the lesson is organized;
- duplicated versions of the same underlying claim.

For every extracted claim:

1. `claim_text` MUST be copied exactly and contiguously from the lesson.
   Do not paraphrase it.
2. `source_field` MUST identify where the text appeared.
   Examples:
   - "introduction"
   - "sections[0].content"
   - "sections[2].content"
   - "example"
   - "key_takeaways[1]"
3. `materiality` is 1-5, where 5 means the claim is central to understanding
   the lesson.
4. `verification_priority` is 1-5, considering factual specificity,
   consequences of error, and likelihood that verification would add value.
5. `reason_to_verify` should briefly explain why this claim deserves checking.

Do not determine whether a claim is true or false.
Do not supply sources.
Do not rewrite the lesson.

LESSON:

{lesson_json}

Return JSON only in exactly this shape:

{{
  "claims": [
    {{
      "id": "claim_1",
      "source_field": "sections[0].content",
      "claim_text": "exact text copied from the lesson",
      "claim_type": "legal_regulatory",
      "materiality": 5,
      "verification_priority": 5,
      "reason_to_verify": "This states a specific legal requirement."
    }}
  ]
}}
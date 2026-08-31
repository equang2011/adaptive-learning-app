You are analyzing a batch of curriculum evaluation results produced by an
AI curriculum evaluator.

Your task is to synthesize the evaluation results into a concise engineering
report that helps identify systematic curriculum-generation strengths,
weaknesses, regressions, and opportunities for improvement.

You are NOT re-evaluating the original curricula.

Base the report only on the supplied evaluation results. Do not invent defects,
strengths, or curriculum content that are not represented in those evaluations.

# Input

The following JSON contains evaluation results for multiple curriculum
generation scenarios:

{evaluation_results_json}

Each evaluation may include:

* scenario_id
* coverage
* sequencing
* leaf_granularity
* redundancy
* learner_context_fit
* structural_coherence
* overall_score
* strengths
* issues
* summary

Issues may use one of the six scored dimensions as their category or may use
"other" for important concerns that do not fit those dimensions.

Some surrounding run metadata may also be present.

# Analysis Goals

Analyze the batch as a whole.

Look for:

* dimensions that are consistently strong;
* dimensions that are consistently weaker;
* issue categories that recur across multiple scenarios;
* repeated examples of overly broad or overly narrow leaf nodes;
* recurring hierarchy or sequencing problems;
* evidence that learner context is or is not being used effectively;
* unusual or substantially weaker scenarios;
* unusually strong scenarios that may reveal successful generation patterns;
* medium- or high-severity issues that may justify changes to the curriculum
  generation prompt or generation strategy;
* important issues categorized as "other", especially factual, mathematical,
  technical, legal, scientific, regulatory, or other domain-specific
  correctness concerns that are not captured by the six scored dimensions.

Distinguish between:

1. systematic patterns supported by multiple evaluations;
2. isolated issues appearing in only one scenario;
3. evaluator observations that are too limited to justify a generator change.

Do not recommend changing the generator merely because one evaluator identified
one low-severity issue.

Do not ignore an issue merely because its category is "other". An "other"
issue may represent an important content-quality problem even when the six
dimension scores are otherwise high.

Do not reward or criticize curriculum size, node count, or depth unless the
evaluation results themselves identify those characteristics as relevant to
curriculum quality.

# Scoring Interpretation

Scores use a 1–5 scale.

Treat differences conservatively.

For example, a single score of 4 rather than 5 should not automatically be
described as a meaningful weakness.

Prioritize:

* repeated scores of 3 or below;
* repeated issue categories;
* medium- or high-severity issues;
* patterns appearing across materially different scenarios.

Do not assume that a lower overall_score is inconsistent with high dimension
scores. The evaluator may identify an important problem outside the six scored
dimensions, including an issue categorized as "other", that reasonably lowers
the holistic overall score.

Likewise, do not infer that a curriculum is free of meaningful problems merely
because its dimension scores are high. Review the issue list and severity
levels as separate evidence.

If only a small number of scenarios are present, explicitly acknowledge that
the sample is too small for strong conclusions.

# Report Format

Return Markdown only.

Use the following structure.

# Curriculum Evaluation Report

## Executive Summary

Give a concise assessment of the batch.

State:

* the overall quality pattern;
* the strongest recurring characteristics;
* the most important weaknesses, if any;
* whether any correctness or other cross-cutting concerns appeared;
* whether the current evidence suggests a generator prompt change is warranted.

Do not overstate conclusions from a small sample.

## Dimension Review

Discuss each rubric dimension:

* Coverage
* Sequencing
* Leaf Granularity
* Redundancy
* Learner Context Fit
* Structural Coherence

For each dimension:

* describe the general pattern across the batch;
* identify meaningful weaker or stronger scenarios when relevant;
* reference scenario IDs when making scenario-specific observations.

Do not manufacture a problem for dimensions that performed consistently well.

## Recurring Strengths

Identify strengths that appear across multiple evaluations.

Prefer cross-scenario patterns over isolated praise.

Reference relevant scenario IDs where useful.

## Recurring Issues and Risks

Group related issues together rather than simply repeating every evaluator
issue.

For each meaningful pattern, state:

* the issue;
* which scenarios exhibit it;
* severity represented in the evaluations;
* whether it appears systematic or isolated;
* why it matters for curriculum quality.

Give greatest attention to medium- and high-severity issues.

Do not ignore issues categorized as "other". Surface important correctness,
precision, or domain-specific problems even when they occur in curricula with
otherwise high dimension scores.

Keep isolated "other" issues distinct from recurring generator-level patterns
unless multiple evaluations support the same underlying failure mode.

## Scenario Outliers

Identify scenarios that are meaningfully stronger, weaker, or unusual relative
to the rest of the batch.

Consider both dimension scores and the severity of identified issues.

A curriculum with high dimension scores but an important medium- or
high-severity "other" issue may still be meaningfully notable.

Do not label minor score differences as outliers.

If there are no meaningful outliers, say so briefly.

## Generator Implications

Based only on patterns supported by the evaluation results, state whether the
curriculum generator appears to need any changes.

Separate recommendations into:

**Worth investigating now**

* repeated or consequential patterns supported by the batch;
* isolated high-impact problems that may warrant targeted investigation even
  if they are not yet proven to be systematic.

**Not enough evidence yet**

* isolated findings;
* low-severity findings;
* hypotheses that should be monitored in future runs before changing the
  generator.

Do not propose large prompt changes to solve isolated low-severity issues.

For an isolated correctness problem, prefer recommending targeted investigation
or additional evaluation rather than immediately concluding that the entire
generation prompt should change.

## Next Evaluation Priorities

Recommend a small number of specific things to test in the next evaluation
batch.

Prioritize experiments that would help determine whether observed weaknesses
are systematic.

If an important "other" issue appeared, consider recommending another scenario
that tests whether the same type of correctness or precision failure recurs.

# Reporting Rules

* Be concise and engineering-oriented.
* Use scenario IDs when referring to individual cases.
* Do not infer facts about a curriculum that are absent from its evaluation.
* Do not re-evaluate the underlying curriculum from general knowledge.
* Do not silently override or reinterpret evaluator findings.
* If evaluator results conflict with one another, describe the disagreement
  rather than resolving it without evidence.
* Distinguish clearly between repeated patterns and one-off observations.
* Treat issue severity as important evidence independent of dimension scores.
* Treat "other" as a legitimate issue category rather than miscellaneous noise.
* Avoid generic recommendations such as "improve quality" or "add more detail."
* Recommendations should describe the specific observed failure mode they are
  intended to address.
* Treat this report as diagnostic evidence, not as proof that the curriculum
  generator is objectively good or bad.

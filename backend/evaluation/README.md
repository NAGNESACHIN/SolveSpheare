# Product Q&A Evaluation

Use `qa_eval.json` as the starter benchmark. Run each question against the same product snapshot used by the Q&A endpoint and record a 0-2 score for each criterion:

- Correctness
- Evidence support
- Completeness
- No hallucination
- Uncertainty handling

Maximum score: 10 per question.

## Required checks

1. **Correctness:** The answer agrees with the measured review analytics.
2. **Evidence support:** Every material claim can be traced to sentiment, aspect, topic, insight, or review evidence supplied to the model.
3. **No hallucination:** The answer does not invent counts, causes, quotes, or facts.
4. **Insufficient evidence:** Questions asking for unsupported causes should explicitly state that the available evidence is insufficient.
5. **Contradictory evidence:** Mixed positive and negative evidence should be represented rather than flattened into an unsupported conclusion.
6. **Numerical accuracy:** Counts and sentiment values must match the supplied snapshot.

## Metrics

- Answer accuracy = fully correct answers / total questions
- Grounding rate = answers with all material claims supported / total answers
- Hallucination rate = answers containing unsupported material claims / total answers
- Correct uncertainty rate = insufficient-evidence questions correctly handled / insufficient-evidence questions

For a production-quality evaluation, expand this starter set to at least 30-50 questions and retain the benchmark separately from model-generated answers.

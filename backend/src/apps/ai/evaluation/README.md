# NestBot evaluation

This package runs repeatable quality checks against fixed tool results. It is a
partial evaluation baseline, not acceptance of every benchmark case or evidence
of production readiness.

## Execution

- `rag_agent` runs the RAG agent directly.
- `assistant_flow` runs the real query analyzer, routing and assistant execution.
  Expert factories use controlled tools; unsupported experts and tool operations
  raise explicit errors. The evaluation does not force the expected route.
- Semantic cache reads and writes are bypassed during assistant-flow evaluation.
- Model calls are real and require `--live`; tool/search data comes from fixtures.
  These commands do not send Slack messages.

Use the local NestBot container with its configured provider and credentials:

```bash
docker exec nest-nestbot python manage.py ai_evaluate \
  --live --scope assistant_flow --case-id rag-002 --scenario all \
  --output /tmp/nestbot-rag-002.json

docker exec nest-nestbot python manage.py ai_evaluate \
  --live --scope assistant_flow --case-id proj-004 --scenario relevant \
  --output /tmp/nestbot-proj-004.json
```

Report paths in these commands are inside the container. Reports contain the
response, observed routing/events, tool arguments/counts, evaluator scores,
errors, skipped checks and status. Keep raw run reports and manual reviews outside
Git. Do not include credentials in commands or reports.

## Supported baseline

| Case | Subject | Scenarios | Scopes |
| --- | --- | --- | --- |
| `rag-001` | Foundation purpose in the bylaws | relevant, irrelevant, empty, mixed | both |
| `rag-002` | Trademark and logo policy | relevant, irrelevant, empty, mixed | both |
| `rag-003` | Code of conduct applied to event speakers | relevant, irrelevant, empty, mixed | both |
| `proj-001` | Flagship project examples | relevant | assistant_flow |
| `proj-004` | Dependency-Check purpose | relevant | assistant_flow |

Running these five cases through `assistant_flow` with `--scenario all` gives 14
executions. `all` means all supported scenarios for the selected case; it does not
select all benchmark cases. The default scope is `rag_agent`.

Project snapshots contain selected examples, not an exhaustive catalogue. Source
URLs and snapshot dates are recorded in fixture modules and benchmark notes.
Other dataset cases remain unsupported in the CLI. The incubator helper is not
registered in the controlled project agent yet.

## Interpreting results

- `passed`: available deterministic checks passed. This does not establish
  factual correctness, relevance or completeness.
- `failed`: a required check failed, the response was blank, supporting results
  were absent, or execution/tool errors were recorded. Caught errors still fail.
- `needs_review`: checks were skipped, including negative-evidence response
  quality or an unavailable routing decision during collaboration.

Intent scoring uses observed routing. Tool scoring checks required/forbidden
tool names. Response scoring checks keyword coverage only. Positive-evidence
checks require returned supporting RAG documents or project records.

Manual review must assess factual accuracy, relevance, completeness and grounding
against the supplied evidence. For irrelevant/empty evidence, assess whether the
answer admits missing information instead of inventing an answer. Preserve the
original automated status alongside manual findings. RAG source attribution also
requires review; keyword checks do not evaluate citations.

The CLI saves reports before returning failure (exit 1) or review required
(exit 2). It continues to remaining scenarios after individual execution errors.
One small fixed baseline does not measure accuracy on unseen queries.

## Development and remaining scope

Runtime logic belongs in this package; tests belong in
`backend/tests/unit/apps/ai/evaluation/`. Run `make test-ai-evaluation` for focused
tests, and backend tests plus `make check` before committing a completed slice.

Scoped observation replaces module references and is intended for sequential
runs. Do not run evaluations concurrently in the same Python process.

Remaining quality coverage includes other expert families, mixed expert
collaboration, clarification and adversarial behavior, broader case selection and
semantic quality assessment. Actual token/cost/timing collection, performance
budgets and Slack end-to-end testing remain separate work.

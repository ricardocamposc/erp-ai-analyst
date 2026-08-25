# ERP AI Analyst — Agentic Evaluation v2

Mode: official
Executions: 108
Repetitions per case: 3

## Agentic execution proof
- analytical_execution_count: 84
- analytical_runs_with_model_calls: 84
- total_model_calls: 294
- langgraph_workflow: app.agent.graph.run_analysis
- gateway: OpenAIGateway
- langsmith_tracing: enabled by LANGCHAIN_TRACING_V2/LANGCHAIN_API_KEY

## Metrics
- tool_selection_accuracy: 1.0
- calculation_correctness: 1.0
- key_fact_coverage: 0.9583
- unsupported_quantitative_claim_rate: 0.2481
- unnecessary_tool_call_rate: 0.1111
- successful_workflow_rate: 1.0
- guardrail_success_rate: 1.0
- cross_domain_success_rate: 1.0

## Failures
- `EVAL-GUARD-004`
- `EVAL-GUARD-006`
- `EVAL-GUARD-004`
- `EVAL-GUARD-006`
- `EVAL-GUARD-004`
- `EVAL-GUARD-006`
- None

## Method
Each analytical case calls OpenAIGateway through the bounded LangGraph workflow. Registered tools remain deterministic; LangSmith tracing is controlled by the repository environment.

# Slice 8 — Application Experience

## 1. Objective
Expose the completed analytical/agentic capability as a usable chat application through a stable FastAPI analysis API and a focused frontend/demo UX. A user must be able to ask multiple ERP questions in one visible session and receive each answer as an assistant message with findings, evidence, analysis performed, warnings and structured visual data.

## 2. Dependencies
Slices 0–7 accepted.

## 3. Scope
### API
- stabilize `POST /api/v1/analysis` request/response contracts;
- add readiness behavior if justified separately from `/health`;
- consistent error/status mapping;
- request ID returned end-to-end;
- API integration tests.

### Minimal UX
- chat conversation shell with user and assistant messages;
- persistent composer for submitting new questions without leaving the conversation;
- visible transcript for multiple questions in the active browser session;
- question input with submit, disabled/loading and retry behavior;
- answer display associated with the submitted question;
- key findings;
- evidence/source/tool provenance suitable for a business-data application;
- analysis-performed summary;
- warnings/limitations;
- tables and chart-ready/actual simple charts when they add value;
- clear loading, error, empty, unsupported and insufficient-data states;
- starter prompts that insert or submit representative domain questions;
- a new-conversation/reset action that clears only the visible client session.

Containerize the frontend only if the selected implementation architecture justifies it and update Docker Compose accordingly in this slice.

## 4. Out of scope
- Full BI dashboard suite.
- Authentication/enterprise RBAC unless required for the public MVP demo baseline.
- Persistent conversation storage, cross-device history and advanced conversational memory. The active chat transcript may be client-side and session-scoped.
- Real ERP connection/setup screens.
- Design-system complexity unrelated to demonstrating the product.

## 5. Files and components affected
- `backend/app/api/`
- stable API schemas
- frontend application directory/technology chosen for the MVP
- Docker/Compose only if frontend runtime is added
- API/UI tests
- demo configuration/examples

## 6. Data / contracts
Primary request concept:
```json
{"question": "Why did sales decline this month?", "conversation_id": null}
```

Response concept must preserve:
- conversation ID for the active chat session;
- request ID/status;
- answer;
- key findings;
- evidence;
- analysis performed;
- warnings;
- structured table/chart data when relevant.

The frontend must send the same non-null `conversation_id` for each request in
the active chat session and append each response to the transcript. The API
remains the product boundary; the minimum Slice 8 requirement is multi-question
chat interaction and traceability, not durable memory across page reloads.

## 7. Implementation rules
- UX must expose evidence instead of hiding it behind prose.
- Each user question and assistant response must remain visually associated in
  the transcript, including failed or unsupported responses.
- Do not turn the frontend into a BI replacement.
- Preserve the API as the product boundary; frontend should consume it rather than bypass domain/agent layers.
- Warnings/insufficient evidence must be visually apparent.
- Keep deployment/runtime simple and documented.

## 8. Synthetic scenarios
Create demo paths for at least:
- commercial signature question;
- supply-chain question;
- payroll/accounting question;
- unsupported/insufficient-evidence question.

## 9. Required tests
- API request/response schema and error tests.
- End-to-end API workflow tests.
- Frontend smoke/component tests appropriate to chosen stack.
- Chat interaction tests for sending multiple questions, preserving transcript
  order, resetting the session and keeping `conversation_id` stable per session.
- Evidence/warning rendering tests where practical.
- Docker startup validation if Compose topology changes.

## 10. Acceptance criteria
1. A user can ask an ERP business question through the application.
2. The response displays findings, evidence, performed analysis and warnings clearly.
3. At least one table/chart is shown when analytically useful.
4. Negative/insufficient cases are understandable to the user.
5. A user can submit a second question and see both turns in the same active
   chat session without losing the first answer.
6. Resetting the conversation clears the client transcript and starts a new
   `conversation_id`.
7. API and UI remain thin consumers of established business/agentic layers.

## 11. Validation commands
Run API integration tests, frontend tests/build/lint as applicable, full backend quality suite and Docker application startup validation.

## 12. Deliverables
A minimal but credible public chat experience for ERP AI Analyst, with
multi-question session behavior and evidence-rich assistant messages.

## 13. Definition of Done
All mandatory demo scenarios can be executed from the user-facing chat
application with understandable evidence and warnings, and at least two
questions can be submitted sequentially without losing the visible transcript.

## 14. Prohibitions
Do not build a general BI suite, duplicate calculations in the frontend or bypass the typed tool/domain architecture.

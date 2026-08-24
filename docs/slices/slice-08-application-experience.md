# Slice 8 — Application Experience

## 1. Objective
Expose the completed analytical/agentic capability as a usable minimal application through a stable FastAPI analysis API and a focused frontend/demo UX that clearly shows answer, findings, evidence, analysis performed, warnings and structured visual data.

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
- question input;
- answer display;
- key findings;
- evidence/source/tool provenance suitable for a business-data application;
- analysis-performed summary;
- warnings/limitations;
- tables and chart-ready/actual simple charts when they add value;
- clear loading/error/empty/insufficient-data states.

Containerize the frontend only if the selected implementation architecture justifies it and update Docker Compose accordingly in this slice.

## 4. Out of scope
- Full BI dashboard suite.
- Authentication/enterprise RBAC unless required for the public MVP demo baseline.
- Advanced conversational memory not required by acceptance cases.
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
{"question": "¿Por qué disminuyeron las ventas este mes?", "conversation_id": null}
```

Response concept must preserve:
- request ID/status;
- answer;
- key findings;
- evidence;
- analysis performed;
- warnings;
- structured table/chart data when relevant.

## 7. Implementation rules
- UX must expose evidence instead of hiding it behind prose.
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
- Evidence/warning rendering tests where practical.
- Docker startup validation if Compose topology changes.

## 10. Acceptance criteria
1. A user can ask an ERP business question through the application.
2. The response displays findings, evidence, performed analysis and warnings clearly.
3. At least one table/chart is shown when analytically useful.
4. Negative/insufficient cases are understandable to the user.
5. API and UI remain thin consumers of established business/agentic layers.

## 11. Validation commands
Run API integration tests, frontend tests/build/lint as applicable, full backend quality suite and Docker application startup validation.

## 12. Deliverables
A minimal but credible public demo experience for ERP AI Analyst.

## 13. Definition of Done
All mandatory demo scenarios can be executed from the user-facing application with understandable evidence and warnings.

## 14. Prohibitions
Do not build a general BI suite, duplicate calculations in the frontend or bypass the typed tool/domain architecture.

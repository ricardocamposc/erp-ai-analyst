# MVP release report

Slice 9 is accepted after the complete MVP validation loop.

## Results

- `make check`: 26 tests passed; Ruff and mypy passed.
- `make evaluate`: 8 cases; successful workflow rate 1.0; tool selection accuracy 1.0.
- PostgreSQL: healthy in Docker on host port 5435.
- FastAPI: Docker endpoint `/health` returned `{"status":"ok"}`.
- Frontend: Docker endpoint `/` served the Spanish demo UI.
- OpenAI: configured credentials were detected through typed application settings; live structured-output smoke test passed earlier in Slice 6.

## Known boundaries

The release remains a local, synthetic-data MVP. Authentication, production deployment,
real ERP adapters, BIZAG, MCP, arbitrary SQL, write operations, and individual-level
PeopleOps analysis remain intentionally out of scope.

The two test warnings are upstream deprecation warnings from LangGraph cache defaults
and Starlette's TestClient/httpx integration; they do not fail the gates.

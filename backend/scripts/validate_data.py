"""Run canonical synthetic data-quality checks."""

from app.db.connection import create_database_engine
from app.db.seed import validate_database

errors = validate_database(create_database_engine())
if errors:
    raise SystemExit("data validation failed: " + "; ".join(errors))
print("data validation passed")

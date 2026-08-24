"""Migrate, seed and validate the local synthetic ERP database."""

from app.db.connection import create_database_engine
from app.db.seed import seed_database, validate_database


def main() -> None:
    engine = create_database_engine()
    seed_database(engine)
    errors = validate_database(engine)
    if errors:
        raise SystemExit("data validation failed: " + "; ".join(errors))
    print("seeded and validated synthetic canonical ERP")


if __name__ == "__main__":
    main()

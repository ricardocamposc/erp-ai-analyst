"""Generate reviewable deterministic synthetic rows and scenario metadata."""

import json
from pathlib import Path

from app.db.synthetic import SEED, build_dataset


def main() -> None:
    output = Path("data/synthetic")
    output.mkdir(parents=True, exist_ok=True)
    rows = build_dataset()
    (output / "canonical_dataset.json").write_text(
        json.dumps(rows, default=str, indent=2, sort_keys=True) + "\n"
    )
    print(
        f"generated seed={SEED} tables={len(rows)} rows={sum(len(value) for value in rows.values())}"
    )


if __name__ == "__main__":
    main()

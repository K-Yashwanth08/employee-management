"""Read only aggregate HR attributes from an optional local Kaggle CSV.

Identity, contact, demographic, and source employee identifier columns are never
loaded. Generated records remain synthetic and do not reuse source records.
"""

from __future__ import annotations

from pathlib import Path
import random

import pandas as pd

from scripts.data_generation import DEPARTMENTS, ROLES

DEFAULT_SOURCE = Path("data/HRDataset_v14.csv")

DEPARTMENT_MAP = {
    "production": "Operations",
    "it/is": "Engineering",
    "software engineering": "Engineering",
    "sales": "Sales",
    "admin offices": "People",
    "executive office": "Finance",
}


def _map_role(position: str, department: str) -> str:
    value = position.casefold()
    if department == "Operations" and ("production" in value or "technician" in value):
        return "Operations Coordinator"
    if any(word in value for word in ("president", "chief", "director", "manager")):
        return "Engineering Manager" if "engineer" in value or "it " in value else "Operations Coordinator"
    if "sales" in value:
        return "Sales Executive"
    if any(word in value for word in ("accountant", "finance")):
        return "Finance Analyst"
    if any(word in value for word in ("hr", "human resource", "administrative")):
        return "HR Specialist"
    if any(word in value for word in ("marketing", "communications")):
        return "Marketing Associate"
    if any(word in value for word in ("engineer", "technician", "developer", "analyst", "architect", "database", "network", "support")):
        return "Software Engineer"
    return "Operations Coordinator"


def load_source_profile(path: Path = DEFAULT_SOURCE) -> dict:
    """Return weighted department/role assignments and salary bounds.

    The local Kaggle source is optional, so clean clones can still be seeded
    with the documented synthetic defaults without Kaggle credentials.
    """
    if not path.is_file():
        return {"assignments": [], "salary_low": 42_000, "salary_high": 150_000}

    frame = pd.read_csv(path, usecols=["Department", "Position", "Salary"])
    frame["Department"] = frame["Department"].astype("string").str.strip()
    frame["Position"] = frame["Position"].astype("string").str.strip()
    frame["Salary"] = pd.to_numeric(frame["Salary"], errors="coerce")
    frame = frame.dropna(subset=["Department", "Position", "Salary"])
    assignments: list[tuple[str, str]] = []
    for row in frame.itertuples(index=False):
        department = DEPARTMENT_MAP.get(row.Department.casefold())
        role = _map_role(row.Position, department or "")
        if department in DEPARTMENTS and role in ROLES:
            assignments.append((department, role))

    if frame.empty:
        return {"assignments": [], "salary_low": 42_000, "salary_high": 150_000}
    # Quantile bounds create new salaries from broad source ranges instead of
    # copying any source person's exact compensation value.
    return {
        "assignments": assignments,
        "salary_low": max(30_000, int(frame["Salary"].quantile(0.1))),
        "salary_high": min(250_000, int(frame["Salary"].quantile(0.9))),
    }


def assignment_for(profile: dict, index: int, rng: random.Random) -> tuple[str, str] | None:
    assignments = profile["assignments"]
    return rng.choice(assignments) if assignments else None

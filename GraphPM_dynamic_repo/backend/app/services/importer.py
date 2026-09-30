import pandas as pd
from datetime import datetime, date
from sqlmodel import Session
from app.db.models import Project, Developer, Task, Dependency, Defect


TABLES = {
    "projects": Project,
    "developers": Developer,
    "tasks": Task,
    "dependencies": Dependency,
    "defects": Defect
}


# Fields that contain dates/datetimes
DATE_FIELDS = {
    "created_at",
    "updated_at",
    "due_date",
    "completed_at",
    "start_date",
    "end_date",
    "resolved_at",
}


def parse_date(value):
    """Convert CSV date strings into Python date/datetime values."""

    if value is None or pd.isna(value):
        return None

    if isinstance(value, (datetime, date)):
        return value

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

        try:
            parsed = pd.to_datetime(value)

            # Return datetime if time information exists
            if isinstance(parsed, pd.Timestamp):
                if parsed.hour != 0 or parsed.minute != 0 or parsed.second != 0:
                    return parsed.to_pydatetime()

                return parsed.date()

        except (ValueError, TypeError):
            return None

    return value


def import_csvs(session: Session, files: dict):
    counts = {}

    for name, path in files.items():

        if name not in TABLES or path is None:
            continue

        df = pd.read_csv(path).replace({pd.NA: None})

        model = TABLES[name]
        n = 0

        for row in df.to_dict("records"):

            clean = {}

            for key, value in row.items():

                # Convert NaN / empty values to None
                if pd.isna(value):
                    value = None

                if isinstance(value, str):
                    value = value.strip()

                    if value == "":
                        value = None

                # Convert date fields
                if key in DATE_FIELDS:
                    value = parse_date(value)

                clean[key] = value

            obj = model(**clean)

            session.merge(obj)
            n += 1

        counts[name] = n

    session.commit()

    return counts
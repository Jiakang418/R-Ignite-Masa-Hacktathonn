"""Preprocess and clean the raw EM-DAT extract for the SEA nat-cat workflow.

This script keeps the cleaning logic explicit and reproducible:
- focus on the climate-relevant natural-disaster rows for Malaysia and the Philippines
- normalize text fields and missing values
- convert the date parts into usable partial ISO dates
- convert damage fields from thousands of USD into full USD
- derive an inflation-adjusted loss proxy for modelling
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RAW_PATH = ROOT / "EM_DAT.csv"

CLEANED_PATH = ROOT / "EM_DAT_cleaned.csv"

TARGET_COUNTRIES = {"Malaysia", "Philippines"}
NATURAL_GROUP = "Natural"
CLIMATE_SUBGROUPS = {"Hydrological", "Meteorological", "Climatological"}


def normalize_text(value: Any) -> str:
    """Strip whitespace and turn empty placeholders into a blank string.

    EM-DAT stores missing values as empty cells, so we keep the representation
    simple and uniform before converting specific fields to numbers.
    """

    if value is None:
        return ""

    text = str(value).strip()
    if text in {"", "-", "NA", "N/A", "null", "None"}:
        return ""
    return text


def parse_int(value: Any) -> int | None:
    """Parse a numeric field that should be an integer."""

    text = normalize_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def parse_float(value: Any) -> float | None:
    """Parse a numeric field that may contain decimals."""

    text = normalize_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_date_parts(year: int | None, month: int | None, day: int | None) -> tuple[str, str]:
    """Build a partial ISO date string and a precision label.

    EM-DAT has many records with missing day-level detail. Preserving the
    highest available precision is better than discarding the row or forcing a
    fake full date.
    """

    if year is None:
        return "", "missing"
    if month is None:
        return f"{year:04d}", "year"
    if day is None:
        return f"{year:04d}-{month:02d}", "month"
    return f"{year:04d}-{month:02d}-{day:02d}", "day"


def to_usd(thousand_usd: float | None) -> float | None:
    """Convert EM-DAT's '000 US$ fields into full USD."""

    if thousand_usd is None:
        return None
    return thousand_usd * 1000.0


def clean_row(row: dict[str, Any]) -> dict[str, Any]:
    """Normalize one EM-DAT event row into a cleaner analysis-ready record."""

    # Keep the climate-relevant scope narrow so the downstream model is not
    # diluted by technological accidents that are outside the nat-cat brief.
    cleaned_country = normalize_text(row.get("Country"))
    cleaned_group = normalize_text(row.get("Disaster Group"))
    cleaned_subgroup = normalize_text(row.get("Disaster Subgroup"))
    if (
        cleaned_country not in TARGET_COUNTRIES
        or cleaned_group != NATURAL_GROUP
        or cleaned_subgroup not in CLIMATE_SUBGROUPS
    ):
        return {}

    start_year = parse_int(row.get("Start Year"))
    start_month = parse_int(row.get("Start Month"))
    start_day = parse_int(row.get("Start Day"))
    end_year = parse_int(row.get("End Year"))
    end_month = parse_int(row.get("End Month"))
    end_day = parse_int(row.get("End Day"))

    start_date, start_precision = parse_date_parts(start_year, start_month, start_day)
    end_date, end_precision = parse_date_parts(end_year, end_month, end_day)

    # We use inflation-adjusted damage as the modelling loss proxy so losses
    # from different years can be compared on the same dollar basis.
    total_damage_adjusted_usd = to_usd(parse_float(row.get("Total Damage, Adjusted ('000 US$)")))
    total_damage_usd = to_usd(parse_float(row.get("Total Damage ('000 US$)")))

    cleaned = {
        "disno": normalize_text(row.get("DisNo.")),
        "historic": normalize_text(row.get("Historic")),
        "classification_key": normalize_text(row.get("Classification Key")),
        "disaster_group": cleaned_group,
        "disaster_subgroup": cleaned_subgroup,
        "disaster_type": normalize_text(row.get("Disaster Type")),
        "disaster_subtype": normalize_text(row.get("Disaster Subtype")),
        "external_ids": normalize_text(row.get("External IDs")),
        "event_name": normalize_text(row.get("Event Name")),
        "iso": normalize_text(row.get("ISO")),
        "country": cleaned_country,
        "subregion": normalize_text(row.get("Subregion")),
        "region": normalize_text(row.get("Region")),
        "location": normalize_text(row.get("Location")),
        "origin": normalize_text(row.get("Origin")),
        "associated_types": normalize_text(row.get("Associated Types")),
        "ofda_bha_response": normalize_text(row.get("OFDA/BHA Response")),
        "appeal": normalize_text(row.get("Appeal")),
        "declaration": normalize_text(row.get("Declaration")),
        "magnitude": parse_float(row.get("Magnitude")),
        "magnitude_scale": normalize_text(row.get("Magnitude Scale")),
        "latitude": parse_float(row.get("Latitude")),
        "longitude": parse_float(row.get("Longitude")),
        "river_basin": normalize_text(row.get("River Basin")),
        "start_year": start_year,
        "start_month": start_month,
        "start_day": start_day,
        "end_year": end_year,
        "end_month": end_month,
        "end_day": end_day,
        "start_date": start_date,
        "start_date_precision": start_precision,
        "end_date": end_date,
        "end_date_precision": end_precision,
        "duration_days": None,
        "total_deaths": parse_int(row.get("Total Deaths")),
        "no_injured": parse_int(row.get("No. Injured")),
        "no_affected": parse_int(row.get("No. Affected")),
        "no_homeless": parse_int(row.get("No. Homeless")),
        "total_affected": parse_int(row.get("Total Affected")),
        "total_damage_usd": total_damage_usd,
        "total_damage_adjusted_usd": total_damage_adjusted_usd,
        "cpi": parse_float(row.get("CPI")),
        "admin_units": normalize_text(row.get("Admin Units")),
        "gadm_admin_units": normalize_text(row.get("GADM Admin Units")),
        "entry_date": normalize_text(row.get("Entry Date")),
        "last_update": normalize_text(row.get("Last Update")),
    }

    if cleaned["start_date_precision"] == "day" and cleaned["end_date_precision"] == "day":
        try:
            start = date(start_year, start_month, start_day)
            end = date(end_year, end_month, end_day)
            cleaned["duration_days"] = (end - start).days + 1
        except ValueError:
            cleaned["duration_days"] = None

    return cleaned


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    """Write a CSV file with empty strings for missing values."""

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output_row = {key: ("" if row.get(key) is None else row.get(key)) for key in fieldnames}
            writer.writerow(output_row)


def main() -> None:
    """Run the preprocessing pipeline and write all derived files."""

    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_PATH}")

    with RAW_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        raw_rows = list(reader)

    cleaned_rows: list[dict[str, Any]] = []
    for row in raw_rows:
        cleaned = clean_row(row)
        if cleaned:
            cleaned_rows.append(cleaned)

    if not cleaned_rows:
        raise ValueError("No EM-DAT rows survived the climate-risk scope filters")

    countries = {row["country"] for row in cleaned_rows}
    if not countries.issubset(TARGET_COUNTRIES):
        unexpected = sorted(countries - TARGET_COUNTRIES)
        raise ValueError(f"Unexpected countries in cleaned EM-DAT output: {unexpected}")

    for row in cleaned_rows:
        if row["disaster_group"] != NATURAL_GROUP:
            raise ValueError(f"Non-natural event survived filter: {row['disno']}")
        if row["disaster_subgroup"] not in CLIMATE_SUBGROUPS:
            raise ValueError(f"Unexpected disaster subgroup in output: {row['disaster_subgroup']}")
        if row["start_month"] is not None and not 1 <= row["start_month"] <= 12:
            raise ValueError(f"Invalid start month for {row['disno']}: {row['start_month']}")
        if row["end_month"] is not None and not 1 <= row["end_month"] <= 12:
            raise ValueError(f"Invalid end month for {row['disno']}: {row['end_month']}")
        if row["start_day"] is not None and not 1 <= row["start_day"] <= 31:
            raise ValueError(f"Invalid start day for {row['disno']}: {row['start_day']}")
        if row["end_day"] is not None and not 1 <= row["end_day"] <= 31:
            raise ValueError(f"Invalid end day for {row['disno']}: {row['end_day']}")
        if row["total_damage_usd"] is not None and row["total_damage_usd"] < 0:
            raise ValueError(f"Negative total_damage_usd for {row['disno']}")
        if row["total_damage_adjusted_usd"] is not None and row["total_damage_adjusted_usd"] < 0:
            raise ValueError(f"Negative total_damage_adjusted_usd for {row['disno']}")
        if row["duration_days"] is not None and row["duration_days"] <= 0:
            raise ValueError(f"Non-positive event duration for {row['disno']}: {row['duration_days']}")

    # Sort so the output is stable and easy to diff from run to run.
    cleaned_rows.sort(key=lambda row: (row.get("country", ""), row.get("start_year") or 0, row.get("start_date", ""), row.get("disno", "")))

    # Keep only the fields that support the later EM-DAT workflow.
    # The rest are raw metadata or administrative fields that do not change
    # the event-loss modelling or the annual loss summaries.
    # 10 columns: location/classification, temporal, and damage metrics.
    cleaned_fields = [
        "country",
        "location",
        "disaster_type",
        "disaster_subtype",
        "start_year",
        "start_month",
        "total_deaths",
        "no_affected",
        "total_affected",
        "total_damage_usd",
        "total_damage_adjusted_usd",
    ]
    write_csv(CLEANED_PATH, cleaned_rows, cleaned_fields)

    print(f"Raw rows: {len(raw_rows)}")
    print(f"Cleaned rows: {len(cleaned_rows)}")
    print(f"Wrote: {CLEANED_PATH}")


if __name__ == "__main__":
    main()
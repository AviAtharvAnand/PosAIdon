"""Read-only analysis of EarthEcho MonitorWater CSV. No DB required."""
from pathlib import Path
import re
import pandas as pd
import calendar

CSV_PATH = Path(__file__).resolve().parent / "water_csv" / "monitorwater_cleaned.csv"

PARAMETERS = {
    "ph": ("ph_clean", "pH", "pH units"),
    "water temperature": ("water_temperature_c", "Water temperature", "°C"),
    "dissolved oxygen (mg/l)": ("dissolved_oxygen_mg_l", "Dissolved oxygen", "mg/L"),
    "dissolved oxygen (ppm)": ("dissolved_oxygen_ppm", "Dissolved oxygen", "ppm"),
    "turbidity (ntu)": ("turbidity_ntu", "Turbidity", "NTU"),
    "turbidity (jtu)": ("turbidity_jtu", "Turbidity", "JTU"),
}

def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def _load():
    # Keep as a normal function; Streamlit caches it at the application layer.
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"Missing dataset: {CSV_PATH}")
    cols = ["Site visited", "Waterbody name", "Surface water type", "latitude", "longitude", "site_key", "monitoring_datetime", "monitoring_year", "quality_flag_count", *[v[0] for v in PARAMETERS.values()]]
    df = pd.read_csv(CSV_PATH, usecols=cols, low_memory=False)
    df["monitoring_datetime"] = pd.to_datetime(df["monitoring_datetime"], errors="coerce")
    df["monitoring_year"] = pd.to_numeric(df["monitoring_year"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    for name, _, _ in PARAMETERS.values():
        df[name] = pd.to_numeric(df[name], errors="coerce")
    df["label"] = df["Site visited"].fillna("").astype(str).str.strip()
    df.loc[df["label"].eq(""), "label"] = df["Waterbody name"].fillna("Unknown site")
    return df


def _parameter(question):
    q = _norm(question)
    if re.search(r"\b(ph|acidity|acidic|alkaline)\b", q): return "ph"
    if re.search(r"\b(oxygen|do)\b", q):
        if "mg l" in q: return "dissolved oxygen (mg/l)"
        if "ppm" in q: return "dissolved oxygen (ppm)"
        return "oxygen_auto"
    if "turbid" in q or "cloudiness" in q:
        if "ntu" in q: return "turbidity (ntu)"
        if "jtu" in q: return "turbidity (jtu)"
        return "turbidity_auto"
    if "temperature" in q: return "water temperature"
    return None


def _analysis_intent(q):
    q = q.lower().strip()

    # General educational questions should use RAG.
    if re.search(
        r"\b(what (?:is|does)|explain|define)\b",
        q
    ) and not re.search(r"\b(what was|what were)\b", q):
        return False

    # Direct measurement questions.
    if re.search(
        r"\b(what was|what were|how much was|"
        r"how high was|how low was)\b",
        q
    ):
        return True

    # Statistical and historical questions.
    return bool(re.search(
        r"\b(graph|graphs|chart|charts|plot|plots|visualize|visualise|"
        r"trend|trends|historical|history|average|mean|median|"
        r"minimum|maximum|over time|change|changed|"
        r"compare|comparison|measurements|readings|"
        r"data|recorded|yearly|annual|"
        r"value|values|level|levels|concentration|"
        r"last\s+\d+\s+years|past\s+\d+\s+years)\b",
        q
    ))

def _available_parameters_intent(question):
    q = question.lower()

    return bool(re.search(
        r"\b(what|which|list|show|available)\b.*"
        r"\b(parameters?|measurements?|readings?|data)\b"
        r"|"
        r"\b(parameters?|measurements?|readings?|data)\b.*"
        r"\b(available|collected|measured|recorded)\b",
        q
    ))

# Maximum distance between candidate points for a same-water-body grouping.
# This is an initial conservative screening radius, not proof of hydrologic identity.
WATERBODY_RADIUS_METERS = 100
NAME_SUFFIXES = {"lake", "pond", "river", "creek", "stream", "bay", "lagoon", "reservoir", "harbor", "wetland", "wetlands"}


def _waterbody_base(name):
    """Remove one generic waterbody-type suffix from a recorded place name."""
    parts = _norm(name).split()
    if len(parts) >= 3 and parts[-1] in NAME_SUFFIXES:
        parts = parts[:-1]
    return " ".join(parts)


def _distance_m(lat1, lon1, lat2, lon2):
    """Haversine distance between two latitude/longitude points in meters."""
    from math import radians, sin, cos, asin, sqrt
    a1, o1, a2, o2 = map(radians, (lat1, lon1, lat2, lon2))
    h = sin((a2 - a1) / 2) ** 2 + cos(a1) * cos(a2) * sin((o2 - o1) / 2) ** 2
    return 2 * 6371000 * asin(min(1, sqrt(h)))


def _find_site(df, q):
    """Resolve a site first; optionally include nearby same-name waterbody records.

    Conservative rules:
    - A site label must match the question (or a narrowly defined alias).
    - A matched label must resolve to one GPS site, otherwise ask for clarification.
    - Additional records require a matching distinctive name, compatible recorded
      waterbody type and name, and coordinates within 100 m of the anchor.
    - GPS proximity alone is never enough to combine observations.
    """
    normalized = _norm(q)
    labels = df["label"].dropna().unique()
    matches = [s for s in labels if len(_norm(s)) >= 7 and re.search(r"(?<!\w)" + re.escape(_norm(s)) + r"(?!\w)", normalized)]
    if not matches:
        aliases = {
            "baltimore": "Inner Harbor Baltimore",
            "inner harbor": "Inner Harbor Baltimore",
            "irvington": "Irvington Mill site - E. 25th. St. & Ridley ave.  bank of creek",
        }
        for alias, label in aliases.items():
            if re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", normalized) and label in labels:
                matches = [label]
                break
    if not matches:
        return None, "Please include a specific monitoring site name (for example, Inner Harbor Baltimore, Walker Creek, or Cedar River)."

    # Prefer the first explicitly mentioned location.
    # If multiple names begin at the same position,
    # prefer the more specific (longer) name.

    chosen = sorted(
        matches,
        key=lambda s: (
            normalized.find(_norm(s)),
            -len(_norm(s))
        )
    )[0]

    print(f"Matched monitoring location: {chosen}", flush=True)
    anchor = df[df["label"].eq(chosen)]
    sites = anchor["site_key"].value_counts(dropna=True)
    if sites.empty:
        return None, f"Site '{chosen}' has no usable location identifier."
    if len(sites) > 1:
        return None, (f"'{chosen}' occurs at {len(sites)} distinct GPS locations. "
                      "Please specify a precise monitoring site before interpreting its trend.")

    # The distinctive stem must contain at least two words: e.g. 'sunset park'
    # can join 'sunset park lake'; 'cedar' alone must not join other waterways.
    stem = _waterbody_base(chosen)
    if len(stem.split()) < 2:
        return anchor.copy(), None

    first = anchor.iloc[0]
    lat, lon = first["latitude"], first["longitude"]
    if pd.isna(lat) or pd.isna(lon):
        return anchor.copy(), None

    anchor_type = _norm(first.get("Surface water type", ""))
    anchor_body = _norm(first.get("Waterbody name", ""))
    # Pre-filter by related full location name before computing distances.
    candidate_labels = [s for s in labels if _waterbody_base(s) == stem]
    candidate = df[df["label"].isin(candidate_labels)].copy()

    def compatible(row):
        if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
            return False
        if _distance_m(lat, lon, row["latitude"], row["longitude"]) > WATERBODY_RADIUS_METERS:
            return False
        other_type = _norm(row.get("Surface water type", ""))
        other_body = _norm(row.get("Waterbody name", ""))
        # Both recorded waterbody classifications must agree when supplied.
        if anchor_type and other_type and anchor_type != other_type:
            return False
        # The named waterbody must agree, unless either entry lacks one.
        # Generic names (like 'Lake') are not sufficient alone: stem + distance
        # and type matching are independently required above.
        if anchor_body and other_body and anchor_body != other_body:
            return False
        return True

    candidate = candidate[candidate.apply(compatible, axis=1)]
    return candidate if not candidate.empty else anchor.copy(), None

def get_available_parameters(site):
    """List available water-quality parameters at a resolved site."""

    if site is None or site.empty:
        return {
            "context": "No matching monitoring location was found.",
            "chart": []
        }

    labels = ", ".join(sorted(site["label"].unique()))
    gps_points = site["site_key"].nunique()

    results = []
    plots = []

    for key, (col, label, unit) in PARAMETERS.items():

        valid = site.dropna(
            subset=[col, "monitoring_datetime"]
        ).copy()

        if valid.empty:
            continue

        valid["sampling_date"] = (
            valid["monitoring_datetime"].dt.date
        )

        count = len(valid)
        days = valid["sampling_date"].nunique()

        first_date = valid["sampling_date"].min()
        last_date = valid["sampling_date"].max()

        median = valid[col].median()

        results.append(
            f"- {label} ({unit}): "
            f"{count} observations, "
            f"{days} sampling days, "
            f"median {median:.3f}, "
            f"recorded {first_date} to {last_date}."
        )
        # Prepare actual daily measurements for charting.
        daily = (
            valid.groupby("sampling_date")[col]
            .median()
            .sort_index()
        )

        plots.append({
            "label": f"{label} ({unit})",
            "points": [
                {"date": str(date), "value": float(value)}
                for date, value in daily.items()
            ]
        })

    if not results:
        return {
            "context": (
                f"No usable measurements for the supported "
                f"parameters were found at {labels}. "
                "This does not establish that the original "
                "dataset contains no other measurements."
            ),
            "chart": []
        }

    context = (
        "DATASET-VERIFIED MONITORWATER MEASUREMENT INVENTORY:\n"
        f"Location: {labels}\n"
        f"GPS monitoring points: {gps_points}\n\n"
        "Available water-quality measurements:\n"
        + "\n".join(results)
        + "\n\n"
        "IMPORTANT:\n"
        "- These are actual measurements in the CSV.\n"
        "- Different units are reported separately.\n"
        "- A missing parameter does not mean its value is zero.\n"
        "- A single measurement cannot establish a trend.\n"
        "- The inventory covers the parameters supported by "
        "the current analysis module, not necessarily every "
        "column in the original dataset."
    )

    return {
        "context": context,
        "chart": [],
        "plots": plots
    }

def analyze_dataset_wide(question):
    """Simple, dataset-wide monitoring site discovery and rankings."""

    q = question.lower()

    # Only handle dataset-wide discovery/ranking questions.
    is_site_question = bool(re.search(
        r"\b(sites?|locations?|stations?)\b", q
    ))

    is_dataset_question = bool(re.search(
        r"\b(csv|dataset|monitorwater|all sites|other sites)\b", q
    ))

    is_ranking = bool(re.search(
        r"\b(top|highest|lowest|most|fewest|rank)\b", q
    ))

    if not is_site_question:
        return None

    if not is_dataset_question and not is_ranking:
        return None

    # Avoid mistakenly handling specific single-site questions.
    # Only site discovery, counts and rankings are handled here.

    df = _load()

    sites = df.dropna(subset=["site_key"]).copy()

    if sites.empty:
        return {
            "context": "No usable monitoring site identifiers found.",
            "chart": []
        }

    site_summary = (
        sites.groupby("site_key")
        .agg(
            site_name=("label", "first"),
            observations=("site_key", "size"),
            first_date=("monitoring_datetime", "min"),
            last_date=("monitoring_datetime", "max")
        )
        .reset_index()
    )

    total_sites = len(site_summary)
    total_observations = len(df)

    summary = [
        "DATASET-WIDE MONITORWATER CSV ANALYSIS:",
        f"Total CSV records: {total_observations:,}",
        f"Distinct GPS monitoring sites: {total_sites:,}",
        "Sites are identified by GPS site_key.",
        "Site names are labels and may not be unique.",
    ]

    # Rank by median pH if requested.
    if "ph" in q and is_ranking:

        ph_sites = (
            sites.dropna(subset=["ph_clean"])
            .groupby("site_key")
            .agg(
                site_name=("label", "first"),
                median_ph=("ph_clean", "median"),
                sample_count=("ph_clean", "count")
            )
            .reset_index()
        )

        # Require at least three measurements for this ranking.
        ph_sites = ph_sites[
            ph_sites["sample_count"] >= 3
        ]

        ascending = bool(re.search(
            r"\b(lowest|smallest)\b", q
        ))

        ph_sites = ph_sites.sort_values(
            "median_ph",
            ascending=ascending
        ).head(10)

        summary.append(
            "Monitoring sites ranked by median pH "
            "(minimum 3 valid observations per GPS site):"
        )

        for rank, row in enumerate(
            ph_sites.itertuples(index=False), start=1
        ):
            summary.append(
                f"{rank}. {row.site_name} "
                f"[GPS: {row.site_key}]: "
                f"median pH {row.median_ph:.2f}, "
                f"{row.sample_count} observations."
            )

    else:
        # List the 10 most frequently sampled GPS sites.
        ranked = site_summary.sort_values(
            "observations", ascending=False
        ).head(10)

        summary.append(
            "Top 10 GPS sites by total CSV records:"
        )

        for rank, row in enumerate(
            ranked.itertuples(index=False), start=1
        ):
            start = (
                str(row.first_date.date())
                if pd.notna(row.first_date) else "unknown"
            )
            end = (
                str(row.last_date.date())
                if pd.notna(row.last_date) else "unknown"
            )

            summary.append(
                f"{rank}. {row.site_name} "
                f"[GPS: {row.site_key}]: "
                f"{row.observations} records, "
                f"{start} to {end}."
            )

    summary.append(
        "IMPORTANT: These results were calculated directly "
        "from the complete loaded MonitorWater CSV. "
        "Rankings do not establish water safety or ecological "
        "condition. Monitoring locations may have different "
        "sampling frequencies, dates and measurement quality."
    )

    return {
        "context": "\n".join(summary),
        "chart": []
    }

def calculate_wqi(question):
    """Provisional CCME-method WQI using illustrative objectives."""

    q = question.lower()

    if not re.search(
        r"\b(wqi|water quality index|water quality score|"
        r"water quality rating|water quality index score)\b",
        q
    ):
        return None

    years = re.findall(r"\b(?:19|20)\d{2}\b", question)

    if len(years) == 0:
        df = _load()
        site, error = _find_site(df, question)

        if error:
            return {"context": error, "chart": []}

        available_years = sorted(
            site["monitoring_year"].dropna().astype(int).unique()
        )

        chart = []
        skipped = []

        for y in available_years:
            result = calculate_wqi(f"{question} in {y}")
            context = result["context"]

            match = re.search(
                r"Score:\s*([\d.]+)\s*/\s*100",
                context
            )

            if match:
                chart.append({
                    "year": int(y),
                    "median": float(match.group(1))
                })
            else:
                skipped.append(int(y))

        if not chart:
            return {
                "context": (
                    "No years had sufficient qualifying measurements "
                    "to calculate the provisional WQI."
                ),
                "chart": []
            }

        lines = [
            "HISTORICAL PROVISIONAL WATER QUALITY INDEX",
            f"Location: {', '.join(sorted(site['label'].unique()))}",
            "",
            "Annual WQI scores:"
        ]

        for item in chart:
            lines.append(
                f"{item['year']}: {item['median']:.1f} / 100"
            )

        if skipped:
            lines.append(
                "Years without sufficient qualifying data: "
                + ", ".join(map(str, skipped))
            )

        lines.append(
            "\nThese scores use the CCME mathematical method "
            "with illustrative screening objectives, not "
            "validated site-specific regulatory objectives. "
            "Missing years are excluded rather than assigned zero. "
            "Changes in scores may reflect differences in sampling "
            "coverage as well as water conditions."
        )

        return {
            "context": "\n".join(lines),
            "chart": chart,
            "unit": "WQI (0–100)",
            "is_wqi": True
        }

    if len(years) != 1:
        return {
            "context": (
                "Please request a single year or omit the year "
                "to display all eligible historical WQI scores."
            ),
            "chart": []
        }

    year = int(years[0])
    df = _load()
    site, error = _find_site(df, question)

    if error:
        return {"context": error, "chart": []}

    rows = site[
        site["monitoring_datetime"].dt.year == year
    ].copy()

    if rows.empty:
        return {
            "context": f"No observations available for {year}.",
            "chart": []
        }

    # ILLUSTRATIVE screening objectives, NOT universal
    # regulatory or aquatic-life standards.
    # Do not compare JTU with NTU.
    objectives = {
        "ph_clean": ("pH", 6.5, 9.0, "pH"),
        "dissolved_oxygen_mg_l": (
            "Dissolved oxygen", 5.0, None, "mg/L"
        ),
        "water_temperature_c": (
            "Water temperature", None, 30.0, "°C"
        ),
        "turbidity_ntu": (
            "Turbidity", None, 25.0, "NTU"
        )
    }

    observations = []
    insufficient = []

    for col, (label, lower, upper, unit) in objectives.items():

        valid = rows.dropna(
            subset=[col, "monitoring_datetime"]
        ).copy()

        valid = valid[valid[col] >= 0]

        days = valid["monitoring_datetime"].dt.date.nunique()

        if days < 4:
            note = f"{label} ({unit}): {days} qualifying sampling days"

            if col == "dissolved_oxygen_mg_l":
                alt = rows["dissolved_oxygen_ppm"].notna().sum()
                if alt:
                    note += f"; {alt} ppm readings excluded (different unit)"

            if col == "turbidity_ntu":
                alt = rows["turbidity_jtu"].notna().sum()
                if alt:
                    note += f"; {alt} JTU readings excluded (different method/unit)"

            insufficient.append(note)
            continue

        for value in valid[col]:
            value = float(value)
            excursion = 0.0

            if lower is not None and value < lower:
                excursion = (
                    lower / value - 1
                    if value > 0 else 1_000_000
                )

            elif upper is not None and value > upper:
                excursion = value / upper - 1

            observations.append({
                "variable": col,
                "excursion": excursion,
                "failed": excursion > 0
            })

    variables = set(x["variable"] for x in observations)

    if len(variables) < 4:
        return {
            "context": (
                f"CCME-method WQI not calculated for {year}.\n"
                "A minimum of four qualifying variables "
                "with at least four sampling occasions each "
                "is required for this implementation.\n"
                "Insufficient measurements: "
                + "; ".join(insufficient)
                + "\nNo numerical WQI should be inferred."
            ),
            "chart": []
        }

    total_tests = len(observations)
    failures = [x for x in observations if x["failed"]]
    failed_variables = set(x["variable"] for x in failures)

    # CCME scope, frequency, and amplitude.
    f1 = 100 * len(failed_variables) / len(variables)
    f2 = 100 * len(failures) / total_tests

    nse = (
        sum(x["excursion"] for x in observations)
        / total_tests
    )

    f3 = nse / (0.01 * nse + 0.01)

    wqi = 100 - (
        (f1**2 + f2**2 + f3**2)**0.5
        / 1.732
    )

    wqi = max(0, min(100, wqi))

    if wqi >= 95:
        category = "Excellent"
    elif wqi >= 80:
        category = "Good"
    elif wqi >= 65:
        category = "Fair"
    elif wqi >= 45:
        category = "Marginal"
    else:
        category = "Poor"

    context = (
        "PROVISIONAL CCME-METHOD WATER QUALITY INDEX\n"
        f"Location: {', '.join(sorted(site['label'].unique()))}\n"
        f"Year: {year}\n"
        f"Score: {wqi:.1f} / 100\n"
        f"Category under CCME scoring bands: {category}\n"
        f"Variables: {len(variables)}\n"
        f"Individual tests: {total_tests}\n"
        f"Failed tests: {len(failures)}\n"
        f"F1 scope: {f1:.2f}\n"
        f"F2 frequency: {f2:.2f}\n"
        f"F3 amplitude: {f3:.2f}\n\n"
        "ILLUSTRATIVE OBJECTIVES USED:\n"
        "pH: 6.5–9.0\n"
        "Dissolved oxygen: at least 5 mg/L\n"
        "Water temperature: at most 30°C\n"
        "Turbidity: at most 25 NTU\n\n"
        "IMPORTANT: This is a demonstration screening score "
        "using the CCME mathematical method and illustrative "
        "objectives, not a regulator-approved or site-calibrated "
        "water-quality index. Thresholds must be validated "
        "for the local waterbody and intended water use. "
        "It cannot establish drinking-water safety, "
        "aquatic-life safety, or ecological health."
    )

    return {
        "context": context,
        "chart": []
    }

def analyze_question(question: str):
    """Analyze MonitorWater CSV questions."""
    wqi_result = calculate_wqi(question)

    if wqi_result is not None:
        return wqi_result
    
    dataset_result = analyze_dataset_wide(question)

    if dataset_result is not None:
        return dataset_result

    # Questions asking which parameters are available
    if _available_parameters_intent(question):

        df = _load()
        site, error = _find_site(df, question)

        if error:
            return {"context": error, "chart": []}

        return get_available_parameters(site)

    # Existing numerical and trend analysis
    if not _analysis_intent(question):
        return None

    param = _parameter(question)

    if param is None:
        return None

    df = _load()
    site, error = _find_site(df, question)

    if error:
        return {"context": error, "chart": []}

    keys = (["dissolved oxygen (mg/l)", "dissolved oxygen (ppm)"] if param == "oxygen_auto"
            else ["turbidity (ntu)", "turbidity (jtu)"] if param == "turbidity_auto" else [param])
    # Choose the most observed compatible unit; never pool incompatible units.
    key = max(keys, key=lambda k: site[PARAMETERS[k][0]].count())
    col, label, unit = PARAMETERS[key]
    rows = site.dropna(subset=[col, "monitoring_datetime"]).copy()
    # Filter observations by month if mentioned in the question.
    question_lower = question.lower()

    for month_number in range(1, 13):
        month_name = calendar.month_name[month_number].lower()
        month_abbr = calendar.month_abbr[month_number].lower()

        if re.search(
            rf"\b(?:{month_name}|{month_abbr})\b",
            question_lower
        ):
            rows = rows[
                rows["monitoring_datetime"].dt.month == month_number
            ]
            break
    if rows.empty: return {"context": f"No usable {label} readings for {site['label'].iloc[0]} ({unit}).", "chart": []}

    # Explicit year bounds; if none, use full history.
    years = [int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", question)]
    if years:
        start, end = min(years), max(years)
        if len(years) == 1 and ("since" in question.lower() or "from" in question.lower()):
            end = int(rows["monitoring_year"].max())
        rows = rows[rows["monitoring_year"].between(start, end)]
    else:
        m = re.search(r"(?:last|past)\s+(\d+)\s+years?", question, re.I)
        if m:
            end = int(rows["monitoring_year"].max())
            rows = rows[rows["monitoring_year"] >= end - int(m.group(1)) + 1]
    if rows.empty: return {"context": "No measurements in the requested date range.", "chart": []}

    rows["sampling_date"] = rows["monitoring_datetime"].dt.date
    daily = rows.groupby("sampling_date", as_index=False).agg({col:"median", "monitoring_year":"first"})
    annual = daily.groupby("monitoring_year").agg(median=(col,"median"), sampling_days=(col,"count")).reset_index()
    annual = annual.sort_values("monitoring_year")
    annual["monitoring_year"] = annual["monitoring_year"].astype(int)
    chart = [{"year":int(r.monitoring_year),"median":round(float(r.median),3),"sampling_days":int(r.sampling_days)} for r in annual.itertuples(index=False)]
    flags = pd.to_numeric(rows["quality_flag_count"], errors="coerce").fillna(0).gt(0).sum()
    summary = [f"DATASET-VERIFIED CALCULATIONS (not source-document prose):",
               f"Waterbody/site labels: {', '.join(sorted(site['label'].unique()))}; "
               f"GPS monitoring points: {site['site_key'].nunique()}; "
               f"anchor GPS key: {site['site_key'].iloc[0]}",
               f"Parameter: {label}; unit: {unit}; never compare or combine with alternate oxygen/turbidity units.",
               f"Valid observations: {len(rows)} on {len(daily)} distinct sampling days; years: {int(annual.monitoring_year.min())}–{int(annual.monitoring_year.max())}.",
               f"Median across observations: {rows[col].median():.3f} {unit}; min: {rows[col].min():.3f}; max: {rows[col].max():.3f}.",
               f"Records with remaining quality flags: {flags}; these need interpretation, not automatic deletion.",
               "Annual daily-median values (year: median, sampling days):"]
    summary.extend(f"{r['year']}: {r['median']} {unit}, n={r['sampling_days']} days" for r in chart)
    if 1 <= len(daily) <= 12:
        summary.append("Individual sampling dates (do not mistake these for a validated trend):")
        for row in daily.sort_values("sampling_date").itertuples(index=False):
            summary.append(f"{row.sampling_date}: {getattr(row, col):.3f} {unit}")
        ordered = daily.sort_values("sampling_date")
        delta = ordered[col].iloc[-1] - ordered[col].iloc[0]
        summary.append(f"First-to-last sampled-day difference: {delta:+.3f} {unit}; "
                       "this is only an observed difference, not evidence of a long-term trend.")
    if len(chart)>=2:
        summary.append(f"Earliest-vs-latest observed year median difference: {chart[-1]['median']-chart[0]['median']:+.3f} {unit}. "
                       "This is not a validated causal or season-adjusted trend.")
    if site["site_key"].nunique() > 1:
        summary.append("WATERBODY GROUPING: Combined nearby monitoring points with matching distinctive place names "
                       "and compatible waterbody labels within 100 m. This is not a verified hydrologic/site identity match. "
                       "Measurements at different points should not be represented as the same station.")
    summary.append("IMPORTANT: Observation dates may be unevenly spaced and seasonally biased. Do not infer safety, cause, or wildlife harm from these data alone. "
                   "Avoid claiming statistical significance without testing. If annual samples are sparse, say so.")
    return {"context":"\n".join(summary),"chart":chart,"label":label,"unit":unit}

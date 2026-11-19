"""Read-only analysis of EarthEcho MonitorWater CSV. No DB required."""
from pathlib import Path
import re
import pandas as pd

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
    cols = ["Site visited", "Waterbody name", "site_key", "monitoring_datetime", "monitoring_year", "quality_flag_count", *[v[0] for v in PARAMETERS.values()]]
    df = pd.read_csv(CSV_PATH, usecols=cols, low_memory=False)
    df["monitoring_datetime"] = pd.to_datetime(df["monitoring_datetime"], errors="coerce")
    df["monitoring_year"] = pd.to_numeric(df["monitoring_year"], errors="coerce")
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
    if re.search(r"\bwhat\s+does\s+.+\s+mean\b", q.lower()):
        return False
    return bool(re.search(r"\b(trend|historical|history|average|mean|median|minimum|maximum|over time|change|changed|compare|comparison|measurements|readings|data|recorded|yearly|annual|last\s+\d+\s+years|past\s+\d+\s+years)\b", q.lower()))


def _find_site(df, q):
    """Require a uniquely identifiable site phrase; avoid mixing similarly named stations."""
    normalized = _norm(q)
    labels = df["label"].dropna().unique()
    # Longer full labels first, with token boundaries to avoid substring collisions.
    matches = [s for s in labels if len(_norm(s)) >= 7 and re.search(r"(?<!\w)" + re.escape(_norm(s)) + r"(?!\w)", normalized)]
    if not matches:
        # Common short geographic mentions; these must still resolve to a single station.
        aliases = {
            "baltimore": "Inner Harbor Baltimore",
            "inner harbor": "Inner Harbor Baltimore",
            "irvington": "Irvington Mill site - E. 25th. St. & Ridley ave.  bank of creek",
        }
        for alias, label in aliases.items():
            if re.search(r"(?<!\w)"+re.escape(alias)+r"(?!\w)", normalized) and label in labels:
                matches = [label]
                break
    if not matches:
        return None, "Please include a specific monitoring site name (for example, Inner Harbor Baltimore, Walker Creek, or Cedar River)."
    # Same-name sites can occur at several coordinates. Never pool these silently.
    chosen = sorted(matches, key=lambda s: (-len(_norm(s)), s))[0]
    group = df[df["label"].eq(chosen)]
    sites = group["site_key"].value_counts(dropna=True)
    if sites.empty:
        return None, f"Site '{chosen}' has no usable location identifier."
    if len(sites) > 1:
        return None, (f"'{chosen}' occurs at {len(sites)} distinct GPS locations. "
                      "Please choose a precise site in the dataset before interpreting a single-site trend.")
    return group, None


def analyze_question(question: str):
    """Return dict with 'context' and 'chart' (list of year/median/count dicts) or None.

    This is only invoked for explicit historical/numerical questions.
    """
    if not _analysis_intent(question): return None
    param = _parameter(question)
    if param is None: return None
    df = _load()
    site, error = _find_site(df, question)
    if error: return {"context": error, "chart": []}

    keys = (["dissolved oxygen (mg/l)", "dissolved oxygen (ppm)"] if param == "oxygen_auto"
            else ["turbidity (ntu)", "turbidity (jtu)"] if param == "turbidity_auto" else [param])
    # Choose the most observed compatible unit; never pool incompatible units.
    key = max(keys, key=lambda k: site[PARAMETERS[k][0]].count())
    col, label, unit = PARAMETERS[key]
    rows = site.dropna(subset=[col, "monitoring_datetime"]).copy()
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
               f"Site label: {site['label'].iloc[0]}; GPS site key: {site['site_key'].iloc[0]}",
               f"Parameter: {label}; unit: {unit}; never compare or combine with alternate oxygen/turbidity units.",
               f"Valid observations: {len(rows)} on {len(daily)} distinct sampling days; years: {int(annual.monitoring_year.min())}–{int(annual.monitoring_year.max())}.",
               f"Median across observations: {rows[col].median():.3f} {unit}; min: {rows[col].min():.3f}; max: {rows[col].max():.3f}.",
               f"Records with remaining quality flags: {flags}; these need interpretation, not automatic deletion.",
               "Annual daily-median values (year: median, sampling days):"]
    summary.extend(f"{r['year']}: {r['median']} {unit}, n={r['sampling_days']} days" for r in chart)
    if len(chart)>=2:
        summary.append(f"Earliest-vs-latest observed year median difference: {chart[-1]['median']-chart[0]['median']:+.3f} {unit}. "
                       "This is not a validated causal or season-adjusted trend.")
    summary.append("IMPORTANT: Observation dates may be unevenly spaced and seasonally biased. Do not infer safety, cause, or wildlife harm from these data alone. "
                   "Avoid claiming statistical significance without testing. If annual samples are sparse, say so.")
    return {"context":"\n".join(summary),"chart":chart,"label":label,"unit":unit}

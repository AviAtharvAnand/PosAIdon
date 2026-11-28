"""Deterministic classification of user-submitted water-quality readings.

Bands come from the EarthEcho Analysis Dictionary (Sheet 3 raw-value reference
bands) and combinations from Sheet 2. Python decides the bands; the LLM only
explains them using the retrieved dictionary text.
"""

# Sheet 2 headings, as (parameter, direction) sets. Kept in code because the
# Docker image ships chunks/Chroma, not the source markdown.
COMBINATIONS = [
    "Temperature High, DO Low",
    "Turbidity High, DO Low",
    "pH High, Temperature High, DO Low",
    "Turbidity High, pH High",
    "pH Low, DO Low",
    "pH High, DO High",
    "pH Low, Turbidity High",
    "Temperature Low, DO Low",
    "Temperature High, Turbidity High",
    "Temperature High, DO High",
    "Turbidity Low, DO Low",
    "pH Low, DO High",
]


def _combo_tokens(name):
    return {tuple(part.strip().rsplit(" ", 1)) for part in name.split(",")}


def _ph(value):
    if value < 6.5:
        return "Too low (acidic)", "Low", "pH below 6.5"
    if value > 9.0:
        return "Too high (alkaline)", "High", "pH above 9.0"
    return "In Range", None, "pH within 6.5–9.0"


def _do(value):
    if value < 3:
        return "Very Low", "Low", "below 3 mg/L"
    if value < 5:
        return "Low", "Low", "3 to under 5 mg/L"
    if value <= 8:
        return "Good", None, "5–8 mg/L"
    return "High", "High", "above 8 mg/L"


def _turbidity_jtu(value):
    if value <= 0:
        return "Excellent", "Low", "0 JTU"
    if value <= 40:
        return "Good", None, "up to 40 JTU"
    if value <= 100:
        return "Fair", "High", "41–100 JTU"
    return "Poor", "High", "above 100 JTU"


def _temperature(value_c):
    if value_c < 20:
        return "Too cold", "Low", "below 68 °F (20 °C)"
    if value_c > 30:
        return "Too hot", "High", "above 86 °F (30 °C)"
    return "In Range", None, "68–86 °F (20–30 °C)"


# Band function and band order (low -> high) per CSV column, shared with panalyze.
# DO bands apply to mg/L only and turbidity bands to JTU only (dictionary rules).
BAND_RULES = {
    "ph_clean": (_ph, ["Too low (acidic)", "In Range", "Too high (alkaline)"]),
    "dissolved_oxygen_mg_l": (_do, ["Very Low", "Low", "Good", "High"]),
    "turbidity_jtu": (_turbidity_jtu, ["Excellent", "Good", "Fair", "Poor"]),
    "water_temperature_c": (_temperature, ["Too cold", "In Range", "Too hot"]),
}


def band_of(column, value):
    """Dictionary band name for one value, or None if the column has no bands."""
    rule = BAND_RULES.get(column)
    return rule[0](value)[0] if rule else None


def format_readings_message(ph=None, do_mg_l=None, turbidity=None,
                            turbidity_unit="JTU", temp_c=None, notes=""):
    """Human-readable chat message describing the submitted readings."""
    parts = []
    if ph is not None:
        parts.append(f"pH {ph:g}")
    if do_mg_l is not None:
        parts.append(f"dissolved oxygen {do_mg_l:g} mg/L")
    if turbidity is not None:
        parts.append(f"turbidity {turbidity:g} {turbidity_unit}")
    if temp_c is not None:
        parts.append(f"water temperature {temp_c:g} °C")
    message = "Analyze my readings: " + ", ".join(parts) + "."
    if notes and notes.strip():
        message += f"\nMy notes: {notes.strip()}"
    return message


def classify_readings(ph=None, do_mg_l=None, turbidity=None,
                      turbidity_unit="JTU", temp_c=None, notes=""):
    """Band each provided reading and find matching combination rules.

    Raises ValueError if no reading is provided.
    """
    if all(v is None for v in (ph, do_mg_l, turbidity, temp_c)):
        raise ValueError("Enter at least one reading.")

    lines = []
    directions = set()
    query_terms = []

    if ph is not None:
        band, direction, rule = _ph(ph)
        lines.append(f"- pH: {ph:g} → {band} (reference band: {rule})")
        query_terms.append(f"pH {band}")
        if direction:
            directions.add(("pH", direction))

    if do_mg_l is not None:
        band, direction, rule = _do(do_mg_l)
        lines.append(f"- Dissolved oxygen: {do_mg_l:g} mg/L → {band} (reference band: {rule})")
        query_terms.append(f"Dissolved Oxygen {band}")
        if direction:
            directions.add(("DO", direction))

    if turbidity is not None:
        if turbidity_unit.upper() == "JTU":
            band, direction, rule = _turbidity_jtu(turbidity)
            lines.append(f"- Turbidity: {turbidity:g} JTU → {band} (reference band: {rule})")
            query_terms.append(f"Turbidity {band}")
            if direction:
                directions.add(("Turbidity", direction))
        else:
            lines.append(
                f"- Turbidity: {turbidity:g} {turbidity_unit} → not banded. The dictionary's "
                "turbidity bands are in JTU and must not be applied directly to NTU readings."
            )
            query_terms.append("Turbidity")

    if temp_c is not None:
        band, direction, rule = _temperature(temp_c)
        temp_f = temp_c * 9 / 5 + 32
        lines.append(
            f"- Water temperature: {temp_c:g} °C ({temp_f:.1f} °F) → {band} "
            f"(rough reference band: {rule}; the dictionary prefers comparing against "
            "historical readings at the same site and season)"
        )
        query_terms.append(f"Temperature {band}")
        if direction:
            directions.add(("Temperature", direction))

    combos = [name for name in COMBINATIONS if _combo_tokens(name) <= directions]

    context_lines = [
        "USER-SUBMITTED READINGS (entered by the user, not MonitorWater CSV data):",
        *lines,
    ]
    if combos:
        context_lines.append("Matching interacting-parameter combinations (EarthEcho Sheet 2): "
                             + "; ".join(combos))
    else:
        context_lines.append("No EarthEcho interacting-parameter combination matches these readings.")
    if notes and notes.strip():
        context_lines.append(f"User's notes on possible causes: {notes.strip()}")
    context_lines.append(
        "IMPORTANT: Bands were assigned in code from the EarthEcho Analysis Dictionary's "
        "simplified reference bands, which are not universal environmental or regulatory "
        "standards. A single set of readings cannot establish a trend. Possible causes are "
        "hypotheses, not diagnoses. Do not declare the water safe or unsafe."
    )

    return {
        "context": "\n".join(context_lines),
        "combinations": combos,
        "search_query": " ".join(query_terms + combos),
    }

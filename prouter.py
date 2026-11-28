"""AI question interpreter: decides how each question is routed.

One LLM call turns the user's question (plus recent history) into a small JSON
"plan". The plan only *routes* the question; every number still comes from the
deterministic pandas analysis in panalyze.py. If the LLM call fails or returns
invalid JSON, a regex-based fallback plan is returned so the app keeps working.
"""
import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["NRP_LLM_TOKEN"],
                base_url=os.environ.get("NRP_LLM_BASE_URL", "https://ellm.nrp-nautilus.io/v1"))

ROUTER_MODEL = os.environ.get("POSAIDON_ROUTER_MODEL", "qwen3-small")

TASKS = {"trend", "values", "inventory", "ranking", "dataset_summary", "wqi", "none", "off_topic"}
PARAMETER_NAMES = {"ph", "dissolved_oxygen", "temperature", "turbidity",
                   "salinity", "nitrate", "nitrite", "phosphate", "fecal_coliform"}

ROUTER_PROMPT = """/no think

You route questions for PosAIdon, a water-quality assistant. It has:
- MonitorWater CSV: historical measurements (pH, dissolved oxygen, water temperature, turbidity, salinity, nitrate, nitrite, phosphate, fecal coliform presence/absence) plus each site's waterbody name and surface water type, at named monitoring sites, 1979-present.
- Scientific documentation explaining water-quality concepts.

Return ONLY a JSON object with exactly these keys:
{
  "standalone_question": string,  // the latest question rewritten to stand alone; resolve "it", "there", "that", "same site" from history. Otherwise copy it unchanged.
  "needs_csv": boolean,           // true if answering needs measurements from the CSV (a site's values, trends, history, rankings, WQI, available data). false for purely conceptual/general questions.
  "task": "trend" | "values" | "inventory" | "ranking" | "dataset_summary" | "wqi" | "none" | "off_topic",
      // trend: change over time / history at a site
      // values: specific measurements (on a date, average, min, max)
      // inventory: which parameters/data exist at a site
      // ranking: ranking or listing individual SITES (most records, highest/lowest pH)
      // dataset_summary: statistics about the WHOLE dataset with no single site: total records, date range, number of sites, records per year, surface water types, fecal coliform results, overall medians or percentages, data quality flags, comparisons between water body types
      // wqi: water quality index / score / rating
      // none: needs_csv is false but the question is about water, water quality, aquatic ecosystems, the environment, monitoring, or this app (also greetings and thanks)
      // off_topic: CLEARLY unrelated to water/environment/this app: e.g. poems, stories or jokes about other subjects, coding help, cryptocurrency, sports, homework on other subjects, general chit-chat requests. If in doubt, use "none", not "off_topic". Set needs_csv false.
      // NEVER off_topic: health or safety questions involving water exposure (drinking, swimming, symptoms after contact) -> "none", so the answer can point the user to a doctor or local health authority; creative or educational requests ABOUT water (a poem about rivers) -> "none".
  "site": string | null,          // the monitoring site exactly as the user named it (after resolving references), else null
  "parameters": [ "ph" | "dissolved_oxygen" | "temperature" | "turbidity" | "salinity" | "nitrate" | "nitrite" | "phosphate" | "fecal_coliform" ],  // [] means not specified (use all)
  "start_year": integer | null,
  "end_year": integer | null,     // for "since 2020" set start_year 2020 and end_year null
  "last_n_years": integer | null, // for "last 5 years"
  "month": integer | null,        // 1-12 if a month is named
  "wants_chart": boolean          // true if a graph/plot/chart/visual would help or is requested: trends and comparisons over time -> true; single values or concepts -> false
}

Follow-up questions ("what could be causing that?", "what should I do next?", "why?", "is that bad?"):
- Use PREVIOUS TURN CONTEXT (if given) to resolve what "that" refers to: the site, the parameter, and its finding/band.
- standalone_question must name the site, the parameter and the finding, e.g. "What could be causing the too low (acidic) pH (median 6.0) at Inner Harbor Baltimore, according to the dictionary?"
- Keep the previous site and parameters. Use task "values" with needs_csv true so the site's data stays available.

Examples:
Q: what is the trend for inner baltimore harbor
{"standalone_question":"what is the trend for inner baltimore harbor","needs_csv":true,"task":"trend","site":"inner baltimore harbor","parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":true}
Q: what is dissolved oxygen and why does it matter?
{"standalone_question":"what is dissolved oxygen and why does it matter?","needs_csv":false,"task":"none","site":null,"parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: what was the pH at Walker Creek in July 2021
{"standalone_question":"what was the pH at Walker Creek in July 2021","needs_csv":true,"task":"values","site":"Walker Creek","parameters":["ph"],"start_year":2021,"end_year":2021,"last_n_years":null,"month":7,"wants_chart":false}
(History: user asked about Cedar River pH) Q: how has turbidity changed there since 2018?
{"standalone_question":"how has turbidity changed at Cedar River since 2018?","needs_csv":true,"task":"trend","site":"Cedar River","parameters":["turbidity"],"start_year":2018,"end_year":null,"last_n_years":null,"month":null,"wants_chart":true}
(PREVIOUS TURN CONTEXT: site=Inner Harbor Baltimore; parameters=ph; findings: pH median 6.000 pH units -> Too low (acidic)) Q: What could be causing that, according to the dictionary?
{"standalone_question":"What could be causing the too low (acidic) pH (median 6.0) at Inner Harbor Baltimore, according to the dictionary?","needs_csv":true,"task":"values","site":"Inner Harbor Baltimore","parameters":["ph"],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
(PREVIOUS TURN CONTEXT: site=Inner Harbor Baltimore; parameters=ph; findings: pH median 6.000 pH units -> Too low (acidic)) Q: And what should I do next?
{"standalone_question":"What re-testing next steps and actions does the dictionary recommend for too low (acidic) pH at Inner Harbor Baltimore?","needs_csv":true,"task":"values","site":"Inner Harbor Baltimore","parameters":["ph"],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: What is the median salinity at Malibu Lagoon - Channel Bottom, and what type of water body is it?
{"standalone_question":"What is the median salinity at Malibu Lagoon - Channel Bottom, and what type of water body is it?","needs_csv":true,"task":"values","site":"Malibu Lagoon - Channel Bottom","parameters":["salinity"],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: Write a haiku about Bitcoin.
{"standalone_question":"Write a haiku about Bitcoin.","needs_csv":false,"task":"off_topic","site":null,"parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: Can you write a Python function to sort a list?
{"standalone_question":"Can you write a Python function to sort a list?","needs_csv":false,"task":"off_topic","site":null,"parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: I swam in a lake and now I have a rash. What should I do?
{"standalone_question":"I swam in a lake and now I have a rash. What should I do?","needs_csv":false,"task":"none","site":null,"parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: Why do fish die when oxygen is low?
{"standalone_question":"Why do fish die when oxygen is low?","needs_csv":false,"task":"none","site":null,"parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: which sites have the highest pH?
{"standalone_question":"which sites have the highest pH?","needs_csv":true,"task":"ranking","site":null,"parameters":["ph"],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: How many records are in the MonitorWater dataset?
{"standalone_question":"How many records are in the MonitorWater dataset?","needs_csv":true,"task":"dataset_summary","site":null,"parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: How does median pH compare between estuaries, lakes and streams?
{"standalone_question":"How does median pH compare between estuaries, lakes and streams?","needs_csv":true,"task":"dataset_summary","site":null,"parameters":["ph"],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: What percentage of fecal coliform results were Present?
{"standalone_question":"What percentage of fecal coliform results were Present?","needs_csv":true,"task":"dataset_summary","site":null,"parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: what is the water quality score for inner harbor baltimore in 2022
{"standalone_question":"what is the water quality score for inner harbor baltimore in 2022","needs_csv":true,"task":"wqi","site":"inner harbor baltimore","parameters":[],"start_year":2022,"end_year":2022,"last_n_years":null,"month":null,"wants_chart":false}
"""


def _to_int(value, low=None, high=None):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    if low is not None and number < low:
        return None
    if high is not None and number > high:
        return None
    return number


def _validate(raw: dict, question: str) -> dict:
    """Coerce the LLM's JSON into a well-formed plan."""
    task = str(raw.get("task", "none")).lower().strip()
    if task not in TASKS:
        task = "none"

    params = raw.get("parameters") or []
    if isinstance(params, str):
        params = [params]
    params = [
        str(p).lower().strip().replace(" ", "_")
        for p in params
    ]
    params = [p for p in params if p in PARAMETER_NAMES]

    site = raw.get("site")
    site = str(site).strip() if site else None

    needs_csv = bool(raw.get("needs_csv")) and task not in {"none", "off_topic"}

    standalone = str(raw.get("standalone_question") or "").strip() or question

    return {
        "standalone_question": standalone,
        "needs_csv": needs_csv,
        "task": task if needs_csv or task == "off_topic" else "none",
        "site": site,
        "parameters": params,
        "start_year": _to_int(raw.get("start_year"), 1900, 2100),
        "end_year": _to_int(raw.get("end_year"), 1900, 2100),
        "last_n_years": _to_int(raw.get("last_n_years"), 1, 200),
        "month": _to_int(raw.get("month"), 1, 12),
        "wants_chart": bool(raw.get("wants_chart")),
        "source": "ai",
    }


def _parse_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError(f"No JSON object in router output: {text[:200]!r}")
    return json.loads(match.group(0))


def fallback_plan(question: str) -> dict:
    """Regex-based plan used only when the AI router is unavailable."""
    wants_chart = bool(re.search(
        r"\b(graph|graphs|plot|plots|chart|charts|trend|trends|visualize|visualise)\b",
        question, re.IGNORECASE,
    ))
    return {
        "standalone_question": question,
        "needs_csv": True,      # let panalyze's legacy regex path decide
        "task": "legacy",
        "site": None,
        "parameters": [],
        "start_year": None,
        "end_year": None,
        "last_n_years": None,
        "month": None,
        "wants_chart": wants_chart,
        "source": "fallback",
    }


_BAND_LINE = re.compile(r"Band of the median value \(([^)]*)\): ([^.]+)\.")
_PARAM_LINE = re.compile(r"^Parameter: ([^;]+);", re.M)


def previous_turn_context(messages: list[dict]) -> str | None:
    """Structured summary of the latest assistant turn: its site, parameters and bands.

    Lets the router resolve "that" in follow-ups even when the answer text is long.
    """
    for message in reversed(messages):
        if message.get("role") != "assistant" or not message.get("plan"):
            continue
        plan = message["plan"]
        parts = []
        if plan.get("site"):
            parts.append(f"site={plan['site']}")
        if plan.get("parameters"):
            parts.append("parameters=" + ",".join(plan["parameters"]))
        context = (message.get("water_result") or {}).get("context", "")
        findings = []
        for block in context.split("DATASET-VERIFIED CALCULATIONS")[1:]:
            name = _PARAM_LINE.search(block)
            band = _BAND_LINE.search(block)
            if name and band:
                findings.append(f"{name.group(1).strip()} median {band.group(1)} -> {band.group(2).strip()}")
        if findings:
            parts.append("findings: " + "; ".join(findings))
        if plan.get("standalone_question"):
            parts.append(f"previous question: {plan['standalone_question']}")
        return "; ".join(parts) if parts else None
    return None


def interpret_question(messages: list[dict], question: str) -> dict:
    """Return a routing plan for `question`, using recent chat history for references."""
    history = []
    for message in [m for m in messages if m["role"] in {"user", "assistant"}][-4:]:
        content = str(message.get("content", ""))
        if message["role"] == "assistant" and len(content) > 600:
            content = content[:600] + " ..."
        history.append({"role": message["role"], "content": content})

    previous = previous_turn_context(messages)
    router_messages = [
        {"role": "system", "content": ROUTER_PROMPT},
        *history,
        {"role": "user", "content": (
            (f"PREVIOUS TURN CONTEXT: {previous}\n" if previous else "")
            + f"Q: {question}\nReturn the JSON object only."
        )},
    ]

    try:
        response = client.chat.completions.create(
            model=ROUTER_MODEL,
            messages=router_messages,
            temperature=0,
            timeout=30,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        plan = _validate(_parse_json(response.choices[0].message.content or ""), question)
    except Exception as error:  # network, timeout, bad JSON: never break the app
        print(f"Router fallback ({type(error).__name__}): {error}", flush=True)
        plan = fallback_plan(question)

    print("ROUTER PLAN:", json.dumps(plan), flush=True)
    return plan

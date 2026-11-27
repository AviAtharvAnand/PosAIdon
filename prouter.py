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

TASKS = {"trend", "values", "inventory", "ranking", "wqi", "none"}
PARAMETER_NAMES = {"ph", "dissolved_oxygen", "temperature", "turbidity"}

ROUTER_PROMPT = """/no think

You route questions for PosAIdon, a water-quality assistant. It has:
- MonitorWater CSV: historical measurements (pH, dissolved oxygen, water temperature, turbidity) at named monitoring sites, 2000s-present.
- Scientific documentation explaining water-quality concepts.

Return ONLY a JSON object with exactly these keys:
{
  "standalone_question": string,  // the latest question rewritten to stand alone; resolve "it", "there", "that", "same site" from history. Otherwise copy it unchanged.
  "needs_csv": boolean,           // true if answering needs measurements from the CSV (a site's values, trends, history, rankings, WQI, available data). false for purely conceptual/general questions.
  "task": "trend" | "values" | "inventory" | "ranking" | "wqi" | "none",
      // trend: change over time / history at a site
      // values: specific measurements (on a date, average, min, max)
      // inventory: which parameters/data exist at a site
      // ranking: comparing or listing sites across the whole dataset
      // wqi: water quality index / score / rating
      // none: needs_csv is false
  "site": string | null,          // the monitoring site exactly as the user named it (after resolving references), else null
  "parameters": [ "ph" | "dissolved_oxygen" | "temperature" | "turbidity" ],  // [] means not specified (use all)
  "start_year": integer | null,
  "end_year": integer | null,     // for "since 2020" set start_year 2020 and end_year null
  "last_n_years": integer | null, // for "last 5 years"
  "month": integer | null,        // 1-12 if a month is named
  "wants_chart": boolean          // true if a graph/plot/chart/visual would help or is requested: trends and comparisons over time -> true; single values or concepts -> false
}

Examples:
Q: what is the trend for inner baltimore harbor
{"standalone_question":"what is the trend for inner baltimore harbor","needs_csv":true,"task":"trend","site":"inner baltimore harbor","parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":true}
Q: what is dissolved oxygen and why does it matter?
{"standalone_question":"what is dissolved oxygen and why does it matter?","needs_csv":false,"task":"none","site":null,"parameters":[],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
Q: what was the pH at Walker Creek in July 2021
{"standalone_question":"what was the pH at Walker Creek in July 2021","needs_csv":true,"task":"values","site":"Walker Creek","parameters":["ph"],"start_year":2021,"end_year":2021,"last_n_years":null,"month":7,"wants_chart":false}
(History: user asked about Cedar River pH) Q: how has turbidity changed there since 2018?
{"standalone_question":"how has turbidity changed at Cedar River since 2018?","needs_csv":true,"task":"trend","site":"Cedar River","parameters":["turbidity"],"start_year":2018,"end_year":null,"last_n_years":null,"month":null,"wants_chart":true}
Q: which sites have the highest pH?
{"standalone_question":"which sites have the highest pH?","needs_csv":true,"task":"ranking","site":null,"parameters":["ph"],"start_year":null,"end_year":null,"last_n_years":null,"month":null,"wants_chart":false}
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

    needs_csv = bool(raw.get("needs_csv")) and task != "none"

    standalone = str(raw.get("standalone_question") or "").strip() or question

    return {
        "standalone_question": standalone,
        "needs_csv": needs_csv,
        "task": task if needs_csv else "none",
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


def interpret_question(messages: list[dict], question: str) -> dict:
    """Return a routing plan for `question`, using recent chat history for references."""
    history = []
    for message in [m for m in messages if m["role"] in {"user", "assistant"}][-4:]:
        content = str(message.get("content", ""))
        if message["role"] == "assistant" and len(content) > 600:
            content = content[:600] + " ..."
        history.append({"role": message["role"], "content": content})

    router_messages = [
        {"role": "system", "content": ROUTER_PROMPT},
        *history,
        {"role": "user", "content": f"Q: {question}\nReturn the JSON object only."},
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

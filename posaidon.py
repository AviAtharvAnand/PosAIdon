import os
import streamlit as st
from psearch import search
from dotenv import load_dotenv
from openai import OpenAI
from openai import BadRequestError
from openai import APITimeoutError
from openai import APIConnectionError
import time
import httpx
import re
from panalyze import analyze_question
import pandas as pd
from pathlib import Path

load_dotenv()
client = OpenAI(api_key=os.environ["NRP_LLM_TOKEN"],
                base_url=os.environ.get("NRP_LLM_BASE_URL", "https://ellm.nrp-nautilus.io/v1"))

st.set_page_config(page_title="PosAIdon", page_icon="🔱")
st.title("🔱 PosAIdon", anchor = False)
st.caption("Your AI-Power Water Quality Intelligence System.")

with st.sidebar:
    st.header("Settings")
    if st.button("🗑️ Clear chat"):
        st.session_state.pop("messages", None)
        st.session_state.pop("last_water_query", None)
        st.rerun()
    st.divider()

    st.subheader("Water Quality Data")

    csv_path = (
        Path(__file__).resolve().parent
        / "water_csv"
        / "monitorwater_cleaned.csv"
    )

    if csv_path.exists():
        with open(csv_path, "rb") as csv_file:
            st.download_button(
                label="Download MonitorWater Dataset",
                data=csv_file,
                file_name="monitorwater_cleaned.csv",
                mime="text/csv",
                icon=":material/download:",
                use_container_width=True
            )

        st.caption(
            "Download the cleaned historical water-quality "
            "dataset used by PosAIdon."
        )
    else:
        st.warning("Dataset file is unavailable.")

# - If the CSV has no matching observation, clearly state that the requested data is unavailable.
# - Never invent numerical measurements.
system_prompt ={
            "role": "system", "content": 
            """
                For every question:
                - If MONITORWATER CSV ANALYSIS is provided, treat it as the authoritative source for historical measurements, dates, locations, and calculated statistics.
                - Answer questions about specific measurements directly using the CSV results.
                - Use retrieved Markdown documentation to explain scientific concepts and ecological implications.
                - Never replace or contradict CSV measurements with general knowledge.
                - For general water-quality questions, prioritize the provided scientific documentation.

                The application has direct access to the MonitorWater CSV through its Python analysis tools.

                When MONITORWATER CSV ANALYSIS is provided:
                - Treat the calculated results as authoritative.
                - Explain the findings without inventing additional data.
                - Never claim that you cannot access the CSV when verified
                results have been provided.
                - Distinguish monitoring sites, sampling records and
                water-quality measurements.
                - Explain limitations caused by sparse or uneven sampling.
                - Do not generalize rankings into water-safety conclusions.

                When interpreting water-quality observations:
                - Use the EarthEcho Analysis Dictionary when relevant.
                - Explain possible causes, ecological impacts, and retesting steps.
                - Treat potential causes as hypotheses, not confirmed diagnoses.
                - Never invent measurements missing from the CSV.
                - Do not treat reference ranges as universal safety standards.
                - Do not calculate a Water Quality Index using this dictionary alone.

                For historical trend questions:
                - If year-by-year statistics are present in MONITORWATER CSV ANALYSIS, report those statistics directly.
                - Do not say yearly data is unavailable when annual measurements or annual summaries are provided.
                - Distinguish observed changes from a statistically validated trend.
                - If only an overall median is provided, do not invent annual values.
                - Never substitute data from a previous monitoring site.
            """
            }



def display_charts(water_result, question=""):
    if not water_result:
        return

    # Only display charts when explicitly requested.
    if not re.search(
        r"\b(graph|graphs|plot|plots|chart|charts|trend|trends|visualize|visualise)\b",
        question,
        re.IGNORECASE
    ):
        return

    q = question.lower()

    plots = water_result.get("plots", [])

    # Select the water-quality parameter requested by the user.
    if re.search(r"dissolved oxygen|\bdo\b", q):
        plots = [
            p for p in plots
            if "dissolved oxygen" in p.get("label", "").lower()
        ]
    elif re.search(r"\bph\b", q):
        plots = [
            p for p in plots
            if "ph" in p.get("label", "").lower()
        ]
    elif "temperature" in q:
        plots = [
            p for p in plots
            if "temperature" in p.get("label", "").lower()
        ]
    elif "turbidity" in q:
        plots = [
            p for p in plots
            if "turbidity" in p.get("label", "").lower()
        ]

    # When annual statistics exist for a requested historical trend,
    # prefer the annual chart instead of plotting every raw sample.
    if water_result.get("chart") and re.search(
        r"\b(trend|trends|annual|yearly)\b", q
    ):
        plots = []

    for plot in plots:
        points = plot.get("points", [])

        if not points:
            continue

        chart_df = pd.DataFrame(points)
        chart_df["date"] = pd.to_datetime(
            chart_df["date"], errors="coerce"
        )
        chart_df = chart_df.dropna(subset=["date", "value"])
        chart_df = chart_df.sort_values("date")

        if chart_df.empty:
            continue

        st.subheader(plot["label"])

        st.line_chart(
            chart_df,
            x="date",
            y="value",
            x_label="Sampling date",
            y_label=plot["label"]
        )

        if len(chart_df) < 3:
            st.caption(
                "Limited sampling: these points do not "
                "establish a reliable long-term trend."
            )

    # Preserve the existing annual chart functionality.
    if not plots and water_result.get("chart"):
        chart_df = pd.DataFrame(water_result["chart"])
        chart_df["year"] = chart_df["year"].astype(int).astype(str)

        st.line_chart(
            chart_df,
            x="year",
            y="median",
            x_label="Year",
            y_label=water_result.get("unit", "")
        )

        if water_result.get("is_wqi"):
            st.caption(
                "Provisional annual CCME-method WQI using illustrative "
                "objectives. Scores are not official water-quality ratings. "
                "Years with insufficient data are excluded."
            )
        else:
            st.caption(
                "Source: MonitorWater historical observations. "
                "Annual daily medians; sampling may be irregular."
            )


def display_sources(chunks):
    if not chunks:
        return

    with st.expander("📚 Sources"):
        for chunk in chunks:
            st.markdown(
                f"- [{chunk['title']}]({chunk['source_url']}) "
                f"*(distance: {chunk['score']:.3f}, "
                f"reranked: {chunk['rank_score']:.3f})*"
            )

if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

            if msg["role"] == "assistant":
                display_charts(
                    msg.get("water_result"),
                    msg.get("question", "")
                )
                display_sources(msg.get("chunks", []))


STOP_WORDS = {
    "a", "an", "the", "is", "are", "i", "you", "we",
    "do", "does", "did", "can", "could", "would", "should",
    "how", "what", "where", "when", "why", "which",
    "to", "of", "for", "in", "on", "with", "and", "or",
    "my", "your", "me", "please",
}

def rerank(question: str, chunks: list[dict]) -> list[dict]:
    normalized_question = question.lower().strip()

    query_words = [
        word
        for word in re.findall(r"\b[a-z0-9]+\b", normalized_question)
        if word not in STOP_WORDS
    ]

    query_word_set = set(query_words)

    # Build general two-word and three-word phrases.
    query_phrases = []

    for size in (2, 3):
        for index in range(len(query_words) - size + 1):
            phrase = " ".join(query_words[index:index + size])
            query_phrases.append(phrase)

    for chunk in chunks:
        title = chunk["title"].lower()
        text = chunk["text"].lower()
        combined_text = f"{title} {text}"

        title_words = set(
            re.findall(r"\b[a-z0-9]+\b", title)
        )

        text_words = set(
            re.findall(r"\b[a-z0-9]+\b", text)
        )

        title_matches = len(query_word_set & title_words)
        text_matches = len(query_word_set & text_words)

        # What fraction of the important query words occur in the chunk?
        coverage = (
            text_matches / len(query_word_set)
            if query_word_set
            else 0
        )

        # Reward matching any query phrase, not specific commands.
        phrase_matches = sum(
            1 for phrase in query_phrases
            if phrase in combined_text
        )

        chunk["rank_score"] = (
            chunk["score"]
            - title_matches * 0.08
            - text_matches * 0.03
            - coverage * 0.15
            - phrase_matches * 0.08
        )

    return sorted(chunks, key=lambda chunk: chunk["rank_score"])


def rewrite_single_query(question: str) -> str:
    query = question.lower().strip()

    query = re.sub(
        r"^(?:how\s+(?:do|can|could|would)\s+(?:i|you)\s+|"
        r"how\s+to\s+)",
        "",
        query,
    )

    query = re.sub(r"[?.!,;:]+$", "", query)

    return " ".join(query.split()) or question


def rewrite_search_query(question: str) -> str:
    questions = question.splitlines()

    rewritten_questions = [
        rewrite_single_query(item)
        for item in questions
        if item.strip()
    ]

    return " ".join(rewritten_questions)

def token_stream(messages):
    request_start = time.time()

    print("Sending request to LLM...", flush=True)

    
    stream = client.chat.completions.create(
        model="qwen3-small",
        messages=messages,
        stream=True,
        timeout=60,
        temperature=0.8,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
    )

    print(
        f"LLM request returned stream object after "
        f"{time.time() - request_start:.2f} seconds",
        flush=True,
    )

    first_token_received = False

    for chunk in stream:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            if not first_token_received:
                print(
                    f"First token received after "
                    f"{time.time() - request_start:.2f} seconds",
                    flush=True,
                )
                first_token_received = True

            yield content

def rewrite_follow_up_with_ai(messages, current_question):
    recent_history = [
        message
        for message in messages
        if message["role"] in {"user", "assistant"}
    ][-4:]

    rewrite_messages = [
        {
            "role": "system",
            "content": (
                "/no think\n\n"
                "Rewrite the latest user question as a standalone search query. "
                "Use conversation history only to resolve references such as "
                "'it', 'them', 'that', or 'there'. "
                "If the latest question is independent, return it unchanged. "
                "Do not answer the question. "
                "Return only the rewritten query."
            ),
        },
        *recent_history,
        {
            "role": "user",
            "content": current_question,
        },
    ]

    response = client.chat.completions.create(
        model="qwen3-small",
        messages=rewrite_messages,
        temperature=0,
        timeout=30,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
    )

    return response.choices[0].message.content.strip()

if prompt := st.chat_input("Ask about Water Quality..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    try:
        with st.spinner("Searching Water Quality docs..."):
            graph_requested = bool(re.search(
                r"\b(graph|graphs|plot|plots|chart|charts|visualize|visualise)\b",
                prompt.lower()
            ))

            # Only rewrite questions that explicitly refer to earlier context.
            needs_context = bool(re.search(
                r"\b(it|its|there|that|those|them|same|previous)\b",
                prompt,
                re.IGNORECASE
            ))

            if needs_context:
                standalone_query = rewrite_follow_up_with_ai(
                    st.session_state.messages[:-1],
                    prompt,
                )
            else:
                standalone_query = prompt

            # Analyze CSV if the question asks about historical measurements
            water_result = analyze_question(standalone_query)
            print("QUERY:", standalone_query, flush=True)
            print("RESULT KEYS:", list(water_result.keys()) if water_result else None, flush=True)
            print("PLOTS:", len(water_result.get("plots", [])) if water_result else 0, flush=True)
            print("CHART:", bool(water_result.get("chart")) if water_result else False, flush=True)
            
            # Show monitoring locations for a site-specific CSV question
            # if water_result is not None and not water_result.get("context", "").startswith("Please include"):
            #     from panalyze import _load, _find_site

            #     site, error = _find_site(_load(), standalone_query)

            #     if error is None and site is not None:
            #         points = site[["latitude", "longitude"]].dropna().drop_duplicates()

            #         if not points.empty:
            #             with st.chat_message("assistant"):
            #                 st.caption("Historical water-quality monitoring locations")
            #                 st.map(points)

            if water_result is not None and (
                water_result.get("plots") or water_result.get("chart")
            ):
                st.session_state["last_water_query"] = standalone_query

            search_query = rewrite_search_query(standalone_query)
            retrieved = search(search_query, k=10)
            reranked = rerank(search_query, retrieved)

            print("All retrieved and reranked chunks:", flush=True)
            for index, chunk in enumerate(reranked, start=1):
                print(
                    f"{index}. {chunk['title']} | "
                    f"distance: {chunk['score']:.3f} | "
                    f"reranked: {chunk['rank_score']:.3f}",
                    flush=True,
                )

            if not reranked and water_result is None:
                st.error("No documentation chunks were returned by search.")
                st.stop()

            chunks = reranked[:5]

            print(f"Original question: {prompt}", flush=True)
            print(f"Rewritten search query: {search_query}", flush=True)

            print("\nChunks being sent to the LLM:", flush=True)

            for index, chunk in enumerate(chunks, start=1):
                print(
                    f"\n===== Chunk {index}: {chunk['title']} =====\n"
                    f"Source: {chunk['source_url']}\n"
                    f"Distance: {chunk['score']:.3f}\n"
                    f"Reranked: {chunk['rank_score']:.3f}\n\n"
                    f"{chunk['text']}\n",
                    flush=True,
                )

    except BadRequestError as error:
        print(f"Embedding gateway error: {error}", flush=True)
        st.error(
            "The embedding service is currently unavailable. "
            "Please try again shortly."
        )
        st.stop()
    
    context = "\n\n---\n\n".join(f"[Source: {c['title']}]\n{c['text']}" for c in chunks)
    if water_result is not None:
        csv_context = water_result["context"]

        context = (
            "MONITORWATER CSV ANALYSIS:\n"
            + csv_context
            + "\n\n"
            + context
        )
    print("\n" + "=" * 80, flush=True)
    print("FULL CONTEXT SENT TO LLM", flush=True)
    print("=" * 80, flush=True)
    print(context, flush=True)
    print("=" * 80 + "\n", flush=True)

    grounded = f"""

    /no think

    DOCUMENTATION:
    {context}
    If MONITORWATER CSV ANALYSIS is provided:
    - Use the calculated statistics exactly.
    - Do not invent measurements or trends.
    - Explain sampling limitations when relevant.
    - Cite the numerical data as MonitorWater historical observations.
    - Do not claim that water is safe or unsafe based only on these measurements.
    - When individual sampling dates are provided in MONITORWATER CSV ANALYSIS,
    use those exact dates to answer the user's question.
    - Do not claim that a date or measurement is unavailable when
    it is explicitly included in the CSV analysis.

    QUESTION:
    {prompt}
    """
    conversation_history = [
        message
        for message in st.session_state.messages[1:-1]
        if message["role"] in {"user", "assistant"}
    ]

    messages_for_llm = [
        system_prompt,
        *conversation_history,
        {
            "role": "user",
            "content": grounded,
        },
    ]

    with st.chat_message("assistant"):
        print("Calling LLM...", flush=True)
        prompt_characters = sum(
            len(message.get("content", ""))
            for message in messages_for_llm
        )

        print(f"Messages sent: {len(messages_for_llm)}", flush=True)

        print(f"Total prompt size: {prompt_characters} characters", flush=True)
        try:
            with st.spinner("Generating answer..."):
                has_graph_data = (
                    water_result is not None
                    and (
                        water_result.get("plots")
                        or water_result.get("chart")
                    )
                )

                if graph_requested and has_graph_data:
                    answer = (
                        "Here are the graphs generated directly from "
                        "the MonitorWater observations."
                    )
                    st.markdown(answer)
                else:
                    answer = st.write_stream(token_stream(messages_for_llm))

                # Display individual parameter charts.
                display_charts(water_result, prompt)

        except (APITimeoutError, httpx.ReadTimeout) as error:
            print(f"LLM timeout: {error}", flush=True)
            st.error(
                "The model stopped responding before completing the answer. "
                "Please try again."
            )
            st.stop()

        except APIConnectionError as error:
            print(f"LLM connection error: {error}", flush=True)
            st.error("Could not connect to the LLM service.")
            st.stop()
        print("LLM finished", flush=True)

        display_sources(chunks)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "question": prompt,
        "water_result": water_result,
        "chunks": chunks
    })
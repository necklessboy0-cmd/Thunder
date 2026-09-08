# ============================================================
# RESEARCH GUIDE — NATIVE STREAMLIT RESEARCH ENGINE
# No Gemini API • No OpenAI API • No API key required
#
# Features:
#   • Live web search through DDGS
#   • Web-page text extraction
#   • 5W1H analysis
#   • Possible fact/evidence detection
#   • Possible myth/warning detection
#   • News search
#   • Image search
#   • Source comparison
#   • Native Streamlit UI
# ============================================================

import html
import json
import re
from urllib.parse import urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup
from ddgs import DDGS


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

APP_TITLE = "Research Guide"
MAX_RESULTS = 10
MAX_PAGE_CHARS = 7000
MAX_SOURCE_CHARS = 45000
REQUEST_TIMEOUT = 12

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0 Safari/537.36"
    )
}


# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------------------

st.markdown(
    """
    <style>
        :root {
            --rg-top: #dff3ff;
            --rg-mid: #b9e5fb;
            --rg-bottom: #5d9ed0;
            --rg-purple: #d9c7f4;
            --rg-purple-border: #bda1e2;
            --rg-text: #18324a;
            --rg-muted: #58718a;
            --rg-white: rgba(255,255,255,.88);
        }

        .stApp {
            background:
                linear-gradient(
                    180deg,
                    var(--rg-top) 0%,
                    var(--rg-mid) 45%,
                    var(--rg-bottom) 100%
                );
            color: var(--rg-text);
            min-height: 100vh;
        }

        [data-testid="stHeader"] {
            background: rgba(223,243,255,.72);
            backdrop-filter: blur(12px);
        }

        [data-testid="stSidebar"] {
            background: rgba(241,249,255,.94);
            border-right: 1px solid rgba(70,130,170,.16);
        }

        [data-testid="stSidebar"] * {
            color: var(--rg-text);
        }

        .block-container {
            max-width: 1120px;
            padding-top: 1.4rem;
            padding-bottom: 2.5rem;
        }

        /* Minimal brand — no lightning, no unnecessary description */
        .thunder-title {
            text-align: center;
            font-size: clamp(2.3rem, 5vw, 3.8rem);
            line-height: 1;
            font-weight: 850;
            letter-spacing: -0.045em;
            margin: .35rem 0 1rem;
            color: #254e70;
            animation: rgFade .55s ease-out both;
        }

        /* Requested light-purple bar between the upper and main areas */
        .research-bar {
            width: min(760px, 86%);
            margin: 0 auto 1.15rem;
            padding: .72rem 1.2rem;
            text-align: center;
            border-radius: 12px;
            background: linear-gradient(90deg, #e7dafa, var(--rg-purple), #e7dafa);
            border: 1px solid var(--rg-purple-border);
            color: #5c4779;
            font-size: .94rem;
            font-weight: 700;
            box-shadow: 0 7px 22px rgba(91,65,130,.10);
            animation: rgBarIn .65s .08s ease-out both;
        }

        /* Search panel */
        div[data-testid="stForm"] {
            background: rgba(255,255,255,.76);
            border: 1px solid rgba(84,145,183,.25);
            border-radius: 18px;
            padding: .9rem;
            box-shadow: 0 14px 35px rgba(40,88,120,.14);
            backdrop-filter: blur(10px);
            animation: rgFade .65s .12s ease-out both;
        }

        div[data-testid="stTextInput"] label {
            color: var(--rg-text);
            font-weight: 700;
        }

        div[data-testid="stTextInput"] input {
            background: rgba(255,255,255,.96) !important;
            color: var(--rg-text) !important;
            border: 1px solid rgba(74,137,179,.30) !important;
            border-radius: 12px !important;
            min-height: 50px;
            font-size: 1rem;
            transition: border-color .2s ease, box-shadow .2s ease;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: #7c65a5 !important;
            box-shadow: 0 0 0 3px rgba(124,101,165,.12) !important;
        }

        div.stButton > button,
        button[kind="primary"],
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #8d76b4, #765a9f) !important;
            color: white !important;
            border: 0 !important;
            border-radius: 12px !important;
            min-height: 50px;
            font-weight: 800 !important;
            letter-spacing: .02em;
            box-shadow: 0 8px 20px rgba(91,70,125,.18);
            transition: transform .18s ease, box-shadow .18s ease;
        }

        div.stButton > button:hover,
        button[kind="primary"]:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px);
            box-shadow: 0 11px 25px rgba(91,70,125,.24);
        }

        /* Navigation */
        button[data-baseweb="tab"] {
            color: #42647d;
            font-weight: 750;
            transition: color .18s ease, transform .18s ease;
        }

        button[data-baseweb="tab"]:hover {
            color: #5c4779;
            transform: translateY(-1px);
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #674b8b;
        }

        div[data-baseweb="tab-highlight"] {
            background: #8064a8;
            height: 3px;
            border-radius: 8px;
        }

        /* Result cards */
        .source-card {
            background: rgba(255,255,255,.84);
            border: 1px solid rgba(75,137,177,.20);
            border-radius: 15px;
            padding: 1rem 1.1rem;
            margin-bottom: .75rem;
            box-shadow: 0 8px 22px rgba(41,91,123,.10);
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
            animation: rgCardIn .4s ease-out both;
        }

        .source-card:hover {
            transform: translateY(-2px);
            border-color: rgba(116,88,157,.32);
            box-shadow: 0 12px 28px rgba(41,91,123,.15);
        }

        .source-number {
            color: #73579a;
            font-weight: 850;
            font-size: .95rem;
        }

        .small-muted {
            color: var(--rg-muted);
            font-size: .82rem;
        }

        .verdict-box {
            background: rgba(255,255,255,.82);
            border: 1px solid rgba(124,101,165,.24);
            border-radius: 16px;
            padding: 1.1rem;
            box-shadow: 0 10px 28px rgba(50,83,108,.12);
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
            border-color: rgba(72,132,172,.18);
        }

        hr {
            border-color: rgba(54,111,149,.15) !important;
        }

        section.main > div {
            animation: rgPage .4s ease-out both;
        }

        @keyframes rgFade {
            from { opacity: 0; transform: translateY(-7px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes rgBarIn {
            from { opacity: 0; transform: scaleX(.96); }
            to { opacity: 1; transform: scaleX(1); }
        }

        @keyframes rgCardIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes rgPage {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @media (max-width: 700px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .thunder-title {
                font-size: 2.65rem;
            }

            div[data-testid="stForm"] {
                border-radius: 15px;
                padding: .7rem;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: .01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: .01ms !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# SEARCH
# ------------------------------------------------------------

def build_research_query(query: str, filters: dict):
    """Translate the visible research filters into search-engine constraints."""
    parts = [query.strip()] if query.strip() else []

    database_domains = {
        "Google Scholar": "scholar.google.com",
        "IEEE Xplore": "ieeexplore.ieee.org",
        "PubMed": "pubmed.ncbi.nlm.nih.gov",
        "Crossref": "crossref.org",
        "arXiv": "arxiv.org",
        "Semantic Scholar": "semanticscholar.org",
        "DOAJ": "doaj.org",
        "JSTOR": "jstor.org",
        "ScienceDirect": "sciencedirect.com",
        "SpringerLink": "link.springer.com",
        "Wiley": "onlinelibrary.wiley.com",
        "ACM Digital Library": "dl.acm.org",
    }

    selected_db = filters.get("database", "Any database")
    if selected_db in database_domains:
        parts.append(f"site:{database_domains[selected_db]}")

    source_types = filters.get("source_types", [])
    source_terms = {
        "Journal article": '"journal article"',
        "Conference paper": '"conference paper"',
        "Book": 'book',
        "Book chapter": '"book chapter"',
        "Thesis / dissertation": 'thesis dissertation',
        "Preprint": preprint,
        "Technical report": '"technical report"',
        "Government report": '"government report"',
        "Dataset": dataset,
        "Patent": patent,
        "News article": '"news article"',
        "Systematic review": '"systematic review"',
        "Meta-analysis": '"meta-analysis"',
    }
    if source_types:
        parts.append("(" + " OR ".join(source_terms[x] for x in source_types if x in source_terms) + ")")

    if filters.get("author"):
        parts.append(f'"{filters["author"].strip()}"')
    if filters.get("publisher"):
        parts.append(f'"{filters["publisher"].strip()}"')
    if filters.get("journal"):
        parts.append(f'"{filters["journal"].strip()}"')
    if filters.get("location"):
        parts.append(f'"{filters["location"].strip()}"')

    language_terms = {
        "English": "English", "Urdu": "Urdu", "Arabic": "Arabic",
        "Chinese": "Chinese", "Spanish": "Spanish", "French": "French",
        "German": "German"
    }
    language = filters.get("language", "Any language")
    if language in language_terms:
        parts.append(language_terms[language])

    methods = filters.get("methods", [])
    if methods:
        parts.append("(" + " OR ".join(f'"{m}"' for m in methods) + ")")

    if filters.get("peer_reviewed"):
        parts.append('"peer reviewed"')
    if filters.get("open_access"):
        parts.append('"open access"')
    if filters.get("q1"):
        parts.append('"Q1"')

    date_from = filters.get("date_from")
    date_to = filters.get("date_to")
    if date_from:
        parts.append(f'after:{date_from}')
    if date_to:
        parts.append(f'before:{date_to}')

    return " ".join(parts)


def search_web(query: str, max_results: int = MAX_RESULTS, filters=None):
    query = (query or "").strip()
    filters = filters or {}

    if not query:
        return []

    search_query = build_research_query(query, filters)
    try:
        with DDGS(timeout=REQUEST_TIMEOUT) as ddgs:
            results = ddgs.text(
                search_query,
                region="wt-wt",
                safesearch="moderate",
                max_results=max_results,
                backend="auto",
            )

        return [
            {
                "title": item.get("title", "Untitled"),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
            }
            for item in results
        ]

    except Exception as exc:
        st.error(f"Search error: {exc}")
        return []


def search_news(query: str, max_results: int = 8):
    query = (query or "").strip()

    if not query:
        return []

    try:
        with DDGS(timeout=REQUEST_TIMEOUT) as ddgs:
            return list(
                ddgs.news(
                    query,
                    region="wt-wt",
                    safesearch="moderate",
                    max_results=max_results,
                )
            )
    except Exception as exc:
        st.warning(f"News search unavailable: {exc}")
        return []


def search_images(query: str, max_results: int = 8):
    query = (query or "").strip()

    if not query:
        return []

    try:
        with DDGS(timeout=REQUEST_TIMEOUT) as ddgs:
            return list(
                ddgs.images(
                    query,
                    region="wt-wt",
                    safesearch="moderate",
                    max_results=max_results,
                )
            )
    except Exception as exc:
        st.warning(f"Image search unavailable: {exc}")
        return []


# ------------------------------------------------------------
# WEB PAGE EXTRACTION
# ------------------------------------------------------------

def extract_page(url: str) -> str:
    if not url:
        return ""

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )

        content_type = response.headers.get("content-type", "").lower()

        if response.status_code != 200:
            return ""

        if "text/html" not in content_type:
            return ""

        soup = BeautifulSoup(response.text, "lxml")

        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "svg",
                "nav",
                "footer",
                "header",
                "form",
                "aside",
                "iframe",
            ]
        ):
            tag.decompose()

        text = soup.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text)

        return text[:MAX_PAGE_CHARS]

    except requests.RequestException:
        return ""
    except Exception:
        return ""


# ------------------------------------------------------------
# TEXT ANALYSIS
# ------------------------------------------------------------

def split_sentences(text: str):
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+", text)

    return [
        part.strip()
        for part in parts
        if len(part.strip()) > 35
    ]


def find_facts(text: str):
    keywords = [
        "according to",
        "official",
        "government",
        "study",
        "research",
        "researchers",
        "scientists",
        "report",
        "data",
        "confirmed",
        "published",
        "university",
        "survey",
        "evidence",
        "record",
        "announced",
    ]

    facts = []

    for sentence in split_sentences(text):
        lower = sentence.lower()

        if any(keyword in lower for keyword in keywords):
            facts.append(sentence)

    return facts[:8]


def find_myths(text: str):
    keywords = [
        "false",
        "fake",
        "hoax",
        "misleading",
        "debunked",
        "incorrect",
        "rumor",
        "rumour",
        "not true",
        "unverified",
        "fabricated",
        "disinformation",
        "misinformation",
    ]

    myths = []

    for sentence in split_sentences(text):
        lower = sentence.lower()

        if any(keyword in lower for keyword in keywords):
            myths.append(sentence)

    return myths[:8]


def analyze_5w1h(query: str, sources_text: str):
    sentences = split_sentences(sources_text)

    result = {
        "WHO": (
            "The available source material does not clearly establish "
            "who is involved."
        ),
        "WHAT": f"The search concerns: {query}.",
        "WHEN": (
            "The available sources did not provide a clearly established "
            "date."
        ),
        "WHERE": (
            "The available sources did not provide a clearly established "
            "location."
        ),
        "WHY": (
            "The available sources do not provide enough evidence to "
            "establish the reason."
        ),
        "HOW": (
            "The available sources describe the subject, but additional "
            "source comparison may be required."
        ),
    }

    if not sentences:
        return result

    for sentence in sentences:
        lower = sentence.lower()

        if (
            "according to" in lower
            or "official" in lower
            or "government" in lower
        ):
            result["WHO"] = sentence
            break

    for sentence in sentences:
        if re.search(r"\b(19|20)\d{2}\b", sentence):
            result["WHEN"] = sentence
            break

    for sentence in sentences:
        lower = sentence.lower()

        if any(
            term in lower
            for term in ["because", "due to", "reason", "caused by"]
        ):
            result["WHY"] = sentence
            break

    for sentence in sentences:
        lower = sentence.lower()

        if any(
            term in lower
            for term in [
                "located",
                "location",
                "in the city",
                "in the country",
                "at the",
            ]
        ):
            result["WHERE"] = sentence
            break

    for sentence in sentences:
        lower = sentence.lower()

        if any(
            term in lower
            for term in [
                "how it works",
                "by using",
                "through",
                "process",
                "method",
                "works by",
            ]
        ):
            result["HOW"] = sentence
            break

    return result


# ------------------------------------------------------------
# SOURCE COLLECTION
# ------------------------------------------------------------

def collect_source_text(results):
    pieces = []
    page_status = []

    # Read a limited number of pages so one search does not
    # generate excessive traffic or take too long.
    for index, result in enumerate(results[:6], start=1):
        snippet = result.get("snippet", "")
        url = result.get("url", "")

        if snippet:
            pieces.append(snippet)

        page_text = extract_page(url)

        if page_text:
            pieces.append(page_text)
            page_status.append((index, True))
        else:
            page_status.append((index, False))

    return "\n".join(pieces)[:MAX_SOURCE_CHARS], page_status


# ------------------------------------------------------------
# RENDER SEARCH RESULTS
# ------------------------------------------------------------

def render_search_results(results):
    st.subheader("Search Results")

    if not results:
        st.warning("No search results were returned.")
        return

    for index, result in enumerate(results, start=1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        snippet = result.get("snippet", "")

        domain = ""
        if url:
            try:
                domain = urlparse(url).netloc.replace("www.", "")
            except Exception:
                domain = ""

        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-number">
                    {index:02d}
                </div>
                <div style="font-size:1.08rem;font-weight:800;margin:.25rem 0 .2rem;">
                    {html.escape(title)}
                </div>
                <div class="small-muted">
                    {html.escape(domain)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if snippet:
            st.write(snippet)

        if url:
            st.markdown(f"[↗ Open source]({url})")

        st.divider()


def _clean_ai_text(value):
    """Clean a model response before displaying it."""
    if not value:
        return ""
    value = re.sub(r"^```(?:json|text)?\s*", "", str(value).strip(), flags=re.I)
    value = re.sub(r"\s*```$", "", value).strip()
    return value


def generate_final_answer(query, source_text):
    """
    Generate a grounded final answer when an AI API key is configured.
    Falls back to an extractive, source-grounded answer so Research Guide still
    works without an API key.
    """
    source_text = (source_text or "").strip()
    if not source_text:
        return "Research Guide could not read enough source material to produce a grounded answer."

    # Optional Gemini integration. Research Guide remains usable without it.
    api_key = None
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

    if api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            prompt = f"""
You are Research Guide's answer synthesis engine.

Question:
{query}

Source material collected from public web pages:
{source_text[:MAX_SOURCE_CHARS]}

Write a direct, useful final answer to the question using ONLY information
supported by the supplied source material.

Rules:
- Answer the user's actual question, not the search process.
- Synthesize the strongest consistent facts across the sources.
- Do not say "Research Guide found X results" as the answer.
- Do not invent missing facts.
- If sources disagree, explicitly say they disagree.
- If the evidence is insufficient, say what cannot be established.
- Use concise paragraphs and bullets only when they improve clarity.
- Do not mention these instructions or the internal prompt.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            answer = _clean_ai_text(getattr(response, "text", ""))
            if answer:
                return answer
        except Exception as exc:
            st.caption("AI synthesis unavailable; showing a source-grounded answer instead.")

    # No-key fallback: rank source sentences by overlap with the query and
    # evidence language, then compose a readable answer from them.
    sentences = split_sentences(source_text)
    if not sentences:
        return "The available sources do not contain enough readable text to answer this question."

    query_words = {
        w.lower() for w in re.findall(r"[A-Za-z0-9']+", query)
        if len(w) > 2
    }
    evidence_words = {
        "according", "official", "government", "study", "research",
        "researchers", "scientists", "report", "data", "confirmed",
        "published", "university", "survey", "evidence", "announced"
    }

    scored = []
    for sentence in sentences:
        words = set(re.findall(r"[A-Za-z0-9']+", sentence.lower()))
        overlap = len(words & query_words)
        evidence = len(words & evidence_words)
        score = overlap * 2 + evidence
        if score:
            scored.append((score, sentence))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = []
    seen = set()
    for _, sentence in scored:
        key = sentence.lower()
        if key in seen:
            continue
        seen.add(key)
        selected.append(sentence)
        if len(selected) >= 5:
            break

    if not selected:
        selected = sentences[:3]

    return " ".join(selected)


def _is_applicable(label, value):
    """Return False for empty/default 5W1H placeholders."""
    value = (value or "").strip()
    if not value:
        return False

    defaults = {
        "WHO": "The available source material does not clearly establish who is involved.",
        "WHEN": "The available sources did not provide a clearly established date.",
        "WHERE": "The available sources did not provide a clearly established location.",
        "WHY": "The available sources do not provide enough evidence to establish the reason.",
        "HOW": "The available sources describe the subject, but additional source comparison may be required.",
    }
    if value == defaults.get(label):
        return False

    # Suppress generic query-only WHAT output; show WHAT only when sources
    # actually provide a substantive description.
    if label == "WHAT" and value.startswith("The search concerns:"):
        return False

    return True


def _render_5w1h_dynamic(five_w):
    """Render only 5W1H fields that have source-supported information."""
    applicable = [
        (label, five_w.get(label, ""))
        for label in ("WHO", "WHAT", "WHEN", "WHERE", "WHY", "HOW")
        if _is_applicable(label, five_w.get(label, ""))
    ]

    if not applicable:
        return

    st.subheader("5W1H Analysis")

    for offset in range(0, len(applicable), 2):
        cols = st.columns(2)
        for col, (label, value) in zip(cols, applicable[offset:offset + 2]):
            with col:
                st.markdown(f"### {label}")
                st.write(value)

    st.divider()

# ------------------------------------------------------------
# RENDER ANALYSIS
# ------------------------------------------------------------

def render_analysis(query, results, source_text, page_status):
    five_w = analyze_5w1h(query, source_text)
    facts = find_facts(source_text)
    myths = find_myths(source_text)

    # The first thing users see is the answer, not a count of search pages.
    st.subheader("Research Guide Answer")
    with st.container():
        with st.spinner("Synthesizing the strongest source-supported answer..."):
            final_answer = generate_final_answer(query, source_text)

        st.markdown(
            f'<div class="verdict-box">{html.escape(final_answer).replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Show only applicable 5W1H fields. Empty / unsupported fields disappear.
    _render_5w1h_dynamic(five_w)

    st.subheader("Facts / Evidence")
    if facts:
        for fact in facts:
            st.markdown(f"- {fact}")
    else:
        st.info("No explicit fact/evidence statements were automatically identified.")

    if myths:
        st.divider()
        st.subheader("Myths / Warnings")
        for myth in myths:
            st.warning(myth)

    st.divider()

    st.subheader("Evidence Summary")
    successful_pages = sum(ok for _, ok in page_status)
    st.markdown(
        f"""
        <div class="verdict-box">
            <strong>Question:</strong> {html.escape(query)}<br><br>
            <strong>Sources considered:</strong> {len(results)}<br>
            <strong>Web pages successfully read:</strong> {successful_pages}/{len(page_status)}
            <br><br>
            The answer above is synthesized from the readable source material.
            Important claims should still be checked against the original sources.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Research Guide prioritizes source-supported information. When AI synthesis is "
        "configured through GEMINI_API_KEY, the final answer is generated from "
        "the collected source material; otherwise Research Guide uses a source-grounded fallback."
    )

# ------------------------------------------------------------
# NEWS TAB
# ------------------------------------------------------------

def render_news(query):
    st.subheader("📰 Research Guide News")

    with st.spinner("Searching news..."):
        news = search_news(query)

    if not news:
        st.info("No news results were returned.")
        return

    for index, item in enumerate(news, start=1):
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        body = item.get("body", "")
        date = item.get("date", "")
        source = item.get("source", "")

        st.markdown(f"### {index}. {title}")

        metadata = " • ".join(
            x for x in [source, date] if x
        )

        if metadata:
            st.caption(metadata)

        if body:
            st.write(body)

        if url:
            st.markdown(f"[🔗 Read article]({url})")

        st.divider()


# ------------------------------------------------------------
# IMAGE TAB
# ------------------------------------------------------------

def render_images(query):
    st.subheader("🖼️ Research Guide Images")

    with st.spinner("Searching images..."):
        images = search_images(query)

    if not images:
        st.info("No image results were returned.")
        return

    columns = st.columns(4)

    shown = 0

    for item in images:
        image_url = item.get("thumbnail") or item.get("image")
        title = item.get("title", "Image")

        if not image_url:
            continue

        with columns[shown % 4]:
            try:
                st.image(image_url, caption=title)
            except Exception:
                st.caption(title)

        shown += 1

    if shown == 0:
        st.info("Image URLs were returned but could not be displayed.")


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

with st.sidebar:
    st.header("Research Guide")



# ------------------------------------------------------------
# RESEARCH FILTERS
# ------------------------------------------------------------

def research_filter_panel():
    """Hidden-by-default research controls; no example content is rendered."""
    filters = st.session_state.get("research_filters", {})
    with st.expander("FILTERS", expanded=False):
        with st.form("research_filters_form", clear_on_submit=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                date_from = st.date_input("Date from", value=None, key="rg_date_from")
                date_to = st.date_input("Date to", value=None, key="rg_date_to")
                source_types = st.multiselect(
                    "Source type",
                    ["Journal article", "Conference paper", "Book", "Book chapter",
                     "Thesis / dissertation", "Preprint", "Technical report",
                     "Government report", "Dataset", "Patent", "News article",
                     "Systematic review", "Meta-analysis"],
                    key="rg_source_types",
                )
            with c2:
                author = st.text_input("Author", key="rg_author")
                publisher = st.text_input("Publisher", key="rg_publisher")
                journal = st.text_input("Journal / venue", key="rg_journal")
                language = st.selectbox(
                    "Publication language",
                    ["Any language", "English", "Urdu", "Arabic", "Chinese", "Spanish", "French", "German"],
                    key="rg_language",
                )
            with c3:
                location = st.text_input("Location", key="rg_location")
                database = st.selectbox(
                    "Academic database / catalog",
                    ["Any database", "Google Scholar", "IEEE Xplore", "PubMed", "Crossref",
                     "arXiv", "Semantic Scholar", "DOAJ", "JSTOR", "ScienceDirect",
                     "SpringerLink", "Wiley", "ACM Digital Library"],
                    key="rg_database",
                )
                methods = st.multiselect(
                    "Research method",
                    ["qualitative", "quantitative", "mixed methods", "experimental",
                     "observational", "survey", "case study", "longitudinal",
                     "cross-sectional", "systematic review", "meta-analysis"],
                    key="rg_methods",
                )

            q1, q2, q3, q4 = st.columns(4)
            with q1:
                peer_reviewed = st.checkbox("Peer reviewed", key="rg_peer_reviewed")
            with q2:
                open_access = st.checkbox("Open access", key="rg_open_access")
            with q3:
                q1_only = st.checkbox("Q1 journals", key="rg_q1")
            with q4:
                sort_by = st.selectbox(
                    "Sort",
                    ["Relevance", "Newest", "Most cited", "Impact factor"],
                    key="rg_sort",
                )

            citation_min = st.number_input("Minimum citation count", min_value=0, value=0, step=10, key="rg_citations")
            impact_min = st.number_input("Minimum impact factor", min_value=0.0, value=0.0, step=0.1, key="rg_impact")

            apply = st.form_submit_button("APPLY FILTERS", use_container_width=True)
            if apply:
                filters = {
                    "date_from": date_from.isoformat() if date_from else "",
                    "date_to": date_to.isoformat() if date_to else "",
                    "source_types": source_types, "author": author, "publisher": publisher,
                    "journal": journal, "language": language, "location": location,
                    "database": database, "methods": methods, "peer_reviewed": peer_reviewed,
                    "open_access": open_access, "q1": q1_only, "sort": sort_by,
                    "citation_min": citation_min, "impact_min": impact_min,
                }
                st.session_state["research_filters"] = filters
                st.session_state["research_filters_applied"] = True
                st.rerun()
    return st.session_state.get("research_filters", {})


research_filters = research_filter_panel()

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown(
    '<div class="thunder-title">Research Guide</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="research-bar">Simple Research · Search · Sources · Understanding</div>',
    unsafe_allow_html=True,
)



# ------------------------------------------------------------
# SEARCH FORM
# ------------------------------------------------------------

with st.form("thunder_search_form", clear_on_submit=False):
    query = st.text_input(
        "Search Research Guide",
        placeholder="",
        value=st.session_state.get("research_query", ""),
    )

    submitted = st.form_submit_button(
        "SEARCH",
        use_container_width=True,
    )


# ------------------------------------------------------------
# SEARCH EXECUTION
# ------------------------------------------------------------

if submitted:
    query = query.strip()

    st.session_state["research_query"] = query

    if not query:
        st.warning("Enter something to search.")
        st.stop()

    with st.spinner("Searching..."):
        results = search_web(query, filters=research_filters)

    if not results:
        st.error(
            "No search results were returned. Try another query or "
            "try again later."
        )
        st.stop()

    with st.spinner("Reading sources..."):
        source_text, page_status = collect_source_text(results)

    tab_search, tab_analysis, tab_news, tab_images = st.tabs(
        [
            "WEB",
            "RESULTS",
            "NEWS",
            "IMAGES",
        ]
    )

    with tab_search:
        render_search_results(results)

    with tab_analysis:
        render_analysis(
            query,
            results,
            source_text,
            page_status,
        )

    with tab_news:
        render_news(query)

    with tab_images:
        render_images(query)


# ------------------------------------------------------------
# WELCOME SCREEN
# ------------------------------------------------------------

else:
    st.info("Enter a topic or question above to begin.")

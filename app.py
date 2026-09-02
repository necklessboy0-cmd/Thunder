# ============================================================
# THUNDER ⚡ — NATIVE STREAMLIT SEARCH ENGINE
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
import re
from urllib.parse import urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup
from ddgs import DDGS


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

APP_TITLE = "Thunder ⚡"
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
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------------------

st.markdown(
    """
    <style>
        .thunder-title {
            text-align: center;
            font-size: 3.1rem;
            font-weight: 800;
            margin-bottom: 0;
            padding-top: 0.3rem;
        }

        .thunder-subtitle {
            text-align: center;
            opacity: 0.72;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }

        .source-card {
            border: 1px solid rgba(128,128,128,.25);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: .8rem;
        }

        .source-number {
            font-weight: 700;
            font-size: 1.05rem;
        }

        .small-muted {
            opacity: .65;
            font-size: .85rem;
        }

        .verdict-box {
            border: 1px solid rgba(128,128,128,.3);
            border-radius: 12px;
            padding: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# SEARCH
# ------------------------------------------------------------

def search_web(query: str, max_results: int = MAX_RESULTS):
    query = (query or "").strip()

    if not query:
        return []

    try:
        with DDGS(timeout=REQUEST_TIMEOUT) as ddgs:
            results = ddgs.text(
                query,
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
    st.subheader("🔎 Search Results")

    if not results:
        st.warning("No search results were returned.")
        return

    st.caption(f"{len(results)} result(s) found")

    for index, result in enumerate(results, start=1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        snippet = result.get("snippet", "")

        st.markdown(
            f"**{index}. {html.escape(title)}**"
        )

        if url:
            st.markdown(f"[🔗 Open source]({url})")

        if snippet:
            st.write(snippet)

        st.divider()


# ------------------------------------------------------------
# RENDER ANALYSIS
# ------------------------------------------------------------

def render_analysis(query, results, source_text, page_status):
    five_w = analyze_5w1h(query, source_text)
    facts = find_facts(source_text)
    myths = find_myths(source_text)

    st.subheader("🧩 5W1H Analysis")

    cols = st.columns(2)

    with cols[0]:
        st.markdown("### WHO")
        st.write(five_w["WHO"])

        st.markdown("### WHAT")
        st.write(five_w["WHAT"])

        st.markdown("### WHEN")
        st.write(five_w["WHEN"])

    with cols[1]:
        st.markdown("### WHERE")
        st.write(five_w["WHERE"])

        st.markdown("### WHY")
        st.write(five_w["WHY"])

        st.markdown("### HOW")
        st.write(five_w["HOW"])

    st.divider()

    st.subheader("✅ Facts / Evidence")

    if facts:
        for fact in facts:
            st.markdown(f"- {fact}")
    else:
        st.info(
            "No explicit fact/evidence statements were automatically "
            "identified."
        )

    st.divider()

    st.subheader("⚠️ Myths / Warnings")

    if myths:
        for myth in myths:
            st.warning(myth)
    else:
        st.info(
            "No explicit myth/debunking statements were automatically "
            "identified."
        )

    st.divider()

    st.subheader("🧠 Thunder Verdict")

    st.markdown(
        f"""
        <div class="verdict-box">
        Thunder found <strong>{len(results)}</strong> web result(s) for
        <strong>{html.escape(query)}</strong> and used available search
        information plus publicly accessible pages for preliminary analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "This is rule-based analysis, not an AI-generated guarantee of truth. "
        "Always inspect the original sources for important claims."
    )

    successful_pages = sum(ok for _, ok in page_status)

    if page_status:
        st.caption(
            f"Web pages successfully read: "
            f"{successful_pages}/{len(page_status)}"
        )


# ------------------------------------------------------------
# NEWS TAB
# ------------------------------------------------------------

def render_news(query):
    st.subheader("📰 Thunder News")

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
    st.subheader("🖼️ Thunder Images")

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
    st.header("⚡ Thunder")

    st.markdown(
        """
        **No API key required.**

        Thunder uses web search and rule-based analysis to organize
        information into search results, 5W1H, facts and warnings.
        """
    )

    st.divider()

    st.subheader("Capabilities")

    st.markdown(
        """
        - 🔎 Web search
        - 🧩 5W1H
        - ✅ Fact/evidence detection
        - ⚠️ Myth/warning detection
        - 📰 News search
        - 🖼️ Image search
        - 🌐 Web-page extraction
        - 🔑 No API key
        """
    )

    st.divider()

    st.caption(
        "Thunder is a research tool. It does not guarantee that "
        "search results are true."
    )


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown(
    '<div class="thunder-title">⚡ Thunder</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="thunder-subtitle">'
    "Free Web Search • 5W1H • Facts • Myths • No API Key"
    "</div>",
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# SEARCH FORM
# ------------------------------------------------------------

with st.form("thunder_search_form", clear_on_submit=False):
    query = st.text_input(
        "🔎 Search Thunder",
        placeholder="Search anything...",
        value=st.session_state.get("thunder_query", ""),
    )

    submitted = st.form_submit_button(
        "⚡ THUNDER SEARCH",
        use_container_width=True,
    )


# ------------------------------------------------------------
# SEARCH EXECUTION
# ------------------------------------------------------------

if submitted:
    query = query.strip()

    st.session_state["thunder_query"] = query

    if not query:
        st.warning("Enter something to search.")
        st.stop()

    with st.spinner("🔎 Thunder is searching the web..."):
        results = search_web(query)

    if not results:
        st.error(
            "No search results were returned. Try another query or "
            "try again later."
        )
        st.stop()

    with st.spinner("🌐 Reading available sources..."):
        source_text, page_status = collect_source_text(results)

    st.success(
        f"Thunder found {len(results)} web result(s)."
    )

    tab_search, tab_analysis, tab_news, tab_images = st.tabs(
        [
            "🔎 Search",
            "🧠 Analysis",
            "📰 News",
            "🖼️ Images",
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
    st.info(
        "Enter a question or topic above and press "
        "**⚡ THUNDER SEARCH**."
    )

    st.markdown("### Try an example")

    examples = [
        "What is quantum computing?",
        "Who discovered electricity?",
        "How does solar energy work?",
        "Is the Earth flat?",
        "What caused the 2008 financial crisis?",
    ]

    for example in examples:
        st.code(example)

    st.markdown(
        """
        ### What Thunder does

        **Search → Collect sources → Read available pages →
        Analyze → Compare evidence**

        The current analyzer is deliberately **rule-based** and does not
        use Gemini, OpenAI, or another cloud AI API.
        """
    )

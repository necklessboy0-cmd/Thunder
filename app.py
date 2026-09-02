import re
import html
import requests
import gradio as gr
from bs4 import BeautifulSoup
from ddgs import DDGS

# ============================================================
# SETTINGS
# ============================================================

MAX_RESULTS = 10
MAX_PAGE_CHARS = 7000
TIMEOUT = 12

HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0 Safari/537.36"
}

# ============================================================
# WEB SEARCH
# ============================================================

def search_web(query, max_results=MAX_RESULTS):

    query = (query or "").strip()

    if not query:
        return []

    try:

        with DDGS(timeout=TIMEOUT) as ddgs:

            results = ddgs.text(
                query,
                region="wt-wt",
                safesearch="moderate",
                max_results=max_results,
                backend="auto"
            )

        output = []

        for item in results:

            output.append({
                "title": item.get("title", "Untitled"),
                "url": item.get("href", ""),
                "snippet": item.get("body", "")
            })

        return output

    except Exception as e:

        print("SEARCH ERROR:", e)

        return []


# ============================================================
# NEWS SEARCH
# ============================================================

def search_news(query, max_results=8):

    try:

        with DDGS(timeout=TIMEOUT) as ddgs:

            results = ddgs.news(
                query,
                region="wt-wt",
                safesearch="moderate",
                max_results=max_results
            )

        return results

    except Exception as e:

        print("NEWS ERROR:", e)

        return []


# ============================================================
# IMAGE SEARCH
# ============================================================

def search_images(query, max_results=8):

    try:

        with DDGS(timeout=TIMEOUT) as ddgs:

            results = ddgs.images(
                query,
                region="wt-wt",
                safesearch="moderate",
                max_results=max_results
            )

        return results

    except Exception as e:

        print("IMAGE ERROR:", e)

        return []


# ============================================================
# WEB PAGE READER
# ============================================================

def extract_page(url):

    if not url:
        return ""

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        for tag in soup([
            "script",
            "style",
            "noscript",
            "svg",
            "nav",
            "footer",
            "header",
            "form",
            "aside"
        ]):

            tag.decompose()

        text = soup.get_text(
            " ",
            strip=True
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text[:MAX_PAGE_CHARS]

    except Exception:

        return ""


# ============================================================
# SENTENCE SPLITTER
# ============================================================

def split_sentences(text):

    if not text:
        return []

    parts = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        x.strip()
        for x in parts
        if len(x.strip()) > 35
    ]


# ============================================================
# EXTRACT POSSIBLE FACTS
# ============================================================

def find_facts(text):

    sentences = split_sentences(text)

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
        "announced"
    ]

    facts = []

    for sentence in sentences:

        lower = sentence.lower()

        if any(k in lower for k in keywords):

            facts.append(sentence)

    return facts[:8]


# ============================================================
# EXTRACT POSSIBLE MYTHS / WARNINGS
# ============================================================

def find_myths(text):

    sentences = split_sentences(text)

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
        "misinformation"
    ]

    myths = []

    for sentence in sentences:

        lower = sentence.lower()

        if any(k in lower for k in keywords):

            myths.append(sentence)

    return myths[:8]


# ============================================================
# 5W1H BASIC EXTRACTION
# ============================================================

def analyze_5w1h(query, sources_text):

    sentences = split_sentences(
        sources_text
    )

    if not sentences:

        return {
            "WHO": "Not enough source text.",
            "WHAT": query,
            "WHEN": "Not established.",
            "WHERE": "Not established.",
            "WHY": "Not established.",
            "HOW": "Not established."
        }

    # Simple evidence-based extraction.
    # This deliberately does NOT pretend to be an AI model.

    who = "Information about the people or organizations involved was not clearly established."

    what = (
        "The search concerns: "
        + query
        + "."
    )

    when = "The available sources did not provide a clearly established date."

    where = "The available sources did not provide a clearly established location."

    why = "The available sources do not provide enough evidence to establish the reason."

    how = "The available sources describe the subject, but additional source comparison may be required."

    # Try simple detection

    for s in sentences:

        lower = s.lower()

        if (
            "according to" in lower
            or "official" in lower
            or "government" in lower
        ):

            who = s
            break

    for s in sentences:

        if re.search(
            r"\b(19|20)\d{2}\b",
            s
        ):

            when = s
            break

    for s in sentences:

        if any(
            x in s.lower()
            for x in [
                "because",
                "due to",
                "reason",
                "caused by"
            ]
        ):

            why = s
            break

    return {
        "WHO": who,
        "WHAT": what,
        "WHEN": when,
        "WHERE": where,
        "WHY": why,
        "HOW": how
    }


# ============================================================
# THUNDER ANALYZER
# ============================================================

def thunder_analyze(query, results):

    if not results:

        return """
# ⚡ Thunder

No search results were found.

Try another query.
"""

    collected = []

    for result in results:

        collected.append(
            result.get("snippet", "")
        )

        url = result.get("url", "")

        # Read a few actual pages
        if url:

            page = extract_page(url)

            if page:

                collected.append(page)

    source_text = "\n".join(
        collected
    )

    # Limit analysis size

    source_text = source_text[:45000]

    five_w = analyze_5w1h(
        query,
        source_text
    )

    facts = find_facts(
        source_text
    )

    myths = find_myths(
        source_text
    )

    output = []

    output.append("# ⚡ Thunder Analysis")

    output.append(
        "\n## 5W1H"
    )

    output.append(
        "\n### WHO\n"
        + five_w["WHO"]
    )

    output.append(
        "\n### WHAT\n"
        + five_w["WHAT"]
    )

    output.append(
        "\n### WHEN\n"
        + five_w["WHEN"]
    )

    output.append(
        "\n### WHERE\n"
        + five_w["WHERE"]
    )

    output.append(
        "\n### WHY\n"
        + five_w["WHY"]
    )

    output.append(
        "\n### HOW\n"
        + five_w["HOW"]
    )

    # --------------------------------------------------------
    # FACTS
    # --------------------------------------------------------

    output.append(
        "\n## ✅ Facts / Evidence"
    )

    if facts:

        for fact in facts:

            output.append(
                "- " + fact
            )

    else:

        output.append(
            "No explicit fact/evidence statements were automatically identified."
        )

    # --------------------------------------------------------
    # MYTHS
    # --------------------------------------------------------

    output.append(
        "\n## ⚠️ Myths / Warnings"
    )

    if myths:

        for myth in myths:

            output.append(
                "- " + myth
            )

    else:

        output.append(
            "No explicit myth/debunking statements were automatically identified."
        )

    # --------------------------------------------------------
    # VERDICT
    # --------------------------------------------------------

    output.append(
        "\n## 🧠 Thunder Verdict"
    )

    output.append(
        "Thunder found "
        + str(len(results))
        + " web results. "
        "The result should be compared across multiple independent sources. "
        "Automatic keyword analysis is not a substitute for professional fact-checking."
    )

    return "\n".join(output)


# ============================================================
# MAIN THUNDER FUNCTION
# ============================================================

def thunder(query):

    query = (query or "").strip()

    if not query:

        yield """
# ⚡ Thunder

Enter something to search.
"""

        return

    yield (
        "# ⚡ Thunder\n\n"
        "🔎 Searching the live web...\n\n"
        "**Query:** `"
        + query
        + "`"
    )

    results = search_web(query)

    if not results:

        yield """
# ❌ Thunder

No results were returned.

Possible reasons:

- Search temporarily rate-limited
- Internet connection problem
- Search engine unavailable
- Query returned no results

Try again.
"""

        return

    # ========================================================
    # SEARCH RESULTS
    # ========================================================

    output = []

    output.append(
        "# 🔎 Thunder Search Results"
    )

    output.append(
        "\n**Query:** `"
        + query
        + "`"
    )

    output.append(
        "\n**Results:** "
        + str(len(results))
    )

    output.append(
        "\n---"
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        title = html.escape(
            result.get(
                "title",
                "Untitled"
            )
        )

        url = result.get(
            "url",
            ""
        )

        snippet = html.escape(
            result.get(
                "snippet",
                ""
            )
        )

        output.append(
            "\n## "
            + str(i)
            + ". "
            + title
        )

        if url:

            output.append(
                "\n🔗 "
                + url
            )

        if snippet:

            output.append(
                "\n\n"
                + snippet
            )

        output.append(
            "\n"
        )

    # ========================================================
    # ANALYSIS
    # ========================================================

    analysis = thunder_analyze(
        query,
        results
    )

    output.append(
        "\n---\n"
    )

    output.append(
        analysis
    )

    yield "\n".join(output)


# ============================================================
# GRADIO UI
# ============================================================

CSS = """

body {
    background: #f5f7fa;
}

.thunder-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    margin-top: 10px;
}

.thunder-subtitle {
    text-align: center;
    font-size: 17px;
    opacity: 0.75;
    margin-bottom: 25px;
}

textarea {
    font-size: 16px !important;
}

button {
    border-radius: 10px !important;
}

"""

with gr.Blocks(
    title="Thunder ⚡"
) as demo:

    gr.HTML(
        """
        <div class="thunder-title">
            ⚡ Thunder
        </div>

        <div class="thunder-subtitle">
            Free Web Search • 5W1H • Facts • Myths
        </div>
        """
    )

    with gr.Row():

        query = gr.Textbox(
            label="🔎 Search Thunder",
            placeholder="Search anything...",
            lines=2,
            scale=5
        )

        search_button = gr.Button(
            "⚡ SEARCH",
            variant="primary",
            scale=1
        )

    clear_button = gr.Button(
        "🗑️ Clear"
    )

    output = gr.Markdown(
        """
# ⚡ Welcome to Thunder

Enter a question or topic above.

Thunder will:

🔎 Search the live web  
📚 Collect search results  
🌐 Read available pages  
🧩 Extract 5W1H  
✅ Identify possible facts  
⚠️ Identify possible myths/warnings  
🧠 Produce a source-based analysis  

**No API key required.**
"""
    )

    search_button.click(
        thunder,
        inputs=query,
        outputs=output
    )

    query.submit(
        thunder,
        inputs=query,
        outputs=output
    )

    clear_button.click(
        lambda: ("", """
# ⚡ Thunder

Enter something to search.

**No API key required.**
"""),
        inputs=[],
        outputs=[
            query,
            output
        ]
    )


# ============================================================
# LAUNCH
# ============================================================

print()
print("=" * 55)
print("⚡ THUNDER — NO API KEY SEARCH ENGINE")
print("=" * 55)
print()
print("✅ Live web search")
print("✅ DDGS metasearch")
print("✅ Web page extraction")
print("✅ 5W1H")
print("✅ Facts")
print("✅ Myths / warnings")
print("✅ News-ready architecture")
print("✅ Image-search-ready architecture")
print("✅ Gradio UI")
print("❌ Gemini API")
print("❌ OpenAI API")
print("❌ API KEY")
print()
print("🚀 Starting Thunder...")
print()

demo.launch(
    share=True,
    debug=True,
    css=CSS
)

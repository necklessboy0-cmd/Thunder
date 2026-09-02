# ⚡ Thunder — Free Web Search & Fact Analyzer

> A lightweight, no-API-key web search engine with 5W1H analysis, fact detection, myth/warning detection, and a simple Gradio interface.

![Thunder](https://img.shields.io/badge/Thunder-⚡-yellow)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange)
![API Key](https://img.shields.io/badge/API%20Key-Not%20Required-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ⚡ Overview

**Thunder** is a lightweight web-search and information-analysis project designed to provide a simple alternative to API-dependent search applications.

Thunder searches the live web, collects search results, optionally reads publicly accessible web pages, and presents the information through a Gradio interface.

The current version requires **no Gemini API key, no OpenAI API key, and no paid API service**.

### What Thunder does

* 🔎 Live web search
* 🌐 Web-page text extraction
* 🧩 5W1H analysis
* ✅ Possible fact/evidence detection
* ⚠️ Possible myth/warning detection
* 📰 News-search support in the backend
* 🖼️ Image-search support in the backend
* 📚 Multiple-source comparison
* 🖥️ Gradio web interface
* 🚀 Temporary public Gradio URL
* 🔑 No API key required

---

# 🚀 Run Thunder in Google Colab

The easiest way to run Thunder is with Google Colab.

## 1. Open Google Colab

Create a new notebook:

https://colab.research.google.com/

## 2. Install dependencies

Run this in the **first code cell**:

```python
!pip install -q ddgs gradio beautifulsoup4 lxml
!pip install -q --force-reinstall --no-deps requests==2.32.4
```

Thunder uses `requests==2.32.4` because Google Colab requires that version.

Verify the version:

```python
import requests
print(requests.__version__)
```

Expected:

```text
2.32.4
```

---

## 3. Run Thunder

Paste the Thunder Python application into the next Colab cell and run it.

When the application starts, Gradio will display a temporary public URL similar to:

```text
https://xxxxxxxx.gradio.live/
```

Open that URL to use Thunder.

---

# 🖥️ Interface

Thunder provides a simple search interface:

```text
┌───────────────────────────────────────────────┐
│                  ⚡ Thunder                    │
│     Free Web Search • 5W1H • Facts • Myths   │
│                                               │
│  🔎 Search anything...       [⚡ SEARCH]       │
│                                               │
└───────────────────────────────────────────────┘
```

After searching, Thunder displays:

1. Search results
2. Source URLs
3. Search snippets
4. 5W1H analysis
5. Possible facts/evidence
6. Possible myths/warnings
7. A source-based verdict

---

# 🔎 Search

Thunder uses the `ddgs` Python package for web search.

A typical query might be:

```text
Who discovered electricity?
```

or:

```text
Is this viral claim true?
```

or:

```text
Latest developments in artificial intelligence
```

Thunder retrieves available web results and displays their titles, URLs, and snippets.

---

# 🧩 5W1H Analysis

Thunder attempts to organize information using the traditional **5W1H framework**:

| Question | Meaning                                 |
| -------- | --------------------------------------- |
| WHO      | Who is involved?                        |
| WHAT     | What happened or what is being claimed? |
| WHEN     | When did it happen?                     |
| WHERE    | Where did it happen?                    |
| WHY      | Why did it happen?                      |
| HOW      | How did it happen?                      |

The system uses information found in search results and publicly accessible pages.

---

# ✅ Fact Detection

Thunder looks for statements containing evidence-related language such as:

* According to
* Official
* Government
* Research
* Study
* Scientists
* Report
* Data
* Confirmed
* Published
* Evidence

These statements are presented as **possible evidence/facts**.

> Thunder does not guarantee that every detected statement is true. Users should verify important claims against the original sources.

---

# ⚠️ Myth & Warning Detection

Thunder also looks for language commonly associated with disputed or debunked claims, including:

* False
* Fake
* Hoax
* Misleading
* Debunked
* Incorrect
* Rumor
* Unverified
* Fabricated
* Misinformation
* Disinformation

These statements are presented as warnings for further investigation.

---

# 🌐 Web Page Extraction

Thunder attempts to retrieve publicly accessible pages from search results.

It removes common non-content elements such as:

* JavaScript
* CSS
* Navigation
* Headers
* Footers
* Forms
* Sidebars

The remaining text is used as additional material for the analysis.

Some websites may prevent automated requests. In those cases, Thunder simply continues with the available search information.

---

# 📰 News Search

The underlying `ddgs` integration also supports news searching.

The project architecture can be extended to provide a dedicated:

```text
📰 Thunder News
```

interface.

---

# 🖼️ Image Search

The underlying search library also supports image searches.

Thunder can therefore be extended with a dedicated:

```text
🖼️ Thunder Images
```

interface.

---

# 🔐 API Key Requirements

Thunder currently requires:

```text
Gemini API Key:    ❌
OpenAI API Key:    ❌
Google API Key:    ❌
Bing API Key:      ❌
Paid Search API:   ❌
```

The core application is designed to work without an API key.

---

# 🧠 Is Thunder an AI Fact Checker?

**Not in the current version.**

The current Thunder implementation is primarily a:

> **Web search + rule-based information analyzer**

It does not use Gemini, OpenAI, or another cloud LLM to generate its analysis.

Its fact/myth detection is based on keywords and extracted web content.

This is intentional because the current version is designed to run without API credentials.

---

# ⚠️ Important Accuracy Notice

Thunder should **not** be treated as an authoritative fact-checking organization.

Search results can contain:

* Incorrect information
* Outdated information
* Biased sources
* Satire
* Unverified claims
* Duplicate reporting
* AI-generated content
* Misleading headlines

Thunder therefore recommends checking the **original source** before accepting an important claim as fact.

For high-impact topics, compare multiple independent sources.

---

# 🛡️ Responsible Use

Thunder is intended for:

* Research
* Education
* Information discovery
* Source comparison
* General web searching
* Preliminary claim investigation

Do not rely on Thunder alone for decisions involving:

* Medical treatment
* Legal matters
* Financial decisions
* Safety-critical situations
* Emergency situations

Always consult an appropriate qualified source for high-stakes decisions.

---

# 📦 Dependencies

Thunder uses several Python packages:

```text
ddgs
gradio
requests
beautifulsoup4
lxml
```

Install them with:

```bash
pip install ddgs gradio beautifulsoup4 lxml
pip install --force-reinstall --no-deps requests==2.32.4
```

---

# 🗂️ Suggested Repository Structure

A simple GitHub repository can look like this:

```text
Thunder/
│
├── README.md
├── thunder.py
├── requirements.txt
└── LICENSE
```

A `requirements.txt` file can contain:

```text
ddgs
gradio
beautifulsoup4
lxml
requests==2.32.4
```

---

# 💻 Running Locally

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/Thunder.git
```

Enter the directory:

```bash
cd Thunder
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python thunder.py
```

The Gradio interface will provide a local address.

---

# ☁️ Google Colab

Thunder is particularly convenient in Google Colab because the application can be launched without configuring a local Python environment.

The notebook can also create a temporary public Gradio link using:

```python
demo.launch(
    share=True,
    debug=True,
    css=CSS
)
```

The public URL is temporary and is not permanent hosting.

---

# 🧪 Example Searches

Try queries such as:

```text
What is quantum computing?
```

```text
Who invented the telephone?
```

```text
Is the Earth flat?
```

```text
How does solar energy work?
```

```text
What caused the 2008 financial crisis?
```

```text
Is this health claim scientifically supported?
```

---

# 🔧 Troubleshooting

## Requests dependency conflict

If Colab reports:

```text
google-colab requires requests==2.32.4
```

run:

```python
!pip install -q --force-reinstall --no-deps requests==2.32.4
```

Then verify:

```python
import requests
print(requests.__version__)
```

It should show:

```text
2.32.4
```

---

## Gradio CSS warning

Newer Gradio versions expect CSS to be passed to `launch()`.

Use:

```python
with gr.Blocks(title="Thunder ⚡") as demo:
    ...
```

and:

```python
demo.launch(
    share=True,
    debug=True,
    css=CSS
)
```

instead of passing `css` directly to `gr.Blocks()`.

---

## No search results

If Thunder cannot retrieve results:

1. Check that Colab Internet access is available.
2. Run the search again.
3. Try a simpler query.
4. Check whether the search service is temporarily rate-limited.
5. Restart the Colab runtime if necessary.

---

# 🚧 Limitations

The current version has several limitations.

### 1. Rule-based analysis

The fact/myth system uses keyword-based analysis rather than a large language model.

### 2. Search dependency

Search availability depends on the external search providers used by `ddgs`.

### 3. Website restrictions

Some websites block automated requests.

### 4. No permanent hosting

A `gradio.live` share URL is temporary.

### 5. No guaranteed truth verification

Thunder reports and analyzes information found online; it does not establish absolute truth.

---

# 🛣️ Roadmap

Future versions may include:

* [ ] Local AI reasoning
* [ ] Better 5W1H extraction
* [ ] Source credibility scoring
* [ ] Source-to-source comparison
* [ ] Claim verification
* [ ] Dedicated news search
* [ ] Image search UI
* [ ] Audio/voice search
* [ ] Speech-to-text
* [ ] Browser-style result pages
* [ ] Search history
* [ ] Dark mode
* [ ] Source timestamps
* [ ] Domain reputation indicators
* [ ] Citation extraction
* [ ] Duplicate-source detection
* [ ] Local open-source LLM support
* [ ] Hugging Face deployment

---

# 🤝 Contributing

Contributions are welcome.

To contribute:

1. Fork the repository.
2. Create a new branch.

```bash
git checkout -b feature/my-feature
```

3. Make your changes.
4. Test Thunder.
5. Commit your changes.

```bash
git commit -m "Add new Thunder feature"
```

6. Push the branch.

```bash
git push origin feature/my-feature
```

7. Open a Pull Request.

---

# 📜 License

This project is intended to be released under the **MIT License**.

See `LICENSE` for the complete license text.

---

# ⚡ Thunder

**Search the web. Examine the evidence. Question the claim.**

> Thunder is a research and information-discovery tool, not an authoritative fact-checking service.

---

## ⭐ Support the Project

If Thunder is useful to you:

* ⭐ Star the repository
* 🐛 Report bugs
* 💡 Suggest features
* 🔧 Submit improvements
* 📢 Share the project

**Built with Python + DDGS + Gradio.**

# ⚡ Thunder

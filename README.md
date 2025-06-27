# AI Daily Briefing Engine

A command-line tool that automatically scrapes the latest AI news, digests the content of multiple articles, and generates a strategic summary tailored for an Applied Science Manager.

## Problem Statement

Technology leaders and applied scientists are inundated with a high volume of technical articles, newsletters, and research papers daily. It's challenging to stay current with relevant advancements while distinguishing signal from noise. This tool addresses this information overload by automating the process of retrieval and analysis, providing a high-level briefing focused on practical application and strategic value.

## How It Works (Methodology)

The application follows a three-step automated pipeline:

1.  **Web Scraping & Data Acquisition**: The script first identifies and fetches the URL for the most recent edition of the TLDR AI Newsletter, a curated source of relevant articles. It then parses this newsletter to extract the URLs of the primary source articles.

2.  **Content Aggregation**: Each source article URL is visited, and its core textual content is extracted. This raw text from multiple sources is aggregated into a single corpus for analysis.

3.  **AI-Powered Summarization & Analysis**: The aggregated text is passed to Google's Gemini Pro 1.5 model. A specific, engineered prompt instructs the model to act as an assistant to an Applied Science Manager. It synthesizes the information and generates a structured summary, focusing not just on *what* the technology is, but on its *so what*—its potential applications, feasibility, and business impact. The tool then provides an interactive Q&A session on the summarized content.

## Tech Stack

-   **Language**: Python 3
-   **Core Libraries**:
    -   `requests` & `BeautifulSoup4`: For web scraping and HTML parsing.
    -   `google-generativeai`: For interacting with the Gemini API.
    -   `python-dotenv`: For secure management of API keys.

## Setup & Usage

**1. Clone the repository:**
```bash
git clone [https://github.com/your-username/ai-summary-engine.git](https://github.com/your-username/ai-summary-engine.git)
cd ai-summary-engine
```

**2. Create a virtual environment and install dependencies:**
```bash
python -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
pip install -r requirements.txt
```

**3. Set up your API Key:**
   - Create a file named `.env` in the project root.
   - Add your Gemini API key to this file:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

**4. Run the tool:**
```bash
python main.py
```

## Example Output

```
================================================================================
AI DAILY BRIEFING
================================================================================

Here is a summary of the key developments from today's articles:

**1. Large Language Model (LLM) Pruning Techniques**

* **Core Idea**: A new technique called "Sparse-Quant" allows for reducing the size of large language models by up to 80% with minimal impact on performance.
* **Potential Application**: This could enable the deployment of powerful LLMs on edge devices like smartphones or in resource-constrained cloud environments, reducing inference costs significantly.
* **Technical Feasibility**: High. The paper provides open-source code for implementation. Requires expertise in model optimization but leverages existing frameworks.
* **Strategic Value**: Unlocks new product categories for on-device AI. Provides a competitive advantage by drastically lowering operational costs for AI features.

...

================================================================================

Interactive Q&A session started. Type 'quit' to exit.

Ask a question about the articles:
```
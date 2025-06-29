# AI News Briefing Engine

A Python tool that automatically scrapes the latest AI news, digests the content of multiple articles, and generates strategic summaries tailored for Applied Science Managers. Available as both a command-line tool and web interface.

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
    -   `flask`: For the web interface.

## Setup & Usage

**1. Clone the repository:**
```bash
git clone https://github.com/christophercosler/ai-news-briefing.git
cd ai-news-briefing
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

Command line version:
```bash
python main.py
```

Web interface version:
```bash
python web_app.py
```
Then open `http://127.0.0.1:5000` in your browser.

## Project Structure

```
ai-news-briefing/
├── main.py              # Command-line interface
├── web_app.py           # Web interface launcher
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── ai/                  # AI client and prompts
│   ├── client.py
│   └── prompts.py
├── newsletter/          # Newsletter fetching and parsing
│   ├── fetcher.py
│   └── parser.py
├── articles/            # Article selection and extraction
│   ├── selector.py
│   └── extractor.py
├── utils/               # Utility functions
│   ├── http.py
│   └── text.py
└── web/                 # Flask web interface
    ├── routes.py
    └── templates/
```

## Example Output

```
================================================================================
AI BRIEFING - TLDR NEWSLETTER 2025-06-29
================================================================================

Here is a summary of the key developments from today's articles:

**1. Large Language Model (LLM) Pruning Techniques**

* **Core Idea**: A new technique called "Sparse-Quant" allows for reducing the size of large language models by up to 80% with minimal impact on performance.
* **Potential Application**: This could enable the deployment of powerful LLMs on edge devices like smartphones or in resource-constrained cloud environments, reducing inference costs significantly.
* **Technical Feasibility**: High. The paper provides open-source code for implementation. Requires expertise in model optimization but leverages existing frameworks.
* **Strategic Value**: Unlocks new product categories for on-device AI. Provides a competitive advantage by drastically lowering operational costs for AI features.

...

================================================================================

Q&A mode - type 'quit', 'exit', or 'q' to stop.

Press Enter to start Q&A mode...

Question about the newsletter:
```

## Requirements

- **Python 3.7+**
- **Google Gemini API Key**: You'll need to sign up for Google AI Studio to get a free API key
- **Internet connection**: Required for fetching newsletters and articles

## Security Notes

- **TODO**: Replace Flask SECRET_KEY with secure random key from environment variable in production
- The current SECRET_KEY is for development only and must be changed before production deployment

## Deployment Options

### Local Execution
Run locally on your machine using either:
- **Command line**: `python main.py`
- **Web interface**: `python web_app.py` then visit `http://127.0.0.1:5000`

### Cloud Deployment (AWS Lambda) - FULLY OPERATIONAL ✅
Successfully deployed to AWS Lambda with **complete end-to-end functionality**:

**🚀 LIVE PRODUCTION SYSTEM**: https://zhqwd82ijl.execute-api.us-east-1.amazonaws.com/Prod/

**✅ COMPLETE SUCCESS STATUS:**
- ✅ **Infrastructure**: AWS Lambda + API Gateway + CloudFormation fully operational
- ✅ **AI Pipeline**: Complete newsletter processing and AI summary generation (~20 seconds)
- ✅ **Web Interface**: Professional UI with home page and generate functionality
- ✅ **Content Handling**: Full AI-generated briefings (no truncation) with content sanitization
- ✅ **Template Rendering**: Proper Jinja2 template system with styled output
- ✅ **Error Handling**: Comprehensive error pages and logging
- ✅ **Production Ready**: Clean codebase with debugging endpoints removed

**🎯 System Capabilities:**
- Automatic TLDR AI newsletter scraping and analysis
- AI-powered article selection and strategic business summaries
- Professional web interface with 20-second processing time
- Complete untruncated briefings using Google Gemini AI
- Robust error handling and CloudWatch logging

**📋 Technical Implementation:**
- Traditional Lambda handler approach (proven stable)
- Docker containerization with SAM deployment
- Content sanitization for AI-generated text
- Proper HTTP response formatting for API Gateway

**⚠️ KNOWN ISSUE:**
- **Button Navigation**: Clicking buttons on the home page returns `{"message":"Forbidden"}` error
- **Workaround**: Access `/generate` endpoint directly: https://zhqwd82ijl.execute-api.us-east-1.amazonaws.com/Prod/generate
- **Status**: Core AI functionality works perfectly when accessed directly

## Features

- **Intelligent Article Selection**: Uses AI to choose the most relevant articles from each newsletter
- **Strategic Focus**: Summaries emphasize business impact, technical feasibility, and practical applications
- **Dual Interface**: Both command-line and web-based interfaces available
- **Interactive Q&A**: Ask follow-up questions about the summarized content
- **Modular Architecture**: Clean, extensible codebase for easy customization

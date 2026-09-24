Scholarship Finder Scraper

Hi, I'm Luis — an aspiring AI engineer, learning by building. This is my first AI engineering project: a web scraper that reads scholarship listing pages and uses an LLM to turn them into clean, structured data.

What it does

The scraper visits a scholarship listing page, pulls the page content, and uses an LLM (via crawl4ai) to extract structured scholarship records — name, organization, amount, deadline, and eligibility — validated against a Pydantic schema, then saved to scholarships.json.

Setup:

1. Clone this repo and set up a virtual environment:
   python3 -m venv tools
   source tools/bin/activate
2. Install dependencies:
   pip install crawl4ai pydantic python-dotenv
3. Get a free API key from Groq and create a .env file in the project root with:
   GROQ_API_TOKEN=your_key_here
4. Run it:
   python3 scraper.py

Results are saved to scholarships.json.

The debugging journey:

I originally planned to run this fully locally with Ollama, since I liked the idea of no token limits. I started with llama3.2:3b, then switched to qwen2.5:7b for better extraction quality. It worked — but it was painfully slow (10+ minutes on a single page) because my machine has no GPU to accelerate it. Oh boy, I ate those words about "no token limits" being obviously better. I asked Claude for advice and switched to Groq's free tier: a hosted API with generous free tokens and dramatically faster responses, at the cost of a rate limit I had to design around instead.

Other things that went wrong along the way:

- Schema design. I originally used a raw JSON Schema file (scholarships_dataschema.json) to define what the model should extract. It worked for a single record but broke down for lists of items. Switching to Pydantic, with a proper List[ScholarshipSchema] model, fixed this and made validation much cleaner.
- Wrong target URL. My first scraper pointed at a category/index page that only had navigation links, not actual scholarship listings — so the model correctly extracted "N/A" for everything, because there was nothing else there to find. I had to inspect the actual page structure to find where the real listings lived, one level deeper.
- Prompt refinement. My extraction instruction (see Zone 4 in scraper.py) went through several rewrites to stop the model from confusing eligibility criteria with the scholarship name — simple instructions weren't enough; explicit field descriptions plus a negative example were what actually fixed it.
- API keys, for the first time. This was new territory — my first time working with an external API key and a .env file. It took a few rounds of confusion (mixing up a variable name with its value) before I understood that os.getenv("SOME_NAME") looks up a name, not a secret — the actual secret only ever lives in .env. python-dotenv made this manageable once I actually understood it.
- Rate limiting. Groq's free tier caps at 8,000 tokens per minute, per model. Large pages get split into chunks by crawl4ai, and a few large chunks alone could blow past that. I lowered chunk_token_threshold to keep individual requests smaller, and made sure a rate-limited chunk fails gracefully now instead of crashing the whole run.

I'll be honest: this project wasn't entirely hardcoded solo — I used Claude to help debug a lot of this, especially the API key handling and rate limiting sections. I'm still learning, and documenting that honestly felt more useful than pretending otherwise.

Known limitations:
- Groq's free tier rate limit means a large page can still occasionally drop a chunk of data on a single run.
- The scraper only reads one page deep — some sites (like PhilScholar) nest real listing details a level or two further than the page you start on, which this doesn't follow automatically yet.
- amount and deadline often come back "N/A" on pages where that detail only lives on each scholarship's own dedicated page.
Tools & libraries:
- pip install pydantic
- pip install crawl4ai
- pip install python-dotenv
- crawl4ai — web crawling + LLM-based extraction
- Pydantic — schema validation
- python-dotenv — loads .env variables
- Groq — LLM inference API

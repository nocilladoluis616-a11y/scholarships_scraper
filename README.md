Hi, I'm Luis. I'm an aspiring AI engineer, I'm learning as of the moment and here is my first AI engineered program.
It's a web scraper, specifically designed to scrape scholarship list website. This is a basic level of AI engineering,
using an LLM to do the work along with the tools such as: crawl4ai, and pydantic. For the LLM, I initially planned to use a locally hosted AI.
It was a journey of trials, and errors. I started with an ollama model; llama:3.2b, then I switched to qwen2.5:7. At first, I thought that
locally hosted AI is better in general because there's no token limit, oh boy- I ate those words. My locally hosted AI definitely worked, but 
it sacrificed speed. Because I have limited storage, I asked Claude about suggestions to make it better. That's when I landed on Groq free tier.
It was a great opportunity knowing that I can have free tokens, although limited. 

Aside from my change of model, let's talk about other things that went wrong with this adventure. If you can see, I have a scholarshipes_data
schema.json. On my first trial, I used json schema to serve as the basis of what my AI model will scrape from websites. The problem with this is inefficiency for lists, it's not effective for multiple-file. And I learned that I can use pydantic as a replacement, by leveraging the use of list in python. Next, the wrong URL I first started with multiple URLs, the problem is the speed because I originally intended for this to run locally. Then, after trying with a single URL, it 
returned the results on my terminal. The problems was, it was mostly N/A. If you look at the code on zone 4, the extraction strategy instruction.
It was reprompted multiple times, from a simple; to refined. Another solution is to double-check the URL, this code raised multiple errors due to wrong URL. The last major problem was the token issue, this is where I stagnated. It's my first time using an external api_key. It was unfamiliar to me, and making the token run took days of frustration. Thanks to Claude, I managed to solve the problem by using load_dotenv(). If your new, I advise you to install the library python-dotenv. There were multiple mistakes on my codes, and I admit that this project wasn't completely hardcoded by yours truly. Again, I'm still learning, and hopefully be better.

List of libraries/ tools:
-pydantic            pip install pydantic
-crawl4ai            pip install crawl4ai
-load_dotenv         pip install python-dotenv

I put all my tools in a .venv I call it tools you can do it as well.
I activate it using source tools/bin/activate


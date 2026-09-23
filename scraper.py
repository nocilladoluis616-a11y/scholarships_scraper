
#ZONE1: IMPORTS
from dotenv import load_dotenv
import json
import os
import asyncio
from pydantic import BaseModel, Field, ValidationError
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from typing import List
import random #random is for retry delays, not file selection
import logging #use this instead of print statements for better logging and debugging

#Setup for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',#logging format = time, level, message
                    handlers=[logging.StreamHandler(), logging.FileHandler("scraper.log")])#logging.StreamHandler() = print to terminal, logging.FileHandler("scraper.log") = write to a log file named scraper.log

logger = logging.getLogger(__name__) #get the logger for this module

load_dotenv()  # Load environment variables from .env file


#ZONE2: MODELS


# pydantic schema for the extracted scholarship data
class ScholarshipSchema(BaseModel):
    scholarship_name: str = Field(description="Only the official title/headline of the scholarship program. e.g., 'DOST Merit Scholarship', 'CHED Full Tuition Grant', 'Ateneo Merit Scholarship'. NEVER put eligibility requirements, GWA/grade thresholds, citizenship, or descriptive criteria here — that belongs in the eligibility field. Cannot be empty..")
    organization: str = Field(description="The name of the organization, foundation, or school offering the scholarship.")
    amount: str = Field(description="The financial value, allowance, or coverage of the scholarship. If not stated, write 'N/A'.")
    deadline: str = Field(description="The final closing date for applications. If not stated, write 'N/A'.")
    eligibility: str = Field(description="Who can apply - grade level,GWA/GPA requirement, income bracket, or other criteria. If not stated, write 'N/A'.")
# pydantic nested list command for the extracted scholarship data
class ScholarshipsListSchema(BaseModel):
    scholarships: List[ScholarshipSchema] = Field(description="A list of scholarship entries extracted from the webpage.")


#ZONE3: HELPER FUNCTIONS

#saving validated file
 #funcition to save json file: breakdeown: filepath will return a pathfile into string. New_data will return the dictionary from the schema
def save_to_json(filepath: str, new_data: list):  #parameter = orange, hints/annotations = green. Hints  explicit what will be returned
    if os.path.exists(filepath):                   #This checks if the parameter filepath exists
        with open(filepath, "r") as f:             #with open = open the file "r" = read mode, as f = assign the file to the variable f
            existing = json.load(f)                #existing is a variale, json.load(f) = load the json to the f variable
    else:
        existing = []                              #if the file does not exist, create an empty list

    existing.extend(new_data)                     #means add the new data  one by one because of extend, to the existing 

    with open(filepath, "w") as f:                # it means open the file in write mode, "w" = write mode, as f = assign the file to the variable f
        json.dump(existing, f, indent=4)          #json.dump = write the data to the file, indent=4 = format the json file with 4 spaces


#scraping retry function
async def scrape_with_retry(crawler, url: str, config, max_retries: int = 3):
    for attempt in range(max_retries): #start of loop usinng the range, max_retries  = 3

        result = await crawler.arun(url=url, config=config) #Use arun to read file individuallly

        if result.success:
            return result #if we're successful to scrape using retry

        logger.warning(f"Attempt {attempt + 1} failed for {url}. Retrying...") #if not successful, print the attempt number and the url
        await asyncio.sleep(random.uniform(2.0, 5.0))   #make a duration to not assume as bot, and not use 1-3 so that site wont be suspicious

    logger.error(f"All {max_retries} attempts failed for {url}")

    return None

#ZONE4:MAIN ASYNC FUNCTION

# ollama activation
async def run_ollama(target_urls: list):
   

#AI model configuration for ollama
    my_llm_config = LLMConfig(
        provider="groq/openai/gpt-oss-120b",

        api_token=os.getenv("GROQ_API_TOKEN")
    )

#Extraction strategy configuration for the AI model
    extraction_strategy = LLMExtractionStrategy(
        llm_config=my_llm_config,  
        schema=ScholarshipsListSchema.model_json_schema(),
        extraction_type="schema",
        instruction=
            "You are a strict data extraction tool. Read the webpage content and extract all available scholarships. "
            "CRITICAL: Do not use placeholders, variable names, or template terms like 'key', 'value', or 'scholarship_name' as values. "
            "If the information is not explicitly written in the webpage text, write 'N/A'. "
            "Example of valid output: {'scholarship_name': 'DOST Merit Scholarship', 'organization': 'Department of Science and Technology', 'amount': 'Free Tuition', 'deadline': 'August 2026'}",
        input_format="fit_markdown",
        chunk_token_threshold=1500,
        overlap_rate=0.05
    )

#Crawl4ai extraction behaviour configuration for the AI model
    browser_config = BrowserConfig(
        headless = True,
        enable_stealth = True
    )

#Crawl4ai run configuration for the AI model
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS,
        magic = True
    )




#Run the web crawler with the specified configuration and target URLs
    async with AsyncWebCrawler(config=browser_config) as crawler:
        logger.info(f"\n--- Scraping: {target_urls} ---")
        
        
 #using set function to remove duplicates
        seen_urls = set()  # Create a set to track seen URLs

        for url in target_urls: #specifying url (no valu yet) main loop
         
            if url in seen_urls:  # Check if the URL has already been processed
                logger.warning(f"Skipping duplicate URL: {url}")
                continue  # Skip to the next URL if it's a duplicate

            seen_urls.add(url)  # Add the URL to the set of seen URLs
            result = await scrape_with_retry(crawler, url, run_config) #Use arun instead of arun.many to scrape independently

            if result is None:
                logger.error(f"Failed to scrape {url} after multiple attempts.")
                continue
        #Add try and except to fix blank output error 
    
            try:
                if result.success:
                    logger.info("---Output---")

                    raw_output = result.extracted_content

                    logger.info(f"Raw output received: {raw_output}")

                    data = json.loads(raw_output)

                    if isinstance(data, list):

                        clean_data = []  # Initialize an empty list to hold cleaned scholarship data

                        for item in data:
                            if item.get("error", False):
                                continue
                            if "scholarships" in item:
                                clean_data.extend(item["scholarships"])  # Extend the clean_data list with scholarships from the item
                            else:
                                clean_data.append(item)  # Append the item directly if it doesn't contain "scholarships"

                        clean_data = [
                            item for item in clean_data 
                            if not (
                                item.get("scholarship_name", "N/A") == "N/A"
                                and item.get("organization", "N/A") == "N/A"
                                and item.get("amount", "N/A") == "N/A"
                                and item.get("deadline", "N/A") == "N/A"
                            )
                        ]

                        if not clean_data:
                            logger.warning(f"No valid scholarships extracted from {result.url}")
                            continue

                        validated_data = ScholarshipsListSchema(scholarships=clean_data)  # Wrap the list in the ScholarshipsListSchema
                    else:
                        validated_data = ScholarshipsListSchema(**data) #**data = dict

                    save_to_json("scholarships.json", [s.model_dump() for s in validated_data.scholarships]) #save the data to a json file loop 

                    logger.info(validated_data.model_dump_json(indent=4)) #makes the data in terminal into json format

                #removed else to avoid the dead code, because the result.success is guaraneteed true and loop wiil continue anyway
                    

            except (ValidationError, json.JSONDecodeError) as e:
                logger.error(f"An error occurred: {e}")

    
#ZONE5: ENTRY POINT
if __name__ == "__main__":
    urls = [
        "https://philscholar.com/first-year-college-scholarship/",
       
        ]
    asyncio.run(run_ollama(target_urls=urls))


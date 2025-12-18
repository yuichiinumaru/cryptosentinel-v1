# scripts/evaluate_markdown.py

"""
This script evaluates the Markdown Awareness of AI agents based on the MDEval paper (2501.15000v1).

It works by:
1. Getting a response from a local agent for a given prompt.
2. Asking a powerful "judge" LLM (e.g., Google's Gemini) to rewrite that response into well-structured Markdown.
3. Converting both the original and rewritten responses from Markdown to HTML.
4. Extracting the sequence of HTML tags from both versions.
5. Calculating the normalized Levenshtein distance between the tag sequences to produce a "Markdown Awareness" score.

**Prerequisites:**
- The backend server must be running (`uvicorn main:app --reload` from the `backend` directory).
- A `.env` file must be present in the `backend` directory with a valid `API_KEY` and `GOOGLE_API_KEY`.
"""

import os
import json
import asyncio
import httpx
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup
from rapidfuzz.distance import Levenshtein
import google.generativeai as genai
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from the backend's .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(dotenv_path=dotenv_path)

# API Configuration
AGENT_API_URL = "http://127.0.0.1:8000/chat"
AGENT_API_KEY = os.getenv("API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not AGENT_API_KEY or AGENT_API_KEY == "CHANGE_ME_IN_PROD_PLEASE":
    raise ValueError("CRITICAL: API_KEY is missing or default in backend/.env")
if not GOOGLE_API_KEY:
    raise ValueError("CRITICAL: GOOGLE_API_KEY is missing in backend/.env")

# Configure the judge LLM
genai.configure(api_key=GOOGLE_API_KEY)
judge_model = genai.GenerativeModel('gemini-1.5-flash')

# --- Core MDEval Functions ---

async def get_agent_response(client: httpx.AsyncClient, prompt: str, agent: str) -> str:
    """Gets a response from the local agent API."""
    headers = {"Authorization": f"Bearer {AGENT_API_KEY}"}
    payload = {"message": prompt, "agent": agent}
    try:
        response = await client.post(AGENT_API_URL, headers=headers, json=payload, timeout=120.0)
        response.raise_for_status()
        return response.json()["response"]
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        return f"Error: Failed to get response from agent. Status: {e.response.status_code}"
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
        return "Error: Could not connect to the agent API. Is the backend server running?"


async def get_rewritten_response(text: str) -> str:
    """Uses a judge LLM to rewrite the text into well-structured Markdown."""
    rewrite_prompt = f"""Given the text below, please rewrite it using rich Markdown formatting to make the output more structured and readable for a web interface.

Key instructions:
- Use headings, bold text, lists (bulleted or numbered), and code blocks where appropriate.
- Do NOT alter the core information or meaning of the text.
- The goal is to improve the *presentation* of the existing content.

### TEXT TO REWRITE:
---
{text}
---
"""
    try:
        response = await judge_model.generate_content_async(rewrite_prompt)
        return response.text
    except Exception as e:
        print(f"Error calling judge LLM: {e}")
        return f"Error: Could not get rewritten response. Details: {e}"


def htmlify_and_extract_tags(markdown_text: str) -> list[str]:
    """Converts Markdown to HTML and extracts a list of tags."""
    md = MarkdownIt()
    html = md.render(markdown_text)
    soup = BeautifulSoup(html, 'html.parser')
    return [tag.name for tag in soup.find_all()]


def calculate_mdeval_score(original_tags: list[str], rewritten_tags: list[str]) -> float:
    """Calculates the normalized Levenshtein distance between two lists of HTML tags."""
    if not rewritten_tags and not original_tags:
        return 1.0  # Both are empty, perfect match
    if not rewritten_tags:
        return 0.0 # No structure was proposed, can't evaluate fairly if original has tags

    distance = Levenshtein.distance(original_tags, rewritten_tags)
    max_len = max(len(original_tags), len(rewritten_tags))

    if max_len == 0:
        return 1.0  # Both were empty

    normalized_distance = distance / max_len
    return 1.0 - normalized_distance

# --- Main Execution ---

async def run_evaluation(prompt_data: dict, client: httpx.AsyncClient, agent: str) -> float:
    """Runs the full MDEval pipeline for a single prompt and returns the score."""
    prompt = prompt_data["prompt"]
    print(f"\n📝 Evaluating Prompt: \"{prompt[:80]}...\"")

    # 1. Get original response
    original_response = await get_agent_response(client, prompt, agent)
    if original_response.startswith("Error:"):
        print(f"   ❌ {original_response}")
        return 0.0

    # 2. Get rewritten response
    rewritten_response = await get_rewritten_response(original_response)
    if rewritten_response.startswith("Error:"):
        print(f"   ❌ {rewritten_response}")
        return 0.0

    # 3. Extract tags
    original_tags = htmlify_and_extract_tags(original_response)
    rewritten_tags = htmlify_and_extract_tags(rewritten_response)

    # 4. Calculate score
    score = calculate_mdeval_score(original_tags, rewritten_tags)
    print(f"   🏆 Score: {score:.4f}")
    return score


async def main():
    """Main function to run the MDEval pipeline."""
    target_agent = "MarketAnalyst"
    prompts_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'ideas', 'markdown_prompts.json')

    try:
        with open(prompts_file, 'r') as f:
            prompts = json.load(f)
    except FileNotFoundError:
        print(f"Error: Prompts file not found at {prompts_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {prompts_file}")
        return


    print(f"▶️  Starting MDEval batch for agent '{target_agent}'...")
    print(f"Found {len(prompts)} prompts to evaluate.")
    print("-" * 50)

    total_score = 0.0
    scores = []

    async with httpx.AsyncClient() as client:
        for prompt_data in prompts:
            score = await run_evaluation(prompt_data, client, target_agent)
            scores.append(score)
            total_score += score

    average_score = total_score / len(prompts) if prompts else 0.0

    print("\n" + "=" * 50)
    print("🏁 BATCH EVALUATION COMPLETE 🏁")
    print("=" * 50)
    print(f"Agent Evaluated: '{target_agent}'")
    print(f"Total Prompts:   {len(prompts)}")
    print(f"Individual Scores: {[f'{s:.3f}' for s in scores]}")
    print(f"📈 Average Markdown Awareness Score: {average_score:.4f}")
    print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())

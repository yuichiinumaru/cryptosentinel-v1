import asyncio
import aiohttp
import os
from pathlib import Path
from rich.progress import Progress

PAPER_IDS_FILE = Path("scripts/research/paper_ids.txt")
OUTPUT_DIR = Path("docs/arxiv")
BASE_URL = "https://arxiv.org/pdf/{}.pdf"
CONCURRENCY = 5

async def fetch_paper(session, paper_id, progress, task_id):
    url = BASE_URL.format(paper_id)
    output_path = OUTPUT_DIR / f"{paper_id}.pdf"

    if output_path.exists():
        progress.update(task_id, advance=1)
        return

    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(output_path, "wb") as f:
                    f.write(content)
                progress.update(task_id, advance=1)
            else:
                progress.console.print(f"[red]Failed {paper_id}: HTTP {response.status}")
                progress.update(task_id, advance=1)
    except Exception as e:
        progress.console.print(f"[red]Error fetching {paper_id}: {e}")
        progress.update(task_id, advance=1)

async def main():
    if not PAPER_IDS_FILE.exists():
        print(f"Error: {PAPER_IDS_FILE} not found.")
        return

    with open(PAPER_IDS_FILE, "r") as f:
        paper_ids = [line.strip() for line in f if line.strip()]

    print(f"Found {len(paper_ids)} papers to download.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def sem_fetch(session, paper_id, progress, task_id):
        async with semaphore:
            await fetch_paper(session, paper_id, progress, task_id)

    async with aiohttp.ClientSession() as session:
        with Progress() as progress:
            task_id = progress.add_task("[cyan]Downloading papers...", total=len(paper_ids))
            tasks = [sem_fetch(session, pid, progress, task_id) for pid in paper_ids]
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

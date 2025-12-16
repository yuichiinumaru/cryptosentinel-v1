from pathlib import Path

IDS_FILE = Path("scripts/research/paper_ids.txt")
BACKLOG_FILE = Path("docs/RESEARCH_BACKLOG.md")
TEMPLATE = """
### [ ] Paper {ID}
- **Status:** Pending
- **Artifact:** `docs/ideas/{ID}.md`
- **Tasks:**
  - [ ] Agent: Read `docs/arxiv/{ID}.pdf` fully.
  - [ ] Agent: Deeply analyze current codebase architecture to understand context.
  - [ ] Agent: Brainstorm integration points (Paper Idea -> Codebase Module).
  - [ ] Agent: Perform Gap Analysis (What exists vs What is needed).
  - [ ] Agent: Write `docs/ideas/{ID}.md` using the Standard Template.
"""

def main():
    if not IDS_FILE.exists():
        print(f"Error: {IDS_FILE} not found")
        return

    with open(IDS_FILE, "r") as f:
        ids = [l.strip() for l in f if l.strip()]

    with open(BACKLOG_FILE, "w") as f:
        f.write("# Research Backlog\n\n")
        for pid in ids:
            f.write(TEMPLATE.format(ID=pid))

    print(f"Generated backlog with {len(ids)} entries.")

if __name__ == "__main__":
    main()

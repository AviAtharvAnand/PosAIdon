"""Split the knowledge markdown into heading-aware chunks.

Each chunk is one markdown section (heading + body) prefixed with its full
heading path, e.g.
    "EarthEcho Water-Quality Analysis Dictionary › Sheet 1 — Individual parameter
     rules (controlled) › pH — Too high (alkaline)"
so the parameter and category a chunk is about are always present for both the
embedding and the keyword rerank. Sections longer than MAX_CHARS are sub-split,
and every piece keeps the heading path.
"""
import json
import re
import shutil
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_CHARS = 2000

shutil.rmtree("water_data/chunks", ignore_errors=True)
Path("water_data/chunks").mkdir(parents=True, exist_ok=True)

splitter = RecursiveCharacterTextSplitter(chunk_size=MAX_CHARS, chunk_overlap=200)

HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def split_sections(text):
    """Yield (heading_path, section_markdown) for every heading-delimited section."""
    path = []  # list of (level, title)
    current_lines = []
    current_path = []

    def flush():
        body = "\n".join(current_lines).strip()
        if body:
            yield list(current_path), body

    for line in text.split("\n"):
        match = HEADING.match(line)
        if match:
            yield from flush()
            level, title = len(match.group(1)), match.group(2)
            path = [(lvl, t) for lvl, t in path if lvl < level] + [(level, title)]
            current_path = [t for _, t in path]
            current_lines = [line]
        else:
            current_lines.append(line)
    yield from flush()


docs = Path("water_markdown")
chunk_count = 0
files = sorted(list(docs.rglob("*.md")) + list(docs.rglob("*.mdx")))

for md_file in files:
    text = md_file.read_text(encoding="utf-8").replace("\r\n", "\n").strip()

    page_name = md_file.relative_to(docs).with_suffix("").as_posix().replace("/", "__")
    title = md_file.stem.replace("-", " ").title()
    relative_path = md_file.relative_to(Path(".")).as_posix()
    url = f"https://github.com/AviAtharvAnand/PosAIdon/blob/main/{relative_path}"

    index = 0
    for heading_path, section in split_sections(text):
        # A bare heading with no body (e.g. "## Sheet 2 ...") adds nothing on its own.
        if not HEADING.sub("", section.split("\n", 1)[0]) and "\n" not in section:
            continue

        breadcrumb = " › ".join(heading_path)
        section_name = heading_path[-1] if heading_path else title
        pieces = splitter.split_text(section) if len(section) > MAX_CHARS else [section]

        for part_number, piece in enumerate(pieces, start=1):
            index += 1
            label = breadcrumb + (f" (part {part_number})" if len(pieces) > 1 else "")
            data = {
                "id": f"{page_name}__{index:03}",
                "source_url": url,
                "title": title,
                "section": section_name,
                "text": f"[{label}]\n{piece}",
            }
            outfile = Path("water_data/chunks") / f"{data['id']}.json"
            with open(outfile, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            chunk_count += 1

print(f"Created {chunk_count} chunks.")

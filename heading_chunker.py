import re

from src import RecursiveChunker


class HeadingChunker:
    """
    Split Markdown documents by headings.

    Each Markdown section becomes a chunk.
    Long sections are split recursively while keeping the heading.
    """

    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []

        sections = re.split(
            r"(?=^#{1,6}\s+)",
            text.strip(),
            flags=re.MULTILINE,
        )

        chunks = []

        for section in sections:
            section = section.strip()

            if not section:
                continue

            lines = section.splitlines()

            if re.match(r"^#{1,6}\s+", lines[0]):
                heading = lines[0].strip()
                body = "\n".join(lines[1:]).strip()
            else:
                heading = "# Document"
                body = section

            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue

            available_size = max(
                100,
                self.chunk_size - len(heading) - 2,
            )

            fallback = RecursiveChunker(
                chunk_size=available_size
            )

            subchunks = fallback.chunk(body)

            for subchunk in subchunks:
                chunks.append(
                    f"{heading}\n{subchunk}".strip()
                )

        return chunks
from pathlib import Path
import re

from src import ChunkingStrategyComparator


DATA_DIR = Path("data/Library")

FILES = [
    "student-borrowing-policy.md",
    "reserve-a-room.md",
    "undergraduate-student-services.md",
]


def remove_frontmatter(text: str) -> str:
    """Remove YAML frontmatter between the first pair of --- markers."""
    return re.sub(
        r"\A---\s*\n.*?\n---\s*\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )


comparator = ChunkingStrategyComparator()

output_lines = []

for filename in FILES:
    path = DATA_DIR / filename

    raw_text = path.read_text(encoding="utf-8")
    text = remove_frontmatter(raw_text)

    result = comparator.compare(
        text,
        chunk_size=500,
    )

    title = f"\n=== {filename} ==="
    print(title)
    output_lines.append(title)

    for strategy_name, stats in result.items():
        line = (
            f"{strategy_name:15} | "
            f"count={stats['count']:2} | "
            f"avg_length={stats['avg_length']:.2f}"
        )

        print(line)
        output_lines.append(line)


Path("report/baseline-results.txt").write_text(
    "\n".join(output_lines),
    encoding="utf-8",
)

print("\nSaved to report/baseline-results.txt")
from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai

from src import (
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    LocalEmbedder,
)
from src.agent import KnowledgeBaseAgent
from benchmark_queries import BENCHMARKS


DATA_DIR = Path("data/Library")
OUTPUT_FILE = Path("agent_answers.txt")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}, text

    frontmatter = parts[1]
    content = parts[2].strip()

    metadata = {}

    for line in frontmatter.splitlines():
        line = line.strip()

        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)

        metadata[key.strip()] = (
            value.strip()
            .strip('"')
            .strip("'")
        )

    return metadata, content


def load_documents() -> list[Document]:
    chunker = FixedSizeChunker(
        chunk_size=500,
        overlap=50,
    )

    documents = []

    for path in sorted(DATA_DIR.glob("*.md")):
        raw_text = path.read_text(
            encoding="utf-8"
        )

        metadata, content = parse_frontmatter(
            raw_text
        )

        chunks = chunker.chunk(content)

        for index, chunk in enumerate(chunks):
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={
                        **metadata,
                        "doc_id": path.stem,
                        "filename": path.name,
                        "chunk_index": index,
                    },
                )
            )

    return documents


def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Không tìm thấy GEMINI_API_KEY trong .env"
        )

    print("Loading LocalEmbedder...")

    embedder = LocalEmbedder()

    documents = load_documents()

    print(
        f"Loaded {len(documents)} chunks."
    )

    store = EmbeddingStore(
        collection_name="tdtu_agent_fixed",
        embedding_fn=embedder,
    )

    store.add_documents(documents)

    client = genai.Client(
        api_key=api_key
    )

    model_name = os.getenv(
        "GEMINI_GENERATION_MODEL",
        "gemini-2.5-flash",
    )

    def gemini_llm(prompt: str) -> str:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        return response.text or ""

    agent = KnowledgeBaseAgent(
        store=store,
        llm_fn=gemini_llm,
    )

    output = []

    output.append(
        "=" * 70
    )
    output.append(
        "AGENT BENCHMARK - FIXED SIZE"
    )
    output.append(
        "=" * 70
    )

    for benchmark in BENCHMARKS:
        query = benchmark["query"]
        metadata_filter = benchmark[
            "metadata_filter"
        ]

        print(
            f"\nRunning Query {benchmark['id']}..."
        )

        try:
            answer = agent.answer(
                question=query,
                top_k=3,
                metadata_filter=metadata_filter,
            )
        except Exception as exc:
            answer = (
                f"ERROR: {type(exc).__name__}: "
                f"{exc}"
            )

        output.append("")
        output.append(
            f"QUERY {benchmark['id']}: "
            f"{query}"
        )
        output.append(
            f"GOLD: "
            f"{benchmark['gold_answer']}"
        )
        output.append(
            f"FILTER: {metadata_filter}"
        )
        output.append(
            "AGENT ANSWER:"
        )
        output.append(
            answer
        )
        output.append(
            "-" * 70
        )

    result = "\n".join(output)

    print("\n")
    print(result)

    OUTPUT_FILE.write_text(
        result,
        encoding="utf-8",
    )

    print(
        "\nSaved to agent_answers.txt"
    )


if __name__ == "__main__":
    main()
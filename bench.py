from pathlib import Path
import re
import sys

from src import (
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    RecursiveChunker,
    LocalEmbedder,
)
from benchmark_queries import BENCHMARKS
from heading_chunker import HeadingChunker


DATA_DIR = Path("data/Library")
OUTPUT_FILE = Path("ket_qua_benchmark.txt")

# Strategy mặc định của R1 = FixedSize.
# Có thể chạy:
#   python bench.py fixed
#   python bench.py recursive
#   python bench.py heading
STRATEGY = sys.argv[1].lower() if len(sys.argv) > 1 else "fixed"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Tách YAML frontmatter và phần nội dung Markdown.

    Không cần PyYAML vì metadata của corpus hiện tại chỉ là key: value đơn giản.
    """
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}, text

    frontmatter_text = parts[1]
    content = parts[2].strip()

    metadata = {}

    for line in frontmatter_text.splitlines():
        line = line.strip()

        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip().strip('"').strip("'")

        metadata[key] = value

    return metadata, content


def get_chunker():
    if STRATEGY == "fixed":
        return FixedSizeChunker(
            chunk_size=500,
            overlap=50,
        )

    if STRATEGY == "recursive":
        return RecursiveChunker(
            chunk_size=500,
        )

    if STRATEGY == "heading":
        return HeadingChunker(
            chunk_size=500,
        )

    raise ValueError(
        "Strategy must be: fixed, recursive, or heading"
    )


def load_and_chunk_documents(chunker) -> list[Document]:
    documents = []

    for path in sorted(DATA_DIR.glob("*.md")):
        raw_text = path.read_text(encoding="utf-8")

        metadata, content = parse_frontmatter(raw_text)

        chunks = chunker.chunk(content)

        for index, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "doc_id": path.stem,
                "filename": path.name,
                "chunk_index": index,
            }

            document = Document(
                id=f"{path.stem}#{index}",
                content=chunk,
                metadata=chunk_metadata,
            )

            documents.append(document)

    return documents


def format_result(rank: int, result: dict) -> str:
    metadata = result["metadata"]

    return (
        f"  Top-{rank}\n"
        f"    doc_id: {metadata.get('doc_id')}\n"
        f"    audience: {metadata.get('audience')}\n"
        f"    chunk_index: {metadata.get('chunk_index')}\n"
        f"    score: {result['score']:.6f}\n"
        f"    content: {result['content'][:300].replace(chr(10), ' ')}\n"
    )


def evaluate_query(
    store: EmbeddingStore,
    benchmark: dict,
    use_filter: bool = True,
) -> tuple[list[dict], int, bool]:

    metadata_filter = (
        benchmark["metadata_filter"]
        if use_filter
        else None
    )

    results = store.search_with_filter(
        query=benchmark["query"],
        top_k=3,
        metadata_filter=metadata_filter,
    )

    must_contain = benchmark["must_contain"].lower()

    relevant_rank = 0

    for rank, result in enumerate(results, start=1):
        content = result["content"].lower()

        if must_contain in content:
            relevant_rank = rank
            break

    relevant = relevant_rank > 0

    return results, relevant_rank, relevant


def main():
    chunker = get_chunker()

    print(f"Strategy: {STRATEGY}")
    print(f"Data directory: {DATA_DIR}")

    documents = load_and_chunk_documents(chunker)

    print(f"Loaded chunks: {len(documents)}")

    embedder = LocalEmbedder()

    store = EmbeddingStore(
        collection_name=f"tdtu_{STRATEGY}",
        embedding_fn=embedder,
    )

    store.add_documents(documents)

    print(
        f"Vector store size: "
        f"{store.get_collection_size()}"
    )

    output = []

    output.append("=" * 70)
    output.append("TDTU LIBRARY BENCHMARK")
    output.append(f"Strategy: {STRATEGY}")
    output.append(f"Total chunks: {len(documents)}")
    output.append("=" * 70)

    total_relevant = 0
    retrieval_score = 0

    for benchmark in BENCHMARKS:
        query_id = benchmark["id"]

        output.append("")
        output.append(
            f"QUERY {query_id}: {benchmark['query']}"
        )

        output.append(
            f"Gold answer: {benchmark['gold_answer']}"
        )

        output.append(
            f"Gold document: {benchmark['source_doc']}"
        )

        output.append(
            f"Metadata filter: "
            f"{benchmark['metadata_filter']}"
        )

        results, relevant_rank, relevant = evaluate_query(
            store,
            benchmark,
            use_filter=True,
        )

        for rank, result in enumerate(results, start=1):
            output.append(
                format_result(rank, result)
            )

        if relevant:
            total_relevant += 1

            if relevant_rank == 1:
                retrieval_score += 2
            else:
                retrieval_score += 1

        output.append(
            f"Relevant chunk rank: "
            f"{relevant_rank if relevant else 'NOT FOUND'}"
        )

        output.append(
            f"Relevant in Top-3: {'YES' if relevant else 'NO'}"
        )

        # Query 5: A/B metadata-filter test
        if benchmark["metadata_filter"] is not None:
            output.append("")
            output.append(
                "--- A/B TEST: WITHOUT METADATA FILTER ---"
            )

            no_filter_results, no_filter_rank, no_filter_relevant = (
                evaluate_query(
                    store,
                    benchmark,
                    use_filter=False,
                )
            )

            for rank, result in enumerate(
                no_filter_results,
                start=1,
            ):
                output.append(
                    format_result(rank, result)
                )

            output.append(
                f"Relevant rank without filter: "
                f"{no_filter_rank if no_filter_relevant else 'NOT FOUND'}"
            )

            output.append(
                "--- END A/B TEST ---"
            )

        output.append("-" * 70)

    output.append("")
    output.append("=" * 70)
    output.append(
        f"Relevant Top-3: {total_relevant}/5"
    )

    output.append(
        f"Retrieval-only score: "
        f"{retrieval_score}/10"
    )

    output.append(
        "NOTE: This score evaluates retrieval only. "
        "The official rubric also considers agent-answer correctness."
    )

    output.append("=" * 70)

    result_text = "\n".join(output)

    print(result_text)

    OUTPUT_FILE.write_text(
        result_text,
        encoding="utf-8",
    )

    print(
        f"\nSaved benchmark output to "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
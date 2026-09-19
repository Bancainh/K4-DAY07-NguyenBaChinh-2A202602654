from src import LocalEmbedder, compute_similarity

embedder = LocalEmbedder()

pairs = [
    (
        "Students can borrow circulating materials for five days.",
        "The loan period for circulating materials is five days.",
        "HIGH",
    ),
    (
        "Renewal is not allowed for overdue materials.",
        "Overdue library items cannot be renewed.",
        "HIGH",
    ),
    (
        "Users can reserve a library room.",
        "The weather is sunny today.",
        "LOW",
    ),
    (
        "Students use portal credentials to access the library.",
        "Library access uses credentials from the student portal.",
        "HIGH",
    ),
    (
        "Course readings are available for students.",
        "Staff can request materials for purchase.",
        "LOW",
    ),
]

for i, (a, b, prediction) in enumerate(pairs, start=1):
    vec_a = embedder(a)
    vec_b = embedder(b)

    score = compute_similarity(vec_a, vec_b)

    print(
        f"{i}. prediction={prediction:4} "
        f"similarity={score:.4f}"
    )
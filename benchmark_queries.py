BENCHMARKS = [
    {
        "id": 1,
        "query": (
            "For undergraduate students, how long is the loan period "
            "for circulating materials, and how many renewals are allowed?"
        ),
        "gold_answer": (
            "5 days; one renewal for an additional 5 days."
        ),
        "metadata_filter": None,
        "source_doc": "student-borrowing-policy",
        "must_contain": "Loan period: 5 days",
    },
    {
        "id": 2,
        "query": "Under what conditions is renewal not allowed?",
        "gold_answer": (
            "Renewal is not allowed when the material is overdue "
            "or another user has placed a hold request."
        ),
        "metadata_filter": None,
        "source_doc": "renewal-guide",
        "must_contain": "material is already overdue",
    },
    {
        "id": 3,
        "query": "How can a user cancel a library room booking?",
        "gold_answer": (
            "By phone, email, Facebook, or by contacting staff "
            "at a Service Desk or Information Desk."
        ),
        "metadata_filter": None,
        "source_doc": "reserve-a-room",
        "must_contain": "To cancel",
    },
    {
        "id": 4,
        "query": "Which credentials are used to sign in to the Library Portal?",
        "gold_answer": (
            "The same credentials as the Student Information Portal "
            "or Lecturer/Staff Information Portal."
        ),
        "metadata_filter": None,
        "source_doc": "library-card-account",
        "must_contain": "same credentials",
    },
    {
    "id": 5,
    "query": "What course-related support resources are available?",
    "gold_answer": (
        "For students: course readings, subject guides, "
        "and required reading lists by course."
    ),
    "metadata_filter": {"audience": "student"},
    "source_doc": "undergraduate-student-services",
    "must_contain": "course readings",
    },
]
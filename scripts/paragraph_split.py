text = (
    "Atomicity means all or nothing.\n\n"
    "Consistency means valid invariants are preserved."
)


paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]


for i, paragraph in enumerate(paragraphs, start=1):
    print(f"p{i}: {paragraph}")

import chromadb

# Fill this in after seeing the exact-copy joke printed below, then re-run.
REWORDED = "PLACEHOLDER"

client = chromadb.PersistentClient(path="./chroma_store")
col = client.get_or_create_collection(name="jokes")

# Fetch the first stored joke to use as the exact-copy query.
first = col.get(limit=1)
exact_text = first["documents"][0]

tests = [
    ("exact copy",            exact_text),
    ("same format, new joke", "How many programmers does it take to change a light bulb? None, that's a hardware problem."),
    ("unrelated",             "The quarterly budget meeting has been moved to Thursday afternoon."),
]

if REWORDED != "PLACEHOLDER":
    tests.insert(1, ("reworded", REWORDED))

print(f"Exact-copy joke (reword this for the 'reworded' test):\n  {exact_text}\n")

for name, query in tests:
    r = col.query(query_texts=[query], n_results=1)
    dist = r["distances"][0][0]
    doc  = r["documents"][0][0]
    print(f"[{name}]")
    print(f"  distance : {dist:.4f}")
    print(f"  top match: {doc[:80].strip()!r}")
    print()

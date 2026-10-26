import uuid
from collections import Counter
import chromadb
from better_profanity import profanity

DB_PATH = "./chroma_store"

# Distance thresholds (L2; lower = more similar; tune these in measure.py)
DUPLICATE     = 0.50   # top match below this → near-exact repost
VARIANT_CAP   = 1.00   # top match below this (and gap large enough) → variant
VARIANT_GAP   = 0.08   # #1 must beat #2 by at least this much to call it a variant


# ── database helpers ──────────────────────────────────────────────────────────

def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(name="jokes")

def check_joke(text, col):
    # col.query returns lists-of-lists: one inner list per query sent.
    # We always send one query, so we index [0] to get the single result list.
    r = col.query(query_texts=[text], n_results=5)
    distances = r["distances"][0]
    documents = r["documents"][0]
    ids       = r["ids"][0]
    metadatas = r["metadatas"][0]

    best   = distances[0]
    second = distances[1] if len(distances) > 1 else float("inf")
    margin = second - best   # how much closer #1 is than #2

    if best < DUPLICATE:
        verdict = "DUPLICATE"
    elif best < VARIANT_CAP and margin >= VARIANT_GAP:
        verdict = "VARIANT"
    else:
        verdict = "ORIGINAL"

    matches = list(zip(ids, documents, distances, metadatas))
    return verdict, matches, margin

def add_joke(text, col, family_id=None):
    jid = "user-" + str(uuid.uuid4())
    fid = family_id or jid          # original jokes are their own family
    col.add(
        documents=[text],
        ids=[jid],
        metadatas=[{"source": "user", "category": "user", "rating": 0.0, "family_id": fid}],
    )
    return jid, fid


# ── display helpers ───────────────────────────────────────────────────────────

def show_matches(matches, n=3):
    for rank, (jid, doc, dist, meta) in enumerate(matches[:n], 1):
        preview = doc[:80].strip().replace("\n", " ")
        print(f"  #{rank} dist={dist:.4f}  id={jid}")
        print(f"       {preview!r}")


# ── menu commands ─────────────────────────────────────────────────────────────

def cmd_submit(col, add):
    print("Paste your joke and press Enter:")
    text = input("> ").strip()
    if not text:
        print("Nothing entered.")
        return

    if profanity.contains_profanity(text):
        print("Please keep it PG-13.")
        return

    verdict, matches, margin = check_joke(text, col)

    print(f"\nVerdict: {verdict}  (margin #1→#2: {margin:.4f})")
    show_matches(matches)

    if not add:
        return

    if verdict == "DUPLICATE":
        print("\nAlready in the collection. Not added.")
        ans = input("Add anyway? (y/n): ").strip().lower()
        if ans == "y":
            fid = matches[0][3]["family_id"]
            jid, fid = add_joke(text, col, family_id=fid)
            print(f"Added. id={jid}  family={fid}")

    elif verdict == "VARIANT":
        fid = matches[0][3]["family_id"]
        jid, fid = add_joke(text, col, family_id=fid)
        print(f"\nAdded as variant. id={jid}  family={fid}")

    else:  # ORIGINAL
        jid, fid = add_joke(text, col)
        print(f"\nAdded as new original. id={jid}  family={fid}")


def cmd_family(col):
    print("Enter a joke id (e.g. ss-123) or paste joke text:")
    text = input("> ").strip()
    if not text:
        return

    # Try it as an id first.
    result = col.get(ids=[text], include=["metadatas"])
    if result["ids"]:
        fid = result["metadatas"][0]["family_id"]
        anchor = text
    else:
        # Not an id — treat the input as joke text and find the closest match.
        r = col.query(query_texts=[text], n_results=1)
        if not r["ids"][0]:
            print("Nothing found.")
            return
        anchor = r["ids"][0][0]
        fid    = r["metadatas"][0][0]["family_id"]
        dist   = r["distances"][0][0]
        preview = r["documents"][0][0][:80].strip().replace("\n", " ")
        print(f"Closest match (dist={dist:.4f}): {preview!r}")
        print(f"Showing family for id={anchor}")

    # Fetch every joke that shares that family_id.
    family = col.get(where={"family_id": fid}, include=["documents", "metadatas"])
    print(f"\nFamily  {fid}  —  {len(family['ids'])} member(s):")
    for i, (mid, doc, meta) in enumerate(
        zip(family["ids"], family["documents"], family["metadatas"]), 1
    ):
        preview = doc[:100].strip().replace("\n", " ")
        src = meta.get("source", "?")
        print(f"  {i}. [{src}] id={mid}")
        print(f"     {preview}")


def cmd_stats(col):
    total = col.count()
    # Fetch all metadatas in one call (no documents needed for stats).
    all_meta = col.get(limit=total, include=["metadatas"])["metadatas"]

    dataset_count = sum(1 for m in all_meta if m.get("source") == "stupidstuff")
    user_count    = sum(1 for m in all_meta if m.get("source") == "user")

    family_counts = Counter(m["family_id"] for m in all_meta)
    num_families  = len(family_counts)
    top_fid, top_count = family_counts.most_common(1)[0]

    print(f"\nTotal jokes :  {total}")
    print(f"  Dataset    :  {dataset_count}")
    print(f"  User-added :  {user_count}")
    print(f"Families    :  {num_families}")
    print(f"Most retold :  {top_fid!r}  ({top_count} version(s))")


# ── main loop ─────────────────────────────────────────────────────────────────

def main():
    col = get_collection()
    if col.count() == 0:
        print("Database is empty. Run  python load_jokes.py  first.")
        return

    while True:
        print("\n--- Heard It ---")
        print("1. Submit a joke (check + add)")
        print("2. Check a joke without adding")
        print("3. Show a joke's family")
        print("4. Stats")
        print("5. Quit")

        choice = input("Choose: ").strip()
        if choice == "1":
            cmd_submit(col, add=True)
        elif choice == "2":
            cmd_submit(col, add=False)
        elif choice == "3":
            cmd_family(col)
        elif choice == "4":
            cmd_stats(col)
        elif choice == "5":
            break


if __name__ == "__main__":
    main()

import json
import os
import chromadb
import requests
from better_profanity import profanity

DATA_PATH = "data/stupidstuff.json"
DATA_URL  = "https://raw.githubusercontent.com/taivop/joke-dataset/master/stupidstuff.json"
DB_PATH   = "./chroma_store"

# Add string ids here to skip specific jokes by hand, e.g. {"ss-42", "ss-7"}
SKIP: set = set()

KEEP_CATEGORIES = {
    "Animals", "Light Bulbs", "Computers", "Business", "School",
    "Science", "Sports", "Food Jokes", "Office Jokes", "Aviation",
    "Farmers", "Holidays", "Music", "Children", "Money", "Old Age",
    "Medical", "Lawyers", "One Liners", "Family Parents", "Miscellaneous",
}

def download_if_missing():
    if os.path.exists(DATA_PATH):
        return
    os.makedirs("data", exist_ok=True)
    print("Downloading stupidstuff.json ...")
    r = requests.get(DATA_URL, timeout=30)
    r.raise_for_status()
    with open(DATA_PATH, "w") as f:
        f.write(r.text)
    print("Saved to", DATA_PATH)

def main():
    download_if_missing()

    with open(DATA_PATH) as f:
        raw = json.load(f)
    total = len(raw)

    docs, ids, metas = [], [], []
    seen_ids = set()

    n_dupe = n_skip = n_category = n_words = n_profanity = 0

    for joke in raw:
        jid  = f"ss-{joke['id']}"
        body = joke.get("body", "").strip()
        cat  = joke.get("category", "")
        rating = float(joke.get("rating", 0))

        # dedupe
        if jid in seen_ids:
            n_dupe += 1
            continue
        seen_ids.add(jid)

        # manual skip list
        if jid in SKIP:
            n_skip += 1
            continue

        # category filter
        if cat not in KEEP_CATEGORIES:
            n_category += 1
            continue

        # require at least 5 words; skip empty / near-empty bodies
        word_count = len(body.split())
        if word_count < 5 or word_count > 80:
            n_words += 1
            continue

        # profanity filter
        if profanity.contains_profanity(body):
            n_profanity += 1
            continue

        docs.append(body)
        ids.append(jid)
        metas.append({
            "source":    "stupidstuff",
            "category":  cat,
            "rating":    rating,
            "family_id": jid,   # original jokes start as their own family
        })

    kept = len(docs)
    print(f"Total in file  : {total}")
    print(f"  dropped dedupe    : {n_dupe}")
    print(f"  dropped category  : {n_category}")
    print(f"  dropped word limit: {n_words}")
    print(f"  dropped profanity : {n_profanity}")
    print(f"  dropped SKIP set  : {n_skip}")
    print(f"Kept           : {kept}")

    client     = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="jokes")

    for i in range(0, kept, 200):
        batch_docs  = docs[i:i+200]
        batch_ids   = ids[i:i+200]
        batch_metas = metas[i:i+200]
        collection.upsert(documents=batch_docs, ids=batch_ids, metadatas=batch_metas)
        print(f"  Upserted {min(i+200, kept)} / {kept}")

    print(f"Done. Total in DB: {collection.count()}")

if __name__ == "__main__":
    main()

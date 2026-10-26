import chromadb

# PersistentClient writes to disk — data survives restarts.
# In-memory client (chromadb.Client()) would lose everything on exit.
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection(name="jokes")

jokes = [
    "Why did the scarecrow win an award? Because he was outstanding in his field.",
    "What do you call a fish without eyes? A fsh.",
    "Why do cows wear bells? Because their horns do not work.",
]
ids = ["smoke-1", "smoke-2", "smoke-3"]

# upsert: safe to run multiple times — updates if id exists, adds if it does not.
collection.upsert(documents=jokes, ids=ids)

print(f"Jokes in collection: {collection.count()}")

# Heard It — near-duplicate joke detector (class project)

Python CLI app using ChromaDB. A user pastes a joke; the app finds the closest known jokes
by meaning and gives a verdict: DUPLICATE (known joke, maybe reworded), VARIANT (same idea or
format, told differently), or ORIGINAL. Originals and variants get added; variants join the
matched joke's "family" via a family_id metadata field.

## Content rule: everything must be PG-13
- Never write profanity, slurs, or explicit content anywhere: code, comments, test jokes, sample data.
- Do NOT write a hand-typed list of bad words. Use the `better-profanity` package for filtering.
- Dataset: stupidstuff.json from github.com/taivop/joke-dataset, loading ONLY these categories:
  Animals, Light Bulbs, Computers, Business, School, Science, Sports, Food Jokes, Office Jokes,
  Aviation, Farmers, Holidays, Music, Children, Money, Old Age, Medical, Lawyers, One Liners,
  Family Parents.
- Also filter dataset jokes and user submissions with better-profanity. A flagged submission
  is rejected with a polite "keep it PG-13" message.
- Test jokes you write must be clean, kid-friendly jokes.

## Technical rules
- chromadb.PersistentClient(path="./chroma_store"). Current Chroma API only: no
  Client(Settings(...)), no collection.persist().
- One item = one joke. Skip jokes over 80 words. ids: "ss-<dataset id>" or "user-<uuid>".
- metadata: source, category, rating, family_id.
- Add in batches of 200 with progress printing. Raw data goes in data/ (gitignored).

## How I work
- One step at a time. Do only what I ask in each prompt, then stop.
- Keep code simple and explain what it does and the shape of Chroma's results.
- Don't write README.md or prompt_log.md. I write those.

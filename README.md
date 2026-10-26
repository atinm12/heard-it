Heard It - near-duplicate joke detector

What it does and why

This is a joke database that allows users to enter a joke and the database tells the user if the joke, or any version of it, is already in the database. I chose this because I have heard different versions of many jokes, and this database helps consolidate different tellings of the same joke into one entry.

What's stored

The data comes from a joke dataset on GitHub called stupidstuff.json, which consists of about 3800 jokes. One item is each individual joke. I only selected jokes that were clean and school-friendly, as many jokes tend to contain cruel language. Each joke contains a category which is the subject of the joke.

How to add and search

A user adds a new item by typing 1 in the console, and a user searches by entering a joke after pressing 2 and the database will check if the joke exists.

Proving it searches by meaning

Test 1:
- Stored: the library joke ("asks the librarian for books about paranoia… 'They're right behind you.'")
- Query: the bookstore version ("something on feeling like he's being watched… 'Check over your shoulder.'")
- Result: the library joke came back #1 (distance 0.963, 0.097 ahead of the next result) → VARIANT
- Why keyword search fails: the key words are all different (library/bookstore, librarian/clerk, paranoia/being watched, right behind you/over your shoulder). The only overlap is filler words like "a" and "the."

Test 2:
- Stored: the flamingo joke ("stop impersonating a flamingo. I had to put my foot down.")
- Query: the pink bird version ("quit acting like a long-legged pink bird… took a stand on one leg.")
- Result: the flamingo joke came back #1 (distance 0.982, 0.144 ahead) → VARIANT
- Why keyword search fails: "flamingo" became "long-legged pink bird," "impersonating" became "acting like," and "put my foot down" became "took a stand on one leg." No important word is shared.

Thresholds

I measured distances by querying jokes against the database. An exact copy of joke ss-1839 came back at distance 0.0000. My two reworded test jokes came back at 0.963 (library) and 0.982 (flamingo). Unrelated jokes came back somewhere between 1.03 and 1.26.

One distance cutoff alone didn't work because reworded jokes and unrelated jokes ended up too close together in that range. So I added a margin rule: the top match also has to be at least 0.08 closer than the second match, otherwise there's no clear winner and I call it ORIGINAL instead of VARIANT.

The three constants in app.py are:
- DUPLICATE = 0.50 (top distance below this → near-exact repost)
- VARIANT_CAP = 1.00 (top distance below this, and margin large enough → variant)
- VARIANT_GAP = 0.08 (minimum gap between #1 and #2 to call it a variant)

Keeping it PG-13

I only loaded clean categories from the dataset (Animals, Light Bulbs, Computers, Business, School, Science, Sports, Food Jokes, Office Jokes, Aviation, Farmers, Holidays, Music, Children, Money, Old Age, Medical, Lawyers, One Liners, Family Parents, Miscellaneous). Every joke that gets loaded and every joke a user submits gets checked with the better-profanity package. I also spot-checked jokes by hand and added any bad ones to a SKIP set in load_jokes.py.

Setup and running

Make a virtual environment and install the dependencies:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Download the dataset and build the database (only needs to run once):

    python load_jokes.py

The dataset downloads into data/ and the database gets built in chroma_store/. Neither folder is in the repo because they're in .gitignore.

Run the app:

    python app.py

Tech

ChromaDB 1.5.9 (from requirements.txt). The default embedding model is all-MiniLM-L6-v2, which downloads automatically the first time you run load_jokes.py or app.py. No API keys needed.

How I used AI

I used Claude in chat to plan the idea, pick the dataset, and help debug, and Claude Code to write and run the code step by step. The test-query write-up was based on notes from Claude. I tested everything myself and picked the thresholds from my own measurements.

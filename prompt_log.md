Heard It - prompt log

Tools I used

I used Claude in chat to plan the project, pick the idea and dataset, and get debugging help. I used Claude Code to write, run, and commit the code one step at a time. I used chat for planning because it was easier to think through ideas there, and Claude Code for building because it can actually run the code and see errors.

Planning (Claude chat)

These are the prompts I sent in chat, word for word:

- "A near-duplicate detector for jokes that keeps growing. i wnat this to be my idea"
- "before you start, i want everything in the project to be pg13 level, nothing worse should be in the code."
- "explain prompt 5"
- "i want to transfer over to claude code, will it know the context or no?"

Building (Claude Code)

4. "Set up a venv, install chromadb and better-profanity, and save requirements.txt. Create a .gitignore for .venv, chroma_store, data, and .env. Then write smoke_test.py that upserts 3 clean jokes into a persistent collection and prints the count. Run it twice to prove the data persists."
   → venv created, both packages installed, smoke_test.py written, ran twice and printed 3 both times confirming data persists.

5. "Delete chroma_store so we start clean."
   → deleted chroma_store/ to start fresh before loading real data.

6. "Write load_jokes.py. Download stupidstuff.json into data/ if it isn't there, keep only the PG-13 categories from CLAUDE.md, drop jokes over 80 words and anything better-profanity flags, dedupe by id, and upsert in batches of 200 with progress. Print how many were kept out of the total. Leave an empty SKIP set for ids I want to exclude by hand."
   → load_jokes.py written and ran, kept 206 of 3773 jokes.

7. "Query the collection with one joke and print the full raw result object. Explain the shape: why it's lists of lists, and what the distances mean."
   → ran a raw query and got an explanation of the results structure and what the distance numbers mean.

8. "Write measure.py to help me pick distance thresholds. It should run these test cases against the jokes collection and, for each one, print the test name, the top distance, and the first 80 characters of the closest match: 1. 'exact copy': pull the first stored joke with col.get(limit=1) and query with it unchanged. Also print the full text of this joke so I can reword it. 2. 'reworded': a variable REWORDED at the top of the file that I'll fill in myself. For now set it to 'PLACEHOLDER'. Skip this test if it still says PLACEHOLDER. 3. 'same format, new joke': 'How many programmers does it take to change a light bulb? None, that's a hardware problem.' 4. 'unrelated': 'The quarterly budget meeting has been moved to Thursday afternoon.' Don't change anything in the database. Only query. Then run it once."
   → measure.py written and ran. Found a bug: 366 of 575 stored documents were empty strings from blank joke bodies. Fixed load_jokes.py to require at least 5 words, reloaded, and got correct distances: exact copy 0.0000, same-format 0.3946, unrelated 1.4783.

9. (pasted stats output showing total 539, 539 families, most retold ss-160)
   → just checking the app output after loading.

10. "Update the verdict logic in app.py to use three rules, checked in order: 1. DUPLICATE if the top distance is below 0.5 (a near-exact repost). 2. VARIANT if the top distance is below 1.0 AND the top match is at least 0.08 closer than the second match (it clearly stands out). 3. Otherwise ORIGINAL. Put 0.5, 1.0 and 0.08 as named constants at the top. In the output, also print the margin between #1 and #2 so I can see why it decided."
   → verdict logic updated with three constants DUPLICATE=0.50, VARIANT_CAP=1.00, VARIANT_GAP=0.08, and margin printed next to the verdict.

11. "load_jokes.py only kept 206 jokes. Add a debug print showing how many jokes are left after each filter step: category whitelist, word limit, profanity filter, SKIP set, and dedupe. Run it and show me the numbers. Don't change the database yet."
   → added per-step counters, ran without touching the database. Category whitelist dropped 2589, word limit dropped 895, profanity dropped 83.

12. "Add 'Miscellaneous' to the safe categories in load_jokes.py, add debug prints showing how many jokes are left after each filter step, and run it."
   → added Miscellaneous, reloaded, kept 539 jokes.

13. (pasted stats output again)
   → confirming counts after reload.

14. (same verdict logic prompt as 10, sent again)
   → already applied, no change needed.

15. "Print the full text of joke ss-1839."
   → printed the bank vault joke.

16. "Change menu option 3 so the user can paste either a joke id or the joke text. If the input isn't an existing id, search for the closest joke and show that joke's family instead."
   → updated cmd_family to try the input as an id first, then fall back to a similarity search.

17. "Update requirements.txt from the current environment, delete smoke_test.py if it's no longer needed, and commit everything with a clear message. Make sure chroma_store, data and .venv are not included."
   → requirements.txt updated, smoke_test.py deleted, initial commit made with the 6 project files.

18. "Did you delete smoke_test.py? If it exists in any earlier commit, restore it with git and commit it again. If it was never committed, recreate it as it was. From now on, never delete any files in this project without asking me first."
   → smoke_test.py was never committed, so it was recreated from earlier in the session and committed separately.

19. "Create a new public GitHub repo named heard-it under my account (atinm12) and push this project to it on the main branch. Don't delete or change any files. After pushing, show me the repo URL and confirm that chroma_store, data and .venv were not uploaded."
   → repo created at github.com/atinm12/heard-it, pushed, confirmed only the 7 project files were uploaded.

20. (pasted README instructions with four sections of user-written text, then additional sections to write)
   → README.md written and pushed.

21. (same README prompt sent again)
   → already done, nothing changed.

Problems and fixes

better_profanity wasn't found when I ran the app. Anaconda's base environment was also active, so I installed it into the venv with python -m pip install better-profanity.

Only 206 jokes loaded at first. I added debug prints to see which filter was cutting the most, then added the Miscellaneous category and got 539.

The reworded jokes came back as the #1 match, but their distances (0.96 and 0.98) were barely lower than unrelated jokes (around 1.03 to 1.26), so one cutoff couldn't tell them apart. I added a margin rule that checks how far ahead the top match is.

pip freeze pulled in my whole Anaconda environment, so requirements.txt was cut down to just chromadb and better-profanity.

smoke_test.py got deleted during a cleanup step. It was never committed, so I had it recreated and committed, and told Claude Code not to delete files without asking.

Menu option 3 asks for a joke id, not the joke text, so I used the id from an earlier result to check persistence.

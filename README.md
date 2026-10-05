# Question-Answer-AI
A Question-Answer AI with Python and MongoDB. Use wolframalpha and wikipedia library on Python site and store the request-response pairs in a MongoDB database

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in MONGO_URI and WOLFRAM_APP_ID
```

On macOS PyAudio needs PortAudio first: `brew install portaudio`.

## Run

```bash
python ui.py
```

- Type a question and press Enter (or **Ask**), or press **Speak** to ask by voice.
- If the same question was asked before, the saved answer is reused. Otherwise the answer comes from
  WolframAlpha, or from Wikipedia if WolframAlpha has none, and is saved to MongoDB.
- The second field searches the saved questions and answers (newest 50). Select a row to see the details.

## Migrating old records

Old records store the date as a string (`2026-1-5`). Convert them once:

```bash
python migrate_dates.py           # dry run
python migrate_dates.py --apply
```

## Tests

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

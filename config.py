import os

from dotenv import load_dotenv

# Read settings from a local .env file (never commit it, see .env.example)
load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")
WOLFRAM_APP_ID = os.environ.get("WOLFRAM_APP_ID")
WIKIPEDIA_LANG = os.environ.get("WIKIPEDIA_LANG", "hu")
SPEECH_LANG = os.environ.get("SPEECH_LANG", "en-US")

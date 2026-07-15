"""Load the single project-root .env for all settings modules."""

from pathlib import Path

from dotenv import load_dotenv

# backend/source/config/settings -> shortink root (parents[4])
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(_PROJECT_ROOT / ".env")

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path(os.getenv("IDEA2UI_OUTPUT_DIR", "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8010"))

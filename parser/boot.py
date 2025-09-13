from dotenv import load_dotenv, find_dotenv
from pathlib import Path

def load_environment():
    env_path = Path(__file__).resolve().parent / "env" / ".env.active"
    load_dotenv(env_path, override=True)


def boot():
    load_environment()
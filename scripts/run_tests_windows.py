import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"

if not ENV_FILE.exists():
    print("ERROR: .env file was not found.")
    raise SystemExit(1)

database_url = dotenv_values(ENV_FILE).get("DATABASE_URL")

if not database_url:
    print("ERROR: DATABASE_URL is missing from .env.")
    raise SystemExit(1)

try:
    url = make_url(database_url)
    if not url.host:
        raise ValueError("Database host is missing.")
    test_url = url.set(host="localhost")
except Exception:
    print("ERROR: DATABASE_URL could not be parsed.")
    raise SystemExit(1)

env = os.environ.copy()
env["DATABASE_URL"] = test_url.render_as_string(hide_password=False)

print("Running API tests with the Windows database host...")
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_api.py", "-q"],
    cwd=ROOT,
    env=env,
)
raise SystemExit(result.returncode)


from pathlib import Path
import subprocess

MODEL = (
    Path(__file__).resolve().parent
    / "machine_learning"
    / "isolated_footing_model_v2.pkl"
)

def ensure_model():
    if MODEL.is_file() and MODEL.stat().st_size > 1_000_000:
        return True

    result = subprocess.run(
        ["git", "lfs", "pull"],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )

    if result.returncode != 0:
        print("Git LFS download failed:", result.stderr)
        return False

    return MODEL.is_file() and MODEL.stat().st_size > 1_000_000

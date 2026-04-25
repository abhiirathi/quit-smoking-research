"""Run the full pipeline: discover apps -> pull reviews -> analyze themes."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def run(script: str) -> None:
    print(f"\n========== {script} ==========")
    r = subprocess.run([sys.executable, str(HERE / script)], cwd=HERE)
    if r.returncode != 0:
        print(f"{script} exited with {r.returncode}")
        sys.exit(r.returncode)


if __name__ == "__main__":
    run("scrape_apps.py")
    run("scrape_reviews.py")
    run("analyze_themes.py")
    run("extract_features.py")
    print("\nDone. Launch dashboard with:")
    print("  streamlit run research/dashboard.py")

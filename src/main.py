"""
Command line runner for the Music Recommender Simulation.

Usage:
    python -m src.main                 # default weights
    python -m src.main --experiment    # energy x2, genre x0.5
"""

import sys

try:
    from src.recommender import EXPERIMENT_WEIGHTS, load_songs, recommend_songs
except ImportError:  # allows `python src/main.py`
    from recommender import EXPERIMENT_WEIGHTS, load_songs, recommend_songs


PROFILES = {
    # --- Core profiles ---
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    # --- Adversarial / edge-case profiles ---
    "Conflicted (sad but 0.9 energy)": {"genre": "blues", "mood": "sad", "energy": 0.9},
    "Ghost Genre (k-pop, not in catalog)": {"genre": "k-pop", "mood": "happy", "energy": 0.7},
    "Energy Only (no genre/mood)": {"energy": 0.5},
}


def print_recommendations(name: str, prefs: dict, songs: list, weights=None, k: int = 5) -> None:
    """Print a ranked, explained block of recommendations for one profile."""
    print("=" * 72)
    print(f"Profile: {name}")
    print("Prefs:   " + ", ".join(f"{key}={val}" for key, val in prefs.items()))
    print("-" * 72)
    for rank, (song, score, explanation) in enumerate(recommend_songs(prefs, songs, k, weights), 1):
        print(f"{rank}. {song['title']} - {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    """Load the catalog and print top-5 recommendations for every profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    weights = EXPERIMENT_WEIGHTS if "--experiment" in sys.argv else None
    if weights:
        print("*** EXPERIMENT MODE: genre weight halved, energy weight doubled ***")
    print()

    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs, weights)


if __name__ == "__main__":
    main()

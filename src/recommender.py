import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Algorithm Recipe (weights)
#   genre match      -> +2.0 (flat bonus)
#   mood match       -> +1.0 (flat bonus)
#   energy closeness -> up to +1.5, scaled by 1 - |song - target|
#   acoustic fit     -> up to +0.5 (only if the user states a preference)
#   valence closeness-> up to +0.5 (only if the user states a target)
# Max possible score with every preference set = 5.5
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 1.5,
    "acoustic": 0.5,
    "valence": 0.5,
}

# Phase 4 experiment: double energy, halve genre.
EXPERIMENT_WEIGHTS: Dict[str, float] = {**DEFAULT_WEIGHTS, "genre": 1.0, "energy": 3.0}

NUMERIC_INT_FIELDS = ("id",)
NUMERIC_FLOAT_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")


@dataclass
class Song:
    """A single catalog track and its audio attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """A user's taste profile used as the scoring target."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

    def to_prefs(self) -> Dict:
        """Convert the profile into the dict format used by score_song."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "likes_acoustic": self.likes_acoustic,
        }


class Recommender:
    """OOP wrapper around the functional scoring and ranking logic."""

    def __init__(self, songs: List[Song], weights: Optional[Dict[str, float]] = None):
        """Store the catalog and the weights used for scoring."""
        self.songs = songs
        self.weights = weights or DEFAULT_WEIGHTS

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects for a user, highest score first."""
        prefs = user.to_prefs()
        ranked = sorted(
            self.songs,
            key=lambda s: score_song(prefs, asdict(s), self.weights)[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of a song's score for a user."""
        score, reasons = score_song(user.to_prefs(), asdict(song), self.weights)
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read the songs CSV into a list of dicts with numeric fields converted."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in NUMERIC_INT_FIELDS:
                row[field] = int(row[field])
            for field in NUMERIC_FLOAT_FIELDS:
                row[field] = float(row[field])
            songs.append(row)
    return songs


def closeness(value: float, target: float) -> float:
    """Return 1.0 for an exact match, falling linearly to 0.0 at a gap of 1.0."""
    return max(0.0, 1.0 - abs(value - target))


def score_song(
    user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None
) -> Tuple[float, List[str]]:
    """Score one song against user prefs, returning (score, list of reasons)."""
    w = weights or DEFAULT_WEIGHTS
    score = 0.0
    reasons: List[str] = []

    genre = user_prefs.get("genre")
    if genre and song["genre"].lower() == genre.lower():
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']:.1f})")

    mood = user_prefs.get("mood")
    if mood and song["mood"].lower() == mood.lower():
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']:.1f})")

    if "energy" in user_prefs:
        pts = w["energy"] * closeness(song["energy"], user_prefs["energy"])
        score += pts
        reasons.append(
            f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{pts:.2f})"
        )

    if "likes_acoustic" in user_prefs:
        fit = song["acousticness"] if user_prefs["likes_acoustic"] else 1 - song["acousticness"]
        pts = w["acoustic"] * fit
        score += pts
        label = "acoustic" if user_prefs["likes_acoustic"] else "non-acoustic"
        reasons.append(f"{label} fit (+{pts:.2f})")

    if "valence" in user_prefs:
        pts = w["valence"] * closeness(song["valence"], user_prefs["valence"])
        score += pts
        reasons.append(f"valence closeness (+{pts:.2f})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest-first, and return the top k with explanations."""
    scored = [(song, *score_song(user_prefs, song, weights)) for song in songs]
    scored.sort(key=lambda item: item[1], reverse=True)  # stable: ties keep CSV order
    return [(song, score, "; ".join(reasons)) for song, score, reasons in scored[:k]]

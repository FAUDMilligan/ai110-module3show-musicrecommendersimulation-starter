# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests the top 5 songs from a small catalog that best fit a user's stated taste: favorite genre, favorite mood, target energy level, and optionally whether they like acoustic sound. It assumes users can describe their taste in those terms and that one profile describes them at a given moment. It's built for classroom exploration of how recommenders work, not for real listeners. It has no listening history, no other users, and only 18 songs.

---

## 3. How the Model Works

Imagine a judge with a score sheet who looks at every song, one at a time:

- If the song's genre is your favorite genre, it gets **2 points**.
- If its mood is your favorite mood, it gets **1 point**.
- It gets up to **1.5 points** for energy. A song with exactly your preferred energy level gets all 1.5, and the further away it is (too calm *or* too intense), the fewer points it earns.
- If you said you like (or dislike) acoustic music, it gets up to **0.5 points** for being acoustic (or electronic).

After every song is scored, the list is sorted from highest to lowest and the top 5 are shown, along with the reasons each one earned its points.

Changes from the starter: I implemented CSV loading with numeric conversion, the scoring rule above, the ranking function, an explanation string for every song, configurable weights (so experiments don't require editing the logic), and an optional valence target.

---

## 4. Data

- **18 songs**: the 10 starter songs plus 8 I added.
- **15 genres**: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, metal, classical, country, reggae, edm, r&b, blues. Lofi (3 songs) and pop (2) are the only genres with more than one song.
- **14 moods**, including happy, chill, intense, relaxed, moody, focused, confident, angry, peaceful, nostalgic, uplifting, euphoric, romantic, sad.
- Numeric features: energy, tempo_bpm, valence, danceability, acousticness (0–1 scales except tempo).
- **Missing:** lyrics, language, vocals vs. instrumental, era/release year, artist popularity, and any listening behavior (skips, replays, playlists). Most real-world musical taste (Latin, K-pop, gospel, punk, etc.) isn't in the catalog at all.

---

## 5. Strengths

- **Clear single-genre profiles work well.** "Chill Lofi" returns all three lofi tracks, then ambient and jazz, which is exactly what a study-music listener would want. "Deep Intense Rock" puts *Storm Runner* first by a 2-point margin.
- **Energy closeness behaves sensibly.** Low-energy fans aren't punished for wanting calm music, because the score rewards being *near* the target rather than being high.
- **Every recommendation is explainable.** The reasons list shows exactly which features earned points, so a surprising pick can be traced in seconds.

---

## 6. Limitations and Bias

The biggest weakness I found is that **genre is an exact-match gate worth almost half the maximum score, and most genres have only one song**. A blues fan gets *Empty Station Blues* at #1 even when they asked for 0.9 energy (the song is 0.33). The categorical bonuses (+3.0) completely override the energy mismatch. After that one song, the rest of the list is filled by high-energy rock, pop, and edm that share nothing with blues except energy. This creates a filter-bubble effect in reverse: lofi listeners (3 lofi songs) get a rich, coherent top 3, while fans of single-song genres get one pick and then filler. Exact string matching also means "indie pop" never counts as "pop", and a genre missing from the catalog (k-pop) silently loses 2 of the 5.5 possible points, so those users always see lower-confidence, mood/energy-only results. Finally, mid-range energy targets (~0.5) produce many near-ties that are broken only by CSV order, which is arbitrary.

---

## 7. Evaluation

**Profiles tested** (full output in [README.md](README.md#experiments-you-tried)):

1. High-Energy Pop: pop, happy, 0.8
2. Chill Lofi: lofi, chill, 0.35, likes acoustic
3. Deep Intense Rock: rock, intense, 0.9, dislikes acoustic
4. Conflicted (adversarial): blues, sad, energy 0.9
5. Ghost Genre (adversarial): k-pop (not in catalog), happy, 0.7
6. Energy Only (edge case): energy 0.5, nothing else

**Does it feel right?** For High-Energy Pop, yes. *Sunrise City* (pop, happy, 0.82) is the obvious #1. Its 4.47 is 2.0 (genre) + 1.0 (mood) + 1.47 (energy is 0.02 off target). *Gym Hero* is #2 only because of the genre bonus. I'd personally rank *Rooftop Lights* (indie pop, happy, 0.76) above it, since it actually sounds happy.

**What surprised me:**
- *Gym Hero* shows up in the top 2 for both the Pop and the Rock profiles. It's pop *and* intense *and* 0.93 energy, so it collects partial credit from very different users.
- The Conflicted profile didn't produce a "sad but energetic" compromise. It just picked the only sad song and then ignored sadness entirely.
- The Energy Only profile ranked country and r&b at the top with *identical* scores (1.47), so the tie was decided by file order.

**Pairwise comparisons:**

- **High-Energy Pop vs. Chill Lofi:** these lists share no songs. Pop pulls bright, 0.75–0.93 energy tracks; Lofi shifts to 0.28–0.42 energy, highly acoustic tracks. That makes sense because both genre and energy targets point in opposite directions.
- **High-Energy Pop vs. Deep Intense Rock:** both have high energy targets, so they share *Gym Hero* and *Sunrise City*. The order flips because the mood bonus moves from "happy" to "intense", so *Gym Hero* (intense) gains and *Sunrise City* (happy) drops to #5 for Rock.
- **High-Energy Pop vs. Conflicted:** Pop stays mostly happy/bright; Conflicted's tail is the same intense high-energy songs as Rock. With no second blues/sad song available, energy is the only remaining signal.
- **High-Energy Pop vs. Ghost Genre:** almost the same songs (*Rooftop Lights*, *Sunrise City*, *Night Drive Loop*), but with no genre match available, *Rooftop Lights* wins on mood + closer energy (0.76 vs. target 0.7). The k-pop user's best score (2.41) is far below the pop user's (4.47), which shows how much the genre bonus inflates confidence.
- **High-Energy Pop vs. Energy Only:** Energy Only jumps to mid-tempo country, r&b, and reggae near 0.5. Without categorical bonuses, every score falls in a narrow 1.35–1.47 band, so the system has very little conviction.
- **Chill Lofi vs. Deep Intense Rock:** these are mirror images. Lofi favors acousticness of 0.7+ and energy below 0.45; Rock favors acousticness below 0.15 and energy above 0.9. The acoustic preference reinforces the energy split.
- **Chill Lofi vs. Conflicted:** the blues song (0.33 energy, 0.81 acousticness) would actually fit the Lofi listener's sound well, but it never appears in the Lofi top 5. It doesn't match genre or mood, and jazz/ambient edge it out on energy and acousticness.
- **Chill Lofi vs. Ghost Genre:** no overlap. Ghost Genre's 0.7 energy target and "happy" mood keep it in brighter territory.
- **Chill Lofi vs. Energy Only:** they share *Midnight Coding* and *Focus Flow*. Lofi tracks sit around 0.4 energy, close to 0.5, so they're the closest thing to a "neutral" sound.
- **Deep Intense Rock vs. Conflicted:** the lists share four of five songs (*Storm Runner*, *Gym Hero*, *Neon Euphoria*, *Iron Cathedral*). Once genre/mood bonuses are used up, any 0.9-energy profile converges on the same high-energy pool.
- **Deep Intense Rock vs. Ghost Genre:** these share only *Sunrise City*. Rock's 0.9 target and "intense" mood pull metal/edm in; Ghost Genre's 0.7 and "happy" pull indie pop/synthwave.
- **Deep Intense Rock vs. Energy Only:** no overlap. 0.9 vs. 0.5 energy targets select completely different songs.
- **Conflicted vs. Ghost Genre:** Conflicted has a confident #1 (genre + mood match) followed by a cliff. Ghost Genre has no confident pick at all, just a smooth slope of mood/energy matches.
- **Conflicted vs. Energy Only:** both show what happens when energy is the only signal left. Conflicted gets loud songs and Energy Only gets mid-tempo songs, and neither list has a clear personality.
- **Ghost Genre vs. Energy Only:** Ghost Genre still has mood to break ties (happy songs float up); Energy Only doesn't, so it relies on CSV order to break ties.

**Experiment: weight shift** (genre 2.0 → 1.0, energy 1.5 → 3.0). *Rooftop Lights* overtook *Gym Hero* for the Pop profile, which I'd call more accurate. *Spacewalk Thoughts* (ambient, chill) overtook *Focus Flow* (lofi, focused) for Lofi, which also feels right. But for the Conflicted profile, intense rock/pop came within 0.3 points of the only sad song. Overall the results were **different more than better**: energy started to dominate, and genre/mood became tiebreakers. Both test cases in `tests/test_recommender.py` pass under the default weights.

---

## 8. Future Work

- Fuzzy genre matching (genre families: "indie pop" → pop, "k-pop" → pop) to soften the exact-match gate.
- A diversity rule in the ranking step, e.g. at most 2 songs per genre or artist in the top 5.
- Let users weight their own preferences ("mood matters more to me than genre"), or let them mark a preference as "flexible".
- Use valence and tempo by default, and add a simulated listening history (likes/skips) to try a tiny collaborative-filtering signal.
- Grow the catalog so every genre has several songs.

---

## 9. Personal Reflection

The biggest lesson is that a recommender's "intelligence" is mostly a set of weights someone chose, and that the dataset quietly decides who gets good results. I was surprised how often a single versatile song (*Gym Hero*) reached the top across very different profiles, and how a user with contradictory tastes simply had half their preferences ignored. It makes me read Spotify's recommendations differently: when a playlist feels repetitive, it's probably a filter bubble created by overweighting a few features, plus a catalog of signals that over-represents what's already popular.

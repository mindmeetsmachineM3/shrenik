# Business Ideas page kit (graphics-explained, 13-year-old-boy style voice)
One new small-business idea per post: Reel (animated icon, cost meter, steps, earning bars, subtitles, voice), 7-slide carousel, 2 poster styles, captions + hashtags.
Look: bright neo-brutalist infographic, all icons drawn by code (no licences).

## Run locally
    pip install -r requirements.txt
    set GEMINI_API_KEY=your_key        (optional; without it the 8 built-in ideas are used)
    python make.py                     -> output/pack_<seed>/  (posters, carousel, reel.mp4, captions_and_hashtags.txt)
    python make.py --voice edge --palette sun --no-reel --offline

## Auto-post to Instagram
See GITHUB_SETUP.md. `autopost.py` posts 4 times a day at random times (reel, carousel, 2 posters), a new idea each time.

## Voice (13-year-old boy)
Gemini TTS voice "Puck" with a "13-year-old Indian boy" style prompt + a gentle pitch lift (VOICE_PITCH, default 1.14). Fallback Edge voice with pitch lift.
Tune: VOICE_PITCH (1.0 = off, 1.25 = very high), VOICE_RATE (e.g. -8%), VOICE_KID=0 for a normal adult voice. A real child's voice cannot be cloned or faked: this is a young-sounding synthetic voice.

## Music
Drop royalty-free .mp3 files in music/ (Pixabay Music, YouTube Audio Library). Empty = generated upbeat beat. Never use copyrighted songs.

## Honest rules built in
Numbers are conservative AI estimates (tier-2 Indian city), always labelled "approx., not guaranteed". No income promises. Check the numbers before posting.

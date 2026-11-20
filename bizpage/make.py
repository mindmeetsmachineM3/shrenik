"""python make.py [--no-reel] [--offline] [--voice auto|none|edge|gemini|sarvam|elevenlabs] [--seed N] [--palette sun|grape|mint|sky|coral|lime]"""
import argparse, json, random, shutil, sys, time

from kit import content, gfx, posters, reel
from kit.common import ROOT

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int); ap.add_argument("--no-reel", action="store_true"); ap.add_argument("--offline", action="store_true")
ap.add_argument("--voice", default="auto"); ap.add_argument("--palette", default="")
a = ap.parse_args()
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
seed = a.seed if a.seed is not None else int(time.time()) % 100000
rng = random.Random(seed)
st_f = ROOT / "state.json"
st = json.loads(st_f.read_text()) if st_f.exists() else {}
used, num = st.get("used", []), st.get("count", 0) + 1
pal = a.palette or rng.choice(list(gfx.PALETTES))
idea, how = content.make_idea(cfg, rng, not a.offline, used)
tf = rng.choice(gfx.TITLE_FONTS[:3]); P = gfx.Pal(pal); h = cfg["handle"]
out = ROOT / "output" / f"pack_{seed}"
shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
posters.post_card(idea, P, seed, h, num, tf).save(out / "post_1_card.jpg", quality=93)
posters.post_numbers(idea, gfx.Pal(rng.choice(list(gfx.PALETTES))), seed + 1, h, num, tf).save(out / "post_2_numbers.jpg", quality=93)
for k, im in enumerate(posters.carousel(idea, P, seed, h, num, tf), 1):
    im.save(out / f"carousel_{k:02d}.jpg", quality=93)
info = "skipped"
if not a.no_reel:
    try:
        info = reel.build(idea, num, h, pal, out / "reel.mp4", a.voice, seed, cfg.get("voice_lang", "hinglish"))
    except Exception as ex:
        info = f"FAILED: {ex}"; print("Reel failed:", ex, file=sys.stderr)
tags = " ".join(idea["hashtags"][:10])
txt = [f"IDEA #{num}: {idea['name']}  |  idea: {how}  |  reel: {info}", ""]
for k in ("post", "carousel", "reel"):
    txt += [f"--- {k.upper()} CAPTION ---", idea["captions"][k], "", tags, ""]
txt += ["CHECK: numbers are AI estimates for a tier-2 Indian city. Edit them if you know better before posting."]
(out / "captions_and_hashtags.txt").write_text("\n".join(txt), encoding="utf-8")
st_f.write_text(json.dumps({"used": (used + [idea["name"]])[-80:], "count": num}))
print("Done ->", out, "|", how, "|", info)

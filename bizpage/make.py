"""python make.py [--no-reel] [--offline] [--voice auto|none|edge|gemini|sarvam|elevenlabs] [--seed N]
Makes one full 'asli hisaab' pack: Reel + 7-slide carousel + 2 posters + captions, for review before posting."""
import argparse, json, random, shutil, sys, time

from kit import hisaab, reel, wb
from kit.common import ROOT

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int); ap.add_argument("--no-reel", action="store_true"); ap.add_argument("--offline", action="store_true")
ap.add_argument("--voice", default="auto")
a = ap.parse_args()
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
seed = a.seed if a.seed is not None else int(time.time()) % 100000
rng = random.Random(seed)
st_f = ROOT / "state.json"
st = json.loads(st_f.read_text()) if st_f.exists() else {}
used, num = st.get("used", []), st.get("count", 0) + 1
idea, how = hisaab.make_idea(cfg, rng, not a.offline, used)
h = cfg["handle"]
out = ROOT / "output" / f"pack_{seed}"
shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
wb.poster_unit(idea, h).save(out / "post_1_unit_cost.jpg", quality=93)
wb.poster_scen(idea, h).save(out / "post_2_scenarios.jpg", quality=93)
for k, im in enumerate(wb.carousel(idea, h), 1):
    im.save(out / f"carousel_{k:02d}.jpg", quality=93)
info = "skipped"
if not a.no_reel:
    try:
        info = reel.build(idea, num, h, "sun", out / "reel.mp4", a.voice, seed, cfg.get("voice_lang", "hinglish"))
    except Exception as ex:
        info = f"FAILED: {ex}"; print("Reel failed:", ex, file=sys.stderr)
tags = " ".join(idea["hashtags"][:10])
txt = [f"HISAAB #{num}: {idea['name']}  |  numbers: {how}  |  reel: {info}", ""]
for k in ("post", "carousel", "reel"):
    txt += [f"--- {k.upper()} CAPTION ---", idea["captions"][k], "", tags, ""]
txt += ["SPOKEN SCRIPT:"] + [f"  {k}: {v}" for k, v in idea["say"].items()]
txt += ["", "CHECK: items tagged 'anumaan' are estimates. Edit them if you know the local rate. Sources found: " + (", ".join(idea["sources"]) or "none")]
(out / "captions_and_hashtags.txt").write_text("\n".join(txt), encoding="utf-8")
st_f.write_text(json.dumps({"used": (used + [idea["name"]])[-80:], "count": num}))
print("Done ->", out, "|", how, "|", info)

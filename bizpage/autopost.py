"""Auto-post to Instagram: 4 random times per day (IST). Each day ONE business gets its "asli hisaab" (real arithmetic) and all of the day's posts use it: Reel, carousel, 2 posters.
python autopost.py [--dry-run] [--diagnose] [--force reel|carousel|poster]"""
import argparse, datetime as dt, json, os, random, sys

from kit import hisaab, ig, reel, wb
from kit.common import ROOT

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
WINS = [(8, 10.5), (11.5, 14), (16, 19), (20, 23)]
FMTS = ["reel", "carousel", "poster", "poster"]
ST = ROOT / "state.json"

ap = argparse.ArgumentParser()
ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--diagnose", action="store_true")
ap.add_argument("--force", choices=["reel", "carousel", "poster"])
a = ap.parse_args()
if a.diagnose:
    ig.diagnose(); sys.exit(0)

cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
os.environ.setdefault("VOICE_GENDER", cfg.get("voice_gender", "M"))
now = dt.datetime.now(IST)
today, hm = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
state = json.loads(ST.read_text()) if ST.exists() else {}
state.setdefault("used", []); state.setdefault("count", 0)
if state.get("date") != today:
    r = random.Random(today); f = FMTS[:]; r.shuffle(f); slots = []
    for (a0, a1), fm in zip(WINS, f):
        m = int(r.uniform(a0, a1) * 60)
        slots.append({"t": f"{m // 60:02d}:{m % 60:02d}", "fmt": fm, "done": False})
    state.update(date=today, slots=sorted(slots, key=lambda s: s["t"]))
    print("Today's plan:", [(s["t"], s["fmt"]) for s in state["slots"]])
if a.force:
    slot = {"t": hm, "fmt": a.force, "done": False}
else:
    slot = None
    for s_ in state["slots"]:
        if s_["done"] or s_["t"] > hm:
            continue
        late = (dt.datetime.strptime(hm, "%H:%M") - dt.datetime.strptime(s_["t"], "%H:%M")).seconds
        if late > 4 * 3600:                                   # too old: skip it, look at the next slot in the same run
            s_["done"] = True; print("Slot missed, skipping", s_); continue
        slot = s_; break
    if not slot:
        print("Nothing due now.", hm, [(x["t"], x["fmt"], x["done"]) for x in state["slots"]]); ST.write_text(json.dumps(state, indent=1)); sys.exit(0)

seed = int(now.strftime("%y%m%d")) * 100 + state["count"] % 100
rng = random.Random(today)
h = cfg["handle"]
td = state.get("today_idea")
fresh = False
if td and td.get("date") == today and td.get("raw"):
    idea, how = hisaab.compute(td["raw"], cfg), "today's hisaab (reused)"
else:
    idea, how = hisaab.make_idea(cfg, rng, True, state["used"])
    fresh = True
num = state["count"] + (1 if fresh else 0)
seed += sum(1 for s_ in state["slots"] if s_["done"])
out = ROOT / "output" / f"post_{seed}"; out.mkdir(parents=True, exist_ok=True)
tags = " ".join(idea["hashtags"][:10]); fmt = slot["fmt"]
print(f"Making a {fmt}: {idea['name']} ({how})")
try:
    if fmt == "reel":
        p = out / "reel.mp4"
        info = reel.build(idea, num, h, "sun", p, "auto", seed, cfg.get("voice_lang", "hinglish"))
        caption = f"{idea['captions']['reel']}\n\n{tags}"; print(info)
        mid = None if a.dry_run else ig.reel(str(p), caption)
    elif fmt == "carousel":
        ps = []
        for k, im in enumerate(wb.carousel(idea, h), 1):
            q = out / f"c{k}.jpg"; im.save(q, quality=93); ps.append(str(q))
        caption = f"{idea['captions']['carousel']}\n\n{tags}"
        mid = None if a.dry_run else ig.carousel(ps, caption)
    else:
        q = out / "poster.jpg"
        n_done = sum(1 for s_ in state["slots"] if s_["fmt"] == "poster" and s_["done"])
        (wb.poster_unit if n_done % 2 == 0 else wb.poster_scen)(idea, h).save(q, quality=93)
        caption = f"{idea['captions']['post']}\n\n{tags}"
        mid = None if a.dry_run else ig.image(str(q), caption)
except ig.TokenError as ex:
    print("TOKEN/ACCOUNT PROBLEM:", ex, file=sys.stderr); sys.exit(3)
(out / "caption_and_hashtags.txt").write_text(f"FORMAT: {fmt}\nIDEA: {idea['name']} ({how})\n\n--- CAPTION ---\n{caption}\n", encoding="utf-8")
print("Caption:\n" + caption)
print("Posted media id:" if mid else "Dry run (not posted).", mid or "")
if not a.dry_run:
    slot["done"] = True
    if fresh:
        state["used"] = (state["used"] + [idea["name"]])[-80:]; state["count"] += 1
    state["today_idea"] = {"date": today, "raw": idea["_raw"] if "_raw" in idea else td["raw"]}
ST.write_text(json.dumps(state, indent=1))

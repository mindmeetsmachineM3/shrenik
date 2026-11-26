"""'Asli hisaab' content: one small business, worked out with real arithmetic (capital split, cost of ONE unit, 3 scenarios, payback, FD comparison).
The AI (or the built-in library) only supplies the raw numbers; ALL sums are done here in code, so the spoken script, graphics and caption always agree.
Every number is tagged 'listing' (found on a source Gemini returned) or 'anumaan' (estimate). Nothing is shown as sourced unless a source came back."""
import json
import os
import re
import sys

from .common import ROOT
from .icons import NAMES as ICONS

DAYS = 26                       # working days per month used in all sums
FD_RATE = float(os.getenv("FD_RATE") or 6.5)      # % a year, shown as approx; change in config/workflow if needed

IDEA_TYPES = ["street food stall", "small shop or kiosk", "doorstep service", "home-based food business", "small manufacturing / packing unit at home",
              "tiffin or catering", "retail on wheels (cart / van)", "repair or service point", "beverage or snack counter", "online + offline reselling"]

PROMPT = """You prepare the raw numbers for a short Instagram video called 'asli hisaab' (the real accounts) of ONE small Indian business, for a tier-2 Indian city, in {month}.
Business type to pick from: {typ}. Capital budget (batwara) to explain: Rs {budget}. Do not repeat: {avoid}.
{search_note}
RULES
- Realistic, conservative, legal, no big licence. Per-unit costs must be for ONE unit that is sold (e.g. one plate, one cup, one tiffin) and their total must be clearly LESS than the selling price.
- Use rupees. unit costs may have decimals (e.g. 1.32). Capital items are one-time buys (equipment, deposits, licence); their total must be LESS than the budget (the rest is working capital, we add it).
- tag each number: "listing" ONLY if you found it on a web page now, else "anumaan" (estimate). Never invent a source.
- on-screen text: simple English or Hinglish, short. icon must be exactly one of: {icons}
Return ONLY JSON:
{{"name":"max 4 words, the business","unit":"one word or two: what is sold per sale, e.g. plate","icon":"one of the list","price":int selling price of one unit,
 "hook":"max 8 words, curiosity, e.g. 'Rs 1 lakh se stall: kitna bachega?'",
 "capital_items":[{{"n":"max 3 words","amt":int,"d":"max 6 words","tag":"listing|anumaan"}} x4 to 5],
 "unit_costs":[{{"n":"max 4 words incl. quantity","amt":number,"tag":"listing|anumaan"}} x4 to 6],
 "scenarios":[{{"label":"Kamzor jagah","per_day":int units sold a day,"fixed":int extra fixed cost per month (rent, helper, licence),"note":"max 6 words"}},{{"label":"Theek-thaak","per_day":int,"fixed":int,"note":""}},{{"label":"Viral jagah","per_day":int,"fixed":int,"note":""}}],
 "truths":["3 hard truths of this business, max 12 words each, honest"],
 "tasks":[{{"t":"max 4 words","d":"max 10 words"}} x4 first things to do],
 "question":"one easy question for followers, max 9 words",
 "sources":["site names you really used, may be empty"],
 "hashtags":["8 to 10 relevant tags, no #viral #fyp"]}}"""

# built-in library: ESTIMATES (anumaan) for a tier-2 city. Used when Gemini is not available.
LIBRARY = [
    dict(name="Sandwich Cart", unit="sandwich", icon="food", price=40, hook="Rs 1 lakh se sandwich cart: kitna bachega?",
         capital_items=[dict(n="Cart", amt=28000, d="Steel cart with shelves"), dict(n="Grill + toaster", amt=9000, d="Two commercial units"), dict(n="Gas set", amt=6500, d="Cylinder, burner, regulator"), dict(n="Utensils", amt=6000, d="Boxes, knives, trays"), dict(n="FSSAI + board", amt=3500, d="Licence and sign")],
         unit_costs=[dict(n="Bread 4 slices", amt=6.0), dict(n="Butter + sauces", amt=4.5), dict(n="Veg filling", amt=7.0), dict(n="Cheese", amt=4.0), dict(n="Gas + packing", amt=3.5)],
         scenarios=[dict(label="Kamzor jagah", per_day=40, fixed=3000, note="Gali ke andar"), dict(label="Theek-thaak", per_day=90, fixed=5000, note="College ke paas"), dict(label="Viral jagah", per_day=170, fixed=13000, note="Market + helper")],
         truths=["Pehle 2 mahine customer banane mein jaate hain", "Bread aur sabzi roz fresh chahiye, waste hota hai", "Barish ke din bikri aadhi ho sakti hai"],
         tasks=[dict(t="Jagah test karo", d="3 din subah aur shaam gino kitne log guzarte hain"), dict(t="FSSAI le lo", d="Basic registration online"), dict(t="Menu chhota rakho", d="4 sandwich se shuru karo"), dict(t="Roz ka hisaab likho", d="Kharcha aur bikri alag likho")],
         question="Aapke sheher mein sabse chalne wala stall kaunsa?"),
    dict(name="Fresh Juice Counter", unit="glass", icon="cup", price=30, hook="Rs 1 lakh ka juice counter: asli hisaab",
         capital_items=[dict(n="Counter", amt=25000, d="Table, shelves, shade"), dict(n="Juicer machine", amt=12000, d="Heavy duty juicer"), dict(n="Fridge", amt=14000, d="Small commercial fridge"), dict(n="Glasses + tools", amt=5000, d="Glasses, jugs, knives"), dict(n="FSSAI + board", amt=3500, d="Licence and sign")],
         unit_costs=[dict(n="Fruit 250 g", amt=11.0), dict(n="Ice + sugar", amt=2.0), dict(n="Glass + straw", amt=2.5), dict(n="Water + electricity", amt=1.5)],
         scenarios=[dict(label="Kamzor jagah", per_day=45, fixed=3500, note="Kam foot-fall"), dict(label="Theek-thaak", per_day=100, fixed=5500, note="Bus stop ke paas"), dict(label="Viral jagah", per_day=190, fixed=13500, note="Hospital ya college")],
         truths=["Garmi mein bikri doguni, sardi mein aadhi", "Fruit ka rate roz badalta hai", "Kharab fruit ka waste seedha nuksaan hai"],
         tasks=[dict(t="Rate list banao", d="Mandi ke 3 dukandaron se bhav pucho"), dict(t="Season dekho", d="Garmi se 1 mahina pehle shuru karo"), dict(t="Safai pe dhyan", d="Saaf glass aur dhakke hue fruit"), dict(t="Combo offer", d="Do glass pe chhoot")],
         question="Aapke sheher mein juice ka best spot kaunsa?"),
    dict(name="Pani Puri Cart", unit="plate", icon="food", price=30, hook="Rs 1 lakh se pani puri cart: kitna kamaya?",
         capital_items=[dict(n="Cart", amt=22000, d="Glass-top cart"), dict(n="Pani containers", amt=5000, d="Steel pots and taps"), dict(n="Gas set", amt=6500, d="For boiling potatoes"), dict(n="Utensils", amt=5000, d="Plates, spoons, trays"), dict(n="FSSAI + board", amt=3500, d="Licence and sign")],
         unit_costs=[dict(n="6 puri", amt=4.0), dict(n="Pani + masala", amt=5.0), dict(n="Aloo + chana", amt=4.0), dict(n="Plate + gas", amt=3.0)],
         scenarios=[dict(label="Kamzor jagah", per_day=40, fixed=3000, note="Chhoti gali"), dict(label="Theek-thaak", per_day=90, fixed=5000, note="Society gate"), dict(label="Viral jagah", per_day=170, fixed=12500, note="Market + helper")],
         truths=["Shaam ke 3-4 ghante hi asli bikri hoti hai", "Hygiene pe ek complaint, aur customer gaya", "Barish mein bikri gir jaati hai"],
         tasks=[dict(t="Jagah chuno", d="Shaam ko bheed wali jagah 3 din dekho"), dict(t="Swad pakka karo", d="Pani ka swad 20 logon se test karo"), dict(t="FSSAI le lo", d="Basic registration online"), dict(t="Safai dikhao", d="Saaf plate, dhakka hua pani")],
         question="Aapke sheher ka best pani puri wala kaunsa?"),
    dict(name="Home Tiffin Service", unit="tiffin", icon="home", price=90, hook="Rs 1 lakh se tiffin service: asli hisaab",
         capital_items=[dict(n="Gas + cooker", amt=9000, d="Gas set, cookers, kadhai"), dict(n="Utensils", amt=8000, d="Large pots, ladles"), dict(n="Tiffin boxes", amt=9000, d="60 steel boxes"), dict(n="Bike for delivery", amt=0, d="Use your own"), dict(n="FSSAI + packaging", amt=4000, d="Licence, labels")],
         unit_costs=[dict(n="Roti + sabzi", amt=24.0), dict(n="Dal + rice", amt=16.0), dict(n="Oil, masala, gas", amt=9.0), dict(n="Packing", amt=3.0), dict(n="Delivery petrol", amt=4.0)],
         scenarios=[dict(label="Kamzor start", per_day=15, fixed=2000, note="15 tiffin roz"), dict(label="Theek-thaak", per_day=40, fixed=5000, note="Offices + PG"), dict(label="Viral jagah", per_day=90, fixed=16000, note="2 helpers")],
         truths=["Customer bharosa banane mein 2-3 mahine lagte hain", "Roz subah jaldi uthna padta hai", "Ek din khana kharab, to sab customer jaate hain"],
         tasks=[dict(t="Menu fix karo", d="2 sabzi, dal, rice, roti"), dict(t="Free trial do", d="10 logon ko ek-ek tiffin"), dict(t="Monthly plan", d="Advance leke shuru karo"), dict(t="Time pakka rakho", d="Roz ek hi time pe delivery")],
         question="Aapke area mein tiffin ka kitna rate hai?"),
]


# ------------------------------------------------------------------ number helpers
def ig(n):
    """Indian digit grouping: 1234567 -> 12,34,567"""
    s = str(int(round(abs(n))))
    if len(s) > 3:
        s = re.sub(r"(\d+?)(?=(\d\d)+(\d)(?!\d))", r"\1,", s)
    return ("-" if n < 0 else "") + s


def rs(n, dec=None):
    if dec is None:
        dec = 0 if abs(n - round(n)) < 1e-9 else 2
    return "₹" + (ig(n) if dec == 0 else f"{abs(n):,.{dec}f}".join(["-" if n < 0 else "", ""]))


def lakh(n):
    """short label: ₹6.3 lakh / ₹52,500 / ₹8,800"""
    if abs(n) >= 100000:
        return f"₹{abs(n) / 100000:.2f}".rstrip("0").rstrip(".") + " lakh" if n > 0 else f"-₹{abs(n) / 100000:.2f}".rstrip("0").rstrip(".") + " lakh"
    return rs(n)


def say_rs(n):
    n = float(n)
    if n < 0:
        return "minus " + say_rs(-n)
    if n >= 100000:
        return f"{n / 100000:g} lakh"
    if n >= 1000:
        return f"{round(n / 1000, 1):g} hazaar"
    if abs(n - round(n)) < 1e-9:
        return str(int(round(n)))
    r, p = divmod(round(n * 100), 100)
    return f"{int(r)} rupaye {int(p)} paise" if r else f"{int(p)} paise"


# ------------------------------------------------------------------ normalise + all the sums
def compute(raw, cfg):
    d = dict(raw)
    d["kind"] = "hisaab"
    d["icon"] = d.get("icon") if d.get("icon") in ICONS else "coin"
    d["price"] = int(d["price"])
    d["budget"] = int(d.get("budget") or 100000)
    items = [dict(n=str(x["n"]), amt=int(x["amt"]), d=str(x.get("d", "")), tag=_tag(x)) for x in d["capital_items"] if int(x["amt"]) > 0][:5]
    spent = sum(x["amt"] for x in items)
    if not items or spent >= d["budget"]:
        raise ValueError("capital items must be less than the budget")
    items.append(dict(n="Kachcha maal + reserve", amt=d["budget"] - spent, d="First stock and 1-2 months buffer", tag="anumaan"))
    d["capital_items"], d["capital"] = items, d["budget"]
    costs = [dict(n=str(x["n"]), amt=round(float(x["amt"]), 2), tag=_tag(x)) for x in d["unit_costs"]][:6]
    cost = round(sum(x["amt"] for x in costs), 2)
    if cost >= d["price"] * .92 or cost <= 0:
        raise ValueError("unit cost must be clearly less than the price")
    d["unit_costs"], d["cost"], d["profit"] = costs, cost, round(d["price"] - cost, 2)
    sc = []
    for x in d["scenarios"][:3]:
        per_day, fixed = int(x["per_day"]), int(x.get("fixed", 0))
        month = round(per_day * DAYS * d["profit"] - fixed)
        sc.append(dict(label=str(x["label"]), per_day=per_day, fixed=fixed, note=str(x.get("note", "")), month=month, year=month * 12,
                       payback=(d["capital"] / month if month > 0 else None)))
    if len(sc) != 3:
        raise ValueError("need 3 scenarios")
    d["scenarios"] = sc
    d["fd_rate"] = float(cfg.get("fd_rate", FD_RATE))
    d["fd_year"] = round(d["capital"] * d["fd_rate"] / 100)
    d["truths"] = [str(t) for t in d.get("truths", [])][:3] or ["Pehle chhote level pe test karo"]
    d["tasks"] = [(t["t"], t.get("d", "")) if isinstance(t, dict) else tuple(t) for t in d.get("tasks", [])][:4]
    d["question"] = d.get("question") or "Agla kaunsa business ka hisaab chahiye?"
    d["hook"] = d.get("hook") or f"{rs(d['budget'])} se {d['name']}: asli hisaab"
    d["sources"] = [str(s)[:40] for s in d.get("sources", [])][:3]
    d["say"] = script(d)
    d["captions"] = captions(d, cfg)
    d["hashtags"] = d.get("hashtags") or cfg["hashtags_base"]
    return d


def _tag(x):
    return "listing" if str(x.get("tag", "")).lower() == "listing" else "anumaan"


def _pb(s):
    return "kabhi nahi" if s["payback"] is None else f"lagbhag {max(1, round(s['payback']))} mahine"


def script(d):
    s1, s2, s3 = d["scenarios"]
    cap = d["capital_items"]
    big = sorted(cap[:-1], key=lambda x: -x["amt"])[:2]
    unit = d["unit"]
    return dict(
        hook=f"{say_rs(d['capital'])} rupaye lagake {d['name']} shuru karoge toh kitna bachega? Chalo, aaj iska asli hisaab dekhte hain.",
        batwara=f"Pehle dekho paisa jaata kahan hai. {big[0]['n']} ke {say_rs(big[0]['amt'])}, {big[1]['n']} ke {say_rs(big[1]['amt'])}, aur baaki kachche maal aur reserve ke liye.",
        unit=f"Ab ek {unit} ka hisaab. Bikta hai {say_rs(d['price'])} rupaye mein, aur maal mein jaate hain {say_rs(d['cost'])}. Matlab har {unit} pe bachat {say_rs(d['profit'])} rupaye.",
        scen=f"Ab asli sawaal, jagah kaisi hai. Kamzor jagah pe mahine ka {say_rs(s1['month'])}, theek jagah pe {say_rs(s2['month'])}, aur viral jagah pe {say_rs(s3['month'])}. Paisa wapas aane mein {_pb(s1)}, {_pb(s2)} aur {_pb(s3)}.",
        fd=f"Itne hi paise FD mein rakhte toh saal ka lagbhag {say_rs(d['fd_year'])} milta. Business mein theek jagah pe saal ka {say_rs(s2['year'])}, par mehnat aur risk bhi zyada.",
        truths="Kadwe sach. " + " ".join(t.rstrip(".") + "." for t in d["truths"]),
        cta="Ye sirf andaaza hai, apne sheher ke rate zaroor check karo. Follow karo, aur comment mein batao agla business kaunsa ho.")


def captions(d, cfg):
    s1, s2, s3 = d["scenarios"]
    h = cfg["handle"]
    base = (f"{d['hook']}\n\n{rs(d['capital'])} lagao toh: 1 {d['unit']} pe bachat {rs(d['profit'])}. Mahine ki kamai: {lakh(s1['month'])} (kamzor jagah), {lakh(s2['month'])} (theek), {lakh(s3['month'])} (viral).\n"
            f"FD mein wahi paisa lagbhag {lakh(d['fd_year'])} / saal.\n\nNumbers andaaza (anumaan) hain, sheher aur jagah ke hisaab se badalte hain. Sirf education ke liye.\n{d['question']}\nFollow @{h} for a new asli hisaab daily.")
    return dict(post=base, carousel=base, reel=base)


# ------------------------------------------------------------------ getting the raw numbers
def _search_call(prompt, key):
    """Gemini with Google Search grounding; returns (json, [source names])"""
    import requests
    import time
    models = [m for m in (os.getenv("PAGE_MODELS") or "gemini-3.6-flash,gemini-3.5-flash,gemini-3.7-flash").split(",") if m]
    last, deadline = "", time.time() + int(os.getenv("GEMINI_TOTAL_SECONDS") or 150)
    for use_search in (True, False):
        for m in models * 2:
            if time.time() > deadline:
                break
            body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": .7}}
            if use_search:
                body["tools"] = [{"google_search": {}}]
            else:
                body["generationConfig"]["responseMimeType"] = "application/json"
            print(f"Gemini: asking {m} ({'with web search' if use_search else 'no search'}) ...", flush=True)
            try:
                r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                                  json=body, timeout=int(os.getenv("GEMINI_TIMEOUT") or 60))
                if r.ok:
                    c = r.json()["candidates"][0]
                    t = "".join(p.get("text", "") for p in c["content"]["parts"])
                    t = re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.M).strip()
                    t = t[t.index("{"): t.rindex("}") + 1]
                    chunks = (c.get("groundingMetadata") or {}).get("groundingChunks") or []
                    names = []
                    for g in chunks:
                        w = g.get("web") or {}
                        nm = (w.get("title") or w.get("uri") or "")[:40]
                        if nm and nm not in names:
                            names.append(nm)
                    return json.loads(t), names
                last = f"{m}: {r.status_code} {r.text[:100]}"
            except Exception as ex:
                last = f"{m}: {str(ex)[:100]}"
            print("Gemini:", last, file=sys.stderr)
            time.sleep(2)
    raise RuntimeError(last)


def make_idea(cfg, rng, use_ai=True, used=None):
    """returns (idea dict, how)"""
    used = used or []
    key = os.getenv("GEMINI_API_KEY")
    err = ""
    if use_ai and key:
        try:
            import datetime as dt
            budget = rng.choice([100000, 100000, 150000, 200000, 50000])
            p = PROMPT.format(month=dt.date.today().strftime("%B %Y"), typ=rng.choice(IDEA_TYPES), budget=budget, avoid="; ".join(used[-40:]) or "none", icons=", ".join(ICONS),
                              search_note="Search the web for real current prices (equipment listings, raw material rates, licence fees) and use them; mark only those as listing.")
            raw, names = _search_call(p, key)
            raw["budget"] = budget
            if not names:                                      # nothing was found on the web: nothing may be called 'listing'
                for k in ("capital_items", "unit_costs"):
                    for x in raw.get(k, []):
                        x["tag"] = "anumaan"
            raw["sources"] = names
            idea = compute(raw, cfg)
            idea["_raw"] = raw
            return idea, "written by Gemini" + (f" with {len(names)} web sources" if names else " (no web sources, all numbers are estimates)")
        except Exception as ex:
            err = str(ex)[:160]
            print("AI hisaab failed, using the built-in library:", ex, file=sys.stderr)
    pool = [x for x in LIBRARY if x["name"] not in used] or LIBRARY
    raw = json.loads(json.dumps(rng.choice(pool)))
    raw["budget"] = 100000
    idea = compute(raw, cfg)
    idea["_raw"] = raw
    return idea, "built-in library, estimates (" + (err or "no GEMINI_API_KEY") + ")"

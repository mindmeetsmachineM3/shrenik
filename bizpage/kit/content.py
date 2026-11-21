"""One business idea per post. Gemini writes it (conservative approx. numbers for an Indian tier-2 city); without a key a built-in idea library is used."""
import json
import os
import re
import sys

from .common import ROOT
from .icons import NAMES as ICONS

CATEGORIES = ["very low investment (under Rs 10,000)", "home-based business", "business for college students", "business for women from home", "small-town / village business",
              "online or digital side hustle", "food business", "local service business (doorstep services)", "trending business of this year", "business for working professionals as a side income",
              "business that needs no shop", "low-risk business for first-timers"]

PROMPT = """You write Instagram content for an Indian page that explains one business idea per post using simple graphics (page tone: {tone}).
Pick ONE realistic business idea for this category: {cat}. Audience: {aud}.
RULES
- Be realistic and conservative. Money in Indian rupees for a tier-2 Indian city, monthly, approximate. Never promise income, never say "guaranteed", "easy money" or "get rich".
- Only ideas that are legal and need no big licence. Do not repeat these earlier ideas: {avoid}
- Short punchy text for graphics. On-image text: simple Indian English. Spoken lines ("say"): natural Hinglish in Roman letters (Hindi+English mix like a young Indian creator), each 10-22 words, write money in words (e.g. "das hazaar", "do lakh").
- icon must be exactly one of: {icons}
Return ONLY JSON:
{{"name":"max 4 words","icon":"one of the list","hook":"max 7 words, curiosity or bold claim","pitch":"max 18 words what it is","who":"max 9 words who it suits","time":"e.g. 2-3 hours/day",
 "invest_low":int,"invest_high":int,"earn_low":int,"earn_high":int,
 "steps":[{{"t":"max 4 words","d":"max 11 words"}},{{"t":"","d":""}},{{"t":"","d":""}},{{"t":"","d":""}}],
 "tips":["max 11 words","max 11 words"],"mistakes":["max 11 words","max 11 words"],"first_customers":"max 16 words",
 "say":{{"hook":"","what":"","invest":"","steps":"","earn":"","cta":"ask to follow, save, and comment which business to explain next"}},
 "question":"one easy question to ask followers, max 10 words",
 "captions":{{"post":"2-3 short lines ending with the question and: Follow @{handle} for a new business idea daily","carousel":"","reel":""}},
 "hashtags":["8 to 10 relevant tags, no #viral #fyp"]}}"""

IDEAS = [
    dict(name="Home Tiffin Service", icon="food", hook="Cook at home. Earn monthly.", pitch="Cook fresh meals at home and deliver daily tiffins to offices, students and PG residents.",
         who="People who cook well and live near offices or colleges", time="3-4 hours/day", invest_low=8000, invest_high=25000, earn_low=15000, earn_high=45000,
         steps=[("Pick a menu", "Offer 2 simple veg and non-veg meals"), ("Test with 5 people", "Free trial tiffins for neighbours and friends"), ("Fix price and area", "Monthly plans work better than daily orders"), ("Deliver on time", "Use a helper or a local delivery partner")],
         tips=["Take advance for monthly plans", "Ask for reviews and referrals"], mistakes=["Cooking too many dishes at first", "No fixed delivery time"], first="Post your menu in local WhatsApp, PG and office groups."),
    dict(name="Online Thrift Store", icon="bag", hook="Sell old clothes for profit", pitch="Buy good second-hand clothes cheap, clean them, photograph them and sell on Instagram.",
         who="Students and young people who love fashion", time="2-3 hours/day", invest_low=5000, invest_high=20000, earn_low=10000, earn_high=40000,
         steps=[("Source stock", "Buy from wholesalers, markets and friends"), ("Clean and fix", "Wash, iron and repair small defects"), ("Shoot photos", "Good light and a plain background sell"), ("Sell on Instagram", "Post reels and take orders in DMs")],
         tips=["Show real photos and sizes", "Offer cash on delivery in your city"], mistakes=["Buying stock without checking quality", "Mixing too many styles"], first="Ask 10 friends to share your first post and offer a launch discount."),
    dict(name="Video Editing Freelance", icon="laptop", hook="Edit reels, get paid", pitch="Edit short videos for creators, shops and coaches who have no time to edit.",
         who="Students and creative people with a laptop or phone", time="3-5 hours/day", invest_low=0, invest_high=15000, earn_low=10000, earn_high=50000,
         steps=[("Learn one tool", "CapCut or DaVinci Resolve is enough"), ("Make 3 samples", "Edit free sample reels in your own style"), ("Pitch local brands", "DM salons, gyms, cafes and coaches"), ("Fix a monthly price", "Offer 8 to 12 reels per month")],
         tips=["Deliver on the promised day", "Keep a portfolio on Instagram"], mistakes=["Working free for too long", "No clear revision limit"], first="DM 20 local businesses with one free sample reel each."),
    dict(name="Doorstep Car Wash", icon="truck", hook="Wash cars at their door", pitch="Clean cars at society parking lots using a small kit and monthly subscriptions.",
         who="Hard-working people who want a service business", time="4-5 hours/day", invest_low=12000, invest_high=35000, earn_low=20000, earn_high=50000,
         steps=[("Buy a basic kit", "Vacuum, microfiber cloths, foam and a pump"), ("Pick 1-2 societies", "Take permission from the secretary"), ("Offer monthly plans", "Weekly wash plans give fixed income"), ("Add extras", "Interior cleaning and polishing earn more")],
         tips=["Take monthly advance", "Keep a neat uniform"], mistakes=["Starting without society permission", "Ignoring water arrangement"], first="Offer the first wash free to 10 car owners in one society."),
    dict(name="Custom T-Shirt Printing", icon="shop", hook="Print your own brand", pitch="Print custom designs on t-shirts and mugs for gifts, groups and small brands.",
         who="Creative people who want a small product business", time="3-4 hours/day", invest_low=15000, invest_high=60000, earn_low=15000, earn_high=60000,
         steps=[("Choose a method", "Start with outsourced printing to learn demand"), ("Create 10 designs", "Use Canva for simple trending designs"), ("Take group orders", "College groups and events order in bulk"), ("Scale slowly", "Buy a press machine after steady orders")],
         tips=["Show mockups before printing", "Take 50% advance"], mistakes=["Printing stock before orders", "Copying brand logos"], first="Offer a free design for the first 5 group orders in nearby colleges."),
    dict(name="Balcony Plant Nursery", icon="plant", hook="Turn a balcony into income", pitch="Grow and sell indoor plants, herbs and planters from your balcony or terrace.",
         who="People with a balcony, terrace or small space", time="2 hours/day", invest_low=5000, invest_high=20000, earn_low=8000, earn_high=30000,
         steps=[("Pick easy plants", "Money plant, tulsi, aloe vera and succulents"), ("Prepare saplings", "Use cuttings and seeds to keep cost low"), ("Style the pots", "Painted pots sell for more"), ("Sell locally", "Societies, WhatsApp groups and Instagram")],
         tips=["Sell care tips along with plants", "Offer plant gift combos"], mistakes=["Choosing plants that die easily", "Ignoring watering schedule"], first="Gift 5 small plants to neighbours and ask for a review."),
    dict(name="Social Media For Local Shops", icon="megaphone", hook="Run Instagram for shops", pitch="Manage Instagram pages for local shops: posts, reels and replies for a monthly fee.",
         who="People who understand Instagram and Canva", time="3-4 hours/day", invest_low=0, invest_high=10000, earn_low=10000, earn_high=50000,
         steps=[("Pick a niche", "Salons, gyms, cafes or clothing stores"), ("Make a sample plan", "Show a 30-day content calendar"), ("Pitch the owner", "Visit in person with 3 sample posts"), ("Report monthly", "Share reach and enquiries every month")],
         tips=["Start with 2 clients only", "Put the scope in writing"], mistakes=["Promising followers or sales", "Taking too many clients"], first="Walk into 10 nearby shops with 3 sample posts made for them."),
    dict(name="Home Bakery", icon="cup", hook="Bake at home, sell for more", pitch="Bake cakes, cookies and brownies at home and take orders for birthdays and gifting.",
         who="People who enjoy baking and have a basic oven", time="3-4 hours/day", invest_low=10000, invest_high=40000, earn_low=15000, earn_high=50000,
         steps=[("Choose 3 products", "Brownies, cupcakes and one signature cake"), ("Get FSSAI registration", "Needed for selling food legally"), ("Photograph every order", "Clean photos bring repeat orders"), ("Take advance orders", "Fix a 24-hour minimum notice")],
         tips=["Take advance for custom cakes", "Pack neatly with a label"], mistakes=["Skipping food safety rules", "Underpricing your time"], first="Make 10 free tasters for neighbours and ask them to post a story."),
]

TEMPLATES = {
    "hook": "{hook} Aaj ka business idea hai {name}.",
    "what": "{pitch} Ye {who_l} ke liye kaafi accha hai.",
    "invest": "Shuru karne ke liye lagbhag {lo} se {hi} rupaye lag sakte hain.",
    "steps": "Steps simple hain. Pehle {s1}, phir {s2}, phir {s3}, aur aakhir mein {s4}.",
    "earn": "Mahine ki kamai lagbhag {elo} se {ehi} rupaye ho sakti hai. Ye sirf andaaza hai, guarantee nahi.",
    "cta": "Roz ek nayi business idea ke liye follow karo, ise save karo, aur comment mein batao agla idea kis business ka chahiye.",
}


def words(n):
    n = int(n)
    if n == 0:
        return "zero"
    if n >= 100000:
        return f"{n / 100000:g} lakh"
    if n >= 1000:
        return f"{n / 1000:g} hazaar"
    return str(n)


def _steps(s):
    return [(x["t"], x.get("d", "")) if isinstance(x, dict) else (x[0], x[1]) for x in s]


def normalise(i, cfg):
    i = dict(i)
    i["icon"] = i.get("icon") if i.get("icon") in ICONS else "coin"
    i["steps"] = _steps(i["steps"])[:4]
    while len(i["steps"]) < 4:
        i["steps"].append(("Start small", ""))
    i["invest_low"], i["invest_high"] = sorted((int(i["invest_low"]), int(i["invest_high"])))
    i["earn_low"], i["earn_high"] = sorted((int(i["earn_low"]), int(i["earn_high"])))
    i["first"] = i.get("first_customers") or i.get("first") or ""
    s = i["steps"]
    fill = dict(hook=i["hook"], name=i["name"], pitch=i["pitch"], who_l=i["who"].lower(), lo=words(i["invest_low"]), hi=words(i["invest_high"]),
                elo=words(i["earn_low"]), ehi=words(i["earn_high"]), s1=s[0][0].lower(), s2=s[1][0].lower(), s3=s[2][0].lower(), s4=s[3][0].lower())
    say = i.get("say") or {}
    i["say"] = {k: (say.get(k) or t.format(**fill)) for k, t in TEMPLATES.items()}
    h = cfg["handle"]
    q = i.get("question") or "Which business should we explain next?"
    i["question"] = q
    cap = i.get("captions") or {}
    from .gfx import inr
    base = f"{i['name']}: {i['pitch']}\nStart: ~{inr(i['invest_low'])} to {inr(i['invest_high'])}. Earn: ~{inr(i['earn_low'])} to {inr(i['earn_high'])} per month (approx, not guaranteed).\n{q}\nFollow @{h} for a new business idea daily."
    i["captions"] = {k: cap.get(k) or base for k in ("post", "carousel", "reel")}
    i["hashtags"] = i.get("hashtags") or cfg["hashtags_base"]
    return i


def _call(prompt, key):
    import requests
    last = ""
    import time
    deadline = time.time() + int(os.getenv("GEMINI_TOTAL_SECONDS") or 150)
    tries = [m for m in (os.getenv("PAGE_MODELS") or "gemini-3.6-flash,gemini-3.5-flash,gemini-3.7-flash").split(",") if m] * 3   # 3 rounds: 503 "high demand" is usually short
    for n_try, m in enumerate(tries):
        if time.time() > deadline:
            break
        if n_try and n_try % 3 == 0:
            time.sleep(12)                                                                                                       # wait a little between rounds
        print(f"Gemini: asking {m} ...", flush=True)
        try:
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                              json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": .95, "responseMimeType": "application/json"}}, timeout=int(os.getenv("GEMINI_TIMEOUT") or 45))
            if r.ok:
                t = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.M).strip())
            last = f"{m}: {r.status_code} {r.text[:100]}"
        except Exception as ex:
            last = f"{m}: {str(ex)[:100]}"
        print("Gemini:", last, file=sys.stderr)
    raise RuntimeError(last)


def make_idea(cfg, rng, use_ai=True, used=None):
    """returns (idea dict, how). `used` = names already posted."""
    used = used or []
    key = os.getenv("GEMINI_API_KEY")
    err = ""
    if use_ai and key:
        try:
            p = PROMPT.format(tone=cfg["tone"], cat=rng.choice(CATEGORIES), aud=cfg["audience_note"], avoid="; ".join(used[-40:]) or "none", icons=", ".join(ICONS), handle=cfg["handle"])
            raw = _call(p, key)
            for k in ("name", "icon", "hook", "pitch", "who", "invest_low", "invest_high", "earn_low", "earn_high", "steps"):
                if k not in raw:
                    raise ValueError("Gemini JSON missing " + k)
            return normalise(raw, cfg), "written by Gemini"
        except Exception as ex:
            err = str(ex)[:160]
            print("AI idea failed, using the built-in library:", ex, file=sys.stderr)
    pool = [i for i in IDEAS if i["name"] not in used] or IDEAS
    i = dict(rng.choice(pool))
    i["tips"], i["mistakes"] = i["tips"], i["mistakes"]
    return normalise(i, cfg), "built-in idea library (" + (err or "no GEMINI_API_KEY") + ")"

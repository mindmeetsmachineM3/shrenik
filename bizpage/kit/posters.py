"""Posts (1080x1350) and carousel slides for one business idea, built from the infographic components in gfx.py."""
import random

from PIL import Image, ImageDraw

from . import gfx
from .common import df, pf
from .gfx import Pal, card, chip, footer, header, inr, para, rrect, sticker, title

W, H = 1080, 1350


def _base(P, seed, handle, label, right):
    img = gfx.background(W, H, P, seed)
    header(img, P, label, right, handle)
    footer(img, P, handle)
    return img


def _stat(img, x, y, w, h, label, value, P, fill):
    card(img, (x, y, x + w, y + h), P, fill=fill, sh=8, r=24, bw=5)
    d = ImageDraw.Draw(img)
    d.text((x + w / 2, y + 26), label, font=pf("Bold", 24), fill=gfx.on(fill) + (220,) if False else gfx.on(fill), anchor="mt")
    f = pf("Bold", 46 if len(value) < 12 else 36)
    d.text((x + w / 2, y + h - 30), value, font=f, fill=gfx.on(fill), anchor="ms")


# ------------------------------------------------------------------ single posts
def post_card(i, P, seed, handle, num, tf):
    """icon + name + 3 stat tiles"""
    img = _base(P, seed, handle, f"BUSINESS IDEA #{num}", "SAVE THIS")
    sticker(img, i["icon"], W // 2, 330, 400, P, 1, rot=-6)
    y = title(img, i["name"], i["name"].split()[-1], (60, 570, W - 60, 760), P, tf, 120, "center")
    para(img, i["pitch"], (90, y + 34, W - 90, y + 150), P, 34, "Bold", align="center")
    ty = 905
    cw = (W - 120 - 40) // 3
    _stat(img, 60, ty, cw, 150, "START WITH", f"{inr(i['invest_low'])}-{inr(i['invest_high'])}", P, P.white)
    _stat(img, 60 + cw + 20, ty, cw, 150, "EARN / MONTH*", f"{inr(i['earn_low'])}-{inr(i['earn_high'])}", P, P.a2)
    _stat(img, 60 + 2 * (cw + 20), ty, cw, 150, "TIME NEEDED", i["time"].replace("hours", "hrs"), P, P.a1)
    card(img, (60, 1100, W - 60, 1225), P, fill=P.ink, sh=0, r=26, bw=4)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 1162), i["question"], font=pf("Bold", 34), fill=(255, 255, 255), anchor="mm")
    return img.convert("RGB")


def post_numbers(i, P, seed, handle, num, tf):
    """numbers-first headline poster"""
    img = _base(P, seed, handle, f"BUSINESS IDEA #{num}", i["name"].upper()[:22])
    y = title(img, f"Start with {inr(i['invest_low'])}.", f"{inr(i['invest_low'])}.", (60, 150, W - 60, 420), P, tf, 190, "left", .95)
    y = title(img, f"Earn up to {inr(i['earn_high'])}*", f"{inr(i['earn_high'])}*", (60, y + 10, W - 60, y + 270), P, tf, 190, "left", .95)
    bars_box = (150, 760, W - 90, 1130)
    card(img, (50, 730, W - 50, 1160), P, sh=10)
    gfx.bars(img, (110, 790, W - 110, 1130), [("Slow month", i["earn_low"], P.a2), ("Average", (i["earn_low"] + i["earn_high"]) // 2, P.a1), ("Good month", i["earn_high"], P.a3)], P, 1, 38)
    sticker(img, i["icon"], W - 150, 640, 230, P, 1, rot=8)
    d = ImageDraw.Draw(img)
    d.text((60, 1200), "* approx. monthly income for " + i["name"] + ". Not guaranteed.", font=pf("Medium", 22), fill=P.ink)
    return img.convert("RGB")


# ------------------------------------------------------------------ carousel
def carousel(i, P, seed, handle, num, tf):
    n = 7
    out = []

    def base(k, label):
        return _base(P, seed + k, handle, label, f"{k + 1:02d} / {n:02d}")

    # 1 cover
    im = base(0, f"BUSINESS IDEA #{num}")
    sticker(im, i["icon"], W // 2, 400, 520, P, 1, rot=-5)
    card(im, (50, 740, W - 50, 1190), P, sh=12)
    title(im, i["hook"], i["hook"].split()[-1], (90, 775, W - 90, 1040), P, tf, 140, "left", .98)
    chip(im, i["name"], 90, 1090, P, 30, P.a2)
    ImageDraw.Draw(im).text((W - 70, 1226), "SWIPE  >>", font=pf("Bold", 34), fill=P.ink, anchor="ra")
    out.append(im)
    # 2 what is it
    im = base(1, "WHAT IS IT?")
    sticker(im, i["icon"], 200, 270, 250, P, 1, rot=-6)
    title(im, i["name"], i["name"].split()[-1], (350, 160, W - 60, 380), P, tf, 110, "left")
    card(im, (50, 470, W - 50, 800), P, sh=10)
    para(im, i["pitch"], (90, 505, W - 90, 760), P, 46, "Bold")
    chip(im, "WHO IS IT FOR", 50, 850, P, 28, P.a2)
    card(im, (50, 930, W - 50, 1090), P, sh=8)
    para(im, i["who"], (86, 955, W - 86, 1070), P, 40, "Medium")
    chip(im, "TIME: " + i["time"], 50, 1150, P, 28, P.a1)
    out.append(im)
    # 3 investment
    im = base(2, "STARTUP COST")
    title(im, "How much to start?", "start?", (60, 150, W - 60, 380), P, tf, 120)
    card(im, (50, 430, W - 50, 1000), P, sh=10)
    ImageDraw.Draw(im).text((W // 2, 560), f"{inr(i['invest_low'])} - {inr(i['invest_high'])}", font=df(tf, 150), fill=P.a1, anchor="mm")
    gfx.meter(im, (100, 700, W - 100, 800), i["invest_low"], i["invest_high"], max(i["invest_high"] * 1.5, 1000), P, 1)
    para(im, "Approx. for a tier-2 city. Start smaller, test first, then scale.", (100, 890, W - 100, 980), P, 30, "Medium", align="center")
    sticker(im, "coin", W - 130, 1170, 180, P, 1, rot=10)
    out.append(im)
    # 4 steps
    im = base(3, "HOW TO START")
    title(im, "4 simple steps", "4", (60, 140, W - 60, 300), P, tf, 120)
    gfx.steps(im, (50, 330, W - 70, 1260), i["steps"], P, None, 42)
    out.append(im)
    # 5 earning
    im = base(4, "EARNING")
    title(im, "What can you earn?", "earn?", (60, 140, W - 60, 340), P, tf, 120)
    card(im, (50, 380, W - 50, 1160), P, sh=10)
    gfx.bars(im, (110, 440, W - 110, 1130), [("Slow month", i["earn_low"], P.a2), ("Average", (i["earn_low"] + i["earn_high"]) // 2, P.a1), ("Good month", i["earn_high"], P.a3)], P, 1, 44)
    ImageDraw.Draw(im).text((W // 2, 1200), "Approx. monthly income. Not guaranteed.", font=pf("Bold", 28), fill=P.ink, anchor="mm")
    out.append(im)
    # 6 do / avoid
    im = base(5, "DO THIS, AVOID THAT")
    card(im, (50, 150, W - 50, 640), P, fill=P.white, sh=10)
    chip(im, "DO THIS", 80, 128, P, 30, P.a2)
    gfx.bullets(im, i["tips"], (90, 235, W - 80, 610), P, P.a2, 42)
    card(im, (50, 720, W - 50, 1200), P, fill=P.white, sh=10)
    chip(im, "AVOID THIS", 80, 698, P, 30, P.a1)
    gfx.bullets(im, i["mistakes"], (90, 805, W - 80, 1170), P, P.a1, 42)
    out.append(im)
    # 7 cta
    im = base(6, "YOUR TURN")
    title(im, "Save it. Follow for the next idea.", "Save", (60, 150, W - 60, 520), P, tf, 140, "left", .98)
    card(im, (50, 560, W - 50, 860), P, sh=10)
    chip(im, "FIRST CUSTOMERS", 80, 538, P, 26, P.a2)
    para(im, i["first"], (90, 625, W - 90, 835), P, 38, "Bold")
    card(im, (50, 940, W - 50, 1170), P, fill=P.ink, sh=0)
    para(im, i["question"], (90, 970, W - 90, 1140), P, 46, "Bold", color=(255, 255, 255), align="center")
    sticker(im, "megaphone", W - 130, 880, 170, P, 1, rot=-8)
    out.append(im)
    return [x.convert("RGB") for x in out]

"""Whiteboard-style 'asli hisaab' visuals. The same components draw the animated Reel scenes (1080x1920) and the static carousel / posters (1080x1350).
Each component takes a box and p (0..1 progress)."""
import math

from PIL import Image, ImageDraw

from . import gfx
from .common import df, pf
from .gfx import card, chip, ease, rrect, sticker
from .hisaab import ig, lakh, rs


class WPal:
    name = "wb"
    bg = bg2 = (244, 239, 227)
    ink = (28, 28, 34)
    white = (255, 255, 255)
    a1 = (250, 176, 5)          # yellow
    a2 = (47, 108, 214)         # blue
    a3 = (35, 134, 84)          # green
    red = (226, 78, 66)
    brown = (110, 85, 75)
    purple = (122, 92, 170)
    orange = (232, 140, 40)
    teal = (24, 150, 160)
    grey = (96, 96, 104)
    mist = (226, 220, 205)


P = WPal()
COLS = [P.a2, P.red, P.brown, P.purple, P.orange, P.teal]
TABS = ["Kitna lagta?", "Kitna kamata?", "Kab wapas?"]


def H(size):
    return df("Kalam-Bold.ttf", size)


def _fit_font(d, text, maxw, size, mk):
    while size > 18 and d.textlength(text, font=mk(size)) > maxw:
        size -= 2
    return mk(size)


def paper(w, h):
    return Image.new("RGBA", (w, h), P.bg + (255,))


def title(img, text, x, y, maxw, size=84):
    """handwritten title with a yellow underline"""
    d = ImageDraw.Draw(img)
    f = _fit_font(d, text, maxw, size, H)
    d.text((x, y), text, font=f, fill=P.ink)
    wd = int(d.textlength(text, font=f))
    d.rounded_rectangle((x, y + f.size + 8, x + int(wd * .55), y + f.size + 18), 5, fill=P.a1)
    return y + f.size + 30


def tabs(img, x, y, active):
    d = ImageDraw.Draw(img)
    for k, t in enumerate(TABS):
        f = pf("Bold", 25)
        w = int(d.textlength(t, font=f)) + 36
        on = k == active
        d.rounded_rectangle((x, y, x + w, y + 46), 23, fill=P.a1 if on else P.white, outline=P.ink, width=3)
        d.text((x + w / 2, y + 23), t, font=f, fill=P.ink, anchor="mm")
        x += w + 12
    return y + 46


def note(img, text, w, y, size=22):
    ImageDraw.Draw(img).text((w // 2, y), text, font=pf("Medium", size), fill=P.grey, anchor="mm")


def tag_chip(img, x, y, tag, size=22, anchor="l"):
    d = ImageDraw.Draw(img)
    f = pf("Bold", size)
    w = int(d.textlength(tag, font=f)) + 22
    if anchor == "r":
        x -= w
    col = P.a2 if tag == "listing" else P.red
    d.rounded_rectangle((x, y, x + w, y + size + 12), 8, fill=P.white, outline=col, width=3)
    d.text((x + w / 2, y + (size + 12) / 2), tag, font=f, fill=col, anchor="mm")


def coin(img, cx, cy, r, slices=None):
    """gold rupee coin. slices = [(fraction, colour)] drawn clockwise from the top over the gold (the 'spent' parts)"""
    k = 3
    s = int(2 * r + 6)
    L = Image.new("RGBA", (s * k, s * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    c = s * k / 2
    R = r * k
    d.ellipse((c - R, c - R, c + R, c + R), fill=P.a1, outline=P.ink, width=3 * k)
    a = -90.0
    for fr, col in slices or []:
        if fr <= .001:
            continue
        d.pieslice((c - R, c - R, c + R, c + R), a, a + 360 * fr, fill=col, outline=P.ink, width=2 * k)
        a += 360 * fr
    if not slices:
        d.text((c, c), "₹", font=H(int(R * 1.05)), fill=P.ink, anchor="mm")
    else:
        d.ellipse((c - R, c - R, c + R, c + R), outline=P.ink, width=3 * k)
    L = L.resize((s, s), Image.LANCZOS)
    img.alpha_composite(L, (int(cx - s / 2), int(cy - s / 2)))


# ------------------------------------------------------------------ components
def batwara(img, box, d, p):
    x0, y0, x1, y1 = box
    w = x1 - x0
    items = d["capital_items"]
    cap = d["capital"]
    dr = ImageDraw.Draw(img)
    dr.text((x0, y0), f"Total {rs(cap)}", font=pf("Medium", 30), fill=P.grey)
    by = y0 + 46
    rrect(img, (x0, by, x1, by + 84), 10, P.mist, P.ink, 3)
    n = len(items)
    cum = 0
    for i, it in enumerate(items):
        e = ease(p * (n + 1) - i)
        wd = (w - 6) * it["amt"] / cap * e
        if wd > 1:
            ax = x0 + 3 + (w - 6) * cum / cap
            dr.rectangle((ax, by + 4, ax + wd, by + 80), fill=COLS[i % 6], outline=P.ink, width=2)
        cum += it["amt"]
    ry0 = by + 130
    rh = min(130, (y1 - ry0) // n)
    for i, it in enumerate(items):
        e = ease(p * (n + 1) - i)
        if e < .3:
            continue
        y = ry0 + i * rh
        dr.rounded_rectangle((x0, y + 10, x0 + 36, y + 46), 8, fill=COLS[i % 6], outline=P.ink, width=3)
        nm = _fit_font(dr, it["n"], 300, 44, H)
        dr.text((x0 + 56, y), it["n"], font=nm, fill=P.ink)
        dr.text((x0 + 56, y + 52), it["d"], font=_fit_font(dr, it["d"], 380, 24, lambda s: pf("Medium", s)), fill=P.grey)
        dr.text((x0 + 620, y + 4), rs(it["amt"]), font=H(52), fill=P.ink, anchor="ra")
        tag_chip(img, x1, y + 14, it["tag"], 22, "r")


def unitcost(img, box, d, p):
    x0, y0, x1, y1 = box
    dr = ImageDraw.Draw(img)
    costs = d["unit_costs"]
    n = len(costs)
    rh = 66 if (y1 - y0) > 900 else 50
    for i, c in enumerate(costs):
        e = ease(p * 3 - i * .35)
        if e < .3:
            continue
        y = y0 + i * rh
        dr.ellipse((x0, y + 12, x0 + 22, y + 34), fill=COLS[i % 6], outline=P.ink, width=2)
        dr.text((x0 + 36, y + 6), c["n"], font=_fit_font(dr, c["n"], 400, 32, lambda s: pf("Medium", s)), fill=P.ink)
        dr.text((x0 + 620, y), rs(c["amt"]), font=H(44), fill=P.ink, anchor="ra")
        tag_chip(img, x1, y + 8, c["tag"], 20, "r")
    gy = y0 + n * rh + 36
    price = d["price"]
    nc = price if price <= 24 else 20
    val = price / nc
    cols = 5 if nc <= 25 else 5
    rows = math.ceil(nc / cols)
    avail_h = y1 - gy - 8
    dc = int(min(116, avail_h / rows - 12, (x1 - x0) * .6 / cols - 12))
    pos = []
    for k in range(nc):
        cx = x0 + dc / 2 + (k % cols) * (dc + 12)
        cy = gy + dc / 2 + (k // cols) * (dc + 12)
        pos.append((cx, cy))
    bounds, acc = [], 0.0
    for i, c in enumerate(costs):
        bounds.append((acc, acc + c["amt"], COLS[i % 6]))
        acc += c["amt"]
    shown = ease(p * 1.1 - .2) * nc
    for k, (cx, cy) in enumerate(pos):
        if k >= shown:
            break
        lo, hi = k * val, (k + 1) * val
        sl = []
        for a, b, col in bounds:
            ov = max(0.0, min(hi, b) - max(lo, a))
            if ov > 0:
                sl.append((ov / val, col))
        coin(img, cx, cy, dc / 2, sl if sl else None)
    rx = x0 + cols * (dc + 12) + 24
    rw = x1 - rx
    if p > .55 and rw > 200:
        card(img, (rx, gy, x1 - 8, gy + 150), P, sh=6, r=20, bw=4)
        dr.text((rx + 18, gy + 14), "Maal mein gaye", font=pf("Bold", 24), fill=P.red)
        dr.text(((rx + x1) / 2, gy + 94), rs(d["cost"]), font=H(64), fill=P.ink, anchor="mm")
    if p > .75 and rw > 200:
        card(img, (rx, gy + 175, x1 - 8, gy + 335), P, fill=(230, 245, 236), sh=6, r=20, bw=4)
        dr.text((rx + 18, gy + 189), f"1 {d['unit']} pe bachat", font=pf("Bold", 24), fill=P.a3)
        dr.text(((rx + x1) / 2, gy + 270), rs(d["profit"]), font=H(72), fill=P.a3, anchor="mm")
    if val != 1:
        dr.text((x0, y1 + 4), f"1 coin = {rs(val, 2)}", font=pf("Medium", 22), fill=P.grey)


def scenarios(img, box, d, p):
    x0, y0, x1, y1 = box
    dr = ImageDraw.Draw(img)
    sc = d["scenarios"]
    gap = 26
    bw = (x1 - x0 - 2 * gap) // 3
    base = y1 - 215
    top = y0 + 110
    vmax = max(max(s["month"] for s in sc), 1) * 1.05
    cols = [P.red, P.a1, P.a3]
    dr.rectangle((x0 - 8, base, x1 + 8, base + 8), fill=P.ink)
    for i, s in enumerate(sc):
        e = ease(p * 1.5 - i * .2)
        hh = int((base - top) * max(s["month"], 0) / vmax * e) if s["month"] > 0 else int(18 * e)
        bx = x0 + i * (bw + gap)
        if hh > 2:
            dr.rectangle((bx, base - hh, bx + bw, base), fill=cols[i], outline=P.ink, width=4)
        if e > .15:
            lab = f"{rs(max(s['month'] * e, 0) if s['month'] > 0 else s['month'])}/mahina"
            dr.text((bx + bw / 2, base - hh - 54), lab, font=_fit_font(dr, lab, bw + gap - 4, 38, H), fill=P.ink, anchor="mm")
            ycol = P.a3 if s["year"] > 0 else P.red
            yl = f"Saal: {lakh(s['year'])}"
            dr.text((bx + bw / 2, base - hh - 14), yl, font=_fit_font(dr, yl, bw + gap - 4, 34, H), fill=ycol, anchor="mm")
        dr.text((bx + bw / 2, base + 40), s["label"], font=_fit_font(dr, s["label"], bw + gap - 4, 38, H), fill=P.ink, anchor="mm")
        sub = f"{s['per_day']}/din"
        dr.text((bx + bw / 2, base + 82), sub, font=pf("Medium", 24), fill=P.grey, anchor="mm")
        if p > .6:
            pb = "wapsi: nahi" if s["payback"] is None else f"~{max(1, round(s['payback']))} mahine wapsi"
            f = _fit_font(dr, pb, bw + gap - 8, 24, lambda z: pf("Bold", z))
            wd = dr.textlength(pb, font=f) + 24
            dr.rounded_rectangle((bx + bw / 2 - wd / 2, base + 108, bx + bw / 2 + wd / 2, base + 108 + 40), 20, fill=P.ink)
            dr.text((bx + bw / 2, base + 128), pb, font=f, fill=(255, 255, 255), anchor="mm")


def fdcompare(img, box, d, p):
    x0, y0, x1, y1 = box
    dr = ImageDraw.Draw(img)
    rows = [(f"FD mein {rs(d['capital'])} (~{d['fd_rate']:g}%)", d["fd_year"], P.grey)] + [(s["label"], s["year"], c) for s, c in zip(d["scenarios"], [P.red, P.a1, P.a3])]
    vmax = max(max(v for _, v, _ in rows), 1)
    rh = min(215, (y1 - y0 - 80) // len(rows))
    for i, (lab, v, col) in enumerate(rows):
        e = ease(p * 1.6 - i * .25)
        y = y0 + i * rh
        dr.text((x0, y), lab, font=_fit_font(dr, lab, x1 - x0, 42, H), fill=P.ink)
        bwid = int((x1 - x0 - 10) * max(v, 0) / vmax * e)
        dr.rounded_rectangle((x0, y + 62, x1 - 10, y + 62 + 66), 12, fill=P.mist, outline=P.ink, width=3)
        if bwid > 6:
            dr.rounded_rectangle((x0, y + 62, x0 + bwid, y + 62 + 66), 12, fill=col, outline=P.ink, width=3)
        if e > .3:
            t = f"{lakh(v * e if v > 0 else v)} / saal"
            inside = bwid > (x1 - x0) - 330
            tx = x0 + 16 if inside else x0 + max(bwid, 0) + 14
            dr.text((tx, y + 62 + 33), t, font=H(44), fill=((255, 255, 255) if col in (P.red, P.a3, P.grey) else P.ink) if inside else P.ink, anchor="lm")
    if p > .85:
        note(img, "FD mein risk kam, mehnat nahi. Business mein dono zyada.", x1 - x0 + 2 * x0, y1 - 8, 24)


def truths(img, box, d, p):
    x0, y0, x1, y1 = box
    dr = ImageDraw.Draw(img)
    n = len(d["truths"])
    gap = 26
    hh = min(250, (y1 - y0 - gap * (n - 1)) // n)
    for i, t in enumerate(d["truths"]):
        e = ease(p * (n + .6) - i)
        if e <= 0:
            continue
        y = y0 + i * (hh + gap) + int((1 - e) * 60)
        L = Image.new("RGBA", (x1 - x0 + 20, hh + 20), (0, 0, 0, 0))
        card(L, (0, 0, x1 - x0, hh), P, fill=(252, 249, 240), sh=7, r=24, bw=4)
        ld = ImageDraw.Draw(L)
        ld.ellipse((26, hh // 2 - 34, 94, hh // 2 + 34), fill=P.red, outline=P.ink, width=4)
        ld.text((60, hh // 2), str(i + 1), font=H(44), fill=(255, 255, 255), anchor="mm")
        f, lines, lhp, _ = gfx.fit(t, lambda z: pf("Bold", z), x1 - x0 - 170, hh - 40, 40, 24, 1.2)
        yy = hh / 2 - len(lines) * lhp / 2
        for ln in lines:
            ld.text((124, yy), ln, font=f, fill=P.ink)
            yy += lhp
        if e < 1:
            L.putalpha(L.getchannel("A").point(lambda v: int(v * e)))
        img.alpha_composite(L, (x0, y))


def summary(img, box, d, p):
    x0, y0, x1, y1 = box
    dr = ImageDraw.Draw(img)
    s1, s2, s3 = d["scenarios"]
    rows = [("Lagaya", rs(d["capital"]), P.ink), (f"1 {d['unit']} pe bachat", rs(d["profit"]), P.a3), ("1 saal ki kamai", f"{lakh(s1['year'])} - {lakh(s3['year'])}", P.a3)]
    hh = 112
    for i, (a, b, col) in enumerate(rows):
        e = ease(p * 3.4 - i * .8)
        if e <= 0:
            continue
        y = y0 + i * (hh + 20)
        L = Image.new("RGBA", (x1 - x0 + 20, hh + 20), (0, 0, 0, 0))
        card(L, (0, 0, x1 - x0, hh), P, fill=(252, 249, 240), sh=6, r=20, bw=4)
        ld = ImageDraw.Draw(L)
        ld.text((30, hh // 2), a, font=H(44), fill=P.ink, anchor="lm")
        ld.text((x1 - x0 - 30, hh // 2), b, font=_fit_font(ld, b, 430, 50, H), fill=col, anchor="rm")
        if e < 1:
            L.putalpha(L.getchannel("A").point(lambda v: int(v * e)))
        img.alpha_composite(L, (x0, y))
    y = y0 + 3 * (hh + 20) + 20
    for j, (t, c) in enumerate([("SAVE", P.a1), ("FOLLOW", P.a2), ("COMMENT", P.a3)]):
        if ease(p * 4 - 2.2 - j * .4) > 0:
            chip(img, t, x0 + j * 270, y, P, 34, c)
    if p > .8:
        qy = y + 120
        card(img, (x0, qy, x1, qy + 200), P, fill=P.ink, sh=0, r=26, bw=4)
        gfx.para(img, d["question"], (x0 + 30, qy + 22, x1 - 30, qy + 180), P, 44, "Bold", color=(255, 255, 255), align="center")


# ------------------------------------------------------------------ carousel + posters (1080x1350)
W, HH = 1080, 1350


def _slide(titletext, active, d, handle, k=None, n=7):
    img = paper(W, HH)
    y = title(img, titletext, 60, 50, 960, 76)
    if active is not None:
        tabs(img, 60, y + 4, active)
    dr = ImageDraw.Draw(img)
    dr.text((W - 50, 62), "@" + handle, font=pf("Bold", 26), fill=P.grey, anchor="ra")
    if k is not None:
        dr.text((W - 50, 98), f"{k:02d} / {n:02d}", font=pf("Bold", 24), fill=P.grey, anchor="ra")
    dr.text((W // 2, HH - 40), "Numbers are estimates (anumaan) for a tier-2 Indian city. Education only.", font=pf("Medium", 21), fill=P.grey, anchor="mm")
    return img


def carousel(d, handle):
    out = []
    im = paper(W, HH)
    ImageDraw.Draw(im).text((60, 60), "ASLI HISAAB", font=pf("Bold", 34), fill=P.a1)
    sticker(im, d["icon"], W // 2, 470, 460, P, 1, -4)
    from .gfx import para
    y = title(im, d["name"], 60, 800, 960, 110)
    para(im, d["hook"], (60, y + 20, W - 60, y + 190), P, 46, "Bold")
    ImageDraw.Draw(im).text((W - 50, HH - 70), "SWIPE  >>", font=pf("Bold", 34), fill=P.ink, anchor="ra")
    ImageDraw.Draw(im).text((60, HH - 70), "@" + handle, font=pf("Bold", 28), fill=P.grey, anchor="la")
    out.append(im)
    im = _slide(f"{rs(d['capital'])} ka batwara", 0, d, handle, 2)
    batwara(im, (60, 300, W - 60, 1250), d, 1)
    out.append(im)
    im = _slide(f"1 {d['unit']} ka kharcha", 1, d, handle, 3)
    unitcost(im, (60, 300, W - 60, 1230), d, 1)
    out.append(im)
    im = _slide("Kamai: 3 jagah, 1 saal", 2, d, handle, 4)
    scenarios(im, (60, 290, W - 60, 1270), d, 1)
    out.append(im)
    im = _slide("FD ya business?", 2, d, handle, 5)
    fdcompare(im, (60, 320, W - 60, 1250), d, 1)
    out.append(im)
    im = _slide("Kadwe sach", None, d, handle, 6)
    truths(im, (60, 250, W - 60, 1200), d, 1)
    out.append(im)
    im = _slide("Hisaab ye raha", None, d, handle, 7)
    summary(im, (60, 250, W - 60, 1250), d, 1)
    out.append(im)
    return [x.convert("RGB") for x in out]


def poster_unit(d, handle):
    im = _slide(f"1 {d['unit']} ka asli hisaab", 1, d, handle)
    unitcost(im, (60, 300, W - 60, 1230), d, 1)
    return im.convert("RGB")


def poster_scen(d, handle):
    im = _slide(f"{d['name']}: 1 saal ka hisaab", 2, d, handle)
    scenarios(im, (60, 290, W - 60, 1270), d, 1)
    return im.convert("RGB")


# ------------------------------------------------------------------ Reel scenes (1080x1920), used by reel.build
RW, RH = 1080, 1920
KEYS = ["hook", "batwara", "unit", "scen", "fd", "truths", "cta"]


def build_scene_cls(Scene, L):
    class HScene(Scene):
        def __init__(self, _P, tf, idea, num, handle, k, n, seed):
            self.P, self.tf, self.i, self.k, self.n, self.handle = P, tf, idea, k, n, handle
            self.bg = paper(RW, RH)
            ImageDraw.Draw(self.bg).text((RW // 2, RH - 56), "Estimates (anumaan), tier-2 Indian city. Education only.", font=pf("Medium", 22), fill=P.grey, anchor="mm")
            ImageDraw.Draw(self.bg).text((RW - 50, 62), "@" + handle, font=pf("Bold", 26), fill=P.grey, anchor="ra")
            self.layers, self.dyn = [], []
            getattr(self, f"s{k}")()

        def head(self, text, active=None):
            a = L(980, 200)
            y = title(a, text, 0, 0, 960, 84)
            self.add(a, (60, 70), 0)
            if active is not None:
                t = L(980, 60)
                tabs(t, 0, 4, active)
                self.add(t, (60, 70 + y + 6), .3)
                self.tab_y = 70 + y + 10

        def comp(self, fn, box, delay=.5, frac=.62):
            self.dyn.append(lambda fr, t, d, fn=fn, box=box: fn(fr, box, self.i, max(0.0, min(1.0, (t - delay) / max(2.0, d * frac)))) if t > delay else None)

        def s0(self):
            i = self.i
            self.dyn.append(lambda fr, t, d: sticker(fr, i["icon"], 540, 520, 520, P, t / .8, -4))
            a = L(980, 400)
            from .gfx import para
            ImageDraw.Draw(a).text((0, 0), "ASLI HISAAB", font=pf("Bold", 38), fill=P.a1)
            y = title(a, i["name"], 0, 56, 960, 112)
            para(a, i["hook"], (0, y + 10, 960, 390), P, 50, "Bold")
            self.add(a, (60, 940), .5)
            self.dyn.append(lambda fr, t, d: [coin(fr, 130 + k * 118, 1500, 48, None) for k in range(8) if t > 1.4 + k * .18])

        def s1(self):
            self.head(f"{rs(self.i['capital'])} ka batwara", 0)
            self.comp(batwara, (60, 420, 1020, 1500), .6)

        def s2(self):
            self.head(f"1 {self.i['unit']} ka kharcha", 1)
            self.comp(unitcost, (60, 420, 1020, 1500), .6)

        def s3(self):
            self.head("1 saal, 3 jagah", 1)
            self.dyn.append(lambda fr, t, d: tabs(fr, 60, self.tab_y, 2) if t > d * .55 else None)
            self.comp(scenarios, (60, 410, 1020, 1500), .6, .55)

        def s4(self):
            self.head("FD ya business?", 2)
            self.comp(fdcompare, (60, 440, 1020, 1500), .6)

        def s5(self):
            self.head("Kadwe sach")
            self.comp(truths, (60, 340, 1020, 1500), .5, .6)

        def s6(self):
            self.head("Hisaab ye raha")
            self.comp(summary, (60, 340, 1020, 1500), .5, .55)

    return HScene

"""Neo-brutalist infographic components: bright colour, thick outlines, offset shadows, code-drawn icons, animated meters/bars/steps.
Every component takes `p` (0..1 progress) so the same code draws the static post and the animated Reel."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import icons
from .common import df, fit, hexrgb, mix, on, pf

PALETTES = {
    "sun":   dict(bg="#FFD23F", bg2="#FF9F1C", a1="#EE4266", a2="#3BCEAC", a3="#540D6E", ink="#111111"),
    "grape": dict(bg="#7B2CBF", bg2="#C77DFF", a1="#FFD60A", a2="#FF5D8F", a3="#00C2A8", ink="#10002B"),
    "mint":  dict(bg="#00C2A8", bg2="#7AE7C7", a1="#FF5A5F", a2="#FFD23F", a3="#3A0CA3", ink="#0B132B"),
    "sky":   dict(bg="#3A86FF", bg2="#8ECAE6", a1="#FFBE0B", a2="#FB5607", a3="#8338EC", ink="#0B132B"),
    "coral": dict(bg="#FF5D5D", bg2="#FF9A76", a1="#FFE066", a2="#2EC4B6", a3="#1B1B3A", ink="#1B1B3A"),
    "lime":  dict(bg="#B8F13A", bg2="#7BD500", a1="#FF477E", a2="#3A86FF", a3="#1B1B3A", ink="#111111"),
}
TITLE_FONTS = ["Anton-Regular.ttf", "LilitaOne-Regular.ttf", "ArchivoBlack-Regular.ttf", "BowlbyOne-Regular.ttf"]


class Pal:
    def __init__(self, name):
        self.name = name
        d = PALETTES[name]
        for k, v in d.items():
            setattr(self, k, hexrgb(v))
        self.white = (255, 255, 255)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def back(t):
    t = max(0.0, min(1.0, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def inr(n):
    n = int(n)
    if n >= 10000000:
        return f"₹{n / 10000000:g}Cr"
    if n >= 100000:
        return f"₹{n / 100000:g}L"
    if n >= 1000:
        return f"₹{round(n / 1000, 1):g}K"
    return f"₹{n}"


def background(w, h, P, seed=0):
    rng = random.Random(seed)
    ys = np.linspace(0, 1, h)[:, None, None]
    a, b = np.array(P.bg, float), np.array(P.bg2, float)
    arr = (a * (1 - ys) + b * ys) * np.ones((1, w, 1))
    img = Image.fromarray(arr.astype("uint8"), "RGB").convert("RGBA")
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    for _ in range(3):                                                         # big soft shapes
        r = rng.randint(w // 5, w // 3)
        x, y = rng.randint(-r // 2, w), rng.randint(-r // 2, h)
        d.ellipse((x - r, y - r, x + r, y + r), fill=rng.choice([P.a1, P.a2, P.a3]) + (55,))
    step = 46                                                                   # dot grid
    for yy in range(20, h, step):
        for xx in range(20 + (yy // step % 2) * step // 2, w, step):
            d.ellipse((xx - 3, yy - 3, xx + 3, yy + 3), fill=P.ink + (38,))
    img.alpha_composite(L)
    return img


def rrect(img, box, r, fill, outline=None, ow=0):
    x0, y0, x1, y1 = [int(v) for v in box]
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    k = 3
    L = Image.new("RGBA", ((x1 - x0) * k, (y1 - y0) * k), (0, 0, 0, 0))
    ImageDraw.Draw(L).rounded_rectangle((0, 0, L.width - 1, L.height - 1), r * k, fill=fill, outline=outline, width=ow * k)
    img.alpha_composite(L.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))


def card(img, box, P, fill=None, sh=10, r=30, bw=5):
    x0, y0, x1, y1 = box
    rrect(img, (x0 + sh, y0 + sh, x1 + sh, y1 + sh), r, P.ink)
    rrect(img, box, r, fill or P.white, P.ink, bw)


def chip(img, text, x, y, P, size=28, fill=None, align="left"):
    fill = fill or P.a1
    d = ImageDraw.Draw(img)
    f = pf("Bold", size)
    w = int(d.textlength(text, font=f)) + 44
    x = x if align == "left" else x - w // 2
    rrect(img, (x + 5, y + 5, x + w + 5, y + size + 29), 14, P.ink)
    rrect(img, (x, y, x + w, y + size + 24), 14, fill, P.ink, 4)
    ImageDraw.Draw(img).text((x + 22, y + 11), text, font=f, fill=on(fill))
    return x + w


def title(img, text, hl, box, P, tf, start=150, align="left", lh=1.0, color=None, hlcolor=None, upper=True):
    text = text.upper() if upper else text
    hlw = {w.lower().strip(".,!?:") for w in (hl or "").split()}
    x0, y0, x1, y1 = box
    f, lines, lhp, size = fit(text, lambda s: df(tf, s), x1 - x0, y1 - y0, start, 40, lh)
    d = ImageDraw.Draw(img)
    y = y0
    for ln in lines:
        wd = d.textlength(ln, font=f)
        x = x0 if align == "left" else x0 + (x1 - x0 - wd) / 2
        for w in ln.split():
            col = (hlcolor or P.a1) if w.lower().strip(".,!?:") in hlw else (color or P.ink)
            d.text((x + 5, y + 6), w, font=f, fill=P.ink if col != P.ink else P.white)
            d.text((x, y), w, font=f, fill=col)
            x += d.textlength(w + " ", font=f)
        y += lhp
    return int(y)


def para(img, text, box, P, size=38, weight="Medium", color=None, lh=1.28, align="left"):
    x0, y0, x1, y1 = box
    f, lines, lhp, s = fit(text, lambda z: pf(weight, z), x1 - x0, y1 - y0, size, 22, lh)
    d = ImageDraw.Draw(img)
    y = y0
    for ln in lines:
        x = x0 if align == "left" else x0 + (x1 - x0 - d.textlength(ln, font=f)) / 2
        d.text((x, y), ln, font=f, fill=color or P.ink)
        y += lhp
    return int(y)


def sticker(img, name, cx, cy, d, P, p=1.0, rot=0):
    """round white badge with thick border + offset shadow + icon. p<1 = pop-in animation."""
    s = max(.01, back(p)) * d
    if s < 8:
        return
    s = int(s)
    key = (name, s, rot, P.name)
    if key in _ST:
        L = _ST[key]
        img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))
        return
    L = Image.new("RGBA", (s + 40, s + 40), (0, 0, 0, 0))
    ox = 20
    c = (L.width // 2, L.height // 2)
    dd = ImageDraw.Draw(L)
    k = 3
    big = Image.new("RGBA", (L.width * k, L.height * k), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    r = s * k // 2
    bd.ellipse((c[0] * k - r + 14 * k, c[1] * k - r + 14 * k, c[0] * k + r + 14 * k, c[1] * k + r + 14 * k), fill=P.ink)
    bd.ellipse((c[0] * k - r, c[1] * k - r, c[0] * k + r, c[1] * k + r), fill=P.white, outline=P.ink, width=7 * k)
    L = big.resize(L.size, Image.LANCZOS)
    ic = icons.icon(name, int(s * .66), P.a1, P.a2, P.ink)
    L.alpha_composite(ic, (c[0] - ic.width // 2, c[1] - ic.height // 2))
    if rot:
        L = L.rotate(rot, resample=Image.BICUBIC, expand=True)
    if len(_ST) < 400:
        _ST[key] = L
    img.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))


_ST = {}


def header(img, P, label, right, handle):
    w = img.width
    chip(img, label, 44, 40, P, 26, P.ink if False else P.a1)
    d = ImageDraw.Draw(img)
    d.text((w - 44, 48), right, font=pf("Bold", 30), fill=P.ink, anchor="ra")


def footer(img, P, handle, note="Ideas are for education. Earnings are approx. and not guaranteed."):
    d = ImageDraw.Draw(img)
    y = img.height - 58
    d.text((44, y), "@" + handle, font=pf("Bold", 28), fill=P.ink)
    d.text((img.width - 44, y + 6), note, font=pf("Medium", 17), fill=P.ink + (200,), anchor="ra")


def meter(img, box, lo, hi, vmax, P, p=1.0, label_size=44):
    """horizontal range bar: shows where the cost sits between 0 and vmax"""
    x0, y0, x1, y1 = box
    h = y1 - y0
    card(img, box, P, sh=8, r=h // 2, bw=5)
    tx0, tx1 = x0 + 22, x1 - 22
    ty0, ty1 = y0 + 20, y1 - 20
    e = ease(p)
    a = tx0 + (tx1 - tx0) * lo / vmax
    b = tx0 + (tx1 - tx0) * (lo + (hi - lo) * e) / vmax
    rrect(img, (a, ty0, max(a + 6, b), ty1), (ty1 - ty0) // 2, P.a1, P.ink, 4)
    d = ImageDraw.Draw(img)
    d.text((x0 + 8, y1 + 22), "₹0", font=pf("Bold", 30), fill=P.ink)
    d.text((x1 - 8, y1 + 22), inr(vmax) + "+", font=pf("Bold", 30), fill=P.ink, anchor="ra")


def bars(img, box, items, P, p=1.0, size=40):
    """vertical bars [(label, value, colour)]; grow with p, value counts up"""
    x0, y0, x1, y1 = box
    n = len(items)
    gap = 34
    bw = (x1 - x0 - gap * (n - 1)) // n
    vmax = max(v for _, v, _ in items) * 1.12
    base = y1 - 70
    d = ImageDraw.Draw(img)
    rrect(img, (x0 - 10, base, x1 + 10, base + 10), 4, P.ink)
    for i, (lab, v, col) in enumerate(items):
        e = ease(p * (1 + .18 * (n - 1)) - i * .18)
        hh = int((base - y0 - 60) * (v / vmax) * e)
        bx = x0 + i * (bw + gap)
        rrect(img, (bx + 8, base - hh + 8, bx + bw + 8, base + 2), 14, P.ink)
        rrect(img, (bx, base - hh, bx + bw, base), 14, col, P.ink, 5)
        if e > .02:
            t = inr(v * e)
            d.text((bx + bw / 2, base - hh - 14), t, font=pf("Bold", size), fill=P.ink, anchor="ms")
        d.text((bx + bw / 2, base + 22), lab, font=pf("Bold", 27), fill=P.ink, anchor="mt")


def steps(img, box, items, P, shown=None, size=40):
    """numbered step cards, stacked. shown (float) = how many are visible, the last one slides in."""
    x0, y0, x1, y1 = box
    n = len(items)
    shown = n if shown is None else shown
    gap = 22
    hh = (y1 - y0 - gap * (n - 1)) // n
    for i, (t, dsc) in enumerate(items):
        e = ease(shown - i)
        if e <= 0:
            continue
        off = int((1 - e) * 140)
        yy = y0 + i * (hh + gap)
        L = Image.new("RGBA", (x1 - x0 + 30, hh + 30), (0, 0, 0, 0))
        card(L, (0, 0, x1 - x0, hh), P, sh=9, r=26, bw=5)
        ImageDraw.Draw(L)
        rrect(L, (18, hh // 2 - 36, 90, hh // 2 + 36), 36, [P.a1, P.a2, P.a3, P.a1][i % 4], P.ink, 4)
        ImageDraw.Draw(L).text((54, hh // 2), str(i + 1), font=df("Anton-Regular.ttf", 46), fill=on([P.a1, P.a2, P.a3, P.a1][i % 4]), anchor="mm")
        ImageDraw.Draw(L).text((112, hh // 2 - (size * .62 if dsc else 0)), t, font=pf("Bold", size), fill=P.ink, anchor="lm" if not dsc else "lm")
        if dsc:
            f, lines, lhp, s = fit(dsc, lambda z: pf("Medium", z), x1 - x0 - 140, hh // 2 - 12, int(size * .72), 18, 1.15)
            yy2 = hh // 2 + 2
            for ln in lines[:2]:
                ImageDraw.Draw(L).text((112, yy2), ln, font=f, fill=P.ink + (230,))
                yy2 += lhp
        if e < 1:
            L.putalpha(L.getchannel("A").point(lambda v: int(v * e)))
        img.alpha_composite(L, (x0 + off, yy))


def bullets(img, items, box, P, mark, size=42):
    """each item on its own line(s) with a coloured marker"""
    x0, y0, x1, y1 = box
    n = len(items)
    hh = (y1 - y0) // n
    d = ImageDraw.Draw(img)
    for k, t in enumerate(items):
        yy = y0 + k * hh
        d.ellipse((x0, yy + 8, x0 + 46, yy + 54), fill=mark, outline=P.ink, width=4)
        para(img, t, (x0 + 70, yy, x1, yy + hh - 10), P, size, "Bold")

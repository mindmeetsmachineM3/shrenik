"""Flat 'sticker' icons drawn by code (no image files, no licences). icon(name, size, c1, c2, ink) -> RGBA."""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .common import pf

NAMES = ["shop", "food", "truck", "laptop", "phone", "salon", "plant", "book", "camera", "bag", "gear", "home", "heart", "cart", "megaphone", "cup", "chart", "coin"]
K = 4          # supersampling
U = 100        # drawing grid


class _D:
    def __init__(self, size, c1, c2, ink):
        self.s = size * K / U
        self.im = Image.new("RGBA", (size * K, size * K), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.c1, self.c2, self.ink, self.w = c1, c2, ink, max(2, int(3.2 * self.s))
        self.white = (255, 255, 255)

    def p(self, pts):
        return [(x * self.s, y * self.s) for x, y in pts]

    def poly(self, pts, fill):
        self.d.polygon(self.p(pts), fill=fill, outline=self.ink, width=self.w)

    def rr(self, x0, y0, x1, y1, fill, r=3):
        self.d.rounded_rectangle([x0 * self.s, y0 * self.s, x1 * self.s, y1 * self.s], r * self.s, fill=fill, outline=self.ink, width=self.w)

    def ci(self, cx, cy, r, fill, ow=True):
        self.d.ellipse([(cx - r) * self.s, (cy - r) * self.s, (cx + r) * self.s, (cy + r) * self.s], fill=fill, outline=self.ink if ow else None, width=self.w)

    def ln(self, pts, w=4, col=None):
        self.d.line(self.p(pts), fill=col or self.ink, width=int(w * self.s / 3.2), joint="curve")

    def arc(self, box, a0, a1, w=4):
        w = w * 1.5
        self.d.arc([v * self.s for v in box], a0, a1, fill=self.ink, width=int(w * self.s / 3.2))


def _heart(g):
    mask = Image.new("L", g.im.size, 0)
    md = ImageDraw.Draw(mask)
    s = g.s
    for cx in (35, 65):
        md.ellipse([(cx - 19) * s, (38 - 19) * s, (cx + 19) * s, (38 + 19) * s], fill=255)
    md.polygon(g.p([(17, 46), (83, 46), (50, 88)]), fill=255)
    edge = mask.filter(ImageFilter.MaxFilter(int(g.w * 2) | 1))
    g.im.paste(Image.new("RGBA", g.im.size, g.ink), (0, 0), edge)
    g.im.paste(Image.new("RGBA", g.im.size, g.c1), (0, 0), mask)
    g.ci(40, 33, 5, (255, 255, 255, 200), ow=False)


def icon(name, size, c1, c2, ink=(17, 17, 17)):
    g = _D(size, c1, c2, ink)
    W = g.white
    if name == "shop":
        for i in range(6):
            x0 = 10 + i * 13.33
            g.rr(x0, 24, x0 + 13.33, 42, c1 if i % 2 == 0 else W, 0)
        g.rr(14, 42, 86, 90, W, 2)
        for i in range(6):
            g.ci(10 + i * 13.33 + 6.66, 42, 6.6, c1 if i % 2 == 0 else W)
        g.rr(42, 60, 62, 90, c2); g.rr(20, 56, 36, 72, (200, 230, 255)); g.rr(68, 56, 80, 72, (200, 230, 255))
    elif name == "food":
        g.rr(14, 74, 86, 90, c1, 7)
        g.rr(12, 62, 88, 72, c2, 5)
        g.rr(14, 52, 86, 63, ink, 5)
        g.d.pieslice([14 * g.s, 20 * g.s, 86 * g.s, 70 * g.s], 180, 360, fill=c1, outline=ink, width=g.w)
        for x, y in ((34, 36), (50, 30), (64, 38), (44, 44)):
            g.d.ellipse([(x - 3) * g.s, (y - 2) * g.s, (x + 3) * g.s, (y + 2) * g.s], fill=W)
    elif name == "truck":
        g.rr(6, 30, 60, 70, W, 3)
        g.poly([(60, 42), (80, 42), (94, 56), (94, 70), (60, 70)], c1)
        g.poly([(66, 47), (77, 47), (86, 56), (66, 56)], (200, 230, 255))
        g.rr(12, 40, 54, 48, c2, 2)
        for x in (24, 78):
            g.ci(x, 74, 9, ink); g.ci(x, 74, 4, W, ow=False)
    elif name == "laptop":
        g.rr(18, 20, 82, 64, W, 4)
        g.rr(24, 26, 76, 58, (235, 240, 250), 2)
        g.rr(28, 46, 36, 56, c1, 1); g.rr(42, 38, 50, 56, c2, 1); g.rr(56, 32, 64, 56, c1, 1)
        g.poly([(6, 68), (94, 68), (88, 80), (12, 80)], c1)
    elif name == "phone":
        g.rr(28, 6, 72, 94, c1, 9)
        g.rr(34, 16, 66, 78, W, 3)
        g.rr(38, 22, 62, 36, c2, 2); g.rr(38, 42, 62, 48, (210, 215, 225), 1); g.rr(38, 54, 54, 60, (210, 215, 225), 1)
        g.ci(50, 87, 3.6, W, ow=False)
    elif name == "salon":
        g.ln([(34, 74), (66, 14)], 12); g.ln([(66, 74), (34, 14)], 12)
        g.ln([(34, 74), (66, 14)], 7.5, c1); g.ln([(66, 74), (34, 14)], 7.5, c2)
        g.ci(30, 78, 12, c1); g.ci(30, 78, 5, W); g.ci(70, 78, 12, c2); g.ci(70, 78, 5, W)
    elif name == "plant":
        g.poly([(28, 64), (72, 64), (65, 92), (35, 92)], c2)
        g.rr(24, 58, 76, 68, c1, 3)
        g.ln([(50, 58), (50, 30)], 5)
        g.d.ellipse([52 * g.s, 20 * g.s, 84 * g.s, 44 * g.s], fill=(80, 200, 120), outline=ink, width=g.w)
        g.d.ellipse([16 * g.s, 28 * g.s, 48 * g.s, 52 * g.s], fill=(60, 180, 100), outline=ink, width=g.w)
    elif name == "book":
        g.poly([(8, 26), (48, 34), (48, 86), (8, 78)], W)
        g.poly([(92, 26), (52, 34), (52, 86), (92, 78)], W)
        g.ln([(50, 34), (50, 86)], 4)
        for y in (44, 54, 64):
            g.ln([(16, y - 2), (40, y + 2)], 3, c1); g.ln([(84, y - 2), (60, y + 2)], 3, c2)
    elif name == "camera":
        g.rr(34, 20, 62, 34, c2, 3)
        g.rr(8, 28, 92, 84, c1, 9)
        g.ci(50, 56, 21, W); g.ci(50, 56, 13, ink); g.ci(45, 51, 4, W, ow=False)
        g.ci(80, 40, 3.5, W, ow=False)
    elif name == "bag":
        g.arc((34, 10, 66, 54), 180, 360, 5.5)
        g.poly([(20, 34), (80, 34), (88, 92), (12, 92)], c1)
        g.rr(36, 58, 64, 74, W, 3)
        g.ci(30, 44, 3, W, ow=False); g.ci(70, 44, 3, W, ow=False)
    elif name == "gear":
        for i in range(8):
            a = math.radians(i * 45)
            ca, sa = math.cos(a), math.sin(a)
            cx, cy = 50 + 30 * ca, 50 + 30 * sa
            pts = [(cx + 9 * math.cos(a + t) * 1.0 - 0, cy + 9 * math.sin(a + t)) for t in (0.9, 2.24, 3.14 + 0.9, 3.14 + 2.24)]
            g.poly([(cx + 8 * math.cos(a + t), cy + 8 * math.sin(a + t)) for t in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4)], c2)
        g.ci(50, 50, 28, c1); g.ci(50, 50, 11, W)
    elif name == "home":
        g.rr(18, 46, 82, 90, W, 2)
        g.poly([(6, 52), (50, 12), (94, 52)], c1)
        g.rr(42, 62, 60, 90, c2); g.rr(24, 56, 36, 68, (200, 230, 255)); g.rr(66, 56, 78, 68, (200, 230, 255))
    elif name == "heart":
        _heart(g)
    elif name == "cart":
        g.ln([(6, 16), (22, 16), (34, 62), (84, 62)], 5)
        g.poly([(24, 28), (92, 28), (82, 54), (32, 54)], c1)
        g.ln([(40, 28), (44, 54)], 3, W); g.ln([(58, 28), (58, 54)], 3, W); g.ln([(76, 28), (72, 54)], 3, W)
        for x in (42, 76):
            g.ci(x, 78, 8, ink); g.ci(x, 78, 3, W, ow=False)
    elif name == "megaphone":
        g.rr(22, 58, 36, 84, c2, 3)
        g.poly([(10, 38), (40, 38), (78, 16), (78, 80), (40, 60), (10, 60)], c1)
        g.ln([(84, 32), (95, 24)], 4); g.ln([(86, 48), (98, 48)], 4); g.ln([(84, 64), (95, 72)], 4)
    elif name == "cup":
        g.poly([(18, 40), (74, 40), (68, 88), (24, 88)], W)
        g.poly([(19.5, 52), (72.5, 52), (70.5, 66), (21.5, 66)], c1)
        g.arc((60, 46, 92, 78), 270, 90, 5.5)
        for x in (32, 46, 60):
            g.arc((x - 6, 8, x + 6, 22), 90, 270, 4); g.arc((x - 6, 20, x + 6, 34), 270, 90, 4)
    elif name == "chart":
        g.ln([(10, 10), (10, 90), (92, 90)], 4.5)
        g.rr(20, 58, 36, 88, c1, 2); g.rr(44, 42, 60, 88, c2, 2); g.rr(68, 24, 84, 88, c1, 2)
        g.ln([(16, 48), (42, 30), (58, 38), (84, 12)], 5)
        g.poly([(90, 6), (74, 10), (86, 22)], c2)
    else:                                                   # coin
        g.ci(50, 50, 40, c1); g.ci(50, 50, 29, c2)
        f = pf("Bold", int(46 * g.s))
        g.d.text((50 * g.s, 50 * g.s), "₹", font=f, fill=ink, anchor="mm")
    return g.im.resize((size, size), Image.LANCZOS)

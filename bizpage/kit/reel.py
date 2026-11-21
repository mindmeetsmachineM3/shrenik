"""Animated explainer Reel (1080x1920, 24 fps): icon pops in, cost meter fills, steps slide in, bars grow, spoken line shown as subtitles.
Voice: young-man (about 20) style Hinglish (Gemini TTS 'Puck' + kid style prompt, or Edge with a pitch lift). Music: royalty-free from music/ or generated."""
import os
import random
import shutil
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw

from . import gfx, music, voice
from .common import FFMPEG, ROOT, df, pf
from .gfx import Pal, card, chip, ease, footer, header, inr, para, rrect, sticker, title

RW, RH = 1080, 1920
FPS = 24
PAD = .9
SUB = (50, 1545, 1030, 1790)


def _wav_len(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def _f0(path):
    """median pitch (Hz) of a wav clip, simple autocorrelation (good enough to tell a deep voice from a squeaky one)"""
    import numpy as np
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
    out = []
    for s in range(0, len(x) - 1024, 512):
        fr = x[s:s + 1024]
        if np.sqrt((fr ** 2).mean()) < 1500:
            continue
        fr = (fr - fr.mean()) * np.hanning(1024)
        ac = np.correlate(fr, fr, "full")[1024:]
        lo, hi = int(sr / 400), int(sr / 70)
        seg = ac[lo:hi]
        if seg.max() / ac[0] < .4:
            continue
        out.append(sr / (lo + np.where(seg >= .9 * seg.max())[0][0]))
    return float(np.median(out)) if out else 0.0


F0_MAX = float(os.getenv("VOICE_F0_MAX") or 195)      # a natural 16-year-old boy is about 120-190 Hz; above this the voice sounds cartoonish
F0_TARGET = float(os.getenv("VOICE_F0_TARGET") or 160)


def _to_wav(src, dst):
    tmp = Path(str(dst) + ".tmp.wav")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(src), "-ar", "44100", "-ac", "1", str(tmp)], check=True)
    f0 = _f0(tmp)
    f = getattr(voice, "PITCH", 1.0)                   # your own VOICE_PITCH, if set
    if f0 * f > F0_MAX:                                 # still too high: lower towards a natural male pitch
        f = f * (F0_TARGET / (f0 * f))
    f = max(.72, min(1.3, f))
    af = f"asetrate=44100*{f:.3f},aresample=44100,atempo={1 / f:.4f}" if abs(f - 1) > .01 else "anull"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(tmp), "-af", af, str(dst)], check=True)
    tmp.unlink(missing_ok=True)
    print(f"voice pitch: {f0:.0f} Hz, shift x{f:.2f} -> about {f0 * f:.0f} Hz", flush=True)


def _voices(texts, tmp, mode, lang):
    if mode == "none":
        return [None] * len(texts), "no voice"
    prov = voice.chain("auto" if mode == "auto" else mode)
    out, label = [], ""
    for i, t in enumerate(texts):
        raw = tmp / f"v{i}.raw"
        try:
            p, label = voice.speak(t, lang, raw, prov)
            f = next((x for x in tmp.glob(f"v{i}.*") if x.suffix != ".wav"), raw)
            wv = tmp / f"v{i}.wav"
            _to_wav(f, wv)
            out.append(wv)
            prov = [p] + [x for x in prov if x != p]
        except Exception as ex:
            print("voice failed for scene", i, str(ex)[:150], file=sys.stderr)
            out.append(None)
    return out, label


def _L(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


class Scene:
    def __init__(self, P, tf, idea, num, handle, k, n, seed):
        self.P, self.tf, self.i, self.k, self.n = P, tf, idea, k, n
        self.bg = gfx.background(RW, RH, P, seed)
        label = {0: f"BUSINESS IDEA #{num}", 1: "WHAT IS IT?", 2: "STARTUP COST", 3: "HOW TO START", 4: "EARNING", 5: "YOUR TURN"}[k]
        header(self.bg, P, label, f"{k + 1:02d} / {n:02d}", handle)
        footer(self.bg, P, handle)
        self.layers = []                                   # (image, (x, y), t_in)
        self.dyn = []                                      # callables (frame, t, dur)
        getattr(self, f"s{k}")()

    def add(self, img, xy, t_in=0.0):
        self.layers.append((img, xy, t_in))

    # ---- scenes
    def s0(self):
        P, i = self.P, self.i
        self.dyn.append(lambda fr, t, d: sticker(fr, i["icon"], 540, 600, 640, P, t / .8, -5))
        a = _L(1000, 520)
        card(a, (0, 0, 980, 470), P, sh=12)
        title(a, i["hook"], i["hook"].split()[-1], (40, 30, 940, 340), P, self.tf, 150, "left", .98)
        chip(a, i["name"], 40, 370, P, 32, P.a2)
        self.add(a, (50, 1000), .5)

    def s1(self):
        P, i = self.P, self.i
        self.dyn.append(lambda fr, t, d: sticker(fr, i["icon"], 230, 330, 300, P, t / .6, -6))
        a = _L(620, 300); title(a, i["name"], i["name"].split()[-1], (0, 0, 600, 280), P, self.tf, 120, "left")
        self.add(a, (430, 190), .2)
        b = _L(1000, 420); card(b, (0, 0, 980, 380), P, sh=10); para(b, i["pitch"], (36, 34, 944, 350), P, 50, "Bold")
        self.add(b, (50, 560), .7)
        c = _L(1000, 330)
        chip(c, "WHO IS IT FOR", 0, 0, P, 30, P.a2)
        card(c, (0, 80, 980, 290), P, sh=8); para(c, i["who"], (36, 104, 944, 270), P, 44, "Medium")
        self.add(c, (50, 1030), 1.8)
        e = _L(900, 100); chip(e, "TIME: " + i["time"], 0, 0, P, 32, P.a1)
        self.add(e, (50, 1400), 3.0)

    def s2(self):
        P, i = self.P, self.i
        a = _L(980, 200); title(a, "How much to start?", "start?", (0, 0, 960, 190), P, self.tf, 120)
        self.add(a, (60, 170), 0)
        b = _L(1000, 760); card(b, (0, 0, 980, 720), P, sh=12)
        ImageDraw.Draw(b).text((490, 190), f"{inr(i['invest_low'])} - {inr(i['invest_high'])}", font=df(self.tf, 170), fill=P.a1, anchor="mm")
        self.add(b, (50, 420), .3)
        vmax = max(i["invest_high"] * 1.5, 1000)
        self.dyn.append(lambda fr, t, d: gfx.meter(fr, (110, 800, 970, 900), i["invest_low"], i["invest_high"], vmax, P, (t - .7) / 1.3) if t > .6 else None)
        self.dyn.append(lambda fr, t, d: sticker(fr, "coin", 880, 1330, 250, P, (t - .6) / .6, 10) if t > .6 else None)
        n = _L(760, 120); para(n, "Approx. for a tier-2 city. Start small, test first, then scale.", (0, 0, 740, 110), P, 34, "Medium")
        self.add(n, (60, 1180), 1.2)

    def s3(self):
        P, i = self.P, self.i
        a = _L(980, 170); title(a, "4 simple steps", "4", (0, 0, 960, 160), P, self.tf, 120)
        self.add(a, (60, 160), 0)
        self.dyn.append(lambda fr, t, d: gfx.steps(fr, (50, 360, 1010, 1520), i["steps"], P, max(0.0, (t - .3) / max(2.0, d - 1.4) * 4.2), 42))

    def s4(self):
        P, i = self.P, self.i
        a = _L(980, 200); title(a, "What can you earn?", "earn?", (0, 0, 960, 190), P, self.tf, 120)
        self.add(a, (60, 170), 0)
        b = _L(1000, 1010); card(b, (0, 0, 980, 970), P, sh=12)
        self.add(b, (50, 410), .2)
        items = [("Slow month", i["earn_low"], P.a2), ("Average", (i["earn_low"] + i["earn_high"]) // 2, P.a1), ("Good month", i["earn_high"], P.a3)]
        self.dyn.append(lambda fr, t, d: gfx.bars(fr, (110, 470, 970, 1360), items, P, (t - .5) / 1.6, 46) if t > .4 else None)
        n = _L(980, 80); ImageDraw.Draw(n).text((490, 40), "Approx. monthly income. Not guaranteed.", font=pf("Bold", 30), fill=P.ink, anchor="mm")
        self.add(n, (50, 1450), 1.5)

    def s5(self):
        P, i = self.P, self.i
        a = _L(980, 420); title(a, "Save it. Follow. Comment.", "Follow.", (0, 0, 780, 410), P, self.tf, 130, "left", .98)
        self.add(a, (60, 170), 0)
        self.dyn.append(lambda fr, t, d: sticker(fr, "megaphone", 880, 380, 240, P, (t - .3) / .6, -8))
        for j, (txt, col) in enumerate([("SAVE", P.a2), ("FOLLOW", P.a1), ("COMMENT", P.a3)]):
            c = _L(500, 110); chip(c, txt, 0, 0, P, 40, col)
            self.add(c, (60 + j * 20, 650 + j * 120), 1.2 + j * .7)
        q = _L(1000, 330); card(q, (0, 0, 980, 300), P, fill=P.ink, sh=0)
        para(q, i["question"], (36, 24, 944, 280), P, 54, "Bold", color=(255, 255, 255), align="center")
        self.add(q, (50, 1130), 3.2)

    # ---- render one frame
    def frame(self, t, dur, say, vlen, subs):
        fr = self.bg.copy()
        for img, (x, y), t_in in self.layers:
            e = ease((t - t_in) / .45)
            if e <= 0:
                continue
            if e < 1:
                img = img.copy()
                img.putalpha(img.getchannel("A").point(lambda v: int(v * e)))
            fr.alpha_composite(img, (x, y + int((1 - e) * 70)))
        for f in self.dyn:
            f(fr, t, dur)
        if say:                                              # subtitles: the spoken line in chunks
            words = say.split()
            ch = [" ".join(words[a:a + 5]) for a in range(0, len(words), 5)]
            idx = min(len(ch) - 1, int(max(0, t - .25) / max(.5, vlen) * len(ch)))
            if idx not in subs:
                s = _L(SUB[2] - SUB[0] + 20, SUB[3] - SUB[1] + 20)
                card(s, (0, 0, SUB[2] - SUB[0], SUB[3] - SUB[1]), self.P, fill=self.P.ink, sh=8, r=28, bw=4)
                para(s, ch[idx], (36, 20, SUB[2] - SUB[0] - 36, SUB[3] - SUB[1] - 20), self.P, 62, "Bold", color=(255, 255, 255), align="center")
                subs[idx] = s
            fr.alpha_composite(subs[idx], (SUB[0], SUB[1]))
        return fr


def build(idea, num, handle, palette, out_path, voice_mode="auto", seed=7, lang="hinglish", tmp=None):
    out_path = Path(out_path)
    tmp = Path(tmp or out_path.parent / "_reel_tmp")
    tmp.mkdir(parents=True, exist_ok=True)
    P = Pal(palette)
    rng = random.Random(seed)
    tf = rng.choice(gfx.TITLE_FONTS[:3])
    order = ["hook", "what", "invest", "steps", "earn", "cta"]
    texts = [idea["say"][k] for k in order]
    wavs, vlabel = _voices(texts, tmp, voice_mode, lang)
    if voice_mode != "none" and not all(wavs):            # never post a silent Reel by accident
        raise RuntimeError("voice failed for some scenes, Reel not made (see 'voice failed' lines above)")
    vlens = [_wav_len(w) if w else 3.2 for w in wavs]
    durs = [v + PAD + (1.2 if k == 5 else 0) for k, v in enumerate(vlens)]
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-an", str(tmp / "video.mp4")]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = sum(durs)
    done_t = 0.0
    for k in range(6):
        sc = Scene(P, tf, idea, num, handle, k, 6, seed + k * 7)
        subs = {}
        for f in range(int(durs[k] * FPS)):
            t = f / FPS
            fr = sc.frame(t, durs[k], texts[k], vlens[k], subs)
            d = ImageDraw.Draw(fr)
            d.rectangle((0, RH - 14, RW, RH), fill=P.ink + (60,))
            d.rectangle((0, RH - 14, int(RW * (done_t + t) / total), RH), fill=P.a1 + (255,))
            pr.stdin.write(fr.convert("RGB").tobytes())
        done_t += durs[k]
    pr.stdin.close()
    pr.wait()
    if pr.returncode:
        raise RuntimeError("ffmpeg video encode failed")
    mlabel = music.pick(total + 1, seed, tmp / "beat.wav", ROOT / "music", FFMPEG)
    ins = ["-i", str(tmp / "video.mp4"), "-i", str(tmp / "beat.wav")]
    parts, labels, kk, t0 = ["[1:a]volume=0.22[b]"], ["[b]"], 2, 0.0
    for i, w in enumerate(wavs):
        if w:
            ins += ["-i", str(w)]
            ms = int((t0 + .3) * 1000)
            parts.append(f"[{kk}:a]adelay={ms}|{ms},volume=1.7[v{i}]")
            labels.append(f"[v{i}]")
            kk += 1
        t0 += durs[i]
    fc = ";".join(parts) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:duration=first:normalize=0,alimiter=limit=0.95[a]"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", str(out_path)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return f"{total:.0f}s Reel, voice: {vlabel}, music: {mlabel}"

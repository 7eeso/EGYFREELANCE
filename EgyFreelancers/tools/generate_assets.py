"""Regenerates the illustrative images and the hero video in /static.

These are original, locally generated illustrations (no stock photos, no external
downloads). Replace any file in static/img or static/video with your own photography
or footage using the same file name and the site will pick it up.

Usage:  python tools/generate_assets.py          (needs Pillow, numpy and ffmpeg)
"""
import math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG, VID = ROOT / "static" / "img", ROOT / "static" / "video"
IMG.mkdir(parents=True, exist_ok=True); VID.mkdir(parents=True, exist_ok=True)

BLUE, BLUE_D, BLUE_L, BLUE_XL = "#2563eb", "#1d4ed8", "#dbeafe", "#eef2ff"
INK, GRAY, GRAY_L, BG, WHITE, MUTE = "#0a0a0a", "#d1d5db", "#e5e7eb", "#f3f4f6", "#ffffff", "#9ca3af"
SS = 2  # supersampling

def font(size, weight="Bold"):
    for p in (f"/usr/share/fonts/opentype/inter/Inter-{weight}.otf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try: return ImageFont.truetype(p, int(size * SS))
        except OSError: pass
    return ImageFont.load_default()

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (w * SS, h * SS), bg)
        self.d = ImageDraw.Draw(self.im)
    def _s(self, *v): return [x * SS for x in v]
    def rr(self, x0, y0, x1, y1, r=10, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(self._s(x0, y0, x1, y1), radius=r * SS, fill=fill, outline=outline, width=int(width * SS))
    def ell(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.ellipse(self._s(x0, y0, x1, y1), fill=fill, outline=outline, width=int(width * SS))
    def circ(self, cx, cy, r, **k): self.ell(cx - r, cy - r, cx + r, cy + r, **k)
    def poly(self, pts, fill=None): self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)
    def line(self, pts, fill=INK, width=2): self.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=int(width * SS), joint="curve")
    def text(self, x, y, s, size=14, fill=INK, weight="Bold", anchor="la"):
        self.d.text((x * SS, y * SS), s, font=font(size, weight), fill=fill, anchor=anchor)
    def bar(self, x, y, w, h=8, fill=GRAY_L): self.rr(x, y, x + w, y + h, h / 2, fill=fill)
    def card(self, x0, y0, x1, y1, r=14, fill=WHITE, shadow=True):
        if shadow: self.rr(x0, y0 + 5, x1, y1 + 5, r, fill="#dfe3e9")
        self.rr(x0, y0, x1, y1, r, fill=fill, outline=GRAY_L)
    def window(self, x0, y0, x1, y1, bar=30):
        self.card(x0, y0, x1, y1, 14)
        self.rr(x0, y0, x1, y0 + bar, 14, fill=BG); self.d.rectangle(self._s(x0 + 1, y0 + bar - 12, x1 - 1, y0 + bar), fill=BG)
        for i in range(3): self.circ(x0 + 18 + i * 14, y0 + bar / 2, 4, fill=GRAY)
        self.rr(x0 + 70, y0 + 8, x1 - 20, y0 + bar - 8, 7, fill=WHITE)
    def image(self): return self.im.resize((self.w, self.h), Image.LANCZOS)

def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u**3 * p0[0] + 3 * u*u * t * p1[0] + 3 * u * t*t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u*u * t * p1[1] + 3 * u * t*t * p2[1] + t**3 * p3[1]))
    return out

def rot_square(cx, cy, s, ang):
    pts = []
    for k in range(4):
        a = ang + math.pi / 4 + k * math.pi / 2
        pts.append((cx + math.cos(a) * s, cy + math.sin(a) * s))
    return pts

def play(c, cx, cy, r, fill=WHITE):
    c.poly([(cx - r * .45, cy - r * .6), (cx - r * .45, cy + r * .6), (cx + r * .65, cy)], fill=fill)

# ---------------------------------------------------------------- category images (640x400)
def cat_design():
    c = Canvas(640, 400, BLUE_XL)
    c.circ(120, 300, 150, fill=BLUE_L); c.rr(430, -40, 700, 160, 40, fill=GRAY_L)
    c.card(200, 70, 440, 330, 18)
    c.rr(236, 104, 296, 164, 16, fill=BLUE); c.poly(rot_square(266, 134, 14, .2), fill=WHITE)
    c.circ(340, 134, 30, fill=INK); c.bar(236, 190, 170, 10, GRAY_L); c.bar(236, 210, 120, 10, GRAY_L)
    for i, col in enumerate((BLUE, INK, GRAY, BLUE_L)): c.circ(252 + i * 44, 280, 15, fill=col, outline=GRAY_L)
    pts = bezier((470, 340), (470, 220), (540, 300), (580, 180)); c.line(pts, fill=BLUE, width=4)
    for p in (pts[0], pts[-1]): c.rr(p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7, 2, fill=WHITE, outline=BLUE, width=2)
    return c.image()

def cat_development():
    c = Canvas(640, 400, BG)
    c.window(60, 60, 470, 340)
    rows = [(0, 90, BLUE), (1, 160, INK), (1, 120, GRAY), (2, 200, BLUE), (2, 140, INK), (1, 80, GRAY), (0, 110, BLUE), (1, 170, GRAY), (1, 100, INK)]
    for i, (ind, w, col) in enumerate(rows): c.bar(90 + ind * 24, 110 + i * 24, w, 10, col)
    c.card(400, 130, 600, 360, 14)
    c.rr(416, 146, 584, 210, 8, fill=BLUE_L); c.bar(416, 226, 120, 9, INK); c.bar(416, 246, 150, 8); c.bar(416, 262, 90, 8)
    c.rr(416, 296, 480, 326, 7, fill=BLUE); c.text(520, 80, "</>", 40, BLUE)
    return c.image()

def cat_writing():
    c = Canvas(640, 400, BLUE_XL)
    c.card(120, 50, 360, 350, 14); c.bar(150, 90, 120, 14, INK)
    for i in range(7): c.bar(150, 130 + i * 24, 180 - (i % 3) * 30, 9)
    c.card(330, 110, 540, 250, 16); c.text(360, 124, "Aa", 64, INK)
    c.bar(360, 214, 140, 9, BLUE)
    c.rr(400, 280, 580, 350, 16, fill=BLUE); c.poly([(430, 350), (450, 350), (430, 372)], fill=BLUE)
    c.bar(424, 303, 110, 9, WHITE); c.bar(424, 323, 70, 9, BLUE_L)
    return c.image()

def cat_marketing():
    c = Canvas(640, 400, BG)
    c.card(60, 60, 330, 340, 14)
    for i, h in enumerate((60, 95, 80, 140, 120, 190)):
        c.rr(90 + i * 38, 310 - h, 120 + i * 38, 310, 5, fill=BLUE if i % 2 == 0 else INK)
    c.line([(90, 150), (150, 120), (210, 130), (270, 90)], fill=BLUE, width=3); c.poly([(262, 76), (288, 84), (272, 104)], fill=BLUE)
    c.card(370, 90, 590, 340, 16); c.circ(402, 124, 16, fill=BLUE); c.bar(428, 112, 90, 9, INK); c.bar(428, 129, 60, 7)
    c.rr(392, 156, 568, 254, 10, fill=BLUE_L); c.circ(480, 205, 20, fill=BLUE); play(c, 480, 205, 14)
    c.bar(392, 274, 150, 8); c.rr(392, 298, 462, 322, 7, fill=INK)
    return c.image()

def cat_video():
    c = Canvas(640, 400, BLUE_XL)
    c.card(110, 40, 530, 250, 14, fill=INK); c.circ(320, 145, 38, fill=BLUE); play(c, 320, 145, 24)
    c.rr(140, 224, 500, 232, 4, fill="#2b2b2b"); c.rr(140, 224, 330, 232, 4, fill=BLUE)
    c.card(70, 280, 570, 372, 12)
    for (x, w, y, col) in ((90, 150, 292, BLUE), (250, 110, 292, INK), (370, 170, 292, GRAY), (110, 120, 322, INK), (240, 200, 322, BLUE), (450, 90, 322, GRAY)):
        c.rr(x, y, x + w, y + 22, 5, fill=col)
    c.rr(318, 272, 322, 378, 2, fill=BLUE)
    return c.image()

def cat_business():
    c = Canvas(640, 400, BG)
    c.card(70, 50, 340, 350, 14); c.bar(100, 86, 110, 13, INK); c.bar(100, 108, 70, 8)
    for i in range(4):
        y = 150 + i * 46; c.circ(112, y + 8, 11, fill=BLUE if i < 3 else WHITE, outline=BLUE if i == 3 else None, width=2)
        c.bar(138, y, 160 - i * 14, 9, INK if i % 2 == 0 else GRAY); c.bar(138, y + 16, 100, 7)
    c.card(380, 60, 590, 250, 14); c.rr(380, 60, 590, 96, 14, fill=BLUE); c.d.rectangle(c._s(381, 82, 589, 96), fill=BLUE)
    for r in range(3):
        for k in range(5):
            x, y = 400 + k * 36, 116 + r * 40; hi = (r, k) == (1, 2)
            c.rr(x, y, x + 26, y + 28, 6, fill=BLUE if hi else BG)
    c.rr(420, 280, 580, 350, 12, fill=INK); c.rr(480, 266, 520, 286, 6, outline=INK, width=4); c.bar(436, 316, 80, 8, "#444")
    return c.image()

# ---------------------------------------------------------------- showcase images (800x520)
def show_branding():
    c = Canvas(800, 520, BG)
    c.card(80, 90, 400, 290, 16, fill=INK); c.rr(112, 122, 168, 178, 14, fill=BLUE); c.poly(rot_square(140, 150, 13, .3), fill=WHITE)
    c.bar(112, 216, 150, 11, WHITE); c.bar(112, 238, 100, 8, "#5b5b5b")
    c.card(300, 170, 620, 370, 16); c.circ(360, 230, 28, fill=BLUE); c.circ(386, 230, 28, fill=INK)
    c.text(344, 280, "Brand", 34, INK); c.bar(344, 332, 160, 9)
    c.card(520, 60, 730, 230, 16)
    for i, col in enumerate((BLUE, INK, GRAY, BLUE_L)): c.rr(546 + i * 44, 88, 580 + i * 44, 200, 8, fill=col, outline=GRAY_L)
    c.text(120, 400, "Aa", 70, INK); c.bar(120, 470, 140, 9, GRAY)
    return c.image()

def show_website():
    c = Canvas(800, 520, BLUE_XL)
    c.rr(130, 70, 670, 400, 18, fill=INK); c.rr(148, 88, 652, 382, 8, fill=WHITE)
    c.rr(166, 106, 196, 126, 5, fill=BLUE); [c.bar(230 + i * 60, 111, 40, 8) for i in range(3)]; c.rr(570, 104, 634, 128, 6, fill=INK)
    c.bar(180, 160, 260, 18, INK); c.bar(180, 190, 200, 18, INK); c.bar(180, 226, 230, 8); c.bar(180, 242, 180, 8)
    c.rr(180, 270, 252, 298, 6, fill=BLUE); c.rr(470, 150, 634, 250, 10, fill=BLUE_L)
    for i in range(3): c.rr(180 + i * 154, 312, 320 + i * 154, 366, 8, fill=BG)
    c.poly([(90, 400), (710, 400), (740, 430), (60, 430)], fill=GRAY); c.rr(340, 400, 460, 412, 4, fill=MUTE)
    return c.image()

def show_video():
    c = Canvas(800, 520, BG)
    c.card(120, 50, 680, 310, 16, fill=INK); c.rr(150, 80, 520, 280, 8, fill="#1f2937"); c.circ(335, 180, 40, fill=BLUE); play(c, 335, 180, 26)
    for i in range(4): c.bar(550, 90 + i * 34, 100 - i * 12, 10, "#3f3f46")
    c.rr(550, 240, 650, 272, 8, fill=BLUE)
    c.card(80, 340, 720, 480, 14)
    for (x, w, y, col) in ((100, 190, 358, BLUE), (306, 130, 358, INK), (452, 200, 358, GRAY), (120, 140, 394, INK), (276, 230, 394, BLUE), (524, 150, 394, GRAY), (100, 260, 430, GRAY), (376, 120, 430, BLUE)):
        c.rr(x, y, x + w, y + 28, 6, fill=col)
    c.rr(398, 332, 403, 488, 2, fill=BLUE); c.poly([(390, 330), (411, 330), (400.5, 344)], fill=BLUE)
    return c.image()

def show_content():
    c = Canvas(800, 520, BLUE_XL)
    c.rr(290, 30, 510, 500, 34, fill=INK); c.rr(304, 48, 496, 482, 24, fill=WHITE)
    c.circ(334, 84, 16, fill=BLUE); c.bar(360, 74, 90, 9, INK); c.bar(360, 90, 56, 7)
    for r in range(3):
        for k in range(2): c.rr(322 + k * 88, 120 + r * 108, 400 + k * 88, 212 + r * 108, 8, fill=[BLUE_L, GRAY_L, BLUE, BG, INK, GRAY][r * 2 + k])
    c.card(80, 130, 280, 290, 14); c.rr(98, 148, 262, 220, 8, fill=BLUE); c.bar(98, 238, 120, 9, INK); c.bar(98, 256, 80, 7)
    c.card(530, 250, 730, 400, 14); c.text(556, 272, "Aa", 44, INK); c.bar(556, 346, 130, 9, BLUE); c.bar(556, 364, 90, 7)
    return c.image()

# ---------------------------------------------------------------- hero frame / video (1280x540)
HW, HH = 1280, 540
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)

_bg = None
def hero_bg():
    global _bg
    if _bg is None:
        c = Canvas(HW, HH, BG)
        for gx in range(16, HW, 32):
            for gy in range(16, HH, 32): c.circ(gx, gy, 1.4, fill="#dde1e7")
        _bg = c.im.copy()
    return _bg.copy()

def hero_frame(p):
    c = Canvas(HW, HH, BG); c.im = hero_bg(); c.d = ImageDraw.Draw(c.im)
    bob = 5 * math.sin(2 * math.pi * p)
    # centre: website being built
    x0, y0, x1, y1 = 400, 52 + bob, 880, 492 + bob
    c.window(x0, y0, x1, y1, 34)
    r = ease(p / .35); fade = 1 - ease((p - .9) / .1); r *= fade
    c.rr(x0 + 24, y0 + 54, x0 + 54, y0 + 76, 5, fill=BLUE)
    for i in range(3): c.bar(x0 + 96 + i * 62, y0 + 60, 42, 9)
    c.rr(x1 - 94, y0 + 54, x1 - 24, y0 + 80, 7, fill=INK)
    c.bar(x0 + 28, y0 + 118, 330 * r + 1, 22, INK); c.bar(x0 + 28, y0 + 152, 250 * clamp(r * 1.2) + 1, 22, INK)
    c.bar(x0 + 28, y0 + 196, 300 * clamp(r * 1.3) + 1, 9); c.bar(x0 + 28, y0 + 214, 220 * clamp(r * 1.3) + 1, 9)
    btn_on = ease((p - .5) / .1) * (1 - ease((p - .88) / .08))
    c.rr(x0 + 28, y0 + 244, x1 - 28, y0 + 288, 10, fill=WHITE, outline=BLUE if btn_on > .5 else GRAY, width=2)
    c.bar(x0 + 46, y0 + 262, 150, 8, GRAY_L)
    c.rr(x1 - 130, y0 + 250, x1 - 36, y0 + 282, 8, fill=BLUE if btn_on > .5 else INK)
    for i, col in enumerate((BLUE_L, GRAY_L, BLUE_XL)):
        a = ease((p - .18 - i * .06) / .12) * fade
        yy = y0 + 312 + (1 - a) * 18
        if a > 0.02: c.rr(x0 + 28 + i * 146, yy, x0 + 162 + i * 146, yy + 100, 10, fill=col); c.bar(x0 + 40 + i * 146, yy + 76, 70, 8, INK if i != 1 else GRAY)
    # cursor travels to the button and back
    t = ease((p - .30) / .22) - ease((p - .78) / .2)
    cx, cy = x0 + 120 + t * (x1 - x0 - 190), y0 + 330 - t * 62
    c.poly([(cx, cy), (cx, cy + 22), (cx + 6, cy + 17), (cx + 11, cy + 28), (cx + 15, cy + 26), (cx + 10, cy + 16), (cx + 18, cy + 16)], fill=INK)
    # left: branding
    lb = 5 * math.sin(2 * math.pi * p + 2)
    lx0, ly0, lx1, ly1 = 70, 100 + lb, 350, 440 + lb
    c.card(lx0, ly0, lx1, ly1, 16)
    c.rr(lx0 + 20, ly0 + 18, lx0 + 104, ly0 + 42, 8, fill=BLUE_XL); c.text(lx0 + 62, ly0 + 30, "Branding", 12, BLUE, anchor="mm")
    ang = (math.pi / 2) * ease(p * 1.0); 
    c.rr(lx0 + 20, ly0 + 56, lx1 - 20, ly0 + 190, 12, fill=BG)
    c.poly(rot_square((lx0 + lx1) / 2 - 36, ly0 + 123, 36, ang), fill=BLUE); c.circ((lx0 + lx1) / 2 + 40, ly0 + 123, 26, fill=INK)
    sel = int(p * 4) % 4
    for i, col in enumerate((BLUE, INK, GRAY, BLUE_L)):
        c.circ(lx0 + 44 + i * 58, ly0 + 228, 18, fill=col, outline=GRAY_L)
        if i == sel: c.circ(lx0 + 44 + i * 58, ly0 + 228, 25, outline=BLUE, width=2)
    c.text(lx0 + 22, ly0 + 262, "Aa", 44, INK); c.bar(lx0 + 22, ly0 + 322, 150, 9); c.bar(lx0 + 22, ly0 + 340 - 4, 100, 7) if False else None
    # right: video editor
    rb = 5 * math.sin(2 * math.pi * p + 4)
    rx0, ry0, rx1, ry1 = 930, 100 + rb, 1210, 440 + rb
    c.card(rx0, ry0, rx1, ry1, 16)
    c.rr(rx0 + 20, ry0 + 18, rx0 + 86, ry0 + 42, 8, fill=BLUE_XL); c.text(rx0 + 53, ry0 + 30, "Video", 12, BLUE, anchor="mm")
    c.rr(rx0 + 20, ry0 + 56, rx1 - 20, ry0 + 186, 10, fill=INK); play(c, (rx0 + rx1) / 2, ry0 + 121, 24)
    c.rr(rx0 + 34, ry0 + 168, rx1 - 34, ry0 + 174, 3, fill="#2b2b2b"); c.rr(rx0 + 34, ry0 + 168, rx0 + 34 + (rx1 - rx0 - 68) * p, ry0 + 174, 3, fill=BLUE)
    tx = rx0 + 22; tw = rx1 - rx0 - 44
    for row, clips in enumerate(((0, .42, BLUE), (.46, .54, INK)), 0):
        pass
    tracks = [((0, .38, BLUE), (.42, .3, INK), (.76, .24, GRAY)), ((0, .25, INK), (.29, .45, BLUE), (.78, .22, GRAY)), ((.1, .5, GRAY), (.64, .3, BLUE))]
    for i, tr in enumerate(tracks):
        for s, w, col in tr: c.rr(tx + s * tw, ry0 + 206 + i * 38, tx + (s + w) * tw - 3, ry0 + 232 + i * 38, 5, fill=col)
    px = tx + p * tw; c.rr(px - 1.5, ry0 + 196, px + 1.5, ry0 + 322, 1, fill=BLUE); c.poly([(px - 6, ry0 + 194), (px + 6, ry0 + 194), (px, ry0 + 204)], fill=BLUE)
    return c.image()

def build_video(fps=24, seconds=10):
    n = fps * seconds
    out_mp4, out_webm = VID / "hero.mp4", VID / "hero.webm"
    common = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{HW}x{HH}", "-r", str(fps), "-i", "-", "-an"]
    mp4 = subprocess.Popen(common + ["-c:v", "libx264", "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_mp4)], stdin=subprocess.PIPE)
    webm = subprocess.Popen(common + ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "36", "-row-mt", "1", "-pix_fmt", "yuv420p", str(out_webm)], stdin=subprocess.PIPE)
    for i in range(n):
        raw = hero_frame(i / n).tobytes(); mp4.stdin.write(raw); webm.stdin.write(raw)
    for pr in (mp4, webm): pr.stdin.close(); pr.wait()
    hero_frame(0.62).save(IMG / "hero-poster.jpg", quality=84, optimize=True)

def save(im, name): im.save(IMG / name, "WEBP", quality=82, method=6)

if __name__ == "__main__":
    for key, fn in dict(design=cat_design, development=cat_development, writing=cat_writing, marketing=cat_marketing, video=cat_video, business=cat_business).items():
        save(fn(), f"cat-{key}.webp")
    for key, fn in dict(branding=show_branding, website=show_website, video=show_video, content=show_content).items():
        save(fn(), f"showcase-{key}.webp")
    if "--no-video" not in sys.argv: build_video()
    print("assets generated in", IMG, "and", VID)

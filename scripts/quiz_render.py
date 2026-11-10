"""ふくろう博士クイズリール
usage: python3 quiz_render.py a|b preview|full
"""
import json, math, subprocess, sys, wave, array
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 1080, 1920, 30
THEME = sys.argv[1]
ROOT = Path("/home/claude/v10" if THEME == "a" else "/home/claude/v11")
OUTNAME = "fukuro_ondoku" if THEME == "a" else "fukuro_shukan66"
AUD = ROOT / "audio"
OUT = ROOT / "scenes"
OUT.mkdir(exist_ok=True)
NSCENE = 6

F_BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
F_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
CREAM = (255, 244, 214)
DIM = (190, 180, 160)
INK = (24, 16, 10)
RED = (255, 120, 110)

if THEME == "a":
    ACC = (255, 226, 110)      # 黄色チョーク
    PANEL = (22, 46, 36, 225)
    LINES_SUB = [
        "黙読と音読、覚えるのはどっち？",
        "答えは、音読じゃ",
        "黙読は65%、音読は77%じゃ",
        "口と耳の両方で覚えるからじゃ",
        "覚えたいなら、声に出す。ホウ",
        "当たったら、友達にも出題してくれ",
    ]
    TITLE = [("ふくろう博士の", CREAM), ("記憶クイズ", ACC)]
    CHOICES = [("黙読", "だまって読む"), ("音読", "声に出して読む")]
    ANSWER = 1
else:
    ACC = (255, 172, 80)       # 朝日のオレンジ
    PANEL = (30, 26, 48, 225)
    LINES_SUB = [
        "習慣になるまで、21日と66日、どっち？",
        "答えは、66日じゃ",
        "早い人で18日、遅い人は254日じゃった",
        "1日休んでも、ほぼ影響なしじゃ",
        "3週間で、あきらめない。ホウ",
        "当たったら、友達にも出題してくれ",
    ]
    TITLE = [("ふくろう博士の", CREAM), ("習慣クイズ", ACC)]
    CHOICES = [("21日", "3週間説"), ("66日", "約2か月説")]
    ANSWER = 1
GREEN = (130, 222, 150)

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

def text_w(t, f):
    b = f.getbbox(t)
    return b[2] - b[0]

def draw_center(d, y, t, f, fill, stroke=8, sfill=INK, x=None):
    w = text_w(t, f)
    xx = (W - w) // 2 if x is None else x
    d.text((xx, y), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return w

def draw_runs(d, y, runs, size, stroke=10):
    f = font(F_BLACK, size)
    total = sum(text_w(t, f) for t, _ in runs)
    x = (W - total) // 2
    for t, c in runs:
        d.text((x, y), t, font=f, fill=c, stroke_width=stroke, stroke_fill=INK)
        x += text_w(t, f)

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def vgrad(top, bot):
    g = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / H
        g.putpixel((0, y), tuple(int(top[j] * (1 - t) + bot[j] * t) for j in range(3)))
    return g.resize((W, H))

# ---------------------------------------------------------------- 背景
def bg_a():
    """教室の黒板"""
    img = vgrad((92, 78, 64), (70, 58, 48))
    d = ImageDraw.Draw(img)
    d.rectangle((20, 360, W - 20, 1210), fill=(120, 84, 50))          # 木枠
    d.rectangle((44, 384, W - 44, 1186), fill=(30, 66, 50))           # 黒板
    noise = Image.effect_noise((W, H), 18).convert("RGB")
    board = Image.new("L", (W, H), 0)
    ImageDraw.Draw(board).rectangle((44, 384, W - 44, 1186), fill=40)
    img = Image.composite(ImageChops.add(img, noise.point(lambda v: v // 6)), img, board)
    d = ImageDraw.Draw(img)
    # 消し跡
    smear = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(smear).ellipse((120, 980, 620, 1120), fill=(18, 22, 20))
    img = ImageChops.add(img, smear.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(img)
    d.rectangle((20, 1206, W - 20, 1236), fill=(150, 108, 70))         # チョーク置き
    for k, c in enumerate([(250, 250, 240), (255, 226, 110), (255, 140, 140)]):
        d.rounded_rectangle((760 + k * 70, 1196, 820 + k * 70, 1210), 6, fill=c)
    d.rectangle((0, 1590, W, H), fill=(120, 88, 60))                   # 教卓
    d.rectangle((0, 1590, W, 1604), fill=(150, 112, 78))
    # 教科書（左）
    d.rectangle((50, 1700, 300, 1760), fill=(70, 110, 170))
    d.rectangle((70, 1660, 290, 1704), fill=(200, 80, 70))
    return img

def bg_b():
    """朝の部屋とカレンダー"""
    img = vgrad((40, 36, 66), (104, 70, 66))
    sun = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(sun).ellipse((700, 1150, 1300, 1750), fill=(110, 70, 20))
    img = ImageChops.add(img, sun.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(img)
    # うすいカレンダーのマス
    for r in range(6):
        for c in range(7):
            x, y = 70 + c * 136, 400 + r * 130
            d.rounded_rectangle((x, y, x + 122, y + 116), 12, outline=(80, 72, 100), width=3)
    shade = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shade).rounded_rectangle((60, 400, W - 60, 1340), 80, fill=150)
    shade = shade.filter(ImageFilter.GaussianBlur(80))
    img = Image.composite(Image.new("RGB", (W, H), (22, 20, 38)), img, shade)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1590, W, H), fill=(132, 98, 72))                   # 机
    d.rectangle((0, 1590, W, 1604), fill=(164, 124, 92))
    # 卓上カレンダー（左）
    d.polygon([(60, 1780), (150, 1640), (290, 1640), (290, 1780)], fill=(238, 232, 220))
    d.rectangle((150, 1640, 290, 1672), fill=(220, 90, 70))
    for k in range(3):
        d.line((175 + k * 40, 1700, 175 + k * 40, 1760), fill=(200, 190, 175), width=3)
    # 植木鉢（右）
    d.polygon([(860, 1680), (980, 1680), (960, 1780), (880, 1780)], fill=(200, 110, 70))
    for a in (-0.6, 0, 0.6):
        x2, y2 = 920 + int(70 * math.sin(a)), 1680 - int(90 * math.cos(a))
        d.line((920, 1680, x2, y2), fill=(90, 170, 100), width=10)
        d.ellipse((x2 - 26, y2 - 18, x2 + 26, y2 + 18), fill=(110, 196, 120))
    return img

# ---------------------------------------------------------------- 部品
def title(d):
    d.rounded_rectangle((70, 150, W - 70, 330), 30, fill=PANEL, outline=ACC + (170,), width=4)
    draw_runs(d, 175, TITLE, 64, stroke=6)
    draw_center(d, 266, "キミはどっちだと思う？", font(F_BOLD, 38), DIM, stroke=4)

def choice_cards(d, t, reveal):
    """reveal: 0=未発表, >0 正解発表の進行度"""
    boxes = [(100, 520, 520, 860), (560, 520, 980, 860)]
    for k, ((big, small), (x0, y0, x1, y1)) in enumerate(zip(CHOICES, boxes)):
        a = ease((t - 0.15 * k) / 0.3) if reveal == 0 else 1.0
        oy = int((1 - a) * 50)
        win = reveal > 0 and k == ANSWER
        lose = reveal > 0 and k != ANSWER
        fill = (14, 20, 26, 215) if not lose else (14, 20, 26, 150)
        out = ACC + (255,) if win else CREAM + (110,)
        d.rounded_rectangle((x0, y0 + oy, x1, y1 + oy), 34, fill=fill, outline=out, width=8 if win else 4)
        cx = (x0 + x1) // 2
        col_big = ACC if win else (DIM if lose else CREAM)
        f = font(F_BLACK, 130)
        d.text((cx - text_w(big, f) // 2, y0 + 50 + oy), big, font=f, fill=col_big, stroke_width=8, stroke_fill=INK)
        fs = font(F_BOLD, 44)
        d.text((cx - text_w(small, fs) // 2, y0 + 240 + oy), small, font=fs, fill=DIM if lose else CREAM,
               stroke_width=4, stroke_fill=INK)
    draw_center(d, 450, "A", font(F_BLACK, 56), CREAM, x=290, stroke=6)
    draw_center(d, 450, "B", font(F_BLACK, 56), CREAM, x=752, stroke=6)

def qmark(d, t):
    s = 1.0 + 0.08 * math.sin(t * 7)
    f = font(F_BLACK, int(150 * s))
    draw_center(d, 900, "?", f, ACC, stroke=10)

def seikai(L, t):
    b = ease(t / 0.25)
    if b <= 0:
        return
    tmp = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.ellipse((20, 20, 340, 340), outline=RED + (255,), width=22)
    f = font(F_BLACK, 84)
    td.text((180 - text_w("正解", f) // 2, 120), "正解", font=f, fill=RED, stroke_width=6, stroke_fill=INK)
    sc = 1.6 - 0.6 * b
    sz = int(360 * sc)
    tmp = tmp.resize((sz, sz), Image.LANCZOS).rotate(-12, resample=Image.BICUBIC)
    tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * b)))
    L.alpha_composite(tmp, (770 - sz // 2, 1010 - sz // 2))

def hbar(d, x, y, w, h, p, col, label, val):
    d.rounded_rectangle((x, y, x + w, y + h), 20, fill=(40, 48, 52))
    if p > 0:
        d.rounded_rectangle((x, y, x + max(40, int(w * p)), y + h), 20, fill=col)
    d.text((x, y - 70), label, font=font(F_BLACK, 50), fill=CREAM, stroke_width=6, stroke_fill=INK)
    d.text((x + 24, y + 4), val, font=font(F_BLACK, 84), fill=INK)

def save_card(d, t, title_t, rows, plane_t):
    d.rounded_rectangle((80, 400, W - 80, 1060), 30, fill=(248, 244, 232, 245), outline=ACC + (255,), width=4)
    d.rounded_rectangle((110, 425, 340, 485), 18, fill=ACC)
    draw_center(d, 428, "保存用", font(F_BLACK, 44), INK, stroke=0, x=160)
    draw_center(d, 510, title_t, font(F_BLACK, 62), INK, stroke=0)
    for k, (runs, size) in enumerate(rows):
        y = 640 + k * 130
        f = font(F_BLACK, size)
        total = sum(text_w(s, f) for s, _ in runs)
        x = (W - total) // 2
        for s, c in runs:
            d.text((x, y), s, font=f, fill=c)
            x += text_w(s, f)
    cx, cy = 200, 1150
    s = 0.55 + 0.03 * math.sin(t * 6)
    pts = [(-110, 40), (120, -70), (10, 90), (-20, 40)]
    d.polygon([(cx + int(x * s), cy + int(y * s)) for x, y in pts], fill=ACC, outline=INK, width=4)
    draw_center(d, 1110, plane_t, font(F_BLACK, 52), ACC, stroke=6, x=290)

DARK_ACC = (176, 120, 0) if THEME == "a" else (196, 100, 20)

# ---------------------------------------------------------------- シーン
def scene_a(L, d, i, t, dur):
    a = ease(t / 0.3); oy = int((1 - a) * 40)
    if i == 1:
        choice_cards(d, t, 0); qmark(d, t)
    elif i == 2:
        choice_cards(d, t, 1); seikai(L, t - 0.1)
    elif i == 3:
        draw_center(d, 440, "覚えていた割合", font(F_BLACK, 70), CREAM, stroke=6)
        p = ease((t - 0.3) / 1.2)
        q = ease((t - 1.6) / 1.2)
        hbar(d, 110, 640, 860, 110, 0.65 * p, DIM, "黙読", f"{int(round(65 * p))}%")
        hbar(d, 110, 880, 860, 110, 0.77 * q, ACC, "音読", f"{int(round(77 * q))}%")
        draw_center(d, 1060, "Forrin & MacLeod (2018)", font(F_BOLD, 36), DIM, stroke=4)
    elif i == 4:
        for k, (ch, x) in enumerate([("口", 300), ("耳", 780)]):
            b = ease((t - 0.25 * k) / 0.3)
            r = int(150 * (0.6 + 0.4 * b))
            d.ellipse((x - r, 700 - r, x + r, 700 + r), fill=(14, 20, 26, 220), outline=ACC + (255,), width=8)
            f = font(F_BLACK, int(150 * (0.6 + 0.4 * b)))
            d.text((x - text_w(ch, f) // 2, 700 - int(f.size * 0.62)), ch, font=f, fill=CREAM, stroke_width=6, stroke_fill=INK)
        draw_center(d, 610, "＋", font(F_BLACK, 110), ACC, stroke=8)
        c = ease((t - 0.8) / 0.3)
        if c > 0:
            draw_center(d, 920, "両方で覚える", font(F_BLACK, 100), ACC, stroke=10)
    elif i == 5:
        draw_center(d, 500 + oy, "覚えたいなら", font(F_BLACK, 100), CREAM)
        draw_center(d, 660 + oy, "声に出す", font(F_BLACK, 160), ACC, stroke=14)
    elif i == 6:
        save_card(d, t, "Q. 覚えるのはどっち？",
                  [([("答え：", INK), ("音読", DARK_ACC)], 76),
                   ([("音読 77%  ＞  黙読 65%", INK)], 60),
                   ([("大事な所だけ、声に出す", INK)], 54)],
                  "友達に出題してみて")

def scene_b(L, d, i, t, dur):
    a = ease(t / 0.3); oy = int((1 - a) * 40)
    if i == 1:
        choice_cards(d, t, 0); qmark(d, t)
    elif i == 2:
        choice_cards(d, t, 1); seikai(L, t - 0.1)
    elif i == 3:
        draw_center(d, 430, "ロンドン大学の研究", font(F_BLACK, 64), CREAM, stroke=6)
        draw_center(d, 520, "習慣になるまでの日数", font(F_BOLD, 44), DIM, stroke=4)
        x0, x1, y = 120, 960, 820
        p = ease((t - 0.2) / 2.2)
        d.rounded_rectangle((x0, y - 14, x1, y + 14), 14, fill=(60, 56, 80))
        d.rounded_rectangle((x0, y - 14, x0 + int((x1 - x0) * p), y + 14), 14, fill=ACC)
        def mk(day, lab, col, up, show):
            if not show:
                return
            x = x0 + int((x1 - x0) * day / 254)
            d.ellipse((x - 24, y - 24, x + 24, y + 24), fill=col, outline=INK, width=5)
            f = font(F_BLACK, 66); fs = font(F_BOLD, 40)
            s = f"{day}日"
            tx = min(max(x - text_w(s, f) // 2, 80), 1000 - text_w(s, f))
            lx = min(max(x - text_w(lab, fs) // 2, 80), 1000 - text_w(lab, fs))
            if up:
                d.text((tx, y - 150), s, font=f, fill=col, stroke_width=6, stroke_fill=INK)
                d.text((lx, y - 210), lab, font=fs, fill=CREAM, stroke_width=4, stroke_fill=INK)
            else:
                d.text((tx, y + 50), s, font=f, fill=col, stroke_width=6, stroke_fill=INK)
                d.text((lx, y + 130), lab, font=fs, fill=CREAM, stroke_width=4, stroke_fill=INK)
        mk(18, "早い人", GREEN, False, p >= 18 / 254)
        mk(66, "まんなか", ACC, True, p >= 66 / 254)
        mk(254, "遅い人", RED, False, p >= 0.999)
        draw_center(d, 1040, "Lally et al. (2010)", font(F_BOLD, 36), DIM, stroke=4)
    elif i == 4:
        draw_center(d, 450, "1日休んでも", font(F_BLACK, 90), CREAM)
        for k in range(7):
            x = 110 + k * 124
            y = 640
            d.rounded_rectangle((x, y, x + 108, y + 108), 16, fill=(14, 20, 26, 220), outline=CREAM + (120,), width=3)
            b = ease((t - 0.12 * k) / 0.2)
            if b > 0:
                if k == 3:
                    d.line((x + 26, y + 26, x + 82, y + 82), fill=RED, width=12)
                    d.line((x + 82, y + 26, x + 26, y + 82), fill=RED, width=12)
                else:
                    d.line((x + 22, y + 58, x + 46, y + 82), fill=GREEN, width=12)
                    d.line((x + 46, y + 82, x + 88, y + 28), fill=GREEN, width=12)
        c = ease((t - 1.0) / 0.3)
        if c > 0:
            draw_center(d, 860, "ほぼ影響なし", font(F_BLACK, 120), ACC, stroke=12)
    elif i == 5:
        draw_center(d, 500 + oy, "3週間で", font(F_BLACK, 110), CREAM)
        draw_center(d, 660 + oy, "あきらめない", font(F_BLACK, 140), ACC, stroke=14)
    elif i == 6:
        save_card(d, t, "Q. 習慣になるまで何日？",
                  [([("答え：", INK), ("66日", DARK_ACC), ("（まんなか）", INK)], 64),
                   ([("早い人18日〜遅い人254日", INK)], 54),
                   ([("1日休んでも、続ければOK", INK)], 54)],
                  "友達に出題してみて")

def scene_layer(i, t, dur):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    title(d)
    (scene_a if THEME == "a" else scene_b)(L, d, i, t, dur)
    if i != 6:
        sub = LINES_SUB[i - 1]
        fs = font(F_BOLD, 44)
        lines = sub.split("\n")
        y0 = 1240 - (len(lines) - 1) * 30
        for k, ln in enumerate(lines):
            draw_center(d, y0 + k * 60, ln, fs, CREAM, stroke=6)
    return L

# ---------------------------------------------------------------- 音声→口パク
def load_rms(path):
    with wave.open(str(path)) as w:
        sr = w.getframerate(); n = w.getnframes()
        data = array.array("h", w.readframes(n))
    hop = sr // FPS
    out = []
    for k in range(0, n, hop):
        seg = data[k:k + hop]
        if not seg:
            break
        out.append(math.sqrt(sum(v * v for v in seg) / len(seg)))
    return out, sr

BG = None
OWLS = {}

def compose(i, f, nframes, rms):
    t = f / FPS
    img = BG.copy().convert("RGBA")
    talk = f < len(rms) and rms[f] > 900
    blink = (f % 110) in (0, 1, 2)
    owl = OWLS[(talk and (f // 3) % 2 == 0, blink)]
    bob = int(8 * math.sin((f + i * 17) / 9))
    img.alpha_composite(owl, (W // 2 - owl.width // 2, 1350 + bob))
    img.alpha_composite(scene_layer(i, t, nframes / FPS))
    return img.convert("RGB")

def setup():
    global BG
    BG = bg_a() if THEME == "a" else bg_b()
    BG.save(ROOT / "bg.png")
    imgs = {}
    for n in ("owl_normal", "owl_open", "owl_blink"):
        o = Image.open(ROOT / f"{n}_hd.png")
        o = o.crop(o.getbbox())
        h = 475
        imgs[n] = o.resize((int(o.width * h / o.height), h), Image.LANCZOS)
    OWLS[(False, False)] = imgs["owl_normal"]
    OWLS[(True, False)] = imgs["owl_open"]
    OWLS[(False, True)] = imgs["owl_blink"]
    OWLS[(True, True)] = imgs["owl_blink"]

def frames_for(i):
    durs = json.load(open(AUD / "durs.json"))
    d = durs[i - 1] + {1: 0.8, 6: 1.0}.get(i, 0.0)
    return int(round(d * FPS))

def render_scene(i):
    n = frames_for(i)
    rms, _ = load_rms(AUD / f"{i:02d}.wav")
    tmp = OUT / f"s{i:02d}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-r", str(FPS), str(tmp)], stdin=subprocess.PIPE)
    for f in range(n):
        p.stdin.write(compose(i, f, n, rms).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        tmp.rename(OUT / f"s{i:02d}.mp4")
    return n

def build_audio(counts):
    out = array.array("h"); sr = None
    for i, n in enumerate(counts, 1):
        with wave.open(str(AUD / f"{i:02d}.wav")) as w:
            sr = w.getframerate()
            data = array.array("h", w.readframes(w.getnframes()))
        need = int(round(n / FPS * sr))
        data = data[:need]
        data.extend([0] * (need - len(data)))
        out.extend(data)
    with wave.open(str(ROOT / "voice.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(out.tobytes())

if __name__ == "__main__":
    mode = sys.argv[2]
    setup()
    if mode == "preview":
        picks = [(1, 1.5), (2, 1.2), (3, 4.5), (4, 2.0), (5, 1.5), (6, 2.0)]
        for i, t in picks:
            n = frames_for(i)
            rms, _ = load_rms(AUD / f"{i:02d}.wav")
            compose(i, min(int(t * FPS), n - 1), n, rms).save(ROOT / f"preview_{i:02d}.png")
    else:
        counts = []
        for i in range(1, NSCENE + 1):
            counts.append(render_scene(i))
            print("scene", i, counts[-1], flush=True)
        build_audio(counts)
        lst = ROOT / "list.txt"
        lst.write_text("".join(f"file '{OUT}/s{i:02d}.mp4'\n" for i in range(1, NSCENE + 1)))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", str(ROOT / "video_only.mp4")], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ROOT / "video_only.mp4"), "-i", str(ROOT / "voice.wav"),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                        str(ROOT / f"{OUTNAME}.tmp.mp4")], check=True)
        (ROOT / f"{OUTNAME}.tmp.mp4").rename(ROOT / f"{OUTNAME}.mp4")
        print("done")

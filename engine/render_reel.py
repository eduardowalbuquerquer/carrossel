"""Gera o Reels de chamada (9:16, 1080x1920, MP4 H.264 + áudio) a partir do bloco "reel" do spec.

Uso: python render_reel.py posts/AAAA-MM-DD/spec.json
Saída: reel.mp4 e reel_capa.jpg na pasta do spec.

Cada frame do spec vira uma "cena" com texto animado. O tempo é controlado por JS (determinístico),
cada quadro é capturado com Playwright e montado pelo ffmpeg a 30 fps.
"""
import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from brand import DBG, FONTS_LINK, HANDLE, LOGO_URI, P, PL, data_uri

W, H, SCALE, FPS = 360, 640, 3, 30
SCENE = 2.3   # segundos por cena
LAST = 2.6    # cena final (CTA) um pouco mais longa
CHROMIUM = Path("/opt/pw-browsers/chromium")


def build_html(reel, base):
    frames = reel["frames"]
    bg = ""
    if reel.get("image"):
        p = Path(reel["image"])
        bg = f'<img id="bgimg" src="{data_uri(p if p.is_absolute() else base / p)}" alt="">'
    scenes = []
    for k, f in enumerate(frames):
        last = k == len(frames) - 1
        cta = f'<div class="pill sans">{f["cta"]}</div>' if f.get("cta") else ""
        logo = f'<img class="logo" src="{LOGO_URI}" alt="">' if last else ""
        scenes.append(f'''<section class="scene" data-k="{k}">{logo}
          <span class="kicker sans">{f.get("kicker", "")}</span>
          <p class="txt serif">{f["text"]}</p>{cta}</section>''')
    segs = "".join('<div class="seg"><i></i></div>' for _ in frames)
    return f"""<!doctype html><html><head><meta charset="utf-8">{FONTS_LINK}<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:{W}px; height:{H}px; overflow:hidden; background:{DBG}; }}
.serif {{ font-family:'Playfair Display',Georgia,serif; }} .sans {{ font-family:'DM Sans',system-ui,sans-serif; }}
#bgimg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; transform-origin:50% 40%; }}
#shade {{ position:absolute; inset:0; background:{'rgba(23,20,17,0.62)' if bg else 'transparent'}; }}
#glow {{ position:absolute; left:50%; top:58%; width:520px; height:520px; margin:-260px 0 0 -260px; border-radius:50%;
  background:radial-gradient(circle, rgba(200,137,44,0.38) 0%, rgba(200,137,44,0.10) 40%, transparent 70%); }}
.ember {{ position:absolute; width:3px; height:3px; border-radius:50%; background:{PL}; box-shadow:0 0 6px {P}; }}
.bar {{ position:absolute; top:18px; left:16px; right:16px; display:flex; gap:4px; z-index:5; }}
.seg {{ flex:1; height:2.5px; background:rgba(255,255,255,0.18); border-radius:2px; overflow:hidden; }}
.seg i {{ display:block; height:100%; width:0; background:#fff; }}
.brand {{ position:absolute; top:34px; left:16px; display:flex; align-items:center; gap:8px; z-index:5; }}
.brand img {{ width:26px; height:26px; border-radius:50%; }}
.brand span {{ color:rgba(255,255,255,0.85); font-size:11px; font-weight:600; letter-spacing:.4px; }}
.scene {{ position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 30px; opacity:0; }}
.kicker {{ color:{PL}; font-size:11px; font-weight:700; letter-spacing:2.5px; margin-bottom:16px; text-transform:uppercase; }}
.txt {{ color:#fff; font-size:38px; font-weight:600; line-height:1.12; letter-spacing:-0.5px; text-wrap:balance; }}
.txt em {{ color:{PL}; font-style:italic; }}
.logo {{ width:74px; height:74px; border-radius:50%; margin-bottom:22px; box-shadow:0 8px 30px rgba(200,137,44,0.35); }}
.pill {{ align-self:flex-start; margin-top:26px; padding:12px 22px; border-radius:26px; background:{P}; color:{DBG}; font-size:14px; font-weight:700; }}
</style></head><body>
{bg}<div id="shade"></div><div id="glow"></div><div id="embers"></div>
<div class="bar">{segs}</div>
<div class="brand"><img src="{LOGO_URI}" alt=""><span class="sans">@{HANDLE}</span></div>
{''.join(scenes)}
<script>
const N = {len(frames)}, S = {SCENE}, L = {LAST};
const starts = [...Array(N).keys()].map(k => k * S);
const TOTAL = (N - 1) * S + L;
// brasas determinísticas
const em = document.getElementById('embers'); const parts = [];
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
for (let i = 0; i < 26; i++) {{ const d = document.createElement('div'); d.className = 'ember'; em.appendChild(d);
  parts.push({{el: d, x: rnd() * {W}, sp: 18 + rnd() * 40, ph: rnd() * 30, sw: 6 + rnd() * 14, sz: 1 + rnd() * 2.5}}); }}
const ease = t => 1 - Math.pow(1 - Math.min(Math.max(t, 0), 1), 3);
function setTime(t) {{
  const img = document.getElementById('bgimg'); if (img) img.style.transform = 'scale(' + (1.04 + 0.08 * t / TOTAL) + ')';
  document.getElementById('glow').style.opacity = 0.75 + 0.25 * Math.sin(t * 2.1);
  parts.forEach(p => {{ const y = {H} + 20 - ((t + p.ph) * p.sp) % ({H} + 40);
    p.el.style.transform = 'translate(' + (p.x + Math.sin((t + p.ph) * 1.3) * p.sw) + 'px,' + y + 'px) scale(' + p.sz + ')';
    p.el.style.opacity = Math.min(1, y / 200) * 0.8; }});
  document.querySelectorAll('.seg i').forEach((b, k) => {{ const dur = k === N - 1 ? L : S;
    b.style.width = (Math.min(Math.max((t - starts[k]) / dur, 0), 1) * 100) + '%'; }});
  document.querySelectorAll('.scene').forEach((sc, k) => {{
    const dur = k === N - 1 ? L : S, lt = t - starts[k];
    let o = 0; if (lt >= 0 && lt < dur) {{ o = ease(lt / 0.35); if (k < N - 1) o = Math.min(o, 1 - ease((lt - (dur - 0.3)) / 0.3)); }}
    sc.style.opacity = o;
    const kk = sc.querySelector('.kicker'), tx = sc.querySelector('.txt'), pl = sc.querySelector('.pill'), lg = sc.querySelector('.logo');
    kk.style.transform = 'translateY(' + (12 * (1 - ease(lt / 0.4))) + 'px)';
    tx.style.transform = 'translateY(' + (24 * (1 - ease((lt - 0.08) / 0.5))) + 'px)';
    tx.style.opacity = ease((lt - 0.08) / 0.45);
    if (pl) {{ pl.style.opacity = ease((lt - 0.7) / 0.4); pl.style.transform = 'scale(' + (0.9 + 0.1 * ease((lt - 0.7) / 0.4)) + ')'; }}
    if (lg) lg.style.transform = 'scale(' + (0.8 + 0.2 * ease(lt / 0.5)) + ')';
  }});
}}
window.TOTAL = TOTAL; window.setTime = setTime; setTime(0);
</script></body></html>"""


def build_audio(path, total, n):
    """Trilha sintetizada: grave contínuo + 'golpe de bigorna' em cada troca de cena (WAV -> AAC)."""
    import math
    import struct
    import wave
    sr = 44100
    hits = [k * SCENE for k in range(n)]
    wav = path.with_suffix(".wav")
    frames = bytearray()
    for i in range(int(total * sr)):
        t = i / sr
        v = 0.16 * math.sin(2 * math.pi * 55 * t) + 0.10 * math.sin(2 * math.pi * 82.4 * t) * (0.6 + 0.4 * math.sin(2 * math.pi * 0.25 * t))
        for h in hits:
            if t >= h:
                d = t - h
                if d < 1.2:
                    v += math.exp(-d * 9) * (0.35 * math.sin(2 * math.pi * 1180 * t) + 0.22 * math.sin(2 * math.pi * 1870 * t) + 0.25 * math.sin(2 * math.pi * 95 * t))
        v *= min(1, t / 0.6) * min(1, (total - t) / 0.8)
        frames += struct.pack("<h", int(max(-1, min(1, v * 0.9)) * 32767))
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(frames))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", "lowpass=f=4000",
                    "-c:a", "aac", "-b:a", "160k", "-ac", "2", str(path)], check=True)


async def capture(html_path, frames_dir):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        kw = {"executable_path": str(CHROMIUM)} if CHROMIUM.is_file() else {}
        browser = await p.chromium.launch(**kw)
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        await page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(800)
        total = await page.evaluate("window.TOTAL")
        n = int(total * FPS)
        for i in range(n):
            await page.evaluate("t => window.setTime(t)", i / FPS)
            await page.screenshot(path=str(frames_dir / f"f{i:05d}.jpg"), type="jpeg", quality=90)
        await browser.close()
        return total


def main(spec_path):
    spec_path = Path(spec_path)
    base = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    reel = spec["reel"]
    html = base / "reel.html"
    html.write_text(build_html(reel, base), encoding="utf-8")
    tmp = Path(tempfile.mkdtemp(prefix="reel_"))
    try:
        total = asyncio.run(capture(html, tmp))
        audio = tmp / "a.m4a"
        build_audio(audio, total, len(reel["frames"]))
        out = base / "reel.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(tmp / "f%05d.jpg"),
                        "-i", str(audio), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
                        "-preset", "medium", "-crf", "20", "-r", str(FPS), "-c:a", "copy", "-shortest",
                        "-movflags", "+faststart", str(out)], check=True)
        # capa = início da última cena estabilizada
        cover_idx = min(int(((len(reel["frames"]) - 1) * SCENE + 1.4) * FPS), int(total * FPS) - 1)
        shutil.copy(tmp / f"f{cover_idx:05d}.jpg", base / "reel_capa.jpg")
        print(json.dumps({"reel": str(out), "seconds": round(total, 2)}))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1])

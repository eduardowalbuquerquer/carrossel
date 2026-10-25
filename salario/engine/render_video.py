"""Gera o vídeo vertical (1080x1920, H.264 + AAC) do Salário Organizado a partir de um spec.json.

Uso: python3 render_video.py ../posts/<pasta>/spec.json [--so ig,tt,yt]
Saída na pasta do spec: video_ig.mp4, video_tt.mp4, video_yt.mp4 (muda só a chamada final) e capa.jpg.

Cenas (spec["scenes"]), cada uma com "say" (narração) e, opcional, "secs" (duração mínima):
  hook    tag, title (aceita <em>), sub
  list    cap, renda, items [[nome, valor], ...], hot (nome destacado), cap_hot
  number  label, value, text, tone (red|green|warm)
  compare label, value, text, from, to, after
  fact    value, text, source, tone
  steps   title, items [..]
  cta     (texto vem de brand.CTA conforme a plataforma)
Tempo controlado por JS (determinístico); cada quadro é capturado com Playwright e montado pelo ffmpeg a 30 fps.
A narração define a duração de cada cena; sem voz configurada, a duração é estimada pelo tamanho do texto.
"""
import hashlib, html, json, math, re, shutil, struct, subprocess, sys, tempfile, wave
from pathlib import Path

import brand as B
from tts import duration, speak

W, H, FPS = 1080, 1920, 30
CHROMIUM = Path("/opt/pw-browsers/chromium")
ROOT = Path(__file__).resolve().parents[1]


def brl(n):
    return "R$ " + f"{abs(int(round(n))):,}".replace(",", ".")


def fit(v, base, width=900):
    """Encolhe números longos para caberem na largura (fonte mono: ~0,62 em por caractere)."""
    n = len(html.unescape(re.sub("<[^>]+>", "", str(v))))
    return f' style="font-size:{min(base, int(width / (0.62 * n)))}px"' if n * 0.62 * base > width else ""


def scene_html(s, k, cta):
    t = s["type"]
    if t == "hook":
        return f'''<section class="scene dark" data-k="{k}"><div class="tag">{s.get("tag","")}</div>
<h1>{s["title"]}</h1><p class="sub">{s.get("sub","")}</p></section>'''
    if t == "list":
        rows = [f'<div class="it renda" data-i="0"><span>{s.get("renda_label","Salário")}</span><b>{brl(s["renda"])}</b></div>']
        for i, (n, v) in enumerate(s["items"], 1):
            hot = " hotable" if n == s.get("hot") else ""
            rows.append(f'<div class="it{hot}" data-i="{i}"><span>{html.escape(n)}</span><b>{brl(v)}</b></div>')
        return f'''<section class="scene" data-k="{k}"><div class="cap" data-a="{html.escape(s.get("cap",""))}" data-b="{html.escape(s.get("cap_hot",""))}"></div>
<div class="list">{"".join(rows)}</div><div class="bar"><span class="barl">Sobra</span><b class="barv"></b></div></section>'''
    if t in ("number", "fact"):
        src = f'<div class="src">Fonte: {s["source"]}</div>' if s.get("source") else ""
        return f'''<section class="scene" data-k="{k}"><div class="lbl {s.get("tone","red")}">{s.get("label","")}</div>
<div class="big {s.get("tone","red")}"{fit(s["value"], 190)}>{s["value"]}</div><p class="txt">{s.get("text","")}</p>{src}</section>'''
    if t == "compare":
        return f'''<section class="scene" data-k="{k}"><div class="lbl warm">{s["label"]}</div><div class="big warm"{fit(s["value"], 190)}>{s["value"]}</div>
<p class="txt step1">{s.get("text","")}</p><div class="row step2"><span class="from"{fit(s["from"], 120, 360)}>{s["from"]}</span><span class="to"{fit(s["to"], 150, 500)}>{s["to"]}</span></div>
<p class="txt step3">{s.get("after","")}</p></section>'''
    if t == "steps":
        li = "".join(f'<li class="st" data-i="{i}"><i>{i+1}</i><span>{x}</span></li>' for i, x in enumerate(s["items"]))
        return f'<section class="scene" data-k="{k}"><h2>{s["title"]}</h2><ol>{li}</ol></section>'
    if t == "cta":
        return f'''<section class="scene cta" data-k="{k}"><h2>{s.get("title","Quer fazer a sua conta?")}</h2>
<div class="kw">{cta["kw"]}</div><p class="txt">{cta["line"]}</p></section>'''
    raise SystemExit(f"tipo de cena desconhecido: {t}")


def chunks(text, n=4):
    w = text.split()
    return [" ".join(w[i:i + n]) for i in range(0, len(w), n)]


def build_html(spec, timeline, cta):
    scenes = "".join(scene_html(s, k, cta) for k, s in enumerate(spec["scenes"]))
    logo = B.LOGO_SVG.format(fg="#fff")
    return f"""<!doctype html><html><head><meta charset="utf-8">{B.FONTS_LINK}<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{B.BG};font-family:'Source Sans 3',sans-serif;color:{B.INK};position:relative}}
.scene{{position:absolute;inset:0;padding:220px 90px 580px;display:flex;flex-direction:column;justify-content:center;opacity:0}}
.dark{{background:{B.DEEP};color:#fff}} .cta{{background:{B.GREEN};color:#fff}}
.tag{{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:30px;letter-spacing:.14em;text-transform:uppercase;color:{B.MINT2};margin-bottom:36px}}
h1{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:110px;line-height:1.02;letter-spacing:-.02em}}
h1 em,h2 em{{font-style:normal;color:{B.YELLOW}}} .scene:not(.dark):not(.cta) h2 em{{color:{B.GREEN}}}
.sub{{font-size:52px;margin-top:40px;color:#cfe8df;font-weight:600}}
h2{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:84px;line-height:1.05;letter-spacing:-.015em}}
.cap{{position:absolute;left:90px;right:90px;top:210px;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:62px;line-height:1.08}}
.list{{background:#fff;border:2px solid {B.LINE};border-radius:40px;padding:24px 44px;margin-top:110px}}
.it{{display:flex;justify-content:space-between;align-items:center;padding:16px 0;border-top:2px solid {B.LINE};font-size:44px;font-weight:600;opacity:.2}}
.it:first-child{{border-top:0}} .it b{{font-family:'JetBrains Mono',monospace}} .it.on{{opacity:1}} .it.renda{{color:{B.GREEN}}}
.it.hot{{background:{B.WARM_SOFT};color:{B.WARM};margin:0 -44px;padding:20px 44px;border-radius:20px}}
.bar{{margin-top:32px;border-radius:32px;padding:30px 44px;display:flex;justify-content:space-between;align-items:center;background:{B.MINT};color:{B.DEEP}}}
.bar.neg{{background:{B.RED_SOFT};color:{B.RED}}} .bar span{{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:34px;letter-spacing:.12em;text-transform:uppercase}}
.bar b{{font-family:'JetBrains Mono',monospace;font-size:72px}}
.lbl{{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:38px;letter-spacing:.14em;text-transform:uppercase}}
.big{{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:190px;line-height:1.05;letter-spacing:-.04em;margin-top:10px}}
.red{{color:{B.RED}}} .green{{color:{B.GREEN}}} .warm{{color:{B.WARM}}}
.txt{{font-size:56px;font-weight:600;margin-top:36px;line-height:1.2}}
.src{{margin-top:40px;font-family:'JetBrains Mono',monospace;font-size:28px;color:{B.MUTED}}}
.row{{display:flex;align-items:baseline;gap:34px;margin-top:26px;font-family:'JetBrains Mono',monospace;font-weight:700}}
.from{{font-size:120px;color:{B.RED};text-decoration:line-through;text-decoration-thickness:10px;opacity:.5}} .to{{font-size:150px;color:{B.GREEN}}}
ol{{list-style:none;margin-top:50px;display:flex;flex-direction:column;gap:30px}}
.st{{display:flex;gap:30px;align-items:flex-start;font-size:54px;font-weight:600;line-height:1.15;opacity:0}}
.st i{{flex:none;width:76px;height:76px;border-radius:50%;background:{B.GREEN};color:#fff;font-style:normal;font-family:'JetBrains Mono',monospace;font-size:38px;display:grid;place-items:center}}
.kw{{display:inline-block;align-self:flex-start;background:{B.YELLOW};color:{B.INK};font-family:'JetBrains Mono',monospace;font-weight:700;font-size:104px;padding:16px 40px;border-radius:28px;margin:40px 0 10px}}
.cta .txt{{color:#e1f2ec}} .cta .txt b{{color:#fff}}
.brand{{position:absolute;left:90px;top:96px;display:flex;align-items:center;gap:22px;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:40px;z-index:5}}
.logo{{width:64px;height:64px;border-radius:16px;display:grid;place-items:center}} .logo svg{{width:40px;height:40px}}
.prog{{position:absolute;left:90px;right:90px;top:60px;height:8px;border-radius:4px;background:rgba(127,127,127,.25);z-index:5;overflow:hidden}} .prog i{{display:block;height:100%;width:0}}
.subt{{position:absolute;left:70px;right:70px;top:1395px;text-align:center;z-index:6}}
.subt span{{display:inline;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:60px;line-height:1.3;padding:6px 18px;border-radius:14px;background:rgba(20,35,31,.88);color:#fff;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
.subt span b{{color:{B.YELLOW};font-weight:800}}
</style></head><body>
<div class="prog"><i id="pg"></i></div>
<div class="brand" id="brand"><span class="logo" id="lgbox">{logo}</span><span>{B.BRAND}</span></div>
{scenes}
<div class="subt"><span id="sub"></span></div>
<script>
const TL={json.dumps(timeline)};
const ease=x=>x<0?0:x>1?1:1-Math.pow(1-x,3);
const brl=n=>(n<0?'−':'')+'R$ '+Math.abs(Math.round(n)).toLocaleString('pt-BR');
window.TOTAL=TL.total;
window.render=t=>{{
  const secs=[...document.querySelectorAll('.scene')];
  let cur=0; TL.scenes.forEach((s,k)=>{{if(t>=s.start)cur=k}});
  secs.forEach((el,k)=>{{const s=TL.scenes[k];const a=s.start,b=s.start+s.dur;let o=0;
    if(t>=a&&t<b+0.0001){{o=k===0?1:Math.min(1,(t-a)/0.22);}}
    if(k===TL.scenes.length-1&&t>=a)o=Math.min(1,(t-a)/0.22);
    el.style.opacity=o; el.style.transform=`translateY(${{(1-ease((t-a)/0.35))*(k===0?0:40)}}px)`;}});
  const s=TL.scenes[cur], el=secs[cur], lt=t-s.start, dark=el.classList.contains('dark')||el.classList.contains('cta');
  const br=document.getElementById('brand'); br.style.color=dark?'#fff':'{B.INK}';
  document.getElementById('lgbox').style.background=dark?'rgba(255,255,255,.16)':'{B.DEEP}';
  document.getElementById('pg').style.width=(100*t/TL.total)+'%'; document.getElementById('pg').style.background=dark?'#fff':'{B.GREEN}';
  // lista: itens entram um a um, barra calcula sobra/falta
  if(el.querySelector('.list')){{const its=[...el.querySelectorAll('.it')];const step=s.step||0.9;let tot=0;const renda=s.renda||0;
    its.forEach((it,i)=>{{const on=lt>=0.3+i*step;it.classList.toggle('on',on);if(on&&i>0)tot+=s.vals[i-1];}});
    const sob=renda-tot,bar=el.querySelector('.bar');bar.classList.toggle('neg',sob<0);
    el.querySelector('.barl').textContent=sob<0?'Falta':'Sobra';el.querySelector('.barv').textContent=brl(sob);
    const hotOn=lt>=0.3+its.length*step+0.4;el.querySelectorAll('.hotable').forEach(h=>h.classList.toggle('hot',hotOn));
    const cap=el.querySelector('.cap');cap.textContent=hotOn&&cap.dataset.b?cap.dataset.b:cap.dataset.a;}}
  el.querySelectorAll('.step1,.step2,.step3').forEach(x=>{{const n=+x.className.match(/step(\\d)/)[1];x.style.opacity=lt>=s.dur*(n*0.22)?1:0;}});
  el.querySelectorAll('.st').forEach((x,i)=>{{const n=el.querySelectorAll('.st').length;x.style.opacity=lt>=0.4+i*(s.dur-0.8)/n?1:0;}});
  // legenda sincronizada com a narração
  let txt=''; (s.subs||[]).forEach(c=>{{if(lt>=c.a&&lt<c.b)txt=c.t;}});
  document.getElementById('sub').innerHTML=txt; document.getElementById('sub').style.display=txt?'inline':'none';
}};
render(0);
</script></body></html>"""


def build_timeline(spec, variant, voice_dir):
    """Narração por cena -> duração das cenas, legendas e lista de áudios com o início de cada um."""
    scenes, audios, t = [], [], 0.0
    for k, s in enumerate(spec["scenes"]):
        say = B.CTA[variant]["say"] if s["type"] == "cta" and not s.get("say") else s.get("say", "")
        if s["type"] == "cta" and s.get("say"):
            say = s["say"] + " " + B.CTA[variant]["say"]
        wav = speak(say) if say else None
        lead = 0.0 if k == 0 else 0.25
        if wav:
            spoken = duration(wav)
            audios.append((t + lead, wav))
        else:
            spoken = len(say) / 15.0
        dur = max(s.get("secs", 0), lead + spoken + 0.45)
        if s["type"] == "list":
            dur = max(dur, 0.3 + (len(s["items"]) + 1) * s.get("step", 0.9) + 1.6)
        subs, cs = [], chunks(say, 4)
        tot = sum(len(c) for c in cs) or 1
        a = lead
        for c in cs:
            d = spoken * len(c) / tot
            subs.append({"a": round(a, 3), "b": round(a + d, 3), "t": html.escape(c)})
            a += d
        sc = {"start": round(t, 3), "dur": round(dur, 3), "subs": subs if spec.get("legendas", True) else []}
        if s["type"] == "list":
            sc.update(renda=s["renda"], vals=[v for _, v in s["items"]], step=s.get("step", 0.9))
        scenes.append(sc)
        t += dur
    return {"scenes": scenes, "total": round(t + 0.6, 3)}, audios


def synth_bed(path, total, seed):
    """Trilha de fundo própria (sem direitos autorais): pad suave em progressão I-V-vi-IV + batida leve."""
    sr = 44100
    roots = [261.63, 196.0, 220.0, 174.61]  # C G Am F
    rnd = int(hashlib.sha1(seed.encode()).hexdigest(), 16)
    bpm = 92 + rnd % 12
    beat = 60 / bpm
    out = bytearray()
    for i in range(int(total * sr)):
        t = i / sr
        r = roots[int(t / (beat * 8)) % 4]
        third = r * (1.1892 if r == 220.0 else 1.2599)
        v = sum(0.05 * math.sin(2 * math.pi * f * t) for f in (r / 2, r, third, r * 1.4983))
        v *= 0.75 + 0.25 * math.sin(2 * math.pi * t / (beat * 2))
        bt = t % beat
        v += 0.22 * math.exp(-bt * 28) * math.sin(2 * math.pi * 55 * bt * (1 + 2 * math.exp(-bt * 40)))
        hb = (t + beat / 2) % beat
        v += 0.03 * math.exp(-hb * 90) * math.sin(2 * math.pi * 7000 * t + 3 * math.sin(2 * math.pi * 3100 * t))
        v *= min(1, t / 1.0) * min(1, (total - t) / 1.2)
        out += struct.pack("<h", int(max(-1, min(1, v)) * 32767))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(out))


def pick_music(seed):
    tracks = sorted(p for p in (ROOT / "assets" / "music").glob("*") if p.suffix.lower() in (".mp3", ".wav", ".m4a"))
    return tracks[int(hashlib.sha1(seed.encode()).hexdigest(), 16) % len(tracks)] if tracks else None


def build_audio(out, timeline, audios, seed, tmp):
    total = timeline["total"]
    music = pick_music(seed)
    if not music:
        music = tmp / "bed.wav"; synth_bed(music, total, seed)
    inputs = ["-stream_loop", "-1", "-i", str(music)]
    for _, wav in audios:
        inputs += ["-i", str(wav)]
    parts, labels = [], []
    for j, (start, _) in enumerate(audios, 1):
        ms = int(start * 1000)
        parts.append(f"[{j}:a]aformat=sample_rates=44100:channel_layouts=mono,adelay={ms}|{ms},apad[v{j}]")
        labels.append(f"[v{j}]")
    fade = f"afade=t=out:st={max(0, total - 1.2)}:d=1.2"
    if audios:
        parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,atrim=0:{total},"
                     f"highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,asplit=2[voz][sc]")
        parts.append(f"[0:a]aformat=sample_rates=44100:channel_layouts=mono,atrim=0:{total},volume=0.32[m0]")
        parts.append("[m0][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[mus]")
        parts.append(f"[voz][mus]amix=inputs=2:normalize=0,{fade},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    else:
        parts.append(f"[0:a]aformat=sample_rates=44100:channel_layouts=mono,atrim=0:{total},volume=0.6,{fade},loudnorm=I=-16:TP=-1.5[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts),
                    "-map", "[out]", "-ac", "2", "-ar", "44100", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)


def capture(html_path, frames_dir, total):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        kw = {"executable_path": str(CHROMIUM)} if CHROMIUM.is_file() else {}
        b = p.chromium.launch(**kw)
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(html_path.as_uri())
        pg.evaluate("""async()=>{await document.fonts.load('800 100px "Bricolage Grotesque"');
          await document.fonts.load('700 50px "JetBrains Mono"');await document.fonts.load('600 50px "Source Sans 3"');await document.fonts.ready}""")
        for i in range(int(total * FPS)):
            pg.evaluate("t=>render(t)", i / FPS)
            pg.screenshot(path=str(frames_dir / f"{i:05d}.jpg"), type="jpeg", quality=92)
        b.close()


def render(spec_path, variants):
    spec_path = Path(spec_path).resolve()
    spec, folder = json.loads(spec_path.read_text()), spec_path.parent
    for v in variants:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            tl, audios = build_timeline(spec, v, tmp)
            page = tmp / "v.html"; page.write_text(build_html(spec, tl, B.CTA[v]))
            fr = tmp / "f"; fr.mkdir()
            capture(page, fr, tl["total"])
            aud = tmp / "a.m4a"; build_audio(aud, tl, audios, spec.get("id", folder.name), tmp)
            out = folder / f"video_{v}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(fr / "%05d.jpg"), "-i", str(aud),
                            "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
                            "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(out)], check=True)
            if v == variants[0]:
                shutil.copy(fr / f"{min(20, len(list(fr.iterdir())) - 1):05d}.jpg", folder / "capa.jpg")
            print(f"{out.name}: {tl['total']:.1f}s, narração {'sim' if audios else 'não'}")


if __name__ == "__main__":
    args = sys.argv[1:]
    vs = ["ig", "tt", "yt"]
    if "--so" in args:
        vs = args[args.index("--so") + 1].split(","); args = [a for a in args if a not in ("--so", ",".join(vs))]
    render(args[0], vs)

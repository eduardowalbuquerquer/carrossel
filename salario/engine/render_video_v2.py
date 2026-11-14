"""Motor de vídeo v2 do Salário Organizado (proposta de upgrade de qualidade, 14/11/2026).

Mesmo spec.json do motor v1 (render_video.py), com estas mudanças:
  1. Legenda palavra a palavra (2 a 3 palavras por vez, palavra falada em amarelo), grande e no centro da tela.
     Tempo de cada palavra: pausas reais da voz (ffmpeg silencedetect) + sílabas de cada palavra.
     Opcional por cena: "show" = texto da legenda com números em dígitos (mesmas frases do "say").
  2. Movimento o tempo todo: entrada com "soco" em cada cena, zoom lento, números que contam de 0 até o valor,
     tremida no número do gancho, cartões que entram no ritmo da fala.
  3. Efeitos sonoros próprios (gerados aqui, sem direitos autorais): whoosh na troca de cena, pop nos itens,
     tique na contagem e "plim" no resultado.
  4. Voz 10% mais rápida (atempo, sem mudar o tom) e cenas sem pausas mortas.
  5. Fundo escuro com grade de planilha (identidade), conteúdo centralizado e fora das áreas cobertas pelos botões.

Uso: python3 render_video_v2.py ../posts/<pasta>/spec.json [--so tt] [--saida video_v2]
"""
import html, json, re, subprocess, sys, tempfile, wave
from pathlib import Path

import numpy as np

import brand as B
from render_video import FPS, H, W, capture, fit, pick_music, synth_bed
from tts import duration, speak

SPEED = 1.15
CTA_SAY = {"tt": "Comenta PLANILHA. O link da grátis está na tela.", "ig": "Comenta PLANILHA que eu te mando a grátis no direct.", "yt": "A planilha grátis está no link do perfil."}
SR = 44100


# ---------- voz: velocidade e tempo de cada palavra ----------
def faster(wav, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-filter:a", f"atempo={SPEED}",
                    "-ar", str(SR), "-ac", "1", str(out)], check=True)
    return out


def pauses(wav):
    r = subprocess.run(["ffmpeg", "-i", str(wav), "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
                       capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [((a + b) / 2) for a, b in zip(st, en)]


def syl(w):
    w = w.lower()
    if re.search(r"\d", w):
        return 1.5 * len(re.sub(r"\D", "", w)) + (1 if "r$" in w or "%" in w else 0)
    return max(1, len(re.findall(r"[aeiouáéíóúâêôãõà]+", w)))


def phrases(text):
    parts = [p.strip() for p in re.split(r"(?<=[.,;:?!])\s+", text.strip()) if p.strip()]
    return parts or [text]


def align(wav, spoken, say, show):
    """Devolve [(palavra, início, fim, índice da frase)] em segundos, relativos ao começo da fala."""
    ph_say, ph_show = phrases(say), phrases(show)
    if len(ph_show) != len(ph_say):
        ph_show = [show]; ph_say = [say]
    w_say = [sum(syl(w) for w in p.split()) for p in ph_say]
    tot = sum(w_say)
    # fronteiras entre frases: proporção de sílabas, encostada na pausa real mais próxima (até 0,45 s)
    gaps = pauses(wav) if wav else []
    bounds, acc = [0.0], 0
    for x in w_say[:-1]:
        acc += x
        guess = spoken * acc / tot
        near = min(gaps, key=lambda g: abs(g - guess)) if gaps else None
        bounds.append(near if near is not None and abs(near - guess) < 0.45 and near > bounds[-1] else guess)
    bounds.append(spoken)
    out = []
    for i, p in enumerate(ph_show):
        a, b = bounds[i], bounds[i + 1]
        ws = p.split()
        ss = [syl(w) for w in ws]
        t, k = a, (b - a) / (sum(ss) or 1)
        for w, s in zip(ws, ss):
            out.append((w, round(t, 3), round(t + s * k, 3), i))
            t += s * k
    return out, bounds


def pages(words, n=3):
    """Agrupa as palavras em telas de até n palavras, sem misturar frases."""
    pg, cur = [], []
    for w in words:
        if cur and (len(cur) == n or cur[-1][3] != w[3] or re.search(r"[.?!]$", cur[-1][0])):
            pg.append(cur); cur = []
        cur.append(w)
    if cur:
        pg.append(cur)
    res = []
    for j, p in enumerate(pg):
        end = pg[j + 1][0][1] if j + 1 < len(pg) and pg[j + 1][0][1] - p[-1][2] < 0.6 else p[-1][2] + 0.15
        res.append({"a": p[0][1], "b": end, "w": [[html.escape(x[0]), x[1], x[2]] for x in p]})
    return res


# ---------- números que contam ----------
NUM = re.compile(r"\d[\d.]*(?:,\d+)?")


def countable(v):
    m = NUM.search(re.sub("<[^>]+>", "", str(v)))
    if not m:
        return None
    s = m.group(0)
    dec = len(s.split(",")[1]) if "," in s else 0
    n = float(s.replace(".", "").replace(",", "."))
    return {"n": n, "dec": dec, "pre": str(v)[:m.start()], "pos": str(v)[m.end():]}


# ---------- cenas ----------
def scene_html(s, k, cta):
    t = s["type"]
    if t == "hook":
        val = (f'<div class="hlbl">{s.get("value_label","")}</div><div class="hv {s.get("tone","red")}"{fit(s["value"], 250)}>{s["value"]}</div>'
               if s.get("value") else "")
        return f'<section class="scene hook" data-k="{k}"><div class="in">{val}<h1>{s["title"]}</h1></div></section>'
    if t in ("number", "fact"):
        src = f'<div class="src">Fonte: {s["source"]}</div>' if s.get("source") else ""
        return f'''<section class="scene" data-k="{k}"><div class="in"><div class="lbl {s.get("tone","red")}">{s.get("label","")}</div>
<div class="big cnt {s.get("tone","red")}"{fit(s["value"], 200)}>{s["value"]}</div><p class="txt">{s.get("text","")}</p>{src}</div></section>'''
    if t == "compare":
        return f'''<section class="scene" data-k="{k}"><div class="in"><div class="lbl warm">{s["label"]}</div>
<div class="row"><span class="from"{fit(s["from"], 120, 900)}>{s["from"]}<i class="strike"></i></span><span class="arrow">→</span><span class="to"{fit(s["to"], 180, 900)}>{s["to"]}</span></div>
<div class="pill"><b class="cnt">{s["value"]}</b> {s.get("text","").rstrip(":")}</div><p class="txt">{s.get("after","")}</p></div></section>'''
    if t == "steps":
        li = "".join(f'<li class="st" data-i="{i}"><i>{i+1}</i><span>{x}</span></li>' for i, x in enumerate(s["items"]))
        return f'<section class="scene" data-k="{k}"><div class="in"><h2>{s["title"]}</h2><ol>{li}</ol></div></section>'
    if t == "list":
        rows = "".join(f'<li class="st" data-i="{i}"><span>{html.escape(n)}</span><b>R$ {v:,}</b></li>'.replace(",", ".")
                       for i, (n, v) in enumerate(s["items"]))
        return f'<section class="scene" data-k="{k}"><div class="in"><h2>{s.get("cap","")}</h2><ol class="lst">{rows}</ol></div></section>'
    if t == "cta":
        return f'''<section class="scene cta" data-k="{k}"><div class="in"><h2>{s.get("title","Quer fazer a sua conta?")}</h2>
<div class="kw">{cta["kw"]}</div><p class="txt">{cta["line"]}</p><div class="down">↓</div></div></section>'''
    raise SystemExit(f"tipo de cena desconhecido: {t}")


def build_html(spec, tl, cta):
    scenes = "".join(scene_html(s, k, cta) for k, s in enumerate(spec["scenes"]))
    logo = B.LOGO_SVG.format(fg="#fff")
    BGD = "#0c1f1a"
    return f"""<!doctype html><html><head><meta charset="utf-8">{B.FONTS_LINK}<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{BGD};font-family:'Source Sans 3',sans-serif;color:#fff;position:relative}}
#bg{{position:absolute;inset:-60px;background:
  radial-gradient(900px 700px at var(--gx,30%) var(--gy,30%),rgba(15,122,92,.55),transparent 70%),
  radial-gradient(700px 600px at 85% 90%,rgba(255,224,138,.10),transparent 70%),{BGD}}}
#grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.045) 2px,transparent 2px);
  background-size:120px 120px;opacity:.9}}
#flash{{position:absolute;inset:0;background:#ff5a4a;opacity:0;z-index:4;pointer-events:none}}
.scene{{position:absolute;left:0;right:0;top:250px;height:900px;padding:0 84px;display:flex;flex-direction:column;justify-content:center;opacity:0;z-index:2}}
.scene .in{{transform-origin:50% 50%}}
.cta-bg{{position:absolute;inset:0;background:{B.GREEN};opacity:0;z-index:1}}
h1{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:92px;line-height:1.04;letter-spacing:-.015em}}
h1 em,h2 em{{font-style:normal;color:{B.YELLOW}}}
h2{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:92px;line-height:1.04;letter-spacing:-.015em}}
.hlbl,.lbl{{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:38px;letter-spacing:.12em;text-transform:uppercase;color:{B.MINT2}}}
.hv{{font-family:'JetBrains Mono',monospace;font-weight:800;font-size:250px;line-height:1;letter-spacing:-.05em;margin:10px 0 36px;
  text-shadow:0 18px 60px rgba(0,0,0,.45)}}
.red{{color:#ff7b6b}} .warm{{color:{B.YELLOW}}} .green{{color:#5fe0b4}}
.lbl.red{{color:#ff9d90}} .lbl.green{{color:#8fe8c8}} .lbl.warm{{color:{B.YELLOW}}}
.big{{font-family:'JetBrains Mono',monospace;font-weight:800;font-size:200px;line-height:1.02;letter-spacing:-.045em;margin-top:14px;text-shadow:0 18px 60px rgba(0,0,0,.45)}}
.txt{{font-size:62px;font-weight:700;margin-top:30px;line-height:1.18;color:#e6f3ee}} .txt b{{color:{B.YELLOW}}}
.src{{display:inline-block;margin-top:34px;font-family:'JetBrains Mono',monospace;font-size:30px;color:#a9c4ba;background:rgba(255,255,255,.08);padding:10px 18px;border-radius:12px}}
.row{{display:flex;flex-direction:column;align-items:flex-start;gap:6px;margin-top:30px;font-family:'JetBrains Mono',monospace;font-weight:800}}
.from{{position:relative;font-size:120px;color:#ff9d90;white-space:nowrap}} .strike{{position:absolute;left:-6px;top:52%;height:12px;width:0;background:#ff5a4a;border-radius:6px}}
.arrow{{display:none}} .to{{font-size:180px;color:#5fe0b4;white-space:nowrap;transform-origin:left center}}
.pill{{display:inline-block;align-self:flex-start;margin-top:44px;background:{B.YELLOW};color:{B.INK};font-size:58px;font-weight:700;padding:16px 34px;border-radius:24px}}
.pill b{{font-family:'JetBrains Mono',monospace}}
ol{{list-style:none;margin-top:44px;display:flex;flex-direction:column;gap:24px}}
.st{{display:flex;gap:28px;align-items:center;font-size:60px;font-weight:700;line-height:1.15;opacity:0;background:rgba(255,255,255,.08);
  border:2px solid rgba(255,255,255,.12);border-radius:30px;padding:34px 34px}}
.st b{{color:{B.YELLOW}}} .lst .st{{justify-content:space-between}} .lst .st b{{font-family:'JetBrains Mono',monospace}}
.st i{{flex:none;width:78px;height:78px;border-radius:50%;background:{B.YELLOW};color:{B.INK};font-style:normal;font-family:'JetBrains Mono',monospace;font-weight:800;font-size:40px;display:grid;place-items:center}}
.kw{{display:inline-block;align-self:flex-start;background:{B.YELLOW};color:{B.INK};font-family:'JetBrains Mono',monospace;font-weight:800;font-size:120px;padding:18px 44px;border-radius:30px;margin:40px 0 16px;box-shadow:0 20px 60px rgba(0,0,0,.3)}}
.cta .txt b{{color:#fff}} .down{{font-size:120px;font-weight:800;margin-top:10px;color:{B.YELLOW}}}
.top{{position:absolute;left:84px;right:84px;top:70px;z-index:6;display:flex;align-items:center;gap:20px;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:38px}}
.logo{{width:62px;height:62px;border-radius:16px;display:grid;place-items:center;background:rgba(255,255,255,.14)}} .logo svg{{width:38px;height:38px}}
.prog{{position:absolute;left:0;right:0;top:0;height:12px;z-index:6;background:rgba(255,255,255,.12)}} .prog i{{display:block;height:100%;width:0;background:{B.YELLOW}}}
.subt{{position:absolute;left:60px;right:160px;top:1190px;height:300px;display:flex;align-items:center;justify-content:center;text-align:center;z-index:7}}
.subt div{{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:92px;line-height:1.08;letter-spacing:-.01em;color:#fff;
  -webkit-text-stroke:14px #000;paint-order:stroke fill;text-shadow:0 10px 30px rgba(0,0,0,.6)}}
.subt span{{display:inline-block;margin:0 .12em}} .subt span.on{{color:{B.YELLOW}}}
</style></head><body>
<div id="bg"></div><div id="grid"></div><div class="cta-bg" id="ctabg"></div><div id="flash"></div>
<div class="prog"><i id="pg"></i></div>
<div class="top"><span class="logo">{logo}</span><span>@{B.HANDLE}</span></div>
{scenes}
<div class="subt"><div id="sub"></div></div>
<script>
const TL={json.dumps(tl)};
const cl=x=>x<0?0:x>1?1:x, out3=x=>1-Math.pow(1-cl(x),3);
const back=x=>{{x=cl(x);const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2);}};
const fmt=(n,d)=>n.toLocaleString('pt-BR',{{minimumFractionDigits:d,maximumFractionDigits:d}});
window.TOTAL=TL.total;
document.querySelectorAll('.scene').forEach((el,k)=>{{const c=TL.scenes[k].count;el.querySelectorAll('.cnt').forEach(x=>{{x.dataset.full=x.innerHTML;}});}});
let lastPage=-1;
window.render=t=>{{
  const secs=[...document.querySelectorAll('.scene')];
  let cur=0; TL.scenes.forEach((s,k)=>{{if(t>=s.start)cur=k}});
  const s=TL.scenes[cur], el=secs[cur], lt=t-s.start;
  secs.forEach((e,k)=>{{e.style.opacity=k===cur?1:0;}});
  // entrada com "soco" + zoom lento contínuo
  const inn=el.querySelector('.in');
  const ent=cur===0?1:back(lt/0.32);
  const sc=(cur===0?1:0.86+0.14*ent)*(1+0.035*lt/s.dur);
  inn.style.transform=`scale(${{sc}}) translateY(${{cur===0?0:(1-out3(lt/0.32))*60}}px)`;
  inn.style.opacity=cur===0?1:cl(lt/0.12);
  // fundo vivo
  document.getElementById('bg').style.setProperty('--gx',(30+20*Math.sin(t*0.5))+'%');
  document.getElementById('bg').style.setProperty('--gy',(30+15*Math.cos(t*0.4))+'%');
  document.getElementById('ctabg').style.opacity=el.classList.contains('cta')?cl(lt/0.2):0;
  document.getElementById('pg').style.width=(100*t/TL.total)+'%';
  // gancho: número treme e pisca no começo
  el.querySelectorAll('.hv').forEach(x=>{{const a=Math.max(0,1-lt/0.55);x.style.transform=`translate(${{Math.sin(lt*90)*16*a}}px,${{Math.cos(lt*70)*8*a}}px) scale(${{1+0.18*a}})`;}});
  document.getElementById('flash').style.opacity=cur===0?0.35*Math.max(0,1-t/0.25):0;
  // contagem dos números
  if(s.count) el.querySelectorAll('.cnt').forEach(x=>{{const c=s.count;const p=out3((lt-c.t0)/c.d);
    x.innerHTML=p>=1?x.dataset.full:c.pre+fmt(c.n*p,c.dec)+c.pos;
    x.style.display='inline-block';x.style.transform=`scale(${{1+0.12*Math.max(0,1-Math.abs(lt-c.t0-c.d)/0.18)}})`;}});
  // comparação: risca o "de"
  el.querySelectorAll('.strike').forEach(x=>{{x.style.width=(105*out3((lt-s.strike)/0.3))+'%';}});
  el.querySelectorAll('.to').forEach(x=>{{const p=back((lt-s.strike-0.2)/0.35);x.style.opacity=cl((lt-s.strike-0.2)/0.1);x.style.transform=`scale(${{0.6+0.4*p}})`;}});
  // itens no ritmo da fala
  el.querySelectorAll('.st').forEach((x,i)=>{{const a=(s.items||[])[i]??0;const p=back((lt-a)/0.3);x.style.opacity=cl((lt-a)/0.1);
    x.style.transform=`translateX(${{(1-p)*140}}px)`;}});
  el.querySelectorAll('.kw').forEach(x=>{{x.style.transform=`scale(${{1+0.05*Math.sin(lt*7)}}) rotate(-2deg)`;}});
  el.querySelectorAll('.down').forEach(x=>{{x.style.transform=`translateY(${{20*Math.abs(Math.sin(lt*4))}}px)`;}});
  // legenda palavra a palavra
  let pg=null; (s.pages||[]).forEach(p=>{{if(lt>=p.a&&lt<p.b)pg=p;}});
  const sub=document.getElementById('sub');
  if(!pg){{sub.innerHTML='';}} else {{
    sub.innerHTML=pg.w.map(w=>`<span class="${{lt>=w[1]&&lt<w[2]+0.05?'on':''}}">${{w[0]}}</span>`).join(' ');
    const p=back((lt-pg.a)/0.16); sub.style.transform=`scale(${{0.8+0.2*p}})`;
  }}
}};
render(0);
</script></body></html>"""


# ---------- linha do tempo ----------
def build_timeline(spec, variant, tmp):
    scenes, audios, t = [], [], 0.0
    for k, s in enumerate(spec["scenes"]):
        say = s.get("say", "")
        show = s.get("show", say)
        if s["type"] == "cta":
            extra = CTA_SAY.get(variant, B.CTA[variant]["say"])
            say = (say + " " + extra).strip()
            show = (show + " " + extra).strip() if s.get("show") else say
        wav = speak(say) if say else None
        lead = 0.0 if k == 0 else 0.12
        if wav:
            wav = faster(wav, tmp / f"v{k}.wav")
            spoken = duration(wav)
            audios.append((t + lead, wav))
        else:
            spoken = len(say) / 16.5
        dur = max(s.get("secs", 0), lead + spoken + 0.2)
        words, bounds = align(wav, spoken, say, show)
        sc = {"start": round(t, 3), "dur": round(dur, 3),
              "pages": [dict(p, a=round(p["a"] + lead, 3), b=round(min(p["b"] + lead, dur), 3),
                             w=[[w, round(a + lead, 3), round(b + lead, 3)] for w, a, b in p["w"]]) for p in pages(words)]}
        n_items = len(s.get("items", []))
        if n_items:
            if len(bounds) - 1 >= n_items + 1:  # 1ª frase introduz, as seguintes trazem um item cada
                sc["items"] = [round(lead + bounds[i + 1], 3) for i in range(n_items)]
            elif len(bounds) - 1 == n_items:
                sc["items"] = [round(lead + bounds[i], 3) for i in range(n_items)]
            else:
                sc["items"] = [round(lead + 0.2 + i * (spoken * 0.8) / n_items, 3) for i in range(n_items)]
        c = countable(s.get("value", "")) if s["type"] in ("number", "fact", "compare") else None
        if c:
            c.update(t0=0.25 if s["type"] != "compare" else 1.1, d=0.7)
            sc["count"] = c
        if s["type"] == "compare":
            sc["strike"] = 0.45
        scenes.append(sc)
        t += dur
    return {"scenes": scenes, "total": round(t + 0.3, 3)}, audios


# ---------- efeitos sonoros próprios ----------
def _env(n, a=0.004, d=0.1):
    x = np.arange(n) / SR
    return np.minimum(1, x / a) * np.exp(-x / d)


def sfx_whoosh():
    n = int(0.35 * SR); x = np.arange(n) / SR
    noise = np.random.default_rng(7).standard_normal(n)
    # ruído filtrado com "varredura" (passa-faixa simples por média móvel variável)
    out = np.zeros(n); acc = 0.0
    for i in range(n):
        k = 0.02 + 0.5 * (i / n)
        acc += k * (noise[i] - acc); out[i] = acc
    env = np.sin(np.pi * np.clip(x / 0.35, 0, 1)) ** 2
    return 0.5 * out / (np.abs(out).max() + 1e-9) * env


def sfx_pop():
    n = int(0.09 * SR); x = np.arange(n) / SR
    f = 900 * np.exp(-x * 30) + 300
    return 0.45 * np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.03)


def sfx_tick():
    n = int(0.03 * SR); x = np.arange(n) / SR
    return 0.18 * np.sin(2 * np.pi * 2400 * x) * _env(n, 0.001, 0.008)


def sfx_ding():
    n = int(0.6 * SR); x = np.arange(n) / SR
    return 0.22 * (np.sin(2 * np.pi * 1318.5 * x) + 0.6 * np.sin(2 * np.pi * 1975.5 * x)) * _env(n, 0.003, 0.18)


def build_sfx(path, tl):
    total = tl["total"]; buf = np.zeros(int((total + 1) * SR))

    def put(sig, at):
        i = int(at * SR)
        if i < 0 or i >= len(buf):
            return
        j = min(len(buf), i + len(sig)); buf[i:j] += sig[: j - i]
    wh, po, ti, di = sfx_whoosh(), sfx_pop(), sfx_tick(), sfx_ding()
    for k, s in enumerate(tl["scenes"]):
        st = s["start"]
        put(wh if k else po * 1.3, st - (0.12 if k else 0))
        for a in s.get("items", []):
            put(po, st + a)
        c = s.get("count")
        if c:
            for q in np.arange(0, c["d"], 0.06):
                put(ti, st + c["t0"] + q)
            put(di, st + c["t0"] + c["d"])
        if "strike" in s:
            put(wh * 0.5, st + s["strike"])
    buf = np.clip(buf[: int(total * SR)], -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype("<i2").tobytes())


def build_audio(out, tl, audios, seed, tmp):
    total = tl["total"]
    music = pick_music(seed)
    if not music:
        music = tmp / "bed.wav"; synth_bed(music, total, seed)
    sfx = tmp / "sfx.wav"; build_sfx(sfx, tl)
    inputs = ["-stream_loop", "-1", "-i", str(music), "-i", str(sfx)]
    parts, labels = [], []
    for j, (start, wav) in enumerate(audios, 2):
        ms = int(start * 1000); inputs += ["-i", str(wav)]
        parts.append(f"[{j}:a]aformat=sample_rates={SR}:channel_layouts=mono,adelay={ms}|{ms},apad[v{j}]"); labels.append(f"[v{j}]")
    fade = f"afade=t=out:st={max(0, total - 1.0)}:d=1.0"
    parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,atrim=0:{total},highpass=f=80,"
                 f"equalizer=f=3000:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,asplit=2[voz][sc]")
    parts.append(f"[0:a]aformat=sample_rates={SR}:channel_layouts=mono,atrim=0:{total},volume=0.26[m0]")
    parts.append("[m0][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[mus]")
    parts.append(f"[1:a]aformat=sample_rates={SR}:channel_layouts=mono,volume=0.9[fx]")
    parts.append(f"[voz][mus][fx]amix=inputs=3:normalize=0,{fade},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts),
                    "-map", "[out]", "-ac", "2", "-ar", str(SR), "-c:a", "aac", "-b:a", "192k", str(out)], check=True)


def render(spec_path, variants, name="video"):
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
            out = folder / f"{name}_{v}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(fr / "%05d.jpg"), "-i", str(aud),
                            "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
                            "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(out)], check=True)
            if v == variants[0]:
                shutil_copy = __import__("shutil").copy
                shutil_copy(fr / f"{min(45, len(list(fr.iterdir())) - 1):05d}.jpg", folder / "capa.jpg")
            print(f"{out.name}: {tl['total']:.1f}s, narração {'sim' if audios else 'não'}")


if __name__ == "__main__":
    args = sys.argv[1:]
    vs, name = ["ig", "tt", "yt"], "video"
    if "--so" in args:
        i = args.index("--so"); vs = args[i + 1].split(","); del args[i:i + 2]
    if "--saida" in args:
        i = args.index("--saida"); name = args[i + 1]; del args[i:i + 2]
    render(args[0], vs, name)

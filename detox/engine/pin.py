"""Pin do Pinterest do Totalmente Saudável (1000x1500, imagem estática), no padrão dos pins de receita que mais circulam:
foto grande da comida, título forte com destaque manuscrito, cartão com ingredientes/passos e faixa "Salve este pin".

Tudo sai do spec.json (nada inventado): título de `pin_card` (kicker, headline, accent), listas das cenas `steps`,
número com fonte da cena `number`. Uso avulso: python3 pin.py ../posts/<pasta>
"""
import html, json, re, sys, tempfile
from pathlib import Path

import brand as B

ASSETS = Path(__file__).resolve().parent.parent / "assets"
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@800;900'
         '&family=Caveat:wght@700&family=Montserrat:wght@600;700;800;900&display=swap">')
PURPLE, PINK, CREAM, INK = "#5b2a6e", "#e0559c", "#fff8f1", "#2a1233"


def _txt(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def _rich(s):
    """Mantém só <b> (negrito dos itens); o resto vira texto."""
    s = html.escape(_txt(s.replace("<b>", "\x01").replace("</b>", "\x02")))
    return s.replace("\x01", "<b>").replace("\x02", "</b>")


def _img(spec, folder):
    for sc in spec["scenes"]:
        bg = sc.get("bg")
        src = bg if isinstance(bg, str) else (bg or {}).get("src")
        if src and not src.lower().endswith((".mp4", ".mov", ".webm")):
            for c in (folder / src, ASSETS / src):
                if c.exists():
                    return c
    return None


def build_html(spec, folder):
    pc = spec.get("pin_card", {})
    hook = spec["scenes"][0]
    kicker = pc.get("kicker") or "Receita sem açúcar"
    headline = pc.get("headline") or _txt(hook.get("title"))
    accent = pc.get("accent", "")
    photo = _img(spec, folder)
    sections = [(_txt(s.get("title")) or "Passo a passo", s.get("items", [])) for s in spec["scenes"] if s["type"] == "steps"]
    if pc.get("sections"):
        sections = [(t, it) for t, it in pc["sections"]]
    num = next((s for s in spec["scenes"] if s["type"] == "number"), None)
    stat = pc.get("stat") or ({"value": num.get("value"), "label": num.get("label"), "text": num.get("text"),
                               "source": num.get("source")} if num else None)
    numbered = pc.get("numbered", [])  # títulos de seção que viram passos numerados

    def sec(t, items):
        if t in numbered or re.search(r"modo|forno|como fazer|passo", t, re.I):
            lis = "".join(f'<li><i>{n}</i><span>{_rich(x)}</span></li>' for n, x in enumerate(items, 1))
            return f'<div class="sec"><h3>{html.escape(t)}</h3><ol>{lis}</ol></div>'
        lis = "".join(f'<li><i>✓</i><span>{_rich(x)}</span></li>' for x in items)
        return f'<div class="sec"><h3>{html.escape(t)}</h3><ul>{lis}</ul></div>'

    body = "".join(sec(t, it) for t, it in sections[:2])
    stat_html = ""
    if stat and len(_txt(stat["value"])) > 12:
        stat_html = (f'<div class="stat col"><b class="lb">{html.escape(_txt(stat.get("label")))}</b><div class="sv">{html.escape(_txt(stat["value"]))}</div>'
                     f'<div class="sl"><span>{_rich(stat.get("text", ""))}</span><em>Fonte: {html.escape(_txt(stat.get("source")))}</em></div></div>')
    elif stat:
        stat_html = (f'<div class="stat{" col" if len(_txt(stat["value"]))>12 else ""}"><div class="sv">{html.escape(_txt(stat["value"]))}</div>'
                     f'<div class="sl"><b>{html.escape(_txt(stat.get("label")))}</b><span>{_rich(stat.get("text", ""))}</span>'
                     f'<em>Fonte: {html.escape(_txt(stat.get("source")))}</em></div></div>')
    n_items = sum(len(it) for _, it in sections[:2])
    photo_h = 700 if (stat and n_items > 3) or n_items > 5 else 780
    ph = f'<img class="ph" src="{photo.as_uri()}">' if photo else ""
    return f'''<!doctype html><meta charset="utf-8">{FONTS}<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1000px;height:1500px;overflow:hidden;position:relative;background:{CREAM};font-family:Montserrat,sans-serif;color:{INK}}}
.pw{{position:absolute;left:0;right:0;top:0;height:1350px;overflow:hidden}}
.ph{{width:100%;height:100%;object-fit:cover;object-position:50% 62%}}
.pw:after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.28) 0%,rgba(0,0,0,0) 18%,rgba(0,0,0,0) 55%,rgba(42,18,51,.35) 100%)}}
.brand{{position:absolute;z-index:3;left:40px;top:36px;display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.92);
  padding:10px 18px 10px 12px;border-radius:40px;font-weight:800;font-size:24px;color:{PURPLE}}}
.brand svg{{width:30px;height:30px}}
.ai{{position:absolute;z-index:3;right:40px;top:44px;font-size:19px;font-weight:600;color:#fff;background:rgba(0,0,0,.45);padding:6px 12px;border-radius:8px}}
.save{{position:absolute;z-index:3;right:64px;bottom:-26px;background:{PINK};color:#fff;font-weight:900;font-size:24px;
  padding:12px 22px;border-radius:40px;letter-spacing:.04em;box-shadow:0 6px 18px rgba(0,0,0,.25)}}
.card{{position:absolute;z-index:2;left:40px;right:40px;bottom:178px;background:#fff;border-radius:34px;
  box-shadow:0 18px 50px rgba(61,26,74,.18);padding:40px 50px 44px;display:flex;flex-direction:column}}
.k{{align-self:flex-start;background:{PURPLE};color:#fff;font-weight:800;font-size:23px;letter-spacing:.12em;text-transform:uppercase;
  padding:9px 20px;border-radius:10px}}
h1{{font-family:'Playfair Display',serif;font-weight:900;font-size:84px;line-height:1.0;margin-top:18px;letter-spacing:-.01em;color:{INK}}}
.acc{{font-family:Caveat,cursive;font-weight:700;font-size:58px;line-height:1.05;color:{PINK};margin-top:2px}}
.body{{display:flex;gap:34px;margin-top:24px}}
.sec{{flex:1;min-width:0}}
h3{{font-weight:900;font-size:25px;letter-spacing:.1em;text-transform:uppercase;color:{PURPLE};border-bottom:3px solid #f3d3e6;padding-bottom:8px;margin-bottom:12px}}
ul,ol{{list-style:none}} li{{display:flex;gap:12px;align-items:flex-start;font-size:30px;line-height:1.25;margin:0 0 14px;font-weight:600}}
li b{{font-weight:800;color:{INK}}}
li i{{font-style:normal;flex:none;width:36px;height:36px;border-radius:50%;background:#fbe3f0;color:{PINK};font-weight:900;font-size:21px;
  display:flex;align-items:center;justify-content:center;margin-top:-1px}}
ol li i{{background:{PURPLE};color:#fff}}
.stat{{display:flex;gap:22px;align-items:center;background:#fbeff6;border-radius:20px;padding:18px 24px;margin-top:20px}}
.sv{{font-family:'Playfair Display',serif;font-weight:900;font-size:62px;color:{PINK};line-height:1;white-space:nowrap}}
.sl{{display:flex;flex-direction:column;font-size:23px;line-height:1.25}} .sl b{{font-weight:800;text-transform:uppercase;letter-spacing:.06em;font-size:20px;color:{PURPLE}}}
.lb{{font-weight:800;text-transform:uppercase;letter-spacing:.06em;font-size:20px;color:{PURPLE}}}
.sl em{{font-style:normal;font-size:18px;color:#8a7790;margin-top:4px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:150px;background:{PURPLE};color:#fff;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}}
.foot b{{font-weight:900;font-size:34px}} .foot span{{font-size:25px;margin-top:6px;opacity:.95}} .foot u{{text-decoration:none;color:#ffc6ea;font-weight:800}}
.edu{{font-size:16px;color:#8a7790;text-align:center;margin-top:10px}} .stat.col{{flex-direction:column;align-items:flex-start;gap:8px}} .stat.col .sv{{font-size:54px;white-space:normal}}
</style>
<div class="pw">{ph}</div>
<script>addEventListener('load',()=>{{const c=document.querySelector('.card').getBoundingClientRect().top;document.querySelector('.pw').style.height=(c+90)+'px'}})</script>
<div class="brand">{B.LOGO_SVG.format(fg=PURPLE)}{B.BRAND}</div>
{'<div class="ai">Imagem gerada por IA</div>' if photo else ''}
<div class="card"><span class="k">{html.escape(kicker)}</span><h1>{html.escape(headline)}</h1>
{f'<div class="acc">{html.escape(accent)}</div>' if accent else ''}
{stat_html}<div class="body">{body}</div><div class="edu">Conteúdo educativo. Não substitui nutricionista.</div><div class="save">📌 SALVE ESTE PIN</div></div>
<div class="foot"><b>{html.escape(pc.get("cta_pin", "+ 5 receitas doces sem açúcar, grátis"))}</b><span>Toque no pin › <u>{B.FREE}</u></span></div>'''


def make_pin(spec, folder):
    from playwright.sync_api import sync_playwright
    from render_video import CHROMIUM
    page = build_html(spec, folder)
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "pin.html"; f.write_text(page)
        with sync_playwright() as pw:
            br = pw.chromium.launch(**({"executable_path": str(CHROMIUM)} if CHROMIUM.is_file() else {}))
            pg = br.new_page(viewport={"width": 1000, "height": 1500})
            pg.goto(f.as_uri()); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(700)
            over = pg.evaluate("(()=>document.querySelector('.card').getBoundingClientRect().top<130)()")
            pg.screenshot(path=str(folder / "pin.jpg"), type="jpeg", quality=90); br.close()
    print("pin.jpg (Pinterest 1000x1500)" + ("  AVISO: texto do cartão estourou, encurte o pin_card" if over else ""))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        d = Path(p).resolve()
        make_pin(json.loads((d / "spec.json").read_text()), d)

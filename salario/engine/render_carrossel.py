"""Carrossel em quadrinhos do Salário Organizado (casal Bia e Rafa).

Uso:
  python3 render_carrossel.py ../posts/<pasta>        # lê spec.json, gera c01.jpg ... cNN.jpg (Instagram) e cNN-tt.jpg (CTA do TikTok)

spec.json (tipo "carrossel"):
  {"tipo": "carrossel", "redes": ["ig", "tt"],
   "slides": [
     {"tipo": "quadro", "img": "img/p1.png", "cap": "3 meses antes...",            # cap = caixinha amarela opcional
      "baloes": [{"x": 30, "y": 70, "w": 540, "h": 0, "t": 60, "txt": "R$ 734 de parcela?!"}]},
     ...,
     {"tipo": "card", "html": "<h1>...</h1><table>...</table>"}                   # slide-prova (a conta)
   ],
   "cta_titulo": "Quer fazer essa conta com as suas parcelas?",                     # opcional
   "captions": {"ig": "...", "tt": "..."}}

Balões: x, y, w em px no quadro 1080x1350; t = posição da ponta (% da largura do balão) apontando para quem fala;
h = altura mínima (opcional). Texto: <b>vermelho</b> para gasto/dívida, <i>verde</i> para dinheiro que volta.
O último slide (CTA) é gerado aqui, um por rede (brand.CTA). Todo quadro leva o selo "Imagem gerada por IA".
"""
import base64, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import brand as B

W, H = 1080, 1350
CHROMIUM = Path("/opt/pw-browsers/chromium")  # navegador pré-instalado (a versão do Playwright pode divergir)
FONTS = B.FONTS_LINK + '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Kalam:wght@700&display=swap">'

CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:#f3ead8}}
.s{{position:relative;width:{W}px;height:{H}px;background-size:cover;background-position:center}}
.b{{position:absolute;display:flex;flex-direction:column;justify-content:center;background:#fffdf6;border:5px solid #1d1d1b;
   border-radius:46px;padding:26px 34px;font-family:Kalam,cursive;font-weight:700;color:#1d1d1b;font-size:50px;line-height:1.12;
   text-align:center;box-shadow:6px 8px 0 rgba(0,0,0,.18)}}
.b:after,.b:before{{content:"";position:absolute;width:0;height:0;border-style:solid}}
.b:before{{bottom:-46px;left:var(--t);border-width:46px 22px 0 22px;border-color:#1d1d1b transparent transparent}}
.b:after{{bottom:-35px;left:calc(var(--t) + 6px);border-width:38px 16px 0 16px;border-color:#fffdf6 transparent transparent}}
.b b{{color:{B.RED}}} .b i{{font-style:normal;color:{B.GREEN}}}
.cap{{position:absolute;left:40px;top:40px;background:{B.YELLOW};border:4px solid #1d1d1b;padding:10px 24px;font-family:Kalam,cursive;
     font-weight:700;font-size:40px;transform:rotate(-2deg);box-shadow:5px 6px 0 rgba(0,0,0,.18)}}
.cnt{{position:absolute;left:50%;transform:translateX(-50%);bottom:24px;background:rgba(20,35,31,.78);color:#fff;font:700 30px 'Source Sans 3',sans-serif;padding:8px 18px;border-radius:30px}}
.ia{{position:absolute;left:30px;bottom:28px;background:rgba(20,35,31,.72);color:#fff;font:600 24px 'Source Sans 3',sans-serif;padding:6px 14px;border-radius:8px}}
.h{{position:absolute;right:30px;bottom:28px;color:#fff;font:700 28px 'Source Sans 3',sans-serif;text-shadow:0 2px 6px rgba(0,0,0,.7)}}
.card{{padding:110px 80px;display:flex;flex-direction:column;justify-content:center;gap:34px;background:{B.BG}}}
.card h1{{font:800 76px/1.02 'Bricolage Grotesque',sans-serif;color:{B.INK}}} .card h1 em{{font-style:normal;color:{B.RED}}}
.card p{{font:600 38px/1.3 'Source Sans 3',sans-serif;color:{B.MUTED}}}
.card .h{{color:{B.MUTED};text-shadow:none}}
table{{width:100%;border-collapse:collapse;font:600 36px 'Source Sans 3',sans-serif;color:{B.INK}}}
td,th{{padding:16px 10px;border-bottom:3px solid {B.LINE};text-align:left}}
th{{font-size:28px;color:{B.MUTED};text-transform:uppercase;letter-spacing:.04em}}
td.n,th.n{{text-align:right}} tr.tot td{{border-bottom:none;font-weight:700;font-size:40px;color:{B.DEEP}}}
.cta{{background:{B.GREEN};align-items:center;text-align:center}} .cta h1{{color:#fff;font-size:70px}} .cta p{{color:{B.MINT}}} .cta .h{{color:#fff}}
.kw{{display:inline-block;background:{B.YELLOW};color:{B.INK};font:800 120px 'Bricolage Grotesque',sans-serif;padding:14px 50px;border-radius:24px;
    border:6px solid {B.INK};box-shadow:10px 12px 0 {B.DEEP};transform:rotate(-2deg)}}
.url{{display:inline-block;background:#fff;color:{B.DEEP};font:800 52px 'Bricolage Grotesque',sans-serif;padding:22px 34px;border-radius:20px;border:5px dashed {B.YELLOW}}}
.card .cnt{{background:{B.INK}}}
"""


def cta_html(rede, titulo):
    if rede == "tt":  # TikTok: 1º seguir, 2º print do endereço (nunca "comenta PLANILHA")
        return ("<h1>Segue o perfil pra ver a próxima história.</h1><p style='font-size:44px'>E tira print: planilha grátis em</p>"
                f"<div class='url'>{B.SITE}/mini</div><p style='font-size:34px'>(digite no navegador)</p>")
    return (f"<h1>{titulo}</h1><div class='kw'>PLANILHA</div>"
            "<p style='font-size:44px'>Comenta <b>PLANILHA</b> que eu te mando a planilha grátis no direct.</p>")


def slide_html(post, s, i, n):
    cnt = f'<div class="cnt">{i}/{n}</div>'
    handle = f'<div class="h">@{B.HANDLE}</div>'
    if s["tipo"] == "quadro":
        src = post / s["img"]
        mime = "png" if src.suffix.lower() == ".png" else "jpeg"
        out = [f'<div class="s" style="background-image:url(data:image/{mime};base64,{base64.b64encode(src.read_bytes()).decode()})">']
        if s.get("cap"):
            out.append(f'<div class="cap">{s["cap"]}</div>')
        for b in s["baloes"]:
            txt = b["txt"].replace("R$ ", "R$&nbsp;")
            out.append(f'<div class="b" style="left:{b["x"]}px;top:{b["y"]}px;width:{b["w"]}px;min-height:{b.get("h", 0)}px;'
                       f'--t:{b.get("t", 40)}%"><div>{txt}</div></div>')
        out += [cnt, '<div class="ia">Imagem gerada por IA</div>', handle, "</div>"]
        return "".join(out)
    cls = "s card cta" if s["tipo"] == "cta" else "s card"
    return f'<div class="{cls}">{s["html"]}{cnt}{handle}</div>'


def render(post):
    post = Path(post).resolve()
    spec = json.loads((post / "spec.json").read_text(encoding="utf-8"))
    titulo = spec.get("cta_titulo", "Quer organizar o seu salário assim?")
    corpo = spec["slides"]
    n = len(corpo) + 1
    feitos = []
    with sync_playwright() as p:
        br = p.chromium.launch(**({"executable_path": str(CHROMIUM)} if CHROMIUM.exists() else {}))
        pg = br.new_page(viewport={"width": W, "height": H})
        jobs = [(f"c{i:02d}.jpg", s, i) for i, s in enumerate(corpo, 1)]
        jobs += [(f"c{n:02d}.jpg", {"tipo": "cta", "html": cta_html("ig", titulo)}, n),
                 (f"c{n:02d}-tt.jpg", {"tipo": "cta", "html": cta_html("tt", titulo)}, n)]
        for nome, s, i in jobs:
            pg.set_content(f"<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>{CSS}</style></head>"
                           f"<body>{slide_html(post, s, i, n)}</body></html>", wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=str(post / nome), type="jpeg", quality=92)
            feitos.append(nome)
        br.close()
    # lista na ordem para o publish
    spec["arquivos"] = {"ig": [f"c{i:02d}.jpg" for i in range(1, n + 1)],
                        "tt": [f"c{i:02d}.jpg" for i in range(1, n)] + [f"c{n:02d}-tt.jpg"]}
    (post / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"slides": n, "arquivos": feitos}, ensure_ascii=False))


if __name__ == "__main__":
    render(sys.argv[1])

"""Renderiza um post do perfil (perfil.json) a partir de um spec JSON.

Uso: python render_post.py posts/AAAA-MM-DD/spec.json
Saída (na pasta do spec): preview.html, slide_N.png (1080x1350) e slide_N.jpg (para o Instagram).
"""
import asyncio
import json
import sys
from pathlib import Path

from brand import (BODY_STACK, BRAND, CTA_BUTTON, CTA_TAG, CTA_TITLE, DBG, FONTS_LINK, GRAD, HANDLE,
                   HEAD_STACK, LANG, LBG, LBR, LOGO_URI, MUTED, P, PD, PL, SUBTITLE, data_uri, rgba)

W, H = 420, 525
SCALE = 1080 / 420
CHROMIUM = Path("/opt/pw-browsers/chromium")


# ---------- componentes fixos ----------

def progress(i, total, light):
    if total < 2:
        return ""
    pct = (i + 1) / total * 100
    track = "rgba(0,0,0,0.08)" if light else "rgba(255,255,255,0.12)"
    fill = P if light else "#fff"
    label = "rgba(0,0,0,0.3)" if light else "rgba(255,255,255,0.4)"
    return (f'<div class="pb"><div class="pb-track" style="background:{track}">'
            f'<div class="pb-fill" style="width:{pct:.2f}%;background:{fill}"></div></div>'
            f'<span class="sans pb-label" style="color:{label}">{i + 1}/{total}</span></div>')


def arrow(light):
    bg = "rgba(0,0,0,0.06)" if light else "rgba(255,255,255,0.08)"
    stroke = "rgba(0,0,0,0.25)" if light else "rgba(255,255,255,0.35)"
    return (f'<div class="arrow" style="background:linear-gradient(to right,transparent,{bg})">'
            f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" '
            f'stroke="{stroke}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')


def tag(text, color):
    return f'<span class="sans tag" style="color:{color}">{text}</span>' if text else ""


def lockup(color):
    return (f'<div class="lockup"><img src="{LOGO_URI}" alt="" class="lockup-logo">'
            f'<span class="sans lockup-name" style="color:{color}">{BRAND.upper()}</span></div>')


def signature(color):
    """Assinatura discreta para posts de imagem única."""
    return (f'<div class="sig"><img src="{LOGO_URI}" alt="" class="sig-logo">'
            f'<span class="sans sig-handle" style="color:{color}">@{HANDLE}</span></div>')


def quote_box(q, light):
    if not q:
        return ""
    bg = "rgba(0,0,0,0.035)" if light else "rgba(255,255,255,0.05)"
    bd = LBR if light else "rgba(255,255,255,0.1)"
    tc = DBG if light else "#fff"
    rc = MUTED if light else "rgba(255,255,255,0.5)"
    return (f'<div class="quote" style="background:{bg};border-color:{bd}">'
            f'<p class="serif quote-text" style="color:{tc}">"{q["text"]}"</p>'
            f'<p class="sans quote-ref" style="color:{rc}">{q.get("ref", "")}</p></div>')


def body(text, light, on_photo=False):
    if not text:
        return ""
    c = "rgba(255,255,255,0.82)" if on_photo else (MUTED if light else "rgba(255,255,255,0.62)")
    return f'<p class="sans body" style="color:{c}">{text}</p>'


def row(item, light, last):
    border = "none" if last else (f"1px solid {LBR}" if light else "1px solid rgba(255,255,255,0.08)")
    tcol = DBG if light else "#fff"
    dcol = MUTED if light else "rgba(255,255,255,0.55)"
    ncol = P if light else PL
    return (f'<div class="row" style="border-bottom:{border}">'
            f'<span class="serif num" style="color:{ncol}">{item.get("num", "")}</span>'
            f'<div class="row-text"><span class="sans row-title" style="color:{tcol}">{item["title"]}</span>'
            f'<span class="sans row-desc" style="color:{dcol}">{item.get("desc", "")}</span></div></div>')


# ---------- layouts ----------

def theme_of(s):
    if s["layout"] == "cta":
        return "grad"
    if s["layout"] == "photo" or (s["layout"] == "verse" and s.get("image")):
        return "photo"
    return s.get("theme", "light")


def resolve_img(s, base):
    p = Path(s["image"])
    return data_uri(p if p.is_absolute() else base / p)


def layout_html(s, base, single):
    t = theme_of(s)
    light = t == "light"
    ink = DBG if light else "#fff"
    tagc = P if light else PL
    L = s["layout"]

    if L == "hero":
        return f"""<div class="content center">{lockup(ink)}
          <div class="stack-hero">{tag(s.get("tag"), tagc)}
            <h1 class="serif h-hero" style="color:{ink}">{s["title"]}</h1>{body(s.get("body"), light)}</div>
          {f'<span class="sans hint" style="color:{PD if light else PL}">{s["hint"]}</span>' if s.get("hint") else ""}</div>"""

    if L == "photo":
        img = resolve_img(s, base)
        pos = s.get("focus", "center")
        top_logo = lockup("#fff") if s.get("logo") else ""
        return f"""<img class="bg-photo" src="{img}" style="object-position:{pos}" alt="">
          <div class="photo-shade"></div>{top_logo}
          <div class="content bottom">{tag(s.get("tag"), PL)}
            <h2 class="serif {'h-hero' if s.get('big') else 'h2'}" style="color:#fff">{s["title"]}</h2>
            {body(s.get("body"), False, on_photo=True)}</div>
          {signature("rgba(255,255,255,0.75)") if single else ""}"""

    if L == "text":
        return f"""<div class="content {'center' if s.get('center') else 'bottom'}">{tag(s.get("tag"), tagc)}
          <h2 class="serif h2" style="color:{ink}">{s["title"]}</h2>
          {quote_box(s.get("quote"), light)}{body(s.get("body"), light)}</div>"""

    if L == "list":
        items = s["items"]
        rows = "".join(row(it, light, k == len(items) - 1) for k, it in enumerate(items))
        return f"""<div class="content bottom">{tag(s.get("tag"), tagc)}
          <h2 class="serif h2" style="color:{ink}">{s["title"]}</h2><div class="list">{rows}</div></div>"""

    if L == "big":
        return f"""<span class="serif giant" style="color:{P if light else PL}">{s["big"]}</span>
          <div class="content bottom">{tag(s.get("tag"), tagc)}
          <h2 class="serif h2" style="color:{ink}">{s["title"]}</h2>
          {quote_box(s.get("quote"), light)}{body(s.get("body"), light)}</div>"""

    if L == "verse":
        bg = ""
        if s.get("image"):
            bg = (f'<img class="bg-photo" src="{resolve_img(s, base)}" style="object-position:{s.get("focus", "center")}" alt="">'
                  '<div class="photo-shade full"></div>')
            light, ink = False, "#fff"
        refc = PL if not light else P
        return f"""{bg}<div class="content center verse">{tag(s.get("tag"), PL if not light else P)}
          <span class="serif verse-mark" style="color:{refc}">“</span>
          <p class="serif verse-text" style="color:{ink}">{s["text"]}</p>
          <p class="sans verse-ref" style="color:{refc}">{s.get("ref", "")}</p>
          {body(s.get("body"), light, on_photo=bool(s.get("image")))}</div>
          {signature("rgba(255,255,255,0.7)" if not light else MUTED) if single else ""}"""

    if L == "compare":
        lc = s["left"]; rc = s["right"]
        cb = LBR if light else "rgba(255,255,255,0.1)"
        return f"""<div class="content bottom">{tag(s.get("tag"), tagc)}
          <h2 class="serif h2" style="color:{ink}">{s["title"]}</h2>
          <div class="cmp">
            <div class="cmp-col" style="border-color:{cb}"><span class="sans cmp-label" style="color:{MUTED}">{lc["label"]}</span>
              <p class="sans cmp-text bad" style="color:{MUTED if light else 'rgba(255,255,255,0.5)'}">{lc["text"]}</p></div>
            <div class="cmp-col on" style="border-color:{P}"><span class="sans cmp-label" style="color:{P if light else PL}">{rc["label"]}</span>
              <p class="sans cmp-text" style="color:{ink}">{rc["text"]}</p></div>
          </div>{body(s.get("body"), light)}</div>"""

    if L == "cta":
        return f"""<div class="content center cta">
          <img src="{LOGO_URI}" alt="{BRAND}" class="cta-logo">{tag(s.get("tag", CTA_TAG), "rgba(255,255,255,0.7)")}
          <h2 class="serif h2 cta-h" style="color:#fff">{s.get("title", CTA_TITLE)}</h2>
          {f'<p class="sans body" style="color:rgba(255,255,255,0.88)">{s["body"]}</p>' if s.get("body") else ""}
          <div class="sans cta-btn">{s.get("button", CTA_BUTTON)}</div>
          {f'<p class="sans cta-sub">{s["sub"]}</p>' if s.get("sub") else ""}</div>"""

    raise ValueError(f"layout desconhecido: {L}")


def render_slide(i, total, s, base):
    t = theme_of(s)
    bg = {"light": LBG, "dark": DBG, "grad": GRAD, "photo": DBG}[t]
    light = t == "light"
    last = i == total - 1
    single = total == 1
    return (f'<div class="slide" style="background:{bg}">{layout_html(s, base, single)}'
            f'{"" if (last or single) else arrow(light)}{progress(i, total, light)}</div>')


CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: {LBR}; color: {DBG}; min-height: 100vh; display: flex; justify-content: center; align-items: flex-start; padding: 32px 16px; font-family: {BODY_STACK}; }}
.serif {{ font-family: {HEAD_STACK}; }}
.sans {{ font-family: {BODY_STACK}; }}
.stage {{ width: 420px; }}
.ig-frame {{ width: 420px; background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 12px 40px {rgba(DBG, 0.14)}; }}
.ig-header {{ display: flex; align-items: center; gap: 10px; padding: 12px 14px; }}
.ig-avatar {{ width: 32px; height: 32px; border-radius: 50%; background: {P}; padding: 2px; }}
.ig-avatar img {{ width: 100%; height: 100%; border-radius: 50%; object-fit: cover; display: block; }}
.ig-handle {{ font-size: 13px; font-weight: 600; }} .ig-sub {{ font-size: 11px; color: {MUTED}; }}
.carousel-viewport {{ width: 420px; aspect-ratio: 4 / 5; overflow: hidden; position: relative; cursor: grab; touch-action: pan-y; user-select: none; }}
.carousel-track {{ display: flex; height: 100%; transition: transform .35s cubic-bezier(.2,.8,.2,1); }}
.slide {{ position: relative; flex: 0 0 420px; width: 420px; height: 525px; overflow: hidden; }}
.ig-dots {{ display: flex; justify-content: center; gap: 4px; padding: 10px 0 2px; }}
.dot {{ width: 6px; height: 6px; border-radius: 50%; background: {LBR}; }} .dot.on {{ background: {P}; }}
.ig-actions {{ display: flex; gap: 14px; padding: 6px 14px; }}
.ig-actions svg {{ width: 24px; height: 24px; stroke: {DBG}; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
.ig-actions .sp {{ flex: 1; }}
.ig-caption {{ padding: 2px 14px 16px; font-size: 13px; line-height: 1.45; white-space: pre-line; }}
.ig-time {{ display: block; margin-top: 6px; font-size: 10px; letter-spacing: .5px; color: {MUTED}; }}

.pb {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 16px 28px 20px; z-index: 10; display: flex; align-items: center; gap: 10px; }}
.pb-track {{ flex: 1; height: 3px; border-radius: 2px; overflow: hidden; }} .pb-fill {{ height: 100%; border-radius: 2px; }}
.pb-label {{ font-size: 11px; font-weight: 500; font-variant-numeric: tabular-nums; }}
.arrow {{ position: absolute; right: 0; top: 0; bottom: 0; width: 48px; z-index: 9; display: flex; align-items: center; justify-content: center; }}

.content {{ position: absolute; inset: 0; display: flex; flex-direction: column; padding: 0 44px 56px 36px; z-index: 2; }}
.content.center {{ justify-content: center; }} .content.bottom {{ justify-content: flex-end; }}
.tag {{ display: inline-block; font-size: 10px; font-weight: 600; letter-spacing: 2px; margin-bottom: 14px; text-transform: uppercase; }}
.h-hero {{ font-size: 34px; font-weight: 600; letter-spacing: -0.5px; line-height: 1.1; text-wrap: balance; margin-bottom: 16px; }}
.h2 {{ font-size: 28px; font-weight: 600; letter-spacing: -0.4px; line-height: 1.14; text-wrap: balance; margin-bottom: 18px; }}
h1 em, h2 em {{ font-style: italic; }}
.body {{ font-size: 14px; line-height: 1.55; max-width: 32ch; }}
.lockup {{ position: absolute; top: 32px; left: 36px; display: flex; align-items: center; gap: 10px; z-index: 3; }}
.lockup-logo {{ width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: {P}; }}
.lockup-name {{ font-size: 13px; font-weight: 600; letter-spacing: 0.5px; }}
.stack-hero {{ margin-top: 24px; }}
.hint {{ position: absolute; left: 36px; bottom: 56px; font-size: 12px; font-weight: 600; letter-spacing: .3px; }}
.quote {{ padding: 16px 18px; border-radius: 12px; border: 1px solid; margin-bottom: 16px; }}
.quote-text {{ font-size: 15px; font-style: italic; line-height: 1.45; margin-bottom: 8px; }}
.quote-ref {{ font-size: 11px; letter-spacing: .3px; }}
.list {{ display: flex; flex-direction: column; }}
.row {{ display: flex; align-items: flex-start; gap: 16px; padding: 14px 0; }}
.num {{ font-size: 26px; font-weight: 300; min-width: 34px; line-height: 1; }}
.row-text {{ display: flex; flex-direction: column; gap: 4px; min-width: 0; }}
.row-title {{ font-size: 14px; font-weight: 600; line-height: 1.35; }} .row-desc {{ font-size: 12px; line-height: 1.5; }}
.giant {{ position: absolute; top: 18px; right: 52px; font-size: 220px; font-weight: 300; line-height: 1; opacity: .9; }}
.bg-photo {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.photo-shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, {rgba(DBG, 0.15)} 0%, {rgba(DBG, 0.05)} 35%, {rgba(DBG, 0.78)} 68%, {rgba(DBG, 0.95)} 100%); }}
.photo-shade.full {{ background: {rgba(DBG, 0.62)}; }}
.verse {{ align-items: center; text-align: center; padding: 0 40px 56px; }}
.verse-mark {{ font-size: 72px; line-height: .6; margin-bottom: 8px; }}
.verse-text {{ font-size: 24px; font-weight: 600; font-style: italic; line-height: 1.3; text-wrap: balance; margin-bottom: 16px; }}
.verse-ref {{ font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 14px; }}
.verse .body {{ margin: 0 auto; }}
.sig {{ position: absolute; left: 0; right: 0; bottom: 20px; display: flex; justify-content: center; align-items: center; gap: 8px; z-index: 4; }}
.sig-logo {{ width: 20px; height: 20px; border-radius: 50%; object-fit: cover; }}
.sig-handle {{ font-size: 11px; font-weight: 600; letter-spacing: .4px; }}
.cmp {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }}
.cmp-col {{ border: 1px solid; border-radius: 12px; padding: 14px; }}
.cmp-col.on {{ border-width: 1.5px; }}
.cmp-label {{ display: block; font-size: 10px; font-weight: 700; letter-spacing: 2px; margin-bottom: 8px; }}
.cmp-text {{ font-size: 13px; line-height: 1.45; font-weight: 500; }} .cmp-text.bad {{ text-decoration: line-through; text-decoration-thickness: 1px; }}
.cta {{ align-items: center; text-align: center; padding: 0 36px 56px; }}
.cta .tag {{ margin-bottom: 12px; }}
.cta-logo {{ width: 88px; height: 88px; border-radius: 50%; object-fit: cover; margin-bottom: 18px; box-shadow: 0 8px 24px rgba(0,0,0,0.25); }}
.cta-h {{ font-size: 32px; margin-bottom: 14px; }}
.cta .body {{ margin: 0 auto 24px; }}
.cta-btn {{ display: inline-flex; padding: 13px 30px; background: {LBG}; color: {PD}; font-weight: 600; font-size: 14px; border-radius: 28px; box-shadow: 0 6px 18px rgba(0,0,0,0.18); }}
.cta-sub {{ margin-top: 14px; font-size: 12px; font-weight: 500; color: {rgba(DBG, 0.72)}; }}
"""

JS = """
(function(){const W=420,total=document.querySelectorAll('.slide').length,vp=document.getElementById('vp'),tr=document.getElementById('track'),dots=[...document.querySelectorAll('.dot')],st=document.getElementById('stage');let i=0,x0=0,dx=0,down=false,sc=1;
function fit(){sc=Math.min(1,(innerWidth-32)/W);st.style.zoom=sc}
function go(k){i=Math.max(0,Math.min(total-1,k));tr.style.transition='';tr.style.transform='translateX('+(-i*W)+'px)';dots.forEach((d,n)=>d.classList.toggle('on',n===i))}
vp.addEventListener('pointerdown',e=>{down=true;x0=e.clientX;dx=0;vp.setPointerCapture(e.pointerId);tr.style.transition='none'});
vp.addEventListener('pointermove',e=>{if(!down)return;dx=(e.clientX-x0)/sc;tr.style.transform='translateX('+(-i*W+dx)+'px)'});
function end(){if(!down)return;down=false;if(dx<-50)go(i+1);else if(dx>50)go(i-1);else go(i)}
vp.addEventListener('pointerup',end);vp.addEventListener('pointercancel',end);
addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(i+1);if(e.key==='ArrowLeft')go(i-1)});addEventListener('resize',fit);fit()})();
"""


def build_html(spec, base):
    slides = spec["slides"]
    total = len(slides)
    sl = "\n".join(render_slide(i, total, s, base) for i, s in enumerate(slides))
    dots = "".join(f'<span class="dot{" on" if i == 0 else ""}"></span>' for i in range(total)) if total > 1 else ""
    cap = spec.get("caption", "").replace("<", "&lt;")
    return f"""<!doctype html><html lang="{LANG}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{spec.get("title", "Post")} · {BRAND}</title>
{FONTS_LINK}<style>{CSS}</style></head><body>
<div class="stage" id="stage"><div class="ig-frame">
<div class="ig-header"><div class="ig-avatar"><img src="{LOGO_URI}" alt=""></div><div><div class="ig-handle">{HANDLE}</div><div class="ig-sub">{spec.get("series_name", SUBTITLE)}</div></div></div>
<div class="carousel-viewport" id="vp"><div class="carousel-track" id="track">{sl}</div></div>
<div class="ig-dots">{dots}</div>
<div class="ig-actions"><svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg><svg viewBox="0 0 24 24"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg><svg viewBox="0 0 24 24"><path d="M22 3L11 13M22 3l-7 18-4-8-8-4 19-6z"/></svg><span class="sp"></span><svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4-6 4z"/></svg></div>
<div class="ig-caption"><b>{HANDLE}</b> {cap}<span class="ig-time">2 HORAS ATRÁS</span></div>
</div></div><script>{JS}</script></body></html>"""


async def export(html_path, out_dir, total):
    from playwright.async_api import async_playwright
    from PIL import Image
    async with async_playwright() as p:
        kw = {"executable_path": str(CHROMIUM)} if CHROMIUM.is_file() else {}
        browser = await p.chromium.launch(**kw)
        page = await browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
        await page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(1500)
        await page.evaluate("""() => {
          document.querySelectorAll('.ig-header,.ig-dots,.ig-actions,.ig-caption').forEach(e => e.style.display='none');
          document.getElementById('stage').style.zoom = 1;
          document.querySelector('.ig-frame').style.cssText = 'width:420px;height:525px;border-radius:0;box-shadow:none;overflow:hidden;margin:0;';
          document.querySelector('.carousel-viewport').style.cssText = 'width:420px;height:525px;overflow:hidden;';
          document.body.style.cssText = 'padding:0;margin:0;display:block;overflow:hidden;';
        }""")
        files = []
        for i in range(total):
            await page.evaluate("(k)=>{const t=document.getElementById('track');t.style.transition='none';t.style.transform='translateX('+(-k*420)+'px)'}", i)
            await page.wait_for_timeout(300)
            png = out_dir / f"slide_{i + 1}.png"
            await page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": W, "height": H})
            jpg = out_dir / f"slide_{i + 1}.jpg"
            Image.open(png).convert("RGB").save(jpg, "JPEG", quality=92, optimize=True)
            files.append(jpg.name)
        await browser.close()
        return files


def main(spec_path):
    spec_path = Path(spec_path)
    base = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    html = build_html(spec, base)
    out = base / "preview.html"
    out.write_text(html, encoding="utf-8")
    files = asyncio.run(export(out, base, len(spec["slides"])))
    print(json.dumps({"preview": str(out), "slides": files}))


if __name__ == "__main__":
    main(sys.argv[1])

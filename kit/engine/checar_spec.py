"""Confere um spec.json contra as regras de formato e o perfil.json antes de renderizar/publicar.

Uso: python checar_spec.py ../posts/AAAA-MM-DD-serie/spec.json
Sai com código 1 se houver ERRO. AVISOS não bloqueiam. Lembra as premissas do perfil para a revisão humana/IA.
"""
import json
import re
import sys
from pathlib import Path

from brand import HANDLE, PERFIL

LAYOUTS = {"hero", "photo", "text", "list", "big", "verse", "compare", "cta"}
REQ = {"photo": ["image", "title"], "list": ["items", "title"], "big": ["big", "title"], "verse": ["text"],
       "compare": ["left", "right", "title"], "hero": ["title"], "text": ["title"]}


def plain(s):
    return re.sub(r"<[^>]+>", "", s or "")


def main(path):
    path = Path(path)
    spec = json.loads(path.read_text(encoding="utf-8"))
    err, warn = [], []
    slides = spec.get("slides", [])
    if not slides:
        err.append("spec sem slides")
    for i, s in enumerate(slides, 1):
        L = s.get("layout")
        if L not in LAYOUTS:
            err.append(f"slide {i}: layout '{L}' inválido")
            continue
        for k in REQ.get(L, []):
            if not s.get(k):
                err.append(f"slide {i} ({L}): falta '{k}'")
        if s.get("image") and not (path.parent / s["image"]).exists() and not Path(s["image"]).is_absolute():
            err.append(f"slide {i}: imagem {s['image']} não encontrada")
        if len(plain(s.get("title"))) > 80:
            warn.append(f"slide {i}: título com {len(plain(s.get('title')))} caracteres (ideal até ~70)")
        if len(plain(s.get("body"))) > 120:
            warn.append(f"slide {i}: corpo com {len(plain(s.get('body')))} caracteres (ideal até ~110)")
    if len(slides) > 1:
        if slides[-1].get("layout") != "cta":
            err.append("carrossel precisa terminar em slide 'cta'")
        themes = [s.get("theme", "light") for s in slides if s.get("layout") not in ("cta", "photo")]
        if any(a == b for a, b in zip(themes, themes[1:])):
            warn.append("dois slides seguidos com o mesmo tema (alterne claro/escuro)")
        if len(slides) > 10:
            err.append("Instagram aceita no máximo 10 imagens por carrossel")
    cap = spec.get("caption", "")
    if not cap:
        err.append("falta 'caption'")
    if f"@{HANDLE}" not in cap:
        warn.append(f"legenda não menciona @{HANDLE}")
    tags = re.findall(r"#\w+", cap)
    lo, hi = PERFIL.get("legenda", {}).get("hashtags_qtd", [3, 10])
    if not lo <= len(tags) <= hi:
        warn.append(f"legenda com {len(tags)} hashtags (perfil pede {lo} a {hi})")
    if len(cap) > 2200:
        err.append("legenda passa de 2.200 caracteres (limite do Instagram)")
    reel = spec.get("reel")
    if PERFIL.get("agenda", {}).get("reel", True):
        if not reel:
            err.append("perfil pede Reels: falta bloco 'reel'")
        else:
            fr = reel.get("frames", [])
            if not 2 <= len(fr) <= 5:
                warn.append(f"Reels com {len(fr)} cenas (ideal 3 a 4)")
            if fr and not fr[-1].get("cta"):
                warn.append("última cena do Reels sem 'cta'")
            if not reel.get("caption"):
                err.append("Reels sem 'caption'")
    print(json.dumps({"erros": err, "avisos": warn,
                      "revisar_premissas": PERFIL.get("premissas", []) + PERFIL.get("limites", [])}, ensure_ascii=False, indent=2))
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main(sys.argv[1])

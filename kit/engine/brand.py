"""Identidade visual do perfil, lida de perfil.json (fonte única para todo o motor).

Procura o perfil em $PERFIL ou em ../perfil.json (raiz do projeto do perfil).
Só a cor primária é obrigatória: as demais derivam dela (regras das instruções de carrossel).
"""
import base64
import colorsys
import json
import mimetypes
import os
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PERFIL_PATH = Path(os.environ.get("PERFIL", ROOT.parent / "perfil.json")).resolve()
PERFIL = json.loads(PERFIL_PATH.read_text(encoding="utf-8"))
PROJ = PERFIL_PATH.parent

_m = PERFIL["marca"]
BRAND = _m["nome"]
HANDLE = _m["handle"].lstrip("@")
TIMEZONE = PERFIL.get("agenda", {}).get("fuso", "America/Sao_Paulo")
LANG = PERFIL.get("idioma", "pt-BR")
SUBTITLE = _m.get("subtitulo", PERFIL.get("tema", {}).get("nome", ""))


# ---------- cores ----------

def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02X}" for c in rgb)


def _mix(h, other, t):
    a, b = _rgb(h), _rgb(other)
    return _hex(tuple(x + (y - x) * t for x, y in zip(a, b)))


def rgba(h, alpha):
    r, g, b = (round(c * 255) for c in _rgb(h))
    return f"rgba({r},{g},{b},{alpha})"


def _derive(primary):
    """Paleta completa a partir de uma cor: claro +20%, escuro -30%, fundos tingidos pela temperatura."""
    hh, ll, ss = colorsys.rgb_to_hls(*_rgb(primary))
    warm = hh < 0.17 or hh > 0.92  # vermelho, laranja, âmbar, amarelo
    return {
        "primaria": primary,
        "clara": _mix(primary, "#FFFFFF", 0.30),
        "escura": _mix(primary, "#000000", 0.30),
        "fundo_claro": _mix(primary, "#FBF8F2" if warm else "#F6F7F9", 0.90),
        "borda_clara": _mix(primary, "#E9E2D6" if warm else "#E2E5EA", 0.85),
        "fundo_escuro": "#1A1918" if warm else "#0F172A",
        "texto_suave": "#8A8178" if warm else "#6B7280",
    }


_c = {**_derive(_m["cores"]["primaria"]), **{k: v for k, v in _m["cores"].items() if v}}
P, PL, PD = _c["primaria"], _c["clara"], _c["escura"]
LBG, LBR, DBG, MUTED = _c["fundo_claro"], _c["borda_clara"], _c["fundo_escuro"], _c["texto_suave"]
GRAD = f"linear-gradient(165deg, {PD} 0%, {P} 50%, {PL} 100%)"

# ---------- fontes (Google Fonts) ----------
_f = _m.get("fontes", {})
HEAD_FONT = _f.get("titulo", "Playfair Display")
BODY_FONT = _f.get("corpo", "DM Sans")
HEAD_STACK = f"'{HEAD_FONT}', Georgia, serif"
BODY_STACK = f"'{BODY_FONT}', system-ui, sans-serif"


def _family(name, spec):
    return "family=" + urllib.parse.quote_plus(name) + spec


_fams = [_family(HEAD_FONT, ":ital,wght@0,300;0,400;0,600;0,700;1,600;1,700")]
if BODY_FONT != HEAD_FONT:
    _fams.append(_family(BODY_FONT, ":wght@400;500;600;700"))
FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{"&".join(_fams)}&display=swap">'
)


def data_uri(path):
    """Imagem local -> data URI, detectando o tipo real pelo conteúdo (JPEG disfarçado de .png etc.)."""
    path = Path(path)
    raw = path.read_bytes()
    if raw[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif raw[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        mime = "image/webp"
    elif raw.lstrip()[:5] in (b"<?xml", b"<svg ") or raw.lstrip()[:4] == b"<svg":
        mime = "image/svg+xml"
    else:
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def _logo_uri():
    """Logo do perfil; sem logo, gera um círculo na cor primária com a inicial da marca."""
    logo = _m.get("logo")
    if logo:
        p = Path(logo)
        p = p if p.is_absolute() else PROJ / p
        if p.exists():
            return data_uri(p)
    initial = BRAND.strip()[:1].upper()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><circle cx="100" cy="100" r="100" fill="{P}"/>'
           f'<text x="100" y="134" font-family="Georgia,serif" font-size="100" font-weight="700" fill="#fff" '
           f'text-anchor="middle">{initial}</text></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


LOGO_URI = _logo_uri()

# ---------- textos padrão do CTA e do Reels ----------
_cta = PERFIL.get("cta", {})
CTA_TAG = _cta.get("tag", BRAND.upper())
CTA_TITLE = _cta.get("titulo", BRAND)
CTA_BUTTON = _cta.get("botao", f"Siga @{HANDLE}")
REEL_FX = PERFIL.get("reel", {}).get("efeito", "particulas")   # particulas | nenhum
REEL_AUDIO = PERFIL.get("reel", {}).get("audio", "impacto")    # impacto | suave | silencio

"""Identidade visual Forja da Alma: paleta, fontes, logo e handle (fonte única para todo o motor)."""
import base64
import mimetypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo.jpg"

HANDLE = "forjadaalma.oficial"
BRAND = "Forja da Alma"
TIMEZONE = "America/Sao_Paulo"

P = "#C8892C"    # BRAND_PRIMARY
PL = "#E3B566"   # BRAND_LIGHT
PD = "#8A5A17"   # BRAND_DARK
LBG = "#F5EFE4"  # LIGHT_BG
LBR = "#E6DCCB"  # LIGHT_BORDER
DBG = "#171411"  # DARK_BG
MUTED = "#8A8178"
GRAD = f"linear-gradient(165deg, {PD} 0%, {P} 50%, {PL} 100%)"

FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700'
    '&family=Playfair+Display:ital,wght@0,300;0,400;0,600;0,700;1,600;1,700&display=swap">'
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
    else:
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


LOGO_URI = data_uri(LOGO)

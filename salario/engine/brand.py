"""Identidade visual Salário Organizado (fonte única do motor de vídeo)."""
HANDLE = "salario.organizado"
BRAND = "Salário Organizado"
SITE = "salarioorganizado.netlify.app"
TIMEZONE = "America/Sao_Paulo"

BG = "#f6f8f7"; INK = "#14231f"; MUTED = "#56675f"; LINE = "#dbe4e0"
GREEN = "#0f7a5c"; DEEP = "#0b5d46"; MINT = "#e1f2ec"; MINT2 = "#8ccfb9"
WARM = "#b5651d"; WARM_SOFT = "#fbebdd"; RED = "#c0392b"; RED_SOFT = "#fdecea"; YELLOW = "#ffe08a"

FONTS_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:'
              'opsz,wght@12..96,600;12..96,800&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap">')

LOGO_SVG = ('<svg viewBox="0 0 18 18"><g fill="{fg}"><rect x="2" y="1" width="14" height="3" rx="1"/><rect x="2" y="1" width="3" height="8" rx="1"/>'
            '<rect x="2" y="7.5" width="14" height="3" rx="1"/><rect x="13" y="7.5" width="3" height="9" rx="1"/><rect x="2" y="14" width="11" height="3" rx="1"/></g>'
            '<rect x="13" y="14" width="3" height="3" rx="1" fill="#e9a35a"/></svg>')

# Chamada final por plataforma (texto na tela, narração).
CTA = {
    "ig": {"kw": "PLANILHA", "line": "Comenta <b>PLANILHA</b> que eu te mando a grátis no direct.",
           "say": "Comenta planilha aqui embaixo que eu te mando a minha grátis no direct."},
    "tt": {"kw": "PLANILHA", "line": "Comenta <b>PLANILHA</b> no nosso Instagram, <b>@salario.organizado</b>, que eu te mando.",
           "say": "Comenta planilha no nosso Instagram, arroba salário ponto organizado, que eu te mando a grátis."},
    "yt": {"kw": "LINK NO PERFIL", "line": "A planilha grátis está no <b>link do perfil</b>.",
           "say": "A planilha grátis está no link do perfil. Se inscreve para o próximo."},
}

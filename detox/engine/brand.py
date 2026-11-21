"""Identidade visual Totalmente Saudável (fonte única do motor de vídeo da pasta detox/)."""
HANDLE = "insta.totalmentesaudavel"
BRAND = "Totalmente Saudável"
SITE = "detoxdeacucar.netlify.app"
FREE = "detoxdeacucar.netlify.app/receitas"   # isca grátis (5 receitas doces sem açúcar)
PIN_CTA = "Receitas grátis"
TIMEZONE = "America/Sao_Paulo"

# Mesmas chaves do motor do Salário Organizado, com a paleta roxo e rosa da página de vendas.
BG = "#f7f1fa"; INK = "#2a1233"; MUTED = "#6b5a72"; LINE = "#e6d9ec"
GREEN = "#5b2a6e"      # fundo da CTA (roxo da marca)
DEEP = "#3d1a4a"; MINT = "#f4e9f8"; MINT2 = "#f3a6dc"   # rótulos
WARM = "#d2691e"; WARM_SOFT = "#fbebdd"; RED = "#c0392b"; RED_SOFT = "#fdecea"
YELLOW = "#ffc6ea"     # destaque (rosa claro)
BGD = "#140c1f"        # fundo escuro do vídeo

FONTS_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:'
              'opsz,wght@12..96,600;12..96,800&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap">')

# Folha estilizada.
LOGO_SVG = ('<svg viewBox="0 0 18 18"><path fill="{fg}" d="M15.5 2.5C8 2.5 3 6 3 11.5c0 1.3.4 2.5 1 3.5l-1.5 1.5 1 1L5 16c1 .6 2.2 1 3.5 1 '
            '5.5 0 7-5 7-14.5z"/><path d="M5.5 14.5c2-3 4.5-5.5 7.5-7.5" stroke="#f39ad8" stroke-width="1.4" fill="none" stroke-linecap="round"/></svg>')

# Chamada final por plataforma (texto na tela, narração). Só prometer o que acontece de verdade.
CTA = {
    # Instagram: a Zorcha manda as 5 receitas no direct quando a pessoa comenta RECEITA.
    "ig": {"kw": "RECEITA", "line": "Comenta <b>RECEITA</b> que eu te mando as 5 receitas grátis no direct.",
           "say": "Comenta receita aqui embaixo que eu te mando as cinco receitas grátis no direct."},
    # TikTok: conta pessoal, sem resposta automática e sem link clicável (só com 1.000 seguidores).
    "tt": {"kw": "SEGUE AQUI", "line": f"E tira print: receitas grátis em<br><b class=\"url\">{FREE}</b>",
           "say": "Segue o perfil para ver a próxima. E tira print: o endereço das receitas grátis está aqui."},
    "yt": {"kw": "LINK NO PERFIL", "line": "As 5 receitas grátis estão no <b>link do perfil</b>.",
           "say": "As cinco receitas grátis estão no link do perfil. Se inscreve para a próxima."},
}

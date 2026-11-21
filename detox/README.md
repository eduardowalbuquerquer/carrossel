# Totalmente Saudável (detox/)

Fábrica de vídeos curtos do produto "Detox de Açúcar em 3 Dias" (marca Totalmente Saudável).
Cópia do motor do Salário Organizado (`salario/engine`) com a identidade roxo e rosa em `engine/brand.py`
e voz feminina pt-BR do Gemini TTS (`Kore`, definida em `engine/tts.py`; idioma travado em pt-BR).

- Cenas: `assets/cenas/` (20 imagens geradas no Gemini pelo Eduardo, pasta do Drive "Totalmente Saudável - Cenas"). Toda cena mostra o selo "Imagem gerada por IA".
- Site: https://detoxdeacucar.netlify.app/ · isca grátis: /receitas/ (5 receitas doces sem açúcar).
- CTA: Instagram "Comenta RECEITA" (Zorcha); TikTok "Segue o perfil" + "tira print" do endereço /receitas; YouTube "link do perfil"; Pinterest só imagem (pin.jpg).
- Regra de saúde: o vídeo ensina, a página vende, nada promete resultado no corpo (sem emagrecer, desinchar, toxinas, doença). Dado só com fonte conferida na tela.
- Amostras (aguardando aprovação, nada publicado): `posts/a01-*`, `a02-*`, `a03-*`.

Render: `cd detox/engine && python3 render_video_v2.py ../posts/<pasta>/spec.json --so tt`
Publicação e rotina ainda não ligadas (precisam do OK do Eduardo).

# Totalmente Saudável (detox/)

Fábrica de vídeos curtos do produto "Detox de Açúcar em 3 Dias" (marca Totalmente Saudável).
Cópia do motor do Salário Organizado (`salario/engine`) com a identidade roxo e rosa em `engine/brand.py`
e voz feminina pt-BR do Gemini TTS (`Kore`, definida em `engine/tts.py`; idioma travado em pt-BR).

- Cenas: `assets/cenas/` (20 imagens geradas no Gemini pelo Eduardo, pasta do Drive "Totalmente Saudável - Cenas"). Toda cena mostra o selo "Imagem gerada por IA".
- Site: https://detoxdeacucar.netlify.app/ · isca grátis: /receitas/ (5 receitas doces sem açúcar).
- CTA: Instagram "Comenta RECEITA" (Zorcha); TikTok "Segue o perfil" + "tira print" do endereço /receitas; YouTube "link do perfil"; Pinterest só imagem (pin.jpg).
- Regra de saúde: o vídeo ensina, a página vende, nada promete resultado no corpo (sem emagrecer, desinchar, toxinas, doença). Dado só com fonte conferida na tela.
- Amostras aprovadas em 21/11/2026. Fila: `fila.json` (14 roteiros, 22 a 28/11), rotina em `ROTINA.md`.

Render: `cd detox/engine && python3 render_video_v2.py ../posts/<pasta>/spec.json --so tt`
Publicar: `python3 publish.py ../posts/<pasta> --so tt,pin[,fb]` (Buffer da marca, chave DETOX_BUFFER_KEY).

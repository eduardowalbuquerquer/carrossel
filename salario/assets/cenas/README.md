# Biblioteca de cenas (fundos com pessoas)

Imagens verticais 9:16 geradas pelo Eduardo no app Gemini (Nano Banana, plano Google AI Pro, R$ 0 extra).
Fluxo: Eduardo sobe no Drive dele (pasta "Salário Organizado - cenas") → uma sessão com o conector Google Drive
baixa e grava aqui → o motor usa no campo "bg" das cenas.

- `cenas.json` lista cada arquivo com tema e emoção, para a rotina escolher a cena certa por roteiro.
- Uso no spec: `"bg": "cenas/cena-01-fatura-choque.jpg"` (caminho relativo a salario/assets/).
- Toda cena com fundo de IA mostra o selo "Imagem gerada por IA" (exigência TikTok/Meta para conteúdo realista de IA).
  Foto de banco licenciado: `"bg": {"src": "...", "ia": false}`.
- Não reusar a mesma cena em 2 vídeos seguidos.
- Nunca usar foto do Eduardo nem de pessoa real identificável sem licença.

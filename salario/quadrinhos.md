# Carrossel em quadrinhos (Bia e Rafa)

Aprovado pelo Eduardo em 16/11/2026 ("Aprovo sim"): **1 carrossel por dia** no Instagram (carrossel do feed) e no TikTok (carrossel de fotos), às 17h40.
Modelo: `posts/q01-parcelas-734/` (spec + imagens + slides). Inspiração: carrossel em HQ de concorrente (história de casal, 14 quadros, "Comente PLANILHA"); **nunca copiar texto, roteiro ou arte de ninguém**.

## Formato
- **10 slides 4:5 (1080x1350)**: 8 quadros (imagem + 2 balões) + 1 slide-prova (a conta em tabela, `tipo: card`) + CTA (o motor gera: Instagram "Comenta PLANILHA"; TikTok "Segue o perfil" + print do endereço).
- **Arco obrigatório:** 1 gancho no meio da crise (número grande no 1º balão) → 2-4 flashback de como chegaram lá (cada gasto "cabe") → 5 a ficha cai (soma total, % da renda) → 6 decisão simples (planilha, regra) → 7 primeiros resultados (números que voltam) → 8 "N meses depois" com final feliz e número → 9 prova (tabela).
- **Balões:** até ~12 palavras cada, frases de gente comum. `<b>` vermelho = gasto/dívida; `<i>` verde = dinheiro que volta. `cap` = caixinha amarela de tempo ("3 meses antes...", "Hoje...", "9 meses depois...").
- **Números verdadeiros:** a conta fecha (some no `spec.conta`), datas de quitação calculadas, nunca chutadas. Sem juros/dados de mercado sem fonte oficial. Sem recomendar investimento.
- **Sem pessoa real, sem marca, sem banco real.** Bia e Rafa são personagens fictícios; não dizer "história real".

## Personagens e estilo (cole SEMPRE este bloco no início de cada prompt de imagem)
```
Warm hand-drawn gouache comic illustration, soft textured brush strokes, muted teal and warm orange palette. Two recurring characters: BIA, a Black Brazilian woman around 30 with curly hair tied in a puff, mustard-yellow loose t-shirt and jeans; RAFA, a brown-skinned Brazilian man around 32 with short black hair, short beard and round glasses, green polo shirt and dark trousers. Modest clothing, everyday body types.
```
Depois: `Scene: <ação, lugar, emoção de cada um>. Leave empty space in the upper third for speech balloons. No text, no letters, no words, no logos anywhere.`
Nunca sexualizar; roupa comum; corpo comum. Outros personagens (vendedor, filho, mãe) podem aparecer, descritos na cena.

## Gerar as imagens (Magnific, plano grátis: 20 imagens/dia, R$ 0)
1. `magnific_start` (confira `freeToday.images` ≥ 8; se faltar, grave `"pulado": "sem cota de imagem"` e pare).
2. Uma chamada `images_generate` por quadro: `prompt` = bloco acima + cena, `aspectRatio` "4:5", `count` 1, **sem `references`** (o plano grátis recusa). Pode disparar as 8 de uma vez.
3. `creations_wait` com os 8 identificadores; `creations_get` (`identifiers`) para pegar `url` (tamanho cheio, 896x1120).
4. Baixe cada uma: `curl -sS -o ../posts/<pasta>/img/pN.png "<url>"` (o host `pikaso.cdnpk.net` está liberado no ambiente).
5. **Confira cada imagem** (`creations_read`): Bia e Rafa reconhecíveis (cores das roupas, cabelo, óculos), sem texto/letra, sem dedos ou rostos deformados, espaço livre no topo. Se uma falhar, gere de novo só aquela (no máximo 12 imagens por carrossel).

## Montar e publicar
- `spec.json` no formato de `posts/q01-parcelas-734/spec.json` (`tipo: carrossel`, `redes: ["ig","tt"]`, `slides`, `cta_titulo`, `captions.ig`, `captions.tt`, `conta`).
- Balões: o topo (y 40 a ~330) é a área livre. Esquerda `x 30, w ~520`; direita `x ~570, w ~470`; o 2º balão um pouco mais baixo (y +100 a +200) para não encostar no 1º. `t` (0-100) = onde fica a ponta, apontando para a cabeça de quem fala. Use `h` (altura mínima) para cobrir algo no fundo.
- `python3 render_carrossel.py ../posts/<pasta>` → `c01.jpg`…`c10.jpg` + `c10-tt.jpg`. **Abra uma prévia e confira**: balão cobrindo rosto, ponta apontando para a pessoa errada, texto cortado, conta da tabela. Ajuste e renderize de novo.
- Publicar: `python3 publish.py ../posts/<pasta> --so ig,tt` (Instagram carrossel; TikTok fotos pelo Buffer com rótulo de IA ligado). Idempotente (`resultado.json`).

## Legendas
- `ig`: 1ª linha = gancho com o número; 2-3 parágrafos curtos; termina com uma pergunta + "💬 Comenta PLANILHA que eu te mando a planilha grátis no direct." + 5 hashtags.
- `tt`: gancho curto + pedido de comentário que não promete nada + "➕ Segue para o próximo! 📸 Tira print do final: planilha grátis em salarioorganizado.netlify.app/mini (digite no navegador)". Nunca "comenta PLANILHA" no TikTok.

## Pautas (uma por dia, em ordem; marque em `fila_carrossel.json`)
1. Parcelas pequenas que somam R$ 734 (feito: q01).
2. O 13º que sumiu em 1 semana (Natal parcelado) → plano do 13º.
3. Cartão de crédito usado como extensão do salário → fatura maior que o limite "de verdade".
4. Aumento de R$ 400 que virou gasto (delivery, streaming, app) → aumento guardado primeiro.
5. Empréstimo para pagar outro empréstimo → lista de dívidas e ordem de quitação (bola de neve).
6. Mercado do mês sem lista vs. com lista → diferença no mês e no ano.
7. Ajudar a família todo mês sem combinar valor → teto mensal combinado.
8. "Depois eu vejo" a fatura → 15 minutos por semana olhando o dinheiro.
9. Reserva de emergência do zero com R$ 50 por mês → quanto vira em 12 meses (sem rendimento prometido).
10. Pequenos gastos diários (café, lanche, corrida de app) → soma do mês.

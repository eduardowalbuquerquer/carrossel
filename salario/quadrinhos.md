# Carrossel em quadrinhos (Bia e Rafa)

Aprovado pelo Eduardo em 16/11/2026 ("Aprovo sim"): **1 carrossel por dia** no Instagram (carrossel do feed) e no TikTok (carrossel de fotos), às 17h40.
Modelo: `posts/q01-parcelas-734/` (spec + imagens + slides). Inspiração: carrossel em HQ de concorrente (história de casal, 14 quadros, "Comente PLANILHA"); **nunca copiar texto, roteiro ou arte de ninguém**.

## Formato
- **10 slides 4:5 (1080x1350)**: 8 quadros (imagem + 2 balões) + 1 slide-prova (a conta em tabela, `tipo: card`) + CTA (o motor gera: Instagram "Comenta PLANILHA"; TikTok "Segue o perfil" + print do endereço).
- **Arco obrigatório:** 1 gancho no meio da crise (número grande no 1º balão) → 2-4 flashback de como chegaram lá (cada gasto "cabe") → 5 a ficha cai (soma total, % da renda) → 6 decisão simples (planilha, regra) → 7 primeiros resultados (números que voltam) → 8 "N meses depois" com final feliz e número → 9 prova (tabela).
- **Balões:** até ~12 palavras cada, frases de gente comum. `<b>` vermelho = gasto/dívida; `<i>` verde = dinheiro que volta. `cap` = caixinha amarela de tempo ("3 meses antes...", "Hoje...", "9 meses depois...").
- **Números verdadeiros:** a conta fecha (some no `spec.conta`), datas de quitação calculadas, nunca chutadas. Sem juros/dados de mercado sem fonte oficial. Sem recomendar investimento.
- **Sem pessoa real, sem marca, sem banco real.** Bia e Rafa são personagens fictícios; não dizer "história real".

## Personagens e estilo (aprovado pelo Eduardo em 20/11/2026)
Estilo: gibi infantil brasileiro (cabeça grande, olhos redondos, contorno preto grosso, cores chapadas). Inspiração tipo Turma da Mônica, **sem copiar personagem, traço ou marca**.

**Ficha (model sheet) obrigatória:** `quadrinhos/ficha-bia-rafa.jpg` (no Magnific: criação `UPvkJDrwny`). Todo quadro é gerado com ela como referência. Os dois são SEMPRE iguais:

| | Bia | Rafa |
|---|---|---|
| Pele | marrom-escura | morena (marrom média) |
| Cabelo | 1 coque afro no alto da cabeça, elástico vermelho, brinquinho dourado | curto espetado preto, óculos redondos pretos, barbinha no queixo |
| Roupa | camiseta amarela, jeans azul-escuro, tênis branco | polo verde, jeans azul, sapato marrom |
| Altura | baixa | uma cabeça mais alto que a Bia |

Começo de todo prompt (cole sempre):
```
Use the reference image as the exact character design: same Bia and Rafa, same skin tones, same hair, same clothes, same heights (Rafa one head taller), same comic style with thick black outlines and flat colors. New scene, 4:5 comic panel:
```
Depois: `<lugar + hora do dia>, <enquadramento>. <ação de cada um>. The upper third of the panel is plain empty wall. No panel border, no speech bubbles, no text, no letters, no logos.`
Nunca sexualizar; roupa comum; corpo comum. Outros personagens (vendedor, filho, mãe) só se o roteiro pedir, descritos na cena.

## Cenário coerente com o roteiro
- Antes de gerar, escreva a lista de cenas: quadro → lugar, hora do dia (dia/noite) e quem está. O lugar tem que ser o que o balão conta (compra de celular = loja de celular; conta no fim do mês = casa).
- **Mesmo lugar em quadros diferentes** (ex.: "Hoje" no sofá nos quadros 1 e 5): passe o 1º quadro desse lugar como 2ª referência (`references: [ficha, quadro]`) e escreva "the same <sofá/cozinha> as the second reference image".
- Final da história volta para casa (mesma sala/cozinha do começo).

## Gerar as imagens (Magnific, plano grátis: 20 imagens/dia, R$ 0)
1. `magnific_start` (confira `freeToday.images` ≥ 10; se faltar, grave `"pulado": "sem cota de imagem"` e pare).
2. Uma chamada `images_generate` por quadro: `prompt` = início fixo + cena, `aspectRatio` "4:5", `references: [{"type":"image","identifier":"UPvkJDrwny"}]` (+ quadro do mesmo lugar, se houver). O plano grátis aceita até 4 referências do tipo `image`; o tipo `character` é pago.
3. `creations_wait`; baixe cada `url` com `curl` (sai 1824x2288; o host `pikaso.cdnpk.net` está liberado no ambiente).
4. **Conferência obrigatória, quadro a quadro** (abra cada imagem; amplie a parte de baixo):
   - Anatomia: 2 braços, 2 pernas, 5 dedos, um rosto por pessoa; nada sobrando ou faltando (o Rafa de 3 pernas do q01 nunca mais).
   - Aparência: pele, cabelo, óculos, roupa e altura iguais à ficha.
   - Cenário: lugar e hora batem com o roteiro e com os outros quadros do mesmo lugar.
   - Sem balão, letra, moldura ou risco desenhado pela IA. Moldura preta pode ser cortada (corte por dentro e volte para 4:5); balão/letra: refaça.
   - Cenas seguras: sentados, atrás de mesa ou da cintura pra cima. Nada de ajoelhar, cruzar pernas ou abraço embolado.
   Quadro reprovado: gere de novo só ele (no máximo 12 imagens por carrossel). Se não passar, grave `"pulado"` com o motivo e avise o Eduardo; nunca publique quadro com defeito.

## Montar e publicar
- `spec.json` no formato de `posts/q01-parcelas-734/spec.json` (`tipo: carrossel`, `redes: ["ig","tt"]`, `slides`, `cta_titulo`, `captions.ig`, `captions.tt`, `conta`).
- Balões: o topo (y 20 a ~330) é a área livre; o contador (n/10) fica no rodapé. Esquerda `x 30, w ~520`; direita `x ~570, w ~470`; o 2º balão um pouco mais baixo (y +100 a +200) para não encostar no 1º. `t` (0-100) = onde fica a ponta, apontando para a cabeça de quem fala. Use `h` (altura mínima) para cobrir algo no fundo.
- `python3 render_carrossel.py ../posts/<pasta>` → `c01.jpg`…`c10.jpg` + `c10-tt.jpg`. **Abra uma prévia e confira**: balão cobrindo rosto, ponta apontando para a pessoa errada, texto cortado, conta da tabela. Ajuste e renderize de novo.
- Publicar: `python3 publish.py ../posts/<pasta> --so ig,tt` (Instagram carrossel; TikTok fotos pelo Buffer. O TikTok não aceita o rótulo de IA da API em post de fotos, por isso o selo fica em cada quadro). Idempotente (`resultado.json`).

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

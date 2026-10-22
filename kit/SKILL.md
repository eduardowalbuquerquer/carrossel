---
name: fabrica-conteudo-social
description: Cria e automatiza conteúdo diário (carrossel/imagem no feed + Reels de chamada) para um perfil de Instagram e/ou Página do Facebook, a partir de um tema; entrevista o dono sobre marca, premissas, séries e fontes de referência.
---

# Fábrica de conteúdo social (Instagram + Facebook)

Replica o processo validado no **Forja da Alma** (@forjadaalma.oficial, no ar desde 2026-10-11):
1 post por dia no feed (carrossel ou imagem única) + 1 Reels de chamada, criados e publicados sem intervenção humana.
O que muda de um perfil para outro é **só o `perfil.json`**: marca, tema, premissas, séries, plataformas e horário.

Analogia: o motor é a **fábrica** (igual para todos); o `perfil.json` é a **receita** de cada cliente; as premissas são o **controle de qualidade** que nenhum produto pode furar.

## Onde está o motor (kit)
Use a primeira fonte que existir:
1. `/mnt/project-files/skills/conteudo-social/kit/` (projeto "Criador de Carrossel").
2. Pasta `kit/` do repositório público `github.com/eduardowalbuquerquer/carrossel` (`git clone --depth 1` e use `kit/`).

Conteúdo do kit:
| Arquivo | Função |
|---|---|
| `novo_perfil.py` | cria a pasta do perfil (motor + perfil.json + ROTINA.md + historico.json + ideias.json) |
| `referencias.py` | lista, adiciona, remove e sorteia as fontes de referência do perfil |
| `engine/brand.py` | lê o perfil.json; deriva a paleta inteira de 1 cor; fontes Google; logo ou inicial |
| `engine/render_post.py` | spec.json → slides 1080×1350 (JPG) + preview.html no padrão das instruções de carrossel |
| `engine/render_reel.py` | bloco `reel` → MP4 9:16 1080×1920 com áudio sintetizado |
| `engine/checar_spec.py` | confere formato, limites de texto, hashtags e lista as premissas para revisão |
| `engine/fetch_photo.py` | foto realista grátis (Pixabay; Pexels se houver chave), sem repetir |
| `engine/publish.py` | publica no Instagram e/ou Página do Facebook; idempotente; `--check`, `--refresh-token` |
| `guias/acesso-instagram.md`, `guias/acesso-facebook.md` | passo a passo do que só o dono libera (tokens, domínios, Pages) |
| `guias/referencias.md` | como as referências são usadas e os 3 jeitos de acrescentar novas (para o dono) |
| `exemplos/forja-da-alma/` | perfil.json completo, logo e 2 specs reais (carrossel e imagem única) |

## Fluxo (em passos)

### Passo 1 · Entrevista do tema
Antes de qualquer arquivo, faça as perguntas abaixo. Pergunte em blocos curtos (no máximo 4 por mensagem), aceite respostas soltas e **proponha um padrão** quando o dono não souber (marque como sugestão). Use o que já estiver na memória do projeto e não pergunte de novo.

**Bloco A · Perfil e marca**
1. Nome do perfil e @ (Instagram) e/ou nome da Página do Facebook.
2. Em quais plataformas publicar: Instagram, Facebook ou ambas?
3. Cor principal (hex ou descrição) e, se houver, logo (arquivo). Sem logo, uso a inicial num círculo.
4. Estilo de fonte: editorial (Playfair Display + DM Sans), moderno (Plus Jakarta Sans), quente (Lora + Nunito Sans), técnico (Space Grotesk), ousado (Fraunces + Outfit), clássico (Libre Baskerville + Work Sans), arredondado (Bricolage Grotesque).

**Bloco B · Tema e público**
5. Qual é o tema, em uma frase? Qual a "tese" central do perfil?
6. Quem é o público (idade, momento de vida, dor principal)?
7. Objetivo principal: seguidores, autoridade, vendas, comunidade, levar para outro canal?
8. Tom de voz (ex.: direto, acolhedor, técnico, bem-humorado) e palavras que **usa** e que **evita**.

**Bloco C · Premissas (o controle de qualidade)**
9. Quais regras o conteúdo **nunca** pode quebrar? (ex. Forja da Alma: "nunca contradizer as Escrituras"; "respeitar o contraditório com amor, sem abrir mão da firmeza").
10. Existe uma **fonte de autoridade** obrigatória? (ex.: Bíblia ARA; Guia Alimentar do Ministério da Saúde; CFM; legislação). Como citar?
11. Assuntos proibidos ou sensíveis (política, promessas de resultado, saúde, finanças, concorrentes)?
12. Como tratar quem discorda (tom com o contraditório)?

Ajude a escrever as premissas: transforme cada resposta numa frase **verificável** ("Nunca prometer cura" é verificável; "ser ético" não é). Sugira premissas típicas do nicho quando faltar alguma:
- Fé/religião: fidelidade ao texto sagrado, citar referência exata, firmeza com respeito.
- Saúde/nutrição/fitness: sem promessa de cura ou resultado garantido, base em diretriz oficial, "não substitui profissional".
- Finanças/investimentos: sem recomendação individual, sem promessa de retorno, aviso de risco (regras CVM).
- Direito: informativo, não substitui advogado, citar a lei.
- Infantil/família: nada que exponha crianças; linguagem segura.

**Bloco D · Calendário e formato**
13. Quantos posts por dia (padrão 1) e horário (padrão 9h, fuso America/Sao_Paulo)? Quer o Reels de chamada (padrão sim)?
14. Séries semanais: proponha 7 (uma por dia), misturando carrossel tipográfico, carrossel informativo (mito x verdade, lista, passo a passo), imagem com foto realista e pergunta de engajamento. Peça só aprovação ou troca.
15. Estilo das fotos (ex.: cinematográfico, claro e minimalista, natureza) e o que evitar.
16. CTA final padrão (frase do último slide e botão "Siga @...").

**Bloco E · Fontes de referência (inspiração, nunca cópia)**
17. Quais fontes você acompanha e quer que eu vasculhe periodicamente em busca de ideias? Vale perfil do Instagram, TikTok ou Facebook, canal do YouTube, podcast, blog, matéria de portal, artigo científico (link ou DOI), livro ou site. Para cada uma, se quiser, diga o foco (ex.: "paternidade").
18. Com que frequência pesquisar (padrão: todo dia, 3 fontes por vez, começando pelas menos consultadas)?
19. Há alguma fonte que **não** deve ser usada?
Explique a regra: das referências se aproveita só a ideia (tema, pergunta, dor do público, notícia); texto, título, roteiro, imagem e layout são sempre próprios. Diga também que novas fontes podem entrar a qualquer momento e mostre os 3 jeitos do `guias/referencias.md` (pedir no chat, comando `referencias.py`, editar o `perfil.json` no GitHub).

Feche a entrevista com um **resumo de 10 linhas** e peça "ok" antes de gerar arquivos.

### Passo 2 · Gerar o perfil
1. Escreva o `perfil.json` no formato do exemplo `exemplos/forja-da-alma/perfil.json` (campos abaixo).
2. Rode `python3 <kit>/novo_perfil.py <pasta_do_perfil> perfil.json [logo]`. Isso cria motor, ROTINA.md (com as premissas por extenso), historico.json e posts/.
3. Mudou o perfil depois? `python3 <kit>/novo_perfil.py <pasta> --rotina` regenera a ROTINA.md.

Campos do `perfil.json`:
- `marca`: `nome`, `handle`, `subtitulo`, `logo` (caminho relativo à pasta do perfil), `cores.primaria` (as demais são opcionais e derivam dela), `fontes.titulo` e `fontes.corpo`.
- `tema`: `nome`, `descricao`, `publico`, `objetivo`, `tom`, `usar[]`, `evitar[]`.
- `premissas[]` (frases verificáveis), `fontes_autoridade` (`nome`, `regras[]`), `limites[]`.
- `plataformas`: `["instagram"]`, `["facebook"]` ou ambos. `credenciais` (opcional): nomes das variáveis quando há vários perfis no mesmo ambiente, ex. `{"ig_token": "IG_ACCESS_TOKEN_MESA", "ig_user": "IG_USER_ID_MESA", "fb_token": "FB_PAGE_TOKEN_MESA", "fb_page": "FB_PAGE_ID_MESA"}`.
- `agenda`: `fuso`, `horario`, `disparo` (12 min antes), `posts_por_dia`, `reel` (true/false).
- `series`: `"1"`..`"7"` → `key`, `name`, `format` (carousel | image), `slides`, `visual`, `brief`.
- `cta`: `tag`, `titulo`, `botao`. `legenda`: `estrutura`, `hashtags_fixas[]`, `hashtags_qtd` [mín, máx].
- `imagens`: `fonte`, `estilo`, `buscas_exemplo[]`, `evitar[]`. `reel`: `efeito` (particulas | nenhum), `audio` (impacto | suave | silencio), `cenas` [mín, máx], `regra`.
- `referencias[]`: `tipo` (instagram, facebook, youtube, tiktok, blog, portal, artigo, podcast, livro, site, outro), `endereco` (@perfil, URL, DOI ou título), `foco`, `adicionada_em`, `consultada_em`. Preencha com `python3 referencias.py <pasta> adicionar <tipo> <endereco> ["foco"]`. `referencias_regras[]` (anti-plágio; há um padrão se faltar) e `referencias_rodada` (`frequencia`, `quantidade`).
- `repo`: `github` (usuario/repo) e `base_url` (GitHub Pages). `nao_repetir_dias` (padrão 60).

### Passo 3 · Primeiro post de amostra (sem publicar)
0. Se houver referências, rode `python3 referencias.py <pasta> rodada 3`, veja o conteúdo recente das fontes sorteadas e anote ideias em `ideias.json` (com a fonte). Escreva o post com palavras próprias.
1. Escreva `posts/AAAA-MM-DD-<serie>/spec.json` (formato em `exemplos/forja-da-alma/spec-*.json`).
   Layouts: `hero`, `photo`, `text`, `list`, `big`, `verse` (citação), `compare`, `cta`. Carrossel termina em `cta`; imagem única = 1 slide.
2. `cd engine && python3 checar_spec.py ../posts/<pasta>/spec.json` → zero ERROS.
3. **Revisão de premissas**: releia slides, legenda e Reels contra cada premissa e cada regra da fonte de autoridade. Citação só com texto exato conhecido; na dúvida, troque.
4. `python3 render_post.py ...` e `python3 render_reel.py ...`; olhe 2 ou 3 slides e 2 quadros do Reels (texto cortado, barra de progresso, português).
5. Mostre a prévia ao dono (preview.html publicado como Artifact ou os JPGs) e ajuste até ele aprovar o visual.

### Passo 4 · Acessos (só o dono pode fazer)
Envie o guia certo, adaptado com o @ e o repositório do perfil:
- Instagram: `guias/acesso-instagram.md` (conta profissional, app da Meta, `IG_ACCESS_TOKEN` + `IG_USER_ID`).
- Facebook: `guias/acesso-facebook.md` (Página, `FB_PAGE_ID` + `FB_PAGE_TOKEN` sem expiração).
- Ambos: ambiente de nuvem com domínios `graph.instagram.com`, `graph.facebook.com`, `rupload.facebook.com`, `pixabay.com`, `cdn.pixabay.com`, `<usuario>.github.io`; repositório **público** com GitHub Pages para servir as mídias (a Meta baixa as imagens de um link público; reserva: jsDelivr `https://cdn.jsdelivr.net/gh/<usuario>/<repo>@{sha}`).
Nunca peça token no chat. Depois que o dono disser "pronto": `python3 publish.py --check`.

### Passo 5 · Publicação de teste e rotina diária
1. Publicar exige **OK explícito do dono** na conversa (é ação externa e visível). Com o OK: `python3 publish.py ../posts/<pasta>` e confira os links em `resultado.json`.
2. Suba a pasta do perfil para o repositório (motor, perfil.json, ROTINA.md, historico.json, posts/).
3. Crie a rotina diária (gatilho agendado) no horário de `agenda.disparo`, com o prompt: "Siga a ROTINA.md do repositório <usuario>/<repo> para publicar o post de hoje." Rotina recorrente = gatilho, não lembrete manual.
4. Registre na memória do projeto: perfil, @, plataformas, repositório, horário, premissas e a sessão/rotina executora.

## Regras que valem para todo perfil
- **Premissas acima de tudo.** Post que fere uma premissa não sai; troque o tema. A ROTINA repete a checagem antes de publicar.
- **Respeito ao contraditório**: corrigir ideias, nunca humilhar pessoas ou grupos; firmeza sem deboche.
- **Não inventar**: citações, números e versículos só com fonte e redação exata conhecida. Resultado de API sempre real; em falha, avisar com o erro exato.
- **Referências são inspiração, nunca cópia**: aproveitar só a ideia; nunca copiar texto, título, roteiro, imagem ou layout, nem republicar conteúdo alheio. Citação literal só curta, entre aspas e com crédito. Toda ideia passa pelas premissas. Se uma fonte não abrir (login, bloqueio de rede), passar para a próxima e dizer isso; nunca inventar o que ela publicou.
- **Novas referências a qualquer momento**: quando o dono pedir ("adicione a referência X ao perfil Y"), rode `referencias.py ... adicionar`, faça commit e push do `perfil.json` e confirme em uma linha.
- **Não repetir** tema, personagem ou citação dentro de `nao_repetir_dias`.
- **Design** (instruções de carrossel): viewport 420×525 exportado a 1080×1350 com device_scale_factor 1080/420; barra de progresso e seta em cada slide (sem seta no último); alternar claro/escuro; título até ~70 caracteres, corpo até ~110; CTA no último slide.
- **Reels de chamada**: gancho de curiosidade sem entregar a resposta; última cena "a resposta está no post de hoje" + "Toque no perfil →".
- **Limites da Meta**: carrossel até 10 imagens; legenda até 2.200 caracteres; 100 publicações por 24h no Instagram; imagens em JPEG.
- **Token do Instagram** vence em 60 dias: renovar dias 1 e 15 (`--refresh-token`). Token de Página do Facebook gerado de token longo não expira.
- Gere HTML/arquivos com Python, nunca com shell (interpolação corrompe `$` e crases).

## Exemplo validado: Forja da Alma
- Tema: hombridade bíblica. Premissas: (1) nunca contradizer as Escrituras; (2) respeitar o contraditório com amor bíblico, sem abrir mão da firmeza. Fonte de autoridade: Bíblia ARA, com referência exata.
- Referências (exemplo no `perfil.json` do kit): 13 perfis do Instagram indicados pelo Eduardo (@doisdedosdeteologia, @adriano.proposito, @augustusnicodemus, @hernandesdiaslopes, @luizsayao, @papodehomembrasil, @paulo.borges.jr, @prpaulogouvea, @purelifeministriesbrasil, @prmocellin, @sebioficial, @henriquefelini, @ohenriquecafe).
- Séries: seg Arquétipos Bíblicos (carrossel 7) · ter Versículo Forjado (foto) · qua Mito x Verdade · qui Frase de Ferro (foto) · sex Manual do Homem · sáb Homens da Bíblia em 60s · dom Pergunta de Domingo.
- Primeiro post publicado 2026-10-11 às 9h: feed https://www.instagram.com/p/DeWltnpHETw/ · Reels https://www.instagram.com/reel/DeWlvrCiJ0-/
- O kit, rodado com o `perfil.json` do Forja, gera slides idênticos pixel a pixel aos do motor em produção.

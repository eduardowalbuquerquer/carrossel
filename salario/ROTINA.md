# Rotina diária Salário Organizado (instruções para a sessão agendada)

Você é a fábrica de vídeos curtos do @salario.organizado (organização financeira para quem ganha de 1 a 5 salários mínimos).
Todo dia, sem intervenção humana, **4 vídeos novos no formato v3** (aprovado pelo Eduardo em 15/11/2026: "aprovo o v3"):
- **v1 às 12h** (Reels + Shorts + TikTok + Pinterest + Página do Facebook)
- **v3 às 16h** (TikTok + YouTube Shorts + Pinterest)
- **v2 às 19h** (TikTok + YouTube Shorts + Pinterest)
- **v4 às 21h30** (TikTok + YouTube Shorts + Pinterest)
- **YouTube nos 4 horários desde 17/11/2026** (pedido do Eduardo: é onde mais clicam para a planilha grátis; o link do canal leva direto ao site).
Remix (trocar só o gancho) acabou: os 4 são vídeos novos. **Os textos das tarefas agendadas são antigos** (falam em remix, "v1 do mesmo dia com outro gancho", `--so tt` ou rascunho): onde divergirem, **vale esta ROTINA** (vídeo novo v3, publicar `--so tt,yt,pin`; o v4 não depende do v1 ter saído). Cota de voz: o motor faz **1 pedido de voz por vídeo e por rede** (v1 = 3 pedidos, cada um dos outros = 2: TikTok e YouTube). Total ~9 por dia; se o modelo principal bater o limite, o `tts.py` cai nos modelos reserva (mesma voz Charon, pt-BR).

## Série "Sabedoria milenar" (slot v3 das 16h, de 17/11 a 02/12/2026)
Aprovada pelo Eduardo em 16/11/2026 ("Aprovo, 1 por dia às 16h"). Os dias 23 a 38 de `fila.json` já têm o **v3** apontando para `posts/smNN-*/spec.json` (16 roteiros prontos; lista e fontes no doc https://claude.ai/artifact/MLmAXGRDF48NBySzFN33pF). Nesses dias, a rotina das 16h só renderiza (`--so tt,yt`) e publica (`--so tt,yt,pin`).
- **Não altere a citação, a referência (`source`) nem o "Em resumo"** da cena `fact`: foram conferidas na fonte. Só encurte outras falas se passar de 22 s.
- Os outros slots (v1, v2, v4) desses dias seguem a regra de fila vazia: grave o item novo **dentro do mesmo dia** (`dia` 23 = 17/11, 24 = 18/11 ... 38 = 02/12), sem criar outro item com o mesmo número.
- Fora da série, não use citação antiga nova sem fonte conferida (veja a lista de frases falsas no doc).

## Carrossel em quadrinhos (desde 16/11/2026, 1 por dia às 17h40)
Tarefa agendada própria ("carrossel da tarde"), com o conector Magnific. Siga `quadrinhos.md` e a fila `fila_carrossel.json`.
Publica com `python3 publish.py ../posts/<pasta> --so ig,tt` (carrossel no Instagram, fotos no TikTok pelo Buffer). Não mexe nos 4 vídeos.

## Formato v3 (obrigatório desde 15/11/2026; tudo do v2 abaixo continua valendo)
- **Pessoas na tela:** toda cena (menos `cta`, opcional) leva `"bg": "cenas/<arquivo>.jpg"` da biblioteca `../assets/cenas/` (20 imagens geradas no Gemini pelo Eduardo). Escolha pelo `cenas.json` (temas e emoção): gancho com emoção forte (choque, ansiedade, tensão, constrangimento); passos com foco/organização; fim com alívio/conquista. **Não use a mesma imagem no gancho de 2 vídeos seguidos** (veja os 3 últimos specs publicados). O motor põe sozinho o selo "Imagem gerada por IA".
- **Gancho de notificação** (use em pelo menos 2 dos 4 vídeos do dia): `"notif": {"app": "Cartão de crédito", "title": "Parcela 1 de 14", "msg": "Valor: <b>R$ 210,00</b>", "when": "agora"}` na cena `hook`. Nunca nome de banco real. O valor da notificação tem que bater com a conta do vídeo.
- **15 a 22 s**, uma ideia por vídeo, 3 ou 4 cenas (`hook`, 1 ou 2 de prova/passos, `cta`). Modelos: `../posts/amostra-v3-parcela`, `amostra-v3-15reais`, `amostra-v3-casal`.
- **Pinterest:** o motor gera `pin.jpg` (arte 2:3, 1000x1500, com a foto, o número e "Planilha grátis →"), que o publish usa no lugar da capa. Pin de vídeo não leva link, por isso o Pinterest recebe imagem. **Sempre** escreva `captions.pin_title` começando pela palavra que a pessoa busca no Pinterest, antes de dois-pontos (vira a etiqueta amarela da arte): ex. "Planilha de dívidas: quanto você deve de verdade", "Como economizar no mercado: ...", "Organização financeira para casal: ...". E `captions.pin` com 2 a 3 frases de descrição com palavras de busca, sem hashtag. **Pin com curiosidade** (pedido do Eduardo: a arte tem que despertar curiosidade para a pessoa ler o texto e clicar): escreva sempre `"pin_card"` com `title` em forma de pergunta ou laço aberto que a resposta só aparece no site (ex.: "Por que R$ 210 por mês <em>viram R$ 2.940?</em>", "O gasto que some com <em>R$ 450 por mês</em>") e `cta` de ação ("Veja a conta e faça a sua →", "Descubra qual é o seu →"). Campos opcionais: `value`, `label` (vazio `""` tira o número grande). A descrição (`captions.pin`) termina prometendo o que a pessoa vai descobrir no site. Modelos nos 3 specs `amostra-v3-*`.

## Formato v2 (obrigatório desde 14/11/2026)
- Motor: `render_video_v2.py` (nunca mais o `render_video.py` para vídeo novo). Legenda grande palavra por palavra, algo mudando a cada 1 a 2 s, números que contam, efeitos sonoros próprios.
- **Até 30 s no total** (trava aprovada pelo Eduardo). Se passar de 30 s, encurte a narração e renderize de novo antes de publicar.
- **Voz sempre em português do Brasil.** O idioma está travado em `engine/tts.py` (`LANG = "pt-BR"`). Nunca mude, nem use voz ou modelo de outro idioma, salvo pedido explícito do Eduardo. Se a API recusar o idioma, a voz falha: não publique sem voz, avise.
- Cada cena tem `say` (narração, números por extenso) e, quando houver número, `show` (o mesmo texto com dígitos, **mesmas frases e mesma pontuação**), que vira a legenda.
- Em cena `steps`, escreva o `say` com uma frase de abertura e depois **uma frase por item** (separadas por ponto, sem vírgula nem dois-pontos no meio): cada item entra na tela junto com a sua frase.
- Gancho: número grande em `hook.value` e título curto (até 6 palavras). Sem `sub` nem `tag`.

Tudo serve ao cronograma do Projeto 10K: `/mnt/project-files/canais/plano-lancamento-canais.md` (21 roteiros e calendário). A ordem está em `salario/fila.json`.

## Premissas inegociáveis
1. **Identidade:** só a marca "Salário Organizado" e salario.organizado@gmail.com. Nunca o nome, CPF ou e-mail pessoal do Eduardo. Não inventar história pessoal ("eu estava endividado") nem depoimento.
2. **Números verdadeiros:** dado de mercado só com fonte na tela (`source`), conferida em fonte oficial (Banco Central, planalto.gov.br, CNC). Data de quitação só se calculada; nunca chutada. Cenários ("ganho R$ 2.300") somam certo: confira a conta antes de renderizar.
3. **Sem recomendação de investimento específico** (CVM). Fale de organização, dívida e hábito.
4. **Persuasão em toda peça:** gancho nos 3 primeiros segundos (número concreto, dor ou curiosidade), problema, prova (número/conta na tela), virada (solução simples), CTA da plataforma. Legenda: 1ª linha = gancho; pedir comentário (PLANILHA) e compartilhamento.
5. **CTA por rede: só prometa o que acontece de verdade** (cobrança do Eduardo em 15/11/2026). O motor já fala e mostra a CTA certa de cada vídeo (`engine/brand.py`); a legenda tem que bater com ela:
   - **Instagram:** "Comenta PLANILHA" (a Zorcha manda a mini-planilha no direct; funciona).
   - **TikTok:** NUNCA "comenta PLANILHA" nem "link clicável": conta pessoal não tem resposta automática e o link só fica clicável com 1.000 seguidores. A CTA tem 2 tempos (pedido do Eduardo em 15/11/2026): **1º "Segue o perfil"** (meta: 1.000 seguidores para liberar o link na bio) e **2º "tira print"** do endereço `salarioorganizado.netlify.app/mini`, que aparece grande na tela. Legenda `tt` termina com "➕ Segue para o próximo! 📸 Tira print do final: planilha grátis em salarioorganizado.netlify.app/mini (digite no navegador)". Para engajar, peça um comentário que não promete nada (ex.: "Comenta quanto você acha que deve").
   - **YouTube:** "link do perfil" (link na seção Links do canal) + link na descrição.
   - **Facebook:** recebe o vídeo do TikTok (endereço na tela) e a legenda com o link clicável. Nunca "comenta PLANILHA".
   - **Pinterest:** o próprio pin leva ao site (botão "Acessar o site").
6. **Gancho:** siga `ganchos.md` (número grande no 1º quadro com `hook.value`, 1ª fala até 12 palavras, resposta até 10 s, até 30 s no total). Sem `tag` nem "olha o porquê".

## Ambiente
```
cd <clone do repo> && git pull -q origin main
pip install -q playwright pillow numpy
export PAGES_REPO_DIR=$(pwd) PAGES_BASE_URL=https://eduardowalbuquerquer.github.io/carrossel
cd salario/engine
```
Variáveis: `SO_IG_ACCESS_TOKEN`, `SO_IG_USER_ID`, `SO_YT_CLIENT_ID`, `SO_YT_CLIENT_SECRET`, `SO_GEMINI_KEY`, `SO_TT_CLIENT_KEY`, `SO_TT_CLIENT_SECRET` (Sandbox). Tokens de YouTube e TikTok ficam em `/mnt/project-files/canais/automacao/.segredos/`.

## Passo a passo
1. **Qual vídeo.** Leia `../fila.json`: primeiro item com o slot de agora (v1, v2, v3 ou v4) sem `publicado_em`.
   - **Fila vazia (sem item para o slot de agora):** escreva um item novo no formato v3: um tema campeão refeito (`refeito_de`, veja métricas; "quanto você deve de verdade" é o campeão) ou uma pauta nova do plano. Não repita o tema de nenhum dos 4 vídeos anteriores. Grave na fila (dia de hoje, slot de agora) e siga.
   - v2, v3 e v4: renderize com `--so tt,yt` e publique com `--so tt,yt,pin`. Se só o `video_tt.mp4` existir (renderizado antes de 17/11), renderize de novo com `--so yt` (gasta 1 pedido). Se a voz falhar (cota do dia), grave `"pulado": "<motivo>"` no slot e pare: não publique sem voz.
2. **Roteiro.** Se o item já tem `pasta` com `spec.json`, use. Senão, escreva `../posts/rNN-<tema>/spec.json` a partir da linha do roteiro no plano, no formato de `../posts/r01-salario-2300/spec.json`:
   - cenas: `hook` (com `value`, `value_label`, `tone`; ver `ganchos.md`), `list` (renda + gastos; a soma mostra sobra/falta), `number` (valor grande + `source`), `compare` (de → para), `steps` (até 3 itens), `cta`. Sempre começa em `hook` e termina em `cta`.
   - `say` de cada cena = a narração (frases curtas, números por extenso quando a voz tropeçar). No total, até 30 s (formato v2).
   - `captions`: `ig`, `tt` (termina com "➕ Segue para o próximo! 📸 Tira print do final: planilha grátis em salarioorganizado.netlify.app/mini (digite no navegador)"; nunca "Comenta PLANILHA"), `yt_title` (até 60 caracteres + #shorts), `yt_desc` (com o link do site e utm_source=youtube).
   - Pauta nova: antes, veja o que está funcionando nos perfis de `../referencias.md` e escreva **com palavras nossas**; nunca copie roteiro, frase ou arte.
3. **Renderizar.** Se a pasta já tem os vídeos do formato v2 (`video_ig.mp4` no v1, `video_tt.mp4` e `video_yt.mp4` nos outros, e `pin.jpg`) e o item da fila diz `"renderizado": "v3"`, pule para o passo 4. Senão: `python3 render_video_v2.py ../posts/<pasta>/spec.json` (v1) ou `python3 render_video_v2.py ../posts/<pasta>/spec.json --so tt,yt` (v2, v3, v4). O mesmo comando gera o `pin.jpg`. A saída mostra a duração: se passar de 30 s, encurte e renderize de novo. (Motor antigo, só para vídeo antigo: `python3 render_video.py ...` (gera `video_ig.mp4`, `video_tt.mp4`, `video_yt.mp4` e `capa.jpg`; voz Gemini TTS grátis, trilha própria sem direitos autorais, áudio normalizado em -14 LUFS).
4. **Conferir.** Abra o `pin.jpg` e veja se o texto cabe e o rosto aparece. Extraia 4 quadros (`ffmpeg -ss <t> -i video_ig.mp4 -frames:v 1 q.png`) e veja: texto cortado, legenda sobre o conteúdo, português, soma dos números. Ouça a duração: se `narração não` aparecer na saída, a voz falhou; avise antes de publicar.
5. **Publicar.** v1: `python3 publish.py ../posts/<pasta>` (Instagram, YouTube, TikTok, Pinterest e Página do Facebook); v2, v3 e v4: `python3 publish.py ../posts/<pasta> --so tt,yt,pin`. Antes de publicar, confira se o spec tem `captions.yt_title` (até 60 caracteres + #shorts) e `captions.yt_desc` (com o link do site e utm_source=youtube); **se faltar (ex.: specs `sm*` antigos), escreva e grave no spec**.
   - Pinterest: pin de imagem (`pin.jpg` 2:3 do v3; sem ele, a capa do vídeo) pelo Buffer (canal grátis; pin de vídeo perde o link), na pasta `SO_PIN_BOARD` (ou a 1ª), com link clicável para o site e `utm_source=pinterest`. Opcional: `captions.pin_title` (até 100 caracteres, com palavra de busca, ex.: "Planilha de gastos: ...") e `captions.pin` (descrição sem hashtag). Sem eles, usa o título do YouTube e a legenda do Instagram. Enquanto o Pinterest não estiver conectado no Buffer, o publish pula essa rede sem erro. É idempotente (`resultado.json`).
   - TikTok: publica **pelo Buffer** (plano grátis, modo automático, conta pessoal; limite 25 posts/dia), usando `SO_BUFFER_KEY`. O TikTok recusou a auditoria do app próprio em 01/11/2026, então a publicação direta não existe.
   - Página do Facebook (`fb`): o v1 também sai como Reel na Página "Salário Organizado" **pelo Buffer** (vídeo do TikTok, com o endereço na tela; a legenda leva o link `salarioorganizado.netlify.app/mini/?utm_source=facebook`). Post feito pela API do Instagram não passa pelo "compartilhar no Facebook" da Central de Contas, por isso a publicação é direta. Se a Página não estiver conectada no Buffer, o `fb` é pulado sem erro. Não mande v2, v3 e v4 para o Facebook (eles usam `--so`, que já deixa o `fb` de fora).
   - Se o Buffer falhar, o `publish.py` manda o vídeo como **rascunho** (plano B) e `tt_status` fica `SEND_TO_USER_INBOX`. Só nesse caso avise o Eduardo: "abrir o TikTok, tocar na notificação, colar a legenda de `legendas`, publicar", junto com o aviso de erro do Buffer.
6. **Registrar.** Em `../fila.json` grave `publicado_em` e os links do `resultado.json`. Commit e push.
7. **Comentários.** Na rotina das 12h, responda à mão (texto curto e humano) comentários que não sejam PLANILHA, se houver acesso; nunca prometa o que o produto não faz.
8. **Token.** Dias 1 e 15: `python3 publish.py --refresh-token`. `python3 publish.py --check` mostra o estado das redes e dos canais do Buffer (TikTok, Pinterest e Facebook).
9. **Falhas.** Nunca invente resultado. Se uma rede falhar, as outras seguem; avise o Eduardo com o erro exato e o que ele precisa fazer.

## Depois do dia 14 (histórico; desde 14/11/2026 vale o formato v2 acima)
Repita a estrutura dos vídeos que mais trouxeram comentários PLANILHA (veja as métricas e o painel da Zorcha). Os slots v3 e v4 levam o TikTok a 4 vídeos por dia (desde o dia 12). Cota de voz: ~10 pedidos/dia por modelo; um vídeo novo gasta ~6 e um remix ~1 (cache em `/mnt/project-files/canais/automacao/cache_tts`).

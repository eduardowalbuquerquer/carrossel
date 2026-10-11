# Fontes de referência · como funcionam e como acrescentar

As referências são a **despensa de ideias** do perfil: a automação olha o que essas fontes estão discutindo e cozinha um prato próprio. Ela nunca serve o prato do vizinho.

## O que vale como referência
Perfis do Instagram, TikTok ou Facebook, canais do YouTube, podcasts, blogs, matérias de portais jornalísticos, artigos científicos (link ou DOI), livros e sites.

## Regra de ouro (anti-plágio)
1. Da referência se aproveita **só a ideia**: o tema, a pergunta, a dor do público, a notícia.
2. Texto, título, roteiro, imagem e layout são **sempre próprios**. Nada de copiar frase, "traduzir com outras palavras" um post inteiro ou republicar.
3. Citação literal, só curta, entre aspas e com crédito (ou da fonte de autoridade do perfil, como um versículo).
4. Toda ideia passa pelas **premissas** do perfil. Ideia que contradiz uma premissa é descartada.

## Como a automação usa (todo dia)
1. Sorteia as 3 fontes **menos consultadas** (assim todas entram na roda).
2. Vê o conteúdo recente delas (busca na web, perfil público, canal, artigo).
3. Anota 1 a 3 ideias em `ideias.json`, com a fonte.
4. Escolhe a ideia que combina com a série do dia e escreve o post do zero.
5. Registra no `historico.json` qual referência inspirou o post.

Se uma fonte não abrir (o Instagram costuma pedir login para ver perfis), a automação passa para a próxima e registra isso. Ela não inventa o que a fonte publicou.

## Como acrescentar uma referência (3 jeitos)

**Jeito 1 · Pedir aqui no chat (o mais fácil)**
Escreva, por exemplo:
> Adicione ao Forja da Alma a referência youtube https://www.youtube.com/@canal, foco: paternidade.

Eu atualizo o `perfil.json`, faço commit no repositório e a rotina já usa no dia seguinte.

**Jeito 2 · Comando no terminal** (na pasta do perfil)
```
python3 referencias.py . adicionar instagram @perfil "foco opcional"
python3 referencias.py . adicionar portal https://site.com/materia "liderança"
python3 referencias.py . listar
python3 referencias.py . remover @perfil
```
Depois: `git add perfil.json && git commit -m "Nova referência" && git push`.

**Jeito 3 · Editar o arquivo no GitHub**
1. Abra `perfil.json` no repositório do perfil e clique no lápis (Edit).
2. Dentro de `"referencias": [ ... ]`, copie um item e troque os dados:
   ```json
   {"tipo": "instagram", "endereco": "@perfil", "foco": "", "adicionada_em": "2026-10-11", "consultada_em": null}
   ```
3. Confira as vírgulas entre os itens e clique em **Commit changes**.

## Dica de rede
Para ler as fontes direto, o ambiente de nuvem precisa liberar os domínios delas (ex.: `instagram.com`, `youtube.com`, o site do portal). Sem isso, a automação usa a busca na web.

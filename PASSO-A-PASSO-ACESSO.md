# Forja da Alma · O que só você pode liberar

A automação gera o conteúdo sozinha. Para **publicar** no Instagram, ela precisa de 3 chaves que só você tem.
Analogia: eu sou a fábrica; você precisa me entregar a **chave da loja** (token do Instagram), **liberar a estrada** (rede) e me dar uma **vitrine pública** (onde o Instagram busca as imagens).

---

## Passo 1 · Conta Profissional no Instagram (2 min)
1. No app do Instagram, entre em @forjadaalma.oficial.
2. Configurações → **Tipo de conta e ferramentas** → **Mudar para conta profissional** → escolha **Criador de conteúdo**.
3. Não precisa de Página do Facebook (usaremos o "login do Instagram").

Fonte: https://help.instagram.com/502981923235522

## Passo 2 · App da Meta e token (10 min) · fluxo atual do painel
Faça no computador, logado no Facebook que administra o perfil.

**2.1 Criar o app**
1. Acesse https://developers.facebook.com/apps e clique **Criar app** (Create app).
2. **Detalhes do app**: nome `Forja da Alma Publicador` e seu e-mail → **Avançar**.
3. **Casos de uso**: no filtro, escolha **Gerenciamento de conteúdo** e marque
   **Gerenciar mensagens e conteúdo no Instagram** (Manage messaging & content on Instagram) → **Avançar**.
4. **Empresa**: escolha **Ainda não quero conectar um portfólio empresarial** (I don't want to connect a business portfolio yet) → **Avançar**.
5. **Requisitos** → **Avançar**. **Visão geral** → **Ir para o painel** (Go to dashboard).

**2.2 Gerar o token**
1. No menu da esquerda, clique **Casos de uso** (Use cases).
2. No caso "Gerenciar mensagens e conteúdo no Instagram", clique **Personalizar** (Customize).
3. Abra **Configuração da API com login do Instagram** (API setup with Instagram login).
4. Na seção **Gerar tokens de acesso** (Generate access tokens), clique **Adicionar conta** (Add account) e entre com @forjadaalma.oficial. Aceite as permissões.
5. A conta aparece na lista com o **ID** (número). Clique **Gerar token** (Generate token) ao lado dela e copie o token.
6. Guarde os dois valores para o Passo 3:
   - `IG_ACCESS_TOKEN` = o token
   - `IG_USER_ID` = o ID mostrado ao lado da conta

**Não precisa** de verificação de empresa nem de "Revisão do app": o app fica em modo **Desenvolvimento** e publica normalmente na sua própria conta, porque ela foi adicionada como testadora.

**Se travar**
- Erro "Insufficient developer role": vá em **Funções do app → Funções → Adicionar pessoas → Testador do Instagram**, adicione @forjadaalma.oficial e aceite o convite no Instagram em **Configurações → Apps e sites → Convites de testador**. Depois repita o 2.2.
- A conta precisa estar **pública** e ser **Profissional** (Passo 1).
- Se alguma tela estiver diferente, mande um print aqui que eu te guio.

Fontes oficiais:
- Criar o app: https://developers.facebook.com/docs/instagram-platform/create-an-instagram-app/
- Publicar conteúdo: https://developers.facebook.com/docs/instagram-platform/content-publishing

⚠️ **Nunca cole o token aqui no chat.** Ele vai direto nas configurações do projeto (Passo 3).

## Passo 3 · Ambiente de nuvem do projeto (3 min)
Hoje o projeto roda num ambiente padrão, sem configurações, que **bloqueia** o acesso ao Instagram (testei: `graph.instagram.com` e `graph.facebook.com` retornam bloqueio).
1. Abra **Configurações do projeto → Ambiente (Cloud environment)** → **Add cloud environment**.
2. Em **Network access**, escolha **Limited** (ou Custom) e adicione em **Allowed domains**:
   - `graph.instagram.com`
   - `graph.facebook.com`
   - `rupload.facebook.com`
   - `eduardowalbuquerquer.github.io` (para eu conferir que as imagens já estão no ar)
   - se escolher fotos do Pexels: `api.pexels.com` e `images.pexels.com`
   (deixe marcada a opção de permitir gerenciadores de pacotes)
3. Em **Environment variables**, adicione:
   ```
   IG_ACCESS_TOKEN=<o token do passo 2>
   IG_USER_ID=<o ID da conta do passo 2>
   PEXELS_API_KEY=<chave grátis do Pexels, se escolher fotos do Pexels>
   ```
   A chave do Pexels é grátis em https://www.pexels.com/api/ (crie conta e copie "Your API Key").
4. Salve. Ele já fica selecionado para o projeto.

Fonte: https://code.claude.com/docs/en/cloud-environments#network-access

## Passo 4 · Vitrine pública para as imagens (1 min)
O Instagram não aceita upload direto de imagem: ele **baixa** de um link público (só JPEG).
Você já criou e conectou o repositório público `eduardowalbuquerquer/carrossel`, e o motor já está lá. Falta só ligar o Pages:
1. Abra https://github.com/eduardowalbuquerquer/carrossel/settings/pages
2. Em **Build and deployment → Source**, escolha **Deploy from a branch**.
3. Em **Branch**, escolha **main** e a pasta **/ (root)** → **Save**.

Cada post vira um link como `https://eduardowalbuquerquer.github.io/carrossel/posts/2026-10-14-mito/slide_1.jpg`.

---

## Quando terminar
Responda "pronto" na thread. Eu faço um post de teste, confirmo que saiu no perfil e ligo a rotina diária.

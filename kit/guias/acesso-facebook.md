# Facebook · O que só o dono da Página pode liberar

Para publicar na **Página** do Facebook (perfil pessoal não aceita publicação por API), a automação precisa de 2 valores:
`FB_PAGE_ID` (número da Página) e `FB_PAGE_TOKEN` (token da Página, que não expira se gerado como abaixo).
Analogia: o token do Instagram é a chave de uma loja; o da Página é a chave da loja vizinha, gerada no mesmo chaveiro (app da Meta).

---

## Passo 1 · Ter uma Página e ser administrador dela
Você precisa ter acesso total à Página (Configurações da Página → Acesso à Página).
Fonte: https://www.facebook.com/help/1206330326170599

## Passo 2 · App da Meta com o caso de uso de Páginas (5 min)
1. Em https://developers.facebook.com/apps abra o app que já usa para o Instagram (ou crie um).
2. **Casos de uso → Adicionar caso de uso** → **Gerenciar tudo na sua Página** (Manage everything on your Page).
3. Em **Personalizar**, confirme as permissões: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts` e, para Reels, `publish_video`.
4. Em **Configurações do app → Básico**, anote o **ID do app** e a **Chave secreta do app** (só para o Passo 3; não cole no chat).

O app pode continuar em modo **Desenvolvimento**: ele publica normalmente nas Páginas que você administra.

## Passo 3 · Gerar o token da Página que não expira (5 min)
1. Abra o **Explorador da Graph API**: https://developers.facebook.com/tools/explorer/
2. Em **Meta App**, escolha seu app. Em **Usuário ou Página**, escolha **Obter token de acesso do usuário** e marque as 4 permissões do Passo 2. Clique **Generate Access Token** e autorize a sua Página.
3. Transforme esse token curto em token longo (60 dias). No navegador, troque os valores e abra:
   `https://graph.facebook.com/v23.0/oauth/access_token?grant_type=fb_exchange_token&client_id=<ID_DO_APP>&client_secret=<CHAVE_SECRETA>&fb_exchange_token=<TOKEN_CURTO>`
4. Com o token longo, abra:
   `https://graph.facebook.com/v23.0/me/accounts?access_token=<TOKEN_LONGO>`
   Na lista, ache a sua Página: `id` = **FB_PAGE_ID**, `access_token` = **FB_PAGE_TOKEN** (token de Página gerado de um token longo não tem data de expiração).
5. Confira em https://developers.facebook.com/tools/debug/accesstoken/ : deve mostrar **Expira: Nunca**.

Fontes oficiais:
- Começar com a API de Páginas: https://developers.facebook.com/docs/pages-api/getting-started
- Tokens de longa duração: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived
- Publicar posts: https://developers.facebook.com/docs/pages-api/posts
- Publicar Reels: https://developers.facebook.com/docs/video-api/guides/reels-publishing

⚠️ **Nunca cole o token no chat.** Ele vai direto nas variáveis do ambiente (Passo 4).

## Passo 4 · Ambiente de nuvem
1. **Configurações do projeto → Ambiente**: no mesmo ambiente do Instagram, acrescente em **Allowed domains**:
   `graph.facebook.com` e `rupload.facebook.com`.
2. Em **Environment variables**, adicione:
   ```
   FB_PAGE_ID=<id da Página>
   FB_PAGE_TOKEN=<token da Página>
   ```
   Com vários perfis no mesmo ambiente, use nomes próprios (ex.: `FB_PAGE_TOKEN_MESALEVE`) e informe em `perfil.json → credenciais`.

Fonte: https://code.claude.com/docs/en/cloud-environments#network-access

## Como o post aparece no Facebook
- Imagem única → foto publicada na Página.
- Carrossel → post com várias fotos (o Facebook mostra em grade/álbum, não em deslize).
- Reels → Reels da Página (mesmo vídeo 9:16 do Instagram).
- Teste: `python3 publish.py --check` mostra o nome da Página se o token estiver certo.

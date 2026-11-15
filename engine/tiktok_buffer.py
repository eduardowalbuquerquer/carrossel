"""Publica o Reels do Forja da Alma no TikTok pelo Buffer (público e automático).

Por quê: o TikTok recusa a auditoria de apps pessoais, então a Content Posting API (tiktok_publish.py)
só posta "Somente eu". O Buffer grátis publica público, como já faz no Salário Organizado.

Credencial: FA_BUFFER_KEY (chave da conta Buffer do Forja, em publish.buffer.com/settings/api).
Rede: api.buffer.com liberado no ambiente. O vídeo precisa estar numa URL pública (GitHub Pages).
Docs: https://developers.buffer.com/guides/getting-started.html (GraphQL em https://api.buffer.com)

Uso: python3 tiktok_buffer.py --check   (mostra os canais da conta, sem publicar)
"""
import json, os, sys, time, urllib.error, urllib.request

API = "https://api.buffer.com"
CREATE = """mutation($i: CreatePostInput!) { createPost(input: $i) {
  __typename ... on PostActionSuccess { post { id status externalLink } } ... on MutationError { message } } }"""
STATUS = "query($i: PostId!) { post(input: {id: $i}) { status externalLink error { message } } }"


def key():
    return (os.environ.get("FA_BUFFER_KEY") or "").strip().strip("<>\"'").strip()


def gql(query, variables=None):
    req = urllib.request.Request(API, json.dumps({"query": query, "variables": variables or {}}).encode(),
                                 {"Authorization": f"Bearer {key()}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erro no Buffer: {e.code} {e.read().decode()[:400]}")
    if body.get("errors"):
        raise SystemExit(f"Erro no Buffer: {body['errors']}")
    return body["data"]


def channels():
    out = []
    for org in gql("{ account { organizations { id } } }")["account"]["organizations"]:
        q = "query($o: OrganizationId!) { channels(input: {organizationId: $o}) { id service name } }"
        out += gql(q, {"o": org["id"]})["channels"]
    return out


def tiktok_channel():
    for c in channels():
        if c["service"] == "tiktok":
            return c["id"]
    raise SystemExit("Nenhum canal TikTok conectado no Buffer do Forja")


def caption(spec):
    reel = spec.get("reel", {})
    return (reel.get("caption_tiktok") or reel.get("caption") or spec.get("caption", ""))[:2200]


def publish_reel(spec, video_url):
    """Devolve (id do post no Buffer, status, link do TikTok ou None)."""
    i = {"channelId": tiktok_channel(), "text": caption(spec), "mode": "shareNow",
         "schedulingType": "automatic", "needsApproval": False, "source": "forja-da-alma",
         "assets": [{"video": {"url": video_url, "metadata": {"thumbnailOffset": 1000}}}],
         "metadata": {"tiktok": {"isAiGenerated": os.environ.get("FA_TT_IA", "0") == "1"}}}
    r = gql(CREATE, {"i": i})["createPost"]
    if r["__typename"] != "PostActionSuccess":
        raise SystemExit(f"Buffer recusou o post ({r['__typename']}): {r.get('message')}")
    pid, post = r["post"]["id"], r["post"]
    for _ in range(36):  # até ~6 min para o Buffer enviar ao TikTok
        if post.get("status") in ("sent", "error"):
            break
        time.sleep(10)
        post = gql(STATUS, {"i": pid})["post"]
    if post.get("status") == "error":
        raise SystemExit(f"Buffer não conseguiu publicar no TikTok: {post.get('error')}")
    return pid, f"BUFFER_{(post.get('status') or 'enviado').upper()}", post.get("externalLink")


if __name__ == "__main__":
    if "--check" in sys.argv:
        print(json.dumps(channels(), ensure_ascii=False))

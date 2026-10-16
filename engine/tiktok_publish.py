"""Publica o Reels (reel.mp4) no TikTok via Content Posting API (Direct Post, envio do arquivo).

Credenciais: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET (ambiente) e tokens OAuth em TIKTOK_TOKENS_FILE
(padrão: /mnt/project-files/forja-da-alma/automacao/.segredos/tiktok_tokens.json). O access_token dura 24h;
é renovado sozinho com o refresh_token (vale 1 ano). App sem auditoria só posta SELF_ONLY (privado).
Docs: https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
      https://developers.tiktok.com/doc/oauth-user-access-token-management

Uso: python3 tiktok_publish.py posts/AAAA-MM-DD-xxx   (teste isolado)
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

API = "https://open.tiktokapis.com/v2"
TOKENS = Path(os.environ.get("TIKTOK_TOKENS_FILE",
                             "/mnt/project-files/forja-da-alma/automacao/.segredos/tiktok_tokens.json"))
CHUNK = 10_000_000


def _clean(v):
    return (v or "").strip().strip("<>\"'").strip()


def _req(url, data=None, headers=None, method=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers or {}, method=method),
                                    timeout=300) as r:
            body = r.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erro no TikTok ({url.split('?')[0].rsplit('/', 2)[-2]}): {e.code} {e.read().decode()[:600]}")


def token():
    t = json.loads(TOKENS.read_text())
    if time.time() < t["obtido_em"] + t["expires_in"] - 600:
        return t["access_token"]
    r = _req(f"{API}/oauth/token/", urllib.parse.urlencode({
        "client_key": _clean(os.environ["TIKTOK_CLIENT_KEY"]),
        "client_secret": _clean(os.environ["TIKTOK_CLIENT_SECRET"]),
        "grant_type": "refresh_token", "refresh_token": t["refresh_token"]}).encode(),
        {"Content-Type": "application/x-www-form-urlencoded"})
    if "access_token" not in r:
        raise SystemExit(f"Erro ao renovar token do TikTok: {r}")
    r["obtido_em"] = int(time.time())
    TOKENS.write_text(json.dumps(r, indent=2))
    return r["access_token"]


def api(path, payload):
    r = _req(f"{API}/{path}", json.dumps(payload).encode(),
             {"Authorization": f"Bearer {token()}", "Content-Type": "application/json; charset=UTF-8"}, "POST")
    if r.get("error", {}).get("code", "ok") != "ok":
        raise SystemExit(f"Erro no TikTok ({path}): {r['error']}")
    return r.get("data", {})


def caption(spec):
    reel = spec.get("reel", {})
    return (reel.get("caption_tiktok") or reel.get("caption") or spec.get("caption", ""))[:2200]


def publish_reel(spec, video_path):
    info = api("post/publish/creator_info/query/", {})
    opts = info.get("privacy_level_options", [])
    privacy = _clean(os.environ.get("TIKTOK_PRIVACY")) or ("PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in opts else "SELF_ONLY")
    if privacy not in opts:
        privacy = "SELF_ONLY"
    size = Path(video_path).stat().st_size
    n = max(1, size // CHUNK)
    chunk = size if n == 1 else CHUNK
    d = api("post/publish/video/init/", {
        "post_info": {"title": caption(spec), "privacy_level": privacy, "disable_duet": False,
                      "disable_comment": False, "disable_stitch": False, "video_cover_timestamp_ms": 1000},
        "source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": n}})
    raw = Path(video_path).read_bytes()
    for i in range(n):
        a = i * chunk
        b = size if i == n - 1 else a + chunk
        _req(d["upload_url"], raw[a:b], {"Content-Type": "video/mp4", "Content-Length": str(b - a),
                                          "Content-Range": f"bytes {a}-{b - 1}/{size}"}, "PUT")
    pid = d["publish_id"]
    for _ in range(60):
        st = api("post/publish/status/fetch/", {"publish_id": pid})
        if st.get("status") == "PUBLISH_COMPLETE":
            ids = st.get("publicaly_available_post_id") or st.get("publicly_available_post_id") or []
            return pid, privacy, (f"https://www.tiktok.com/@forjadaalma8/video/{ids[0]}" if ids else None)
        if st.get("status") == "FAILED":
            raise SystemExit(f"TikTok recusou o vídeo: {st.get('fail_reason')}")
        time.sleep(5)
    return pid, privacy, None


if __name__ == "__main__":
    d = Path(sys.argv[1])
    print(publish_reel(json.loads((d / "spec.json").read_text()), d / "reel.mp4"))

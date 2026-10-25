"""Publica um vídeo pronto do Salário Organizado: Instagram Reels, YouTube Shorts e TikTok (rascunho na caixa de entrada).

Uso:
  python3 publish.py ../posts/<pasta>                 # publica onde ainda não saiu (idempotente via resultado.json)
  python3 publish.py ../posts/<pasta> --so ig,yt      # só algumas redes
  python3 publish.py --check                          # valida as credenciais de cada rede
  python3 publish.py --refresh-token                  # renova o token do Instagram (60 dias)
  python3 publish.py --yt-auth-url | --yt-auth-code <código>   # autoriza o canal do YouTube (uma vez)
  python3 publish.py --tt-auth-url | --tt-auth-code <código>   # autoriza o TikTok do Salário Organizado (uma vez)

Ambiente:
  SO_IG_ACCESS_TOKEN, SO_IG_USER_ID          Instagram API com login do Instagram (mesmo app da Meta da Forja)
  SO_YT_CLIENT_ID, SO_YT_CLIENT_SECRET       OAuth do Google (app para computador); token salvo em SEGREDOS/yt_token.json
  SO_TT_CLIENT_KEY, SO_TT_CLIENT_SECRET      chaves do Sandbox do app Forja (ou TIKTOK_CLIENT_KEY/SECRET); token em SEGREDOS/tiktok_tokens.json
  PAGES_REPO_DIR, PAGES_BASE_URL             repositório público com GitHub Pages (o Instagram baixa o vídeo de lá)
  SO_SEGREDOS                                pasta dos tokens (padrão /mnt/project-files/canais/automacao/.segredos)
  SO_TIKTOK_MODO                             inbox (padrão: rascunho na caixa de entrada) ou direct (só após a auditoria)

Docs:
  https://developers.facebook.com/docs/instagram-platform/content-publishing
  https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol
  https://developers.tiktok.com/doc/content-posting-api-reference-upload-video
"""
import json, os, secrets, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

SEGREDOS = Path(os.environ.get("SO_SEGREDOS", "/mnt/project-files/canais/automacao/.segredos"))
IG = "https://graph.instagram.com"
TT = "https://open.tiktokapis.com/v2"
YT_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
REDIRECT_YT = "http://localhost"
REDIRECT_TT = os.environ.get("SO_TT_REDIRECT", "https://eduardowalbuquerquer.github.io/carrossel/tiktok.html")
TT_HANDLE = os.environ.get("SO_TT_HANDLE", "salario.organizado")


def env(k):
    return (os.environ.get(k) or "").strip().strip("<>\"'").strip()


def http(url, data=None, headers=None, method=None, timeout=300):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers or {}, method=method), timeout=timeout) as r:
            body = r.read()
            return (json.loads(body) if body and body[:1] in b"{[" else body), r.headers
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erro HTTP {e.code} em {url.split('?')[0]}: {e.read().decode()[:600]}")


def form(d):
    return urllib.parse.urlencode(d).encode()


# ---------------- Instagram ----------------
def ig(method, path, **p):
    p["access_token"] = env("SO_IG_ACCESS_TOKEN")
    if method == "GET":
        return http(f"{IG}/{path}?{urllib.parse.urlencode(p)}")[0]
    return http(f"{IG}/{path}", form(p), method="POST")[0]


def host(post_dir, files):
    """Põe os arquivos no GitHub Pages (commit + push no repositório) e devolve as URLs públicas."""
    repo = Path(env("PAGES_REPO_DIR")); base = env("PAGES_BASE_URL").rstrip("/")
    rel = post_dir.resolve().relative_to(repo.resolve())
    git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True)
    git("add", "--", str(rel))
    if subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--quiet"]).returncode:
        git("commit", "-q", "-m", f"Salário Organizado: mídias de {post_dir.name}")
    for w in (0, 2, 4, 8, 16):
        time.sleep(w)
        if subprocess.run(["git", "-C", str(repo), "push", "-q", "origin", "HEAD:main"]).returncode == 0:
            break
    else:
        raise SystemExit("Falha no git push das mídias")
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    urls = {f: f"{base.replace('{sha}', sha)}/{rel.as_posix()}/{f}" for f in files}
    t0 = time.time()
    while time.time() - t0 < 300:  # o Pages leva ~1 min para publicar
        try:
            with urllib.request.urlopen(urllib.request.Request(urls[files[0]], method="HEAD"), timeout=20) as r:
                if r.status == 200:
                    return urls
        except Exception:
            pass
        time.sleep(10)
    time.sleep(60)
    return urls


def publish_ig(post_dir, spec):
    urls = host(post_dir, ["video_ig.mp4", "capa.jpg"])
    uid = env("SO_IG_USER_ID")
    c = ig("POST", f"{uid}/media", media_type="REELS", video_url=urls["video_ig.mp4"], cover_url=urls["capa.jpg"],
           caption=spec["captions"]["ig"], share_to_feed="true")["id"]
    t0 = time.time()
    while True:
        st = ig("GET", c, fields="status_code,status")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED") or time.time() - t0 > 900:
            raise SystemExit(f"Instagram não processou o vídeo: {st}")
        time.sleep(10)
    mid = ig("POST", f"{uid}/media_publish", creation_id=c)["id"]
    return mid, ig("GET", mid, fields="permalink").get("permalink")


# ---------------- YouTube ----------------
def yt_token():
    f = SEGREDOS / "yt_token.json"
    if not f.exists():
        raise SystemExit("YouTube ainda não autorizado: rode --yt-auth-url e depois --yt-auth-code")
    t = json.loads(f.read_text())
    if time.time() < t.get("obtido_em", 0) + t.get("expires_in", 0) - 300:
        return t["access_token"]
    r = http("https://oauth2.googleapis.com/token", form({"client_id": env("SO_YT_CLIENT_ID"), "client_secret": env("SO_YT_CLIENT_SECRET"),
                                                        "refresh_token": t["refresh_token"], "grant_type": "refresh_token"}))[0]
    t.update(r, obtido_em=int(time.time()))
    f.write_text(json.dumps(t, indent=2))
    return t["access_token"]


def publish_yt(post_dir, spec):
    video = post_dir / "video_yt.mp4"
    cap = spec["captions"]
    meta = {"snippet": {"title": cap["yt_title"][:100], "description": cap["yt_desc"][:4900], "categoryId": "27",
                        "defaultLanguage": "pt-BR", "defaultAudioLanguage": "pt-BR", "tags": cap.get("yt_tags", [])},
            "status": {"privacyStatus": os.environ.get("SO_YT_PRIVACY", "public"), "selfDeclaredMadeForKids": False}}
    tok = yt_token()
    _, h = http("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                json.dumps(meta).encode(), {"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                                            "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(video.stat().st_size)}, "POST")
    r, _ = http(h["Location"], video.read_bytes(), {"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"}, "PUT", timeout=900)
    return r["id"], f"https://youtube.com/shorts/{r['id']}"


# ---------------- TikTok ----------------
def tt_token():
    f = SEGREDOS / "tiktok_tokens.json"
    if not f.exists():
        raise SystemExit("TikTok ainda não autorizado: rode --tt-auth-url e depois --tt-auth-code")
    t = json.loads(f.read_text())
    if time.time() < t["obtido_em"] + t["expires_in"] - 600:
        return t["access_token"]
    r = http(f"{TT}/oauth/token/", form({"client_key": (env("SO_TT_CLIENT_KEY") or env("TIKTOK_CLIENT_KEY")), "client_secret": (env("SO_TT_CLIENT_SECRET") or env("TIKTOK_CLIENT_SECRET")),
                                         "grant_type": "refresh_token", "refresh_token": t["refresh_token"]}),
             {"Content-Type": "application/x-www-form-urlencoded"})[0]
    if "access_token" not in r:
        raise SystemExit(f"Erro ao renovar token do TikTok: {r}")
    r["obtido_em"] = int(time.time()); f.write_text(json.dumps(r, indent=2))
    return r["access_token"]


def tt(path, payload):
    r = http(f"{TT}/{path}", json.dumps(payload).encode(),
             {"Authorization": f"Bearer {tt_token()}", "Content-Type": "application/json; charset=UTF-8"}, "POST")[0]
    if r.get("error", {}).get("code", "ok") != "ok":
        raise SystemExit(f"Erro no TikTok ({path}): {r['error']}")
    return r.get("data", {})


def publish_tt(post_dir, spec):
    video = post_dir / "video_tt.mp4"
    size = video.stat().st_size
    src = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}
    if os.environ.get("SO_TIKTOK_MODO", "inbox") == "direct":
        d = tt("post/publish/video/init/", {"post_info": {"title": spec["captions"]["tt"][:2200], "privacy_level": "PUBLIC_TO_EVERYONE",
                                                          "video_cover_timestamp_ms": 600}, "source_info": src})
    else:  # rascunho: chega como notificação no app; você publica com a legenda de legendas.md
        d = tt("post/publish/inbox/video/init/", {"source_info": src})
    http(d["upload_url"], video.read_bytes(), {"Content-Type": "video/mp4", "Content-Length": str(size),
                                               "Content-Range": f"bytes 0-{size - 1}/{size}"}, "PUT", timeout=900)
    pid = d["publish_id"]
    for _ in range(60):
        st = tt("post/publish/status/fetch/", {"publish_id": pid})
        if st.get("status") in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
            ids = st.get("publicaly_available_post_id") or []
            return pid, st["status"], (f"https://www.tiktok.com/@{TT_HANDLE}/video/{ids[0]}" if ids else None)
        if st.get("status") == "FAILED":
            raise SystemExit(f"TikTok recusou o vídeo: {st.get('fail_reason')}")
        time.sleep(5)
    return pid, "PROCESSING", None


# ---------------- autorizações (uma vez) ----------------
def auth(argv):
    SEGREDOS.mkdir(parents=True, exist_ok=True)
    if "--yt-auth-url" in argv:
        print("https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
            "client_id": env("SO_YT_CLIENT_ID"), "redirect_uri": REDIRECT_YT, "response_type": "code",
            "scope": YT_SCOPE, "access_type": "offline", "prompt": "consent"}))
    elif "--yt-auth-code" in argv:
        code = argv[argv.index("--yt-auth-code") + 1]
        code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query).get("code", [code])[0]
        r = http("https://oauth2.googleapis.com/token", form({"code": code, "client_id": env("SO_YT_CLIENT_ID"),
                 "client_secret": env("SO_YT_CLIENT_SECRET"), "redirect_uri": REDIRECT_YT, "grant_type": "authorization_code"}))[0]
        r["obtido_em"] = int(time.time()); (SEGREDOS / "yt_token.json").write_text(json.dumps(r, indent=2)); print("YouTube autorizado.")
    elif "--tt-auth-url" in argv:
        print("https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode({
            "client_key": (env("SO_TT_CLIENT_KEY") or env("TIKTOK_CLIENT_KEY")), "scope": "user.info.basic,video.upload,video.publish",
            "response_type": "code", "redirect_uri": REDIRECT_TT, "state": secrets.token_hex(8)}))
    elif "--tt-auth-code" in argv:
        code = argv[argv.index("--tt-auth-code") + 1]
        code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query).get("code", [code])[0]
        r = http(f"{TT}/oauth/token/", form({"client_key": (env("SO_TT_CLIENT_KEY") or env("TIKTOK_CLIENT_KEY")), "client_secret": (env("SO_TT_CLIENT_SECRET") or env("TIKTOK_CLIENT_SECRET")),
                 "code": code, "grant_type": "authorization_code", "redirect_uri": REDIRECT_TT}),
                 {"Content-Type": "application/x-www-form-urlencoded"})[0]
        if "access_token" not in r:
            raise SystemExit(f"TikTok não autorizou: {r}")
        r["obtido_em"] = int(time.time()); (SEGREDOS / "tiktok_tokens.json").write_text(json.dumps(r, indent=2)); print("TikTok autorizado.")


def check():
    out = {}
    try:
        out["instagram"] = ig("GET", "me", fields="user_id,username,account_type")
    except SystemExit as e:
        out["instagram"] = str(e)
    for k, f in (("youtube", yt_token), ("tiktok", tt_token)):
        try:
            f(); out[k] = "ok"
        except SystemExit as e:
            out[k] = str(e)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def main(argv):
    if any(a.startswith(("--yt-auth", "--tt-auth")) for a in argv):
        return auth(argv)
    if "--check" in argv:
        return check()
    if "--refresh-token" in argv:
        r = ig("GET", "refresh_access_token", grant_type="ig_refresh_token")
        print(json.dumps({"expira_em_dias": round(r.get("expires_in", 0) / 86400, 1), "mesmo_token": r.get("access_token") == env("SO_IG_ACCESS_TOKEN")}))
        return
    post_dir = Path(argv[0]).resolve()
    spec = json.loads((post_dir / "spec.json").read_text(encoding="utf-8"))
    redes = argv[argv.index("--so") + 1].split(",") if "--so" in argv else spec.get("redes", ["ig", "yt", "tt"])
    rp = post_dir / "resultado.json"
    res = json.loads(rp.read_text()) if rp.exists() else {}
    for rede, fn in (("ig", publish_ig), ("yt", publish_yt), ("tt", publish_tt)):
        if rede not in redes or res.get(f"{rede}_id"):
            continue
        try:  # uma rede com erro não impede as outras
            res[f"{rede}_id"], *rest = fn(post_dir, spec)
            res[f"{rede}_link" if rede != "tt" else "tt_status"] = rest[0]
            if rede == "tt":
                res["tt_link"] = rest[1]
            res.pop(f"{rede}_erro", None)
        except SystemExit as e:
            res[f"{rede}_erro"] = str(e)
            print(f"AVISO {rede}: {e}")
        rp.write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])

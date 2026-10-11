"""Publica um post pronto (feed + Reels) no Instagram e/ou na Página do Facebook.

Uso:
  python publish.py ../posts/AAAA-MM-DD-serie                 # publica em todas as plataformas do perfil.json
  python publish.py ../posts/AAAA-MM-DD-serie --only facebook # só uma plataforma (instagram | facebook)
  python publish.py ../posts/AAAA-MM-DD-serie --dry-run       # só mostra o que faria
  python publish.py --check                                   # valida as credenciais de cada plataforma
  python publish.py --refresh-token                           # renova o token do Instagram (60 dias)

Variáveis de ambiente (os nomes podem ser trocados em perfil.json -> credenciais, útil com vários perfis):
  IG_ACCESS_TOKEN, IG_USER_ID      Instagram API com login do Instagram
  FB_PAGE_TOKEN, FB_PAGE_ID        token de Página (pages_manage_posts, pages_read_engagement, publish_video)
  PAGES_REPO_DIR                   clone local do repositório público que serve as mídias
  PAGES_BASE_URL                   ex.: https://usuario.github.io/repo  ou  https://cdn.jsdelivr.net/gh/usuario/repo@{sha}
  IG_API_VERSION / FB_API_VERSION  opcionais (Facebook padrão v23.0)

Docs:
  Instagram: https://developers.facebook.com/docs/instagram-platform/content-publishing
  Facebook fotos/posts: https://developers.facebook.com/docs/pages-api/posts
  Facebook Reels: https://developers.facebook.com/docs/video-api/guides/reels-publishing
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from brand import PERFIL

CRED = {"ig_token": "IG_ACCESS_TOKEN", "ig_user": "IG_USER_ID", "fb_token": "FB_PAGE_TOKEN", "fb_page": "FB_PAGE_ID",
        **PERFIL.get("credenciais", {})}
PLATFORMS = PERFIL.get("plataformas", ["instagram"])


def env(key, required=True):
    """Lê a credencial pelo nome configurado. Valores colados com espaços ou entre <> quebram a API: limpa."""
    name = CRED.get(key, key)
    val = os.environ.get(name, "").strip().strip("<>\"'").strip()
    if required and not val:
        raise SystemExit(f"Falta a variável de ambiente {name}.")
    return val


# ---------- HTTP ----------

def http(method, url, params=None, headers=None, label=""):
    data = urllib.parse.urlencode(params or {}).encode()
    if method == "GET":
        req = urllib.request.Request(url + ("?" + data.decode() if params else ""), headers=headers or {})
    else:
        req = urllib.request.Request(url, data=data, method="POST", headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erro da API ({label or url.split('?')[0]}): {e.code} {e.read().decode()[:600]}")


def ig(method, path, **params):
    ver = os.environ.get("IG_API_VERSION", "").strip("/")
    params["access_token"] = env("ig_token")
    return http(method, f"https://graph.instagram.com/{ver + '/' if ver else ''}{path.lstrip('/')}", params, label=f"Instagram {path}")


FB_VER = os.environ.get("FB_API_VERSION", "v23.0").strip("/")


def fb(method, path, **params):
    params["access_token"] = env("fb_token")
    return http(method, f"https://graph.facebook.com/{FB_VER}/{path.lstrip('/')}", params, label=f"Facebook {path}")


# ---------- hospedagem pública das mídias ----------

def wait_public(url, timeout=420):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(10)
    return False


def host_files(post_dir, files):
    """Copia as mídias para o repositório público, faz push e devolve as URLs (Instagram e Facebook baixam de lá)."""
    repo = Path(os.environ["PAGES_REPO_DIR"])
    base_url = os.environ["PAGES_BASE_URL"].rstrip("/")
    dest = repo / "posts" / post_dir.name
    dest.mkdir(parents=True, exist_ok=True)
    if dest.resolve() != post_dir.resolve():  # o post pode já estar dentro do repo
        for f in files:
            shutil.copy(post_dir / f, dest / f)
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True)
    run("add", "-A")
    if subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--quiet"]).returncode != 0:
        run("commit", "-m", f"Mídias do post {post_dir.name}")
    for wait in (0, 2, 4, 8, 16):
        time.sleep(wait)
        if subprocess.run(["git", "-C", str(repo), "push", "-u", "origin", "HEAD"]).returncode == 0:
            break
    else:
        raise SystemExit("Falha no git push do repositório de mídias")
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    base_url = base_url.replace("{sha}", sha)
    urls = {f: f"{base_url}/posts/{post_dir.name}/{f}" for f in files}
    if not wait_public(urls[files[0]], timeout=60):  # Pages leva ~1 min; se o ambiente não alcança o host, espera fixa
        time.sleep(90)
    return urls


# ---------- Instagram ----------

def ig_wait(cid, label, timeout=600):
    t0 = time.time()
    while True:
        st = ig("GET", cid, fields="status_code,status").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Container {label} falhou: {ig('GET', cid, fields='status')}")
        if time.time() - t0 > timeout:
            raise SystemExit(f"Container {label} não ficou pronto em {timeout}s (status {st})")
        time.sleep(10 if "reel" in label else 4)


def ig_feed(spec, urls, slides):
    uid = env("ig_user")
    if len(slides) == 1:
        c = ig("POST", f"{uid}/media", image_url=urls[slides[0]], caption=spec["caption"])["id"]
        ig_wait(c, "imagem")
    else:
        children = [ig("POST", f"{uid}/media", image_url=urls[s], is_carousel_item="true")["id"] for s in slides]
        for cid in children:
            ig_wait(cid, "item do carrossel")
        c = ig("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(children), caption=spec["caption"])["id"]
        ig_wait(c, "carrossel")
    mid = ig("POST", f"{uid}/media_publish", creation_id=c)["id"]
    return mid, ig("GET", mid, fields="permalink").get("permalink")


def ig_reel(spec, urls):
    uid = env("ig_user")
    params = dict(media_type="REELS", video_url=urls["reel.mp4"], caption=spec["reel"]["caption"], share_to_feed="true")
    if "reel_capa.jpg" in urls:
        params["cover_url"] = urls["reel_capa.jpg"]
    c = ig("POST", f"{uid}/media", **params)["id"]
    ig_wait(c, "reel", timeout=900)
    mid = ig("POST", f"{uid}/media_publish", creation_id=c)["id"]
    return mid, ig("GET", mid, fields="permalink").get("permalink")


# ---------- Facebook (Página) ----------

def fb_caption(spec, reel=False):
    if reel:
        return spec["reel"].get("caption_facebook") or spec["reel"]["caption"]
    return spec.get("caption_facebook") or spec["caption"]


def fb_feed(spec, urls, slides):
    """1 imagem = foto publicada; carrossel = post com várias fotos (attached_media)."""
    page = env("fb_page")
    msg = fb_caption(spec)
    if len(slides) == 1:
        r = fb("POST", f"{page}/photos", url=urls[slides[0]], message=msg)
        pid = r.get("post_id") or r["id"]
    else:
        ids = [fb("POST", f"{page}/photos", url=urls[s], published="false")["id"] for s in slides]
        media = {f"attached_media[{k}]": json.dumps({"media_fbid": i}) for k, i in enumerate(ids)}
        pid = fb("POST", f"{page}/feed", message=msg, **media)["id"]
    return pid, fb("GET", pid, fields="permalink_url").get("permalink_url")


def fb_reel(spec, urls):
    page = env("fb_page")
    vid = fb("POST", f"{page}/video_reels", upload_phase="start")["video_id"]
    up = urllib.request.Request(f"https://rupload.facebook.com/video-upload/{FB_VER}/{vid}", method="POST",
                                headers={"Authorization": f"OAuth {env('fb_token')}", "file_url": urls["reel.mp4"]})
    try:
        with urllib.request.urlopen(up, timeout=300) as r:
            ok = json.loads(r.read()).get("success")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erro no upload do Reels do Facebook: {e.code} {e.read().decode()[:600]}")
    if not ok:
        raise SystemExit("Upload do Reels do Facebook não confirmou sucesso")
    fb("POST", f"{page}/video_reels", upload_phase="finish", video_id=vid, video_state="PUBLISHED",
       description=fb_caption(spec, reel=True))
    t0 = time.time()
    while time.time() - t0 < 900:  # espera o processamento terminar
        st = fb("GET", vid, fields="status").get("status", {})
        if st.get("video_status") == "ready" or st.get("publishing_phase", {}).get("status") == "complete":
            break
        if st.get("video_status") == "error":
            raise SystemExit(f"Reels do Facebook falhou: {st}")
        time.sleep(10)
    return vid, f"https://www.facebook.com/reel/{vid}"


# ---------- principal ----------

def check():
    out = {}
    if "instagram" in PLATFORMS:
        out["instagram"] = {"conta": ig("GET", "me", fields="user_id,username,account_type"),
                            "limite": ig("GET", f"{env('ig_user')}/content_publishing_limit", fields="quota_usage,config")}
    if "facebook" in PLATFORMS:
        out["facebook"] = fb("GET", env("fb_page"), fields="id,name,link")
    print(json.dumps(out, ensure_ascii=False))


def main(argv):
    if "--check" in argv:
        return check()
    if "--refresh-token" in argv:
        r = ig("GET", "refresh_access_token", grant_type="ig_refresh_token")
        same = r.get("access_token") == env("ig_token")
        print(json.dumps({"expira_em_dias": round(r.get("expires_in", 0) / 86400, 1), "mesmo_token": same}))
        return

    platforms = PLATFORMS
    if "--only" in argv:
        platforms = [argv[argv.index("--only") + 1]]
    post_dir = Path(argv[0]).resolve()
    spec = json.loads((post_dir / "spec.json").read_text(encoding="utf-8"))
    slides = sorted((p.name for p in post_dir.glob("slide_*.jpg")), key=lambda n: int(n.split("_")[1].split(".")[0]))
    reel_files = [f for f in ("reel.mp4", "reel_capa.jpg") if (post_dir / f).exists()]
    result_path = post_dir / "resultado.json"
    result = json.loads(result_path.read_text()) if result_path.exists() else {}

    if "--dry-run" in argv:
        print(json.dumps({"plataformas": platforms, "slides": slides, "reel": reel_files, "ja_publicado": result}, ensure_ascii=False))
        return

    urls = host_files(post_dir, slides + reel_files)
    save = lambda: result_path.write_text(json.dumps(result, indent=2))
    steps = {  # idempotente: o que já saiu não é republicado
        "instagram": [("feed", lambda: ig_feed(spec, urls, slides)), ("reel", lambda: ig_reel(spec, urls))],
        "facebook": [("fb_feed", lambda: fb_feed(spec, urls, slides)), ("fb_reel", lambda: fb_reel(spec, urls))],
    }
    for plat in platforms:
        for key, fn in steps[plat]:
            if key.endswith("reel") and "reel.mp4" not in urls:
                continue
            if not result.get(f"{key}_id"):
                result[f"{key}_id"], result[f"{key}_link"] = fn()
                save()
    print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])

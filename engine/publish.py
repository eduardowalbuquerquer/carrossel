"""Publica um post pronto (feed + Reels) no Instagram via Instagram API com login do Instagram.

Uso:
  python publish.py posts/AAAA-MM-DD-serie            # publica feed e depois o Reels
  python publish.py posts/AAAA-MM-DD-serie --dry-run  # só mostra o que faria
  python publish.py --check                           # valida token e mostra limite de publicação
  python publish.py --refresh-token                   # renova o token (60 dias) e imprime a nova validade

Variáveis de ambiente:
  IG_ACCESS_TOKEN   token da conta (gerado no app da Meta)
  IG_USER_ID        ID da conta do Instagram
  PAGES_REPO_DIR    clone local do repositório público com GitHub Pages
  PAGES_BASE_URL    ex.: https://usuario.github.io/forja-da-alma-posts
  IG_API_VERSION    opcional, ex.: v23.0 (vazio = versão padrão da API)

Docs: https://developers.facebook.com/docs/instagram-platform/content-publishing
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

HOST = "https://graph.instagram.com"

# Valores colados com espaços ou entre <> (ex.: "<IGAA...>") quebram a API: limpa antes de usar.
for _k in ("IG_ACCESS_TOKEN", "IG_USER_ID"):
    if _k in os.environ:
        os.environ[_k] = os.environ[_k].strip().strip("<>\"'").strip()


def api_url(path):
    ver = os.environ.get("IG_API_VERSION", "").strip("/")
    return f"{HOST}/{ver + '/' if ver else ''}{path.lstrip('/')}"


def call(method, path, **params):
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(api_url(path) + "?" + data.decode())
    else:
        req = urllib.request.Request(api_url(path), data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erro da API do Instagram em {path}: {e.code} {e.read().decode()[:600]}")


def wait_container(cid, label, timeout=600):
    """Espera o container ficar FINISHED (vídeo pode levar alguns minutos)."""
    t0 = time.time()
    while True:
        st = call("GET", cid, fields="status_code,status").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            info = call("GET", cid, fields="status")
            raise SystemExit(f"Container {label} falhou: {info}")
        if time.time() - t0 > timeout:
            raise SystemExit(f"Container {label} não ficou pronto em {timeout}s (status {st})")
        time.sleep(10 if "reel" in label else 4)


def wait_public(url, timeout=420):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(10)
    return False


def host_files(post_dir, files):
    """Copia as mídias para o repositório do GitHub Pages, faz push e devolve as URLs públicas."""
    repo = Path(os.environ["PAGES_REPO_DIR"])
    base_url = os.environ["PAGES_BASE_URL"].rstrip("/")
    dest = repo / "posts" / post_dir.name
    dest.mkdir(parents=True, exist_ok=True)
    if dest.resolve() != post_dir.resolve():  # o post pode já estar dentro do repo do Pages
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
    # PAGES_BASE_URL pode conter {sha} (ex.: jsDelivr fixado no commit), útil enquanto o Pages não está no ar.
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    base_url = base_url.replace("{sha}", sha)
    urls = {f: f"{base_url}/posts/{post_dir.name}/{f}" for f in files}
    # O GitHub Pages leva ~1 min para publicar; se este ambiente não alcança github.io, espera fixa.
    probe = urls[files[0]]
    if not wait_public(probe, timeout=60):
        time.sleep(90)
    return urls


def publish_feed(spec, urls, slides):
    uid = os.environ["IG_USER_ID"]
    caption = spec["caption"]
    if len(slides) == 1:
        c = call("POST", f"{uid}/media", image_url=urls[slides[0]], caption=caption)["id"]
        wait_container(c, "imagem")
    else:
        children = []
        for s in slides:
            cid = call("POST", f"{uid}/media", image_url=urls[s], is_carousel_item="true")["id"]
            children.append(cid)
        for cid in children:
            wait_container(cid, "item do carrossel")
        c = call("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(children), caption=caption)["id"]
        wait_container(c, "carrossel")
    mid = call("POST", f"{uid}/media_publish", creation_id=c)["id"]
    return mid


def publish_reel(spec, urls):
    uid = os.environ["IG_USER_ID"]
    params = dict(media_type="REELS", video_url=urls["reel.mp4"], caption=spec["reel"]["caption"],
                  share_to_feed="true")
    if "reel_capa.jpg" in urls:
        params["cover_url"] = urls["reel_capa.jpg"]
    c = call("POST", f"{uid}/media", **params)["id"]
    wait_container(c, "reel", timeout=900)
    return call("POST", f"{uid}/media_publish", creation_id=c)["id"]


def permalink(mid):
    return call("GET", mid, fields="permalink").get("permalink")


def main(argv):
    if "--check" in argv:
        me = call("GET", "me", fields="user_id,username,account_type")
        lim = call("GET", f"{os.environ['IG_USER_ID']}/content_publishing_limit", fields="quota_usage,config")
        print(json.dumps({"conta": me, "limite": lim}, ensure_ascii=False))
        return
    if "--refresh-token" in argv:
        r = call("GET", "refresh_access_token", grant_type="ig_refresh_token")
        same = r.get("access_token") == os.environ["IG_ACCESS_TOKEN"]
        print(json.dumps({"expira_em_dias": round(r.get("expires_in", 0) / 86400, 1), "mesmo_token": same}))
        return

    post_dir = Path(argv[0]).resolve()
    spec = json.loads((post_dir / "spec.json").read_text(encoding="utf-8"))
    slides = sorted((p.name for p in post_dir.glob("slide_*.jpg")), key=lambda n: int(n.split("_")[1].split(".")[0]))
    reel_files = [f for f in ("reel.mp4", "reel_capa.jpg") if (post_dir / f).exists()]
    result_path = post_dir / "resultado.json"
    result = json.loads(result_path.read_text()) if result_path.exists() else {}

    if "--dry-run" in argv:
        print(json.dumps({"slides": slides, "reel": reel_files, "ja_publicado": result}, ensure_ascii=False))
        return

    urls = host_files(post_dir, slides + reel_files)
    if slides and not result.get("feed_id"):  # idempotente: não republica se já saiu
        result["feed_id"] = publish_feed(spec, urls, slides)
        result["feed_link"] = permalink(result["feed_id"])
        result_path.write_text(json.dumps(result, indent=2))
    if "reel.mp4" in urls and not result.get("reel_id"):
        result["reel_id"] = publish_reel(spec, urls)
        result["reel_link"] = permalink(result["reel_id"])
        result_path.write_text(json.dumps(result, indent=2))
    if os.environ.get("FB_ACCESS_TOKEN") and "--no-facebook" not in argv:  # Página do Facebook, depois do Instagram
        import fb_publish
        if slides and not result.get("fb_feed_id"):
            result["fb_feed_id"], result["fb_feed_link"] = fb_publish.publish_feed(spec, urls, slides)
            result_path.write_text(json.dumps(result, indent=2))
        if "reel.mp4" in urls and not result.get("fb_reel_id"):
            result["fb_reel_id"], result["fb_reel_link"] = fb_publish.publish_reel(spec, urls)
            result_path.write_text(json.dumps(result, indent=2))
    if (os.environ.get("TIKTOK_CLIENT_KEY") and "--no-tiktok" not in argv and (post_dir / "reel.mp4").exists()
            and not result.get("tiktok_publish_id")):  # TikTok: falha não derruba IG/FB já publicados
        import tiktok_publish
        if tiktok_publish.TOKENS.exists():
            try:
                result["tiktok_publish_id"], result["tiktok_privacy"], result["tiktok_link"] = \
                    tiktok_publish.publish_reel(spec, post_dir / "reel.mp4")
                result_path.write_text(json.dumps(result, indent=2))
            except SystemExit as e:
                result["tiktok_erro"] = str(e)
                result_path.write_text(json.dumps(result, indent=2))
                print(f"AVISO TikTok: {e}")
    print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1:])

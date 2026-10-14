"""Publica na Página do Facebook (feed + Reels), usando as mesmas mídias já hospedadas para o Instagram.

Credenciais: FB_ACCESS_TOKEN (token de usuário com pages_manage_posts) e, opcional, FB_PAGE_ID.
O token da Página é obtido na hora via me/accounts.
Docs: https://developers.facebook.com/docs/pages-api/posts
      https://developers.facebook.com/docs/video-api/guides/reels-publishing
"""
import json, os, time, urllib.error, urllib.parse, urllib.request

VER = os.environ.get("FB_API_VERSION", "v23.0").strip("/")
_page = {}


def _clean(v):
    return (v or "").strip().strip("<>\"'").strip()


def _http(method, url, params):
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erro no Facebook ({url.split('?')[0].rsplit('/', 1)[-1]}): {e.code} {e.read().decode()[:600]}")


def page():
    if not _page:
        want = _clean(os.environ.get("FB_PAGE_ID"))
        accs = _http("GET", f"https://graph.facebook.com/{VER}/me/accounts",
                     {"fields": "id,name,access_token", "access_token": _clean(os.environ["FB_ACCESS_TOKEN"])})["data"]
        p = next((a for a in accs if not want or a["id"] == want), None)
        if not p:
            raise SystemExit("Página do Facebook não encontrada no token (FB_PAGE_ID/FB_ACCESS_TOKEN)")
        _page.update(p)
    return _page


def fb(method, path, **params):
    params["access_token"] = page()["access_token"]
    return _http(method, f"https://graph.facebook.com/{VER}/{path.lstrip('/')}", params)


def caption(spec, reel=False):
    if reel:
        return spec["reel"].get("caption_facebook") or spec["reel"]["caption"]
    return spec.get("caption_facebook") or spec["caption"]


def publish_feed(spec, urls, slides):
    """1 imagem = foto; carrossel = post com várias fotos (attached_media)."""
    pid_ = page()["id"]
    if len(slides) == 1:
        r = fb("POST", f"{pid_}/photos", url=urls[slides[0]], message=caption(spec))
        pid = r.get("post_id") or r["id"]
    else:
        ids = [fb("POST", f"{pid_}/photos", url=urls[s], published="false")["id"] for s in slides]
        media = {f"attached_media[{k}]": json.dumps({"media_fbid": i}) for k, i in enumerate(ids)}
        pid = fb("POST", f"{pid_}/feed", message=caption(spec), **media)["id"]
    return pid, fb("GET", pid, fields="permalink_url").get("permalink_url")


def publish_reel(spec, urls):
    pid_ = page()["id"]
    vid = fb("POST", f"{pid_}/video_reels", upload_phase="start")["video_id"]
    up = urllib.request.Request(f"https://rupload.facebook.com/video-upload/{VER}/{vid}", method="POST",
                                headers={"Authorization": f"OAuth {page()['access_token']}", "file_url": urls["reel.mp4"]})
    try:
        with urllib.request.urlopen(up, timeout=300) as r:
            ok = json.loads(r.read()).get("success")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erro no upload do Reels do Facebook: {e.code} {e.read().decode()[:600]}")
    if not ok:
        raise SystemExit("Upload do Reels do Facebook não confirmou sucesso")
    fb("POST", f"{pid_}/video_reels", upload_phase="finish", video_id=vid, video_state="PUBLISHED",
       description=caption(spec, reel=True))
    t0 = time.time()
    while time.time() - t0 < 900:
        st = fb("GET", vid, fields="status").get("status", {})
        if st.get("video_status") == "ready" or st.get("publishing_phase", {}).get("status") == "complete":
            break
        if st.get("video_status") == "error":
            raise SystemExit(f"Reels do Facebook falhou: {st}")
        time.sleep(10)
    return vid, f"https://www.facebook.com/reel/{vid}"

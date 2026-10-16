"""Desempenho dos nossos próprios posts por plataforma (Instagram e Facebook), para a revisão de domingo.

Lê posts/*/resultado.json, consulta as métricas e grava metricas.json na raiz do repo.
Instagram: insights do post (views, reach, saved, shares, likes, comments).
Facebook: contadores públicos do post (reações, comentários, compartilhamentos).
TikTok: ainda sem leitura (precisa do escopo video.list, a pedir depois da auditoria).
Uso: python3 metricas.py [--dias 14]
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IG_METRICS = "views,reach,saved,shares,likes,comments"


def _clean(v):
    return (v or "").strip().strip("<>\"'").strip()


def _get(url, params):
    try:
        with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"erro": f"{e.code} {e.read().decode()[:200]}"}


def ig(media_id):
    r = _get(f"https://graph.instagram.com/v23.0/{media_id}/insights",
             {"metric": IG_METRICS, "access_token": _clean(os.environ["IG_ACCESS_TOKEN"])})
    if "erro" in r:
        return r
    return {m["name"]: m["values"][0]["value"] for m in r.get("data", [])}


def fb(obj_id, video=False):
    """Post da Página precisa de pages_read_user_content; Reels (vídeo) usa likes."""
    import fb_publish
    tok = fb_publish.page()["access_token"]
    campos = ("likes.summary(true).limit(0),comments.summary(true).limit(0)" if video else
              "reactions.summary(true).limit(0),comments.summary(true).limit(0),shares")
    r = _get(f"https://graph.facebook.com/{fb_publish.VER}/{obj_id}", {"fields": campos, "access_token": tok})
    if "erro" in r:
        return {"erro": "pages_read_user_content" if "pages_read_user_content" in r["erro"] else r["erro"]}
    return {"reacoes": r.get("reactions", r.get("likes", {})).get("summary", {}).get("total_count", 0),
            "comentarios": r.get("comments", {}).get("summary", {}).get("total_count", 0),
            "compartilhamentos": r.get("shares", {}).get("count", 0)}


def main(argv):
    dias = int(argv[argv.index("--dias") + 1]) if "--dias" in argv else 14
    desde = (date.today() - timedelta(days=dias)).isoformat()
    sys.path.insert(0, str(Path(__file__).parent))
    linhas = []
    for res in sorted(ROOT.glob("posts/*/resultado.json")):
        pasta = res.parent.name
        if pasta[:10] < desde:
            continue
        r = json.loads(res.read_text())
        item = {"post": pasta}
        for chave, fn, campo in (("ig_feed", ig, "feed_id"), ("ig_reel", ig, "reel_id"),
                                 ("fb_feed", fb, "fb_feed_id"), ("fb_reel", lambda i: fb(i, video=True), "fb_reel_id")):
            if r.get(campo) and (campo.startswith("fb") is False or os.environ.get("FB_ACCESS_TOKEN")):
                item[chave] = fn(r[campo])
        if r.get("tiktok_publish_id"):
            item["tiktok"] = {"privacidade": r.get("tiktok_privacy")}
        linhas.append(item)
    (ROOT / "metricas.json").write_text(json.dumps(linhas, indent=2, ensure_ascii=False))
    print(json.dumps(linhas, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])

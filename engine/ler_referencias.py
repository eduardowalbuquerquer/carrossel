"""Lê os posts recentes dos perfis de referência do Instagram (API Business Discovery).

Uso: python3 ler_referencias.py [--dias 7] [--limite 12]  -> imprime JSON com legenda, data, curtidas, comentários e link.
Só para INSPIRAÇÃO: nunca copiar frases, artes ou estrutura. Ideias vão para pautas.md com palavras nossas.
Requer FB_ACCESS_TOKEN com instagram_basic, instagram_manage_insights e pages_read_engagement.
Doc: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/business_discovery
"""
import json, sys, datetime as dt
from pathlib import Path
import fb_publish as f


def main(argv):
    dias = int(argv[argv.index("--dias") + 1]) if "--dias" in argv else 7
    lim = int(argv[argv.index("--limite") + 1]) if "--limite" in argv else 12
    corte = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=dias)
    ig = f._http("GET", f"https://graph.facebook.com/{f.VER}/{f.page()['id']}",
                 {"fields": "instagram_business_account", "access_token": f.page()["access_token"]})["instagram_business_account"]["id"]
    refs = json.loads((Path(__file__).resolve().parent.parent / "referencias.json").read_text(encoding="utf-8"))
    out = []
    for s in refs.get("fontes", []):
        if s.get("tipo") != "instagram":
            continue
        h = s["id"].lstrip("@")
        campos = f"business_discovery.username({h}){{media.limit({lim}){{caption,timestamp,permalink,like_count,comments_count,media_type}}}}"
        try:
            media = f.fb("GET", ig, fields=campos)["business_discovery"].get("media", {}).get("data", [])
        except SystemExit as e:
            out.append({"perfil": h, "erro": str(e)[:200]}); continue
        for m in media:
            if dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z") >= corte:
                out.append({"perfil": h, "data": m["timestamp"][:10], "tipo": m.get("media_type"),
                            "curtidas": m.get("like_count"), "comentarios": m.get("comments_count"),
                            "link": m.get("permalink"), "legenda": (m.get("caption") or "")[:400]})
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])

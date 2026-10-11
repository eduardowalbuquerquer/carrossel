"""Baixa uma foto realista do Pexels (grátis, uso comercial) para um post.

Uso: python fetch_photo.py "man praying sunrise mountain" ../posts/<pasta>/img/foto.jpg [--orientation portrait]
Requer PEXELS_API_KEY. Docs: https://www.pexels.com/api/documentation/#photos-search
Evita fotos já usadas (registro em ../usados_pexels.json).
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

USED = Path(__file__).resolve().parent.parent / "usados_pexels.json"


def main(query, out, orientation="portrait"):
    used = set(json.loads(USED.read_text())) if USED.exists() else set()
    q = urllib.parse.urlencode({"query": query, "orientation": orientation, "per_page": 30, "size": "large"})
    req = urllib.request.Request(f"https://api.pexels.com/v1/search?{q}",
                                 headers={"Authorization": os.environ["PEXELS_API_KEY"]})
    with urllib.request.urlopen(req, timeout=30) as r:
        photos = json.loads(r.read())["photos"]
    pick = next((p for p in photos if str(p["id"]) not in used), None)
    if not pick:
        raise SystemExit(f"Nenhuma foto nova para '{query}'. Tente outra busca.")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    url = pick["src"].get("large2x") or pick["src"]["original"]
    with urllib.request.urlopen(url, timeout=60) as r:
        out.write_bytes(r.read())
    used.add(str(pick["id"]))
    USED.write_text(json.dumps(sorted(used)))
    print(json.dumps({"arquivo": str(out), "fotografo": pick["photographer"], "pexels": pick["url"]}))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ori = sys.argv[sys.argv.index("--orientation") + 1] if "--orientation" in sys.argv else "portrait"
    if "--orientation" in sys.argv:
        args = [a for a in args if a != ori]
    main(args[0], args[1], ori)

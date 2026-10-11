"""Baixa uma foto realista grátis para um post (Pixabay; Pexels se houver chave).

Uso: python fetch_photo.py "man praying sunrise mountain" ../posts/<pasta>/img/foto.jpg [--orientation vertical]
Requer PIXABAY_API_KEY (ou PEXELS_API_KEY).
Docs: https://pixabay.com/api/docs/ · https://www.pexels.com/api/documentation/#photos-search
Evita fotos já usadas (registro em ../usados_fotos.json).
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# Chaves coladas entre <> ou com espaços quebram a API: limpa antes de usar.
for _k in ("PIXABAY_API_KEY", "PEXELS_API_KEY"):
    if _k in os.environ:
        os.environ[_k] = os.environ[_k].strip().strip("<>\"'").strip()

USED = Path(__file__).resolve().parent.parent / "usados_fotos.json"


def get_json(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", **(headers or {})}), timeout=30) as r:
        return json.loads(r.read())


def candidates(query, orientation):
    """Lista (id, url_da_imagem, credito) da melhor fonte disponível."""
    if os.environ.get("PIXABAY_API_KEY"):
        q = urllib.parse.urlencode({"key": os.environ["PIXABAY_API_KEY"], "q": query[:100], "image_type": "photo",
                                    "orientation": orientation, "per_page": 50, "safesearch": "true",
                                    "min_width": 1000, "order": "popular"})
        for h in get_json(f"https://pixabay.com/api/?{q}")["hits"]:
            yield f"pixabay:{h['id']}", h["largeImageURL"], {"autor": h["user"], "pagina": h["pageURL"]}
    elif os.environ.get("PEXELS_API_KEY"):
        ori = {"vertical": "portrait", "horizontal": "landscape"}.get(orientation, orientation)
        q = urllib.parse.urlencode({"query": query, "orientation": ori, "per_page": 30, "size": "large"})
        for p in get_json(f"https://api.pexels.com/v1/search?{q}", {"Authorization": os.environ["PEXELS_API_KEY"]})["photos"]:
            yield f"pexels:{p['id']}", p["src"].get("large2x") or p["src"]["original"], {"autor": p["photographer"], "pagina": p["url"]}
    else:
        raise SystemExit("Defina PIXABAY_API_KEY (ou PEXELS_API_KEY) no ambiente.")


def main(query, out, orientation="vertical"):
    used = set(json.loads(USED.read_text())) if USED.exists() else set()
    pick = next(((i, u, c) for i, u, c in candidates(query, orientation) if i not in used), None)
    if not pick:
        raise SystemExit(f"Nenhuma foto nova para '{query}'. Tente outra busca.")
    pid, url, credit = pick
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
        out.write_bytes(r.read())  # baixamos a foto (não fazemos hotlink)
    used.add(pid)
    USED.write_text(json.dumps(sorted(used)))
    print(json.dumps({"arquivo": str(out), "id": pid, **credit}, ensure_ascii=False))


if __name__ == "__main__":
    args = sys.argv[1:]
    ori = "vertical"
    if "--orientation" in args:
        k = args.index("--orientation"); ori = args[k + 1]; del args[k:k + 2]
    main(args[0], args[1], ori)

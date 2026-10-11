"""Gerencia as fontes de referência de um perfil (onde buscar ideias, nunca copiar).

Uso (rode da pasta do kit ou do perfil):
  python referencias.py <pasta_do_perfil> listar
  python referencias.py <pasta_do_perfil> adicionar <tipo> <endereco> ["foco ou observação"]
  python referencias.py <pasta_do_perfil> remover <endereco>
  python referencias.py <pasta_do_perfil> rodada [N]     # escolhe as N menos consultadas (padrão 3) e marca a data

Tipos: instagram, facebook, youtube, tiktok, blog, portal, artigo, podcast, livro, site, outro.
Endereço: @perfil, URL completa, DOI do artigo ou título do livro.
As referências ficam em perfil.json -> "referencias". A ROTINA usa a "rodada" para variar as fontes.
"""
import datetime as dt
import json
import sys
from pathlib import Path

TIPOS = {"instagram", "facebook", "youtube", "tiktok", "blog", "portal", "artigo", "podcast", "livro", "site", "outro"}
URL_BASE = {"instagram": "https://www.instagram.com/{}/", "tiktok": "https://www.tiktok.com/@{}",
            "youtube": "https://www.youtube.com/@{}", "facebook": "https://www.facebook.com/{}"}


def norm(addr):
    return addr.strip().rstrip("/").lower()


def load(dest):
    path = Path(dest) / "perfil.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def save(path, perfil):
    path.write_text(json.dumps(perfil, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv):
    path, perfil = load(argv[0])
    refs = perfil.setdefault("referencias", [])
    cmd = argv[1] if len(argv) > 1 else "listar"
    today = dt.date.today().isoformat()

    if cmd == "adicionar":
        tipo, addr = argv[2].lower(), argv[3].strip()
        if tipo not in TIPOS:
            raise SystemExit(f"Tipo '{tipo}' inválido. Use: {', '.join(sorted(TIPOS))}")
        if any(norm(r["endereco"]) == norm(addr) for r in refs):
            raise SystemExit(f"{addr} já está na lista.")
        ref = {"tipo": tipo, "endereco": addr, "foco": argv[4] if len(argv) > 4 else "", "adicionada_em": today,
               "consultada_em": None}
        if tipo in URL_BASE and addr.startswith("@"):
            ref["url"] = URL_BASE[tipo].format(addr.lstrip("@"))
        elif addr.startswith("http"):
            ref["url"] = addr
        refs.append(ref)
        save(path, perfil)
        print(json.dumps({"adicionada": ref, "total": len(refs)}, ensure_ascii=False))
    elif cmd == "remover":
        before = len(refs)
        perfil["referencias"] = [r for r in refs if norm(r["endereco"]) != norm(argv[2])]
        save(path, perfil)
        print(json.dumps({"removidas": before - len(perfil["referencias"]), "total": len(perfil["referencias"])}))
    elif cmd == "rodada":
        n = int(argv[2]) if len(argv) > 2 else 3
        pick = sorted(refs, key=lambda r: (r.get("consultada_em") or "", r["adicionada_em"]))[:n]
        for r in pick:
            r["consultada_em"] = today
        save(path, perfil)
        print(json.dumps({"consultar_hoje": pick}, ensure_ascii=False, indent=2))
    else:
        for r in refs:
            print(f"- [{r['tipo']}] {r['endereco']}  {r.get('foco', '')}  (consultada: {r.get('consultada_em') or 'nunca'})")
        print(f"Total: {len(refs)}")


if __name__ == "__main__":
    main(sys.argv[1:])

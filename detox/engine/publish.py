"""Publica um vídeo do Totalmente Saudável pelo Buffer da marca (TikTok, Pinterest e Página do Facebook).

Reaproveita o publish.py do Salário Organizado (salario/engine) trocando a chave do Buffer, os links e os textos.
Instagram e YouTube ficam de fora até as contas novas serem autorizadas no app (decisão de 21/11/2026).

Uso:
  python3 publish.py ../posts/<pasta> --so tt,pin      # vídeos do dia (padrão: tt,pin)
  python3 publish.py ../posts/<pasta> --so tt,pin,fb   # 1 vídeo por dia também na Página do Facebook
  python3 publish.py --check                           # canais conectados no Buffer da marca

Ambiente: DETOX_BUFFER_KEY (Buffer grátis da marca), PAGES_REPO_DIR, PAGES_BASE_URL. Opcional DETOX_PIN_BOARD.
"""
import os, sys
from pathlib import Path

key = (os.environ.get("DETOX_BUFFER_KEY") or "").strip()
if not key:
    raise SystemExit("Falta DETOX_BUFFER_KEY no ambiente (Buffer do Totalmente Saudável).")
os.environ["SO_BUFFER_KEY"] = key                     # o motor lê SO_BUFFER_KEY: aqui vale a chave da marca
os.environ["SO_PIN_BOARD"] = os.environ.get("DETOX_PIN_BOARD", "Receitas sem açúcar")
os.environ["SO_TIKTOK_MODO"] = "buffer"
# Tokens próprios da marca (o token do YouTube fica numa pasta separada da do Salário Organizado).
os.environ["SO_SEGREDOS"] = os.environ.get("DETOX_SEGREDOS", "/mnt/project-files/canais/automacao/.segredos-detox")
IG_OK = bool(os.environ.get("DETOX_IG_ACCESS_TOKEN") and os.environ.get("DETOX_IG_USER_ID"))
if IG_OK:
    os.environ["SO_IG_ACCESS_TOKEN"] = os.environ["DETOX_IG_ACCESS_TOKEN"]
    os.environ["SO_IG_USER_ID"] = os.environ["DETOX_IG_USER_ID"]
else:  # nunca cair no Instagram do Salário Organizado
    os.environ.pop("SO_IG_ACCESS_TOKEN", None); os.environ.pop("SO_IG_USER_ID", None)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "salario" / "engine"))
import publish as P  # noqa: E402

SITE = "detoxdeacucar.netlify.app"
FREE = f"https://{SITE}/receitas/"
P.SITE = SITE
P.MINI = FREE


def publish_tt(post_dir, spec):
    # Só Buffer. Sem plano B de rascunho: o token do rascunho é do TikTok do Salário Organizado.
    return P.publish_tt_buffer(post_dir, spec)


def fb_caption(spec, link):
    cap = spec["captions"].get("fb") or spec["captions"].get("ig", "").replace("Comenta RECEITA que eu te mando", "Pegue grátis")
    return cap if link in cap else f"{cap}\n\n👉 5 receitas doces sem açúcar, grátis: {link}"


_pin = P.publish_pin


def publish_pin(post_dir, spec):
    # Mesmo pin de imagem do Salário, com o texto do link trocado.
    orig = P.buffer

    def buffer(query, variables=None):
        if variables and isinstance(variables.get("i"), dict) and "text" in variables["i"]:
            variables["i"]["text"] = variables["i"]["text"].replace("\n\nPlanilha grátis: ", "\n\nReceitas grátis: ")
        return orig(query, variables)
    P.buffer = buffer
    try:
        return _pin(post_dir, spec)
    finally:
        P.buffer = orig


P.publish_tt = publish_tt
P.fb_caption = fb_caption
P.publish_pin = publish_pin
if not IG_OK:
    P.publish_ig = lambda *a: (_ for _ in ()).throw(SystemExit("Instagram do Totalmente Saudável ainda não autorizado (faltam DETOX_IG_ACCESS_TOKEN e DETOX_IG_USER_ID)"))
if not (P.SEGREDOS / "yt_token.json").exists():
    P.publish_yt = lambda *a: (_ for _ in ()).throw(SystemExit("YouTube do Totalmente Saudável ainda não autorizado (falta o token em .segredos-detox)"))


def check():
    import json
    out = {}
    out["instagram"] = "configurado" if IG_OK else "falta autorizar"
    out["youtube"] = "configurado" if (P.SEGREDOS / "yt_token.json").exists() else "falta autorizar"
    for s in ("tiktok", "pinterest", "facebook"):
        try:
            out[s] = P.buffer_channel(s)
        except SystemExit as e:
            out[s] = str(e)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--check" in argv:
        check()
    elif any(a.startswith("--yt-auth") for a in argv):
        P.auth(argv)  # autoriza o canal do YouTube da marca; token vai para SO_SEGREDOS (.segredos-detox)
    else:
        if "--so" not in argv:
            argv += ["--so", "tt,pin"]
        P.main(argv)

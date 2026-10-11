"""Cria (ou atualiza) a pasta de um perfil a partir de um perfil.json preenchido.

Uso:
  python novo_perfil.py <pasta_do_perfil> <perfil.json> [logo.png|jpg|svg]
  python novo_perfil.py <pasta_do_perfil> --rotina      # só regenera ROTINA.md depois de editar o perfil.json

Resultado:
  <pasta>/perfil.json, engine/ (motor), assets/logo.*, posts/, historico.json, ideias.json, referencias.py, ROTINA.md
"""
import json
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
REGRAS_REF = [
    "Referências servem só de inspiração: extrair o tema, a pergunta ou o ângulo e escrever com palavras, estrutura e exemplos próprios.",
    "Nunca copiar texto, título, roteiro, imagem ou layout de outro perfil; nunca republicar conteúdo alheio.",
    "Citação literal só curta, entre aspas e com crédito ao autor (ou da fonte de autoridade do perfil).",
    "Toda ideia aproveitada passa pelas premissas do perfil; ideia que contradiz uma premissa é descartada.",
]
DAYS = {"1": "segunda", "2": "terça", "3": "quarta", "4": "quinta", "5": "sexta", "6": "sábado", "7": "domingo"}


def rotina(p):
    m, t = p["marca"], p["tema"]
    plats = " + ".join(x.capitalize() for x in p.get("plataformas", ["instagram"]))
    ag = p.get("agenda", {})
    fa = p.get("fontes_autoridade") or {}
    series = "\n".join(f"- {DAYS.get(k, k)}: **{v['name']}** (`{v['key']}`, {v['format']}, {v.get('slides', '')} slide(s)) · {v.get('visual', '')}. {v.get('brief', '')}"
                       for k, v in sorted(p["series"].items()))
    prem = "\n".join(f"{i}. {x}" for i, x in enumerate(p.get("premissas", []), 1)) or "1. (nenhuma definida)"
    lim = "\n".join(f"- {x}" for x in p.get("limites", [])) or "- (nenhum)"
    fonte = ""
    if fa:
        fonte = f"\n## Fonte de autoridade\n**{fa['nome']}**\n" + "\n".join(f"- {r}" for r in fa.get("regras", [])) + "\n"
    img = p.get("imagens", {})
    leg = p.get("legenda", {})
    reel = p.get("reel", {})
    rr = p.get("referencias_rodada", {"frequencia": "diária", "quantidade": 3})
    regras_ref = "\n".join(f"- {x}" for x in p.get("referencias_regras", REGRAS_REF))
    return f"""# Rotina diária · {m['nome']} (@{m['handle']})

Você é a fábrica de conteúdo de **@{m['handle']}** ({t['nome']}). Plataformas: **{plats}**.
Todo dia, sem intervenção humana, crie e publique {ag.get('posts_por_dia', 1)} post no feed{' + 1 Reels de chamada' if ag.get('reel', True) else ''}.
Horário de publicação: {ag.get('horario', '09:00')} ({ag.get('fuso', 'America/Sao_Paulo')}).

- **Tema:** {t.get('descricao', '')}
- **Público:** {t.get('publico', '')}
- **Objetivo:** {t.get('objetivo', '')}
- **Tom:** {t.get('tom', '')}
- **Usar:** {', '.join(t.get('usar', [])) or '-'} · **Evitar:** {', '.join(t.get('evitar', [])) or '-'}

## Premissas inegociáveis
{prem}

**Antes de publicar**, releia slides, legenda e Reels e confirme cada premissa acima. Se alguma falhar, corrija o spec e renderize de novo. Na dúvida, troque o tema: é melhor um post mais simples do que um post que viole uma premissa.

## Limites
{lim}
{fonte}
## Fontes de referência (inspiração, nunca cópia)
{len(p.get('referencias', []))} referências cadastradas em `perfil.json -> referencias` (lista: `python3 referencias.py . listar`).
{regras_ref}

## Ambiente (antes do passo 1)
```
cd <clone do repositório do perfil> && git pull -q origin main
pip install -q playwright pillow
export PAGES_REPO_DIR=$(pwd) PAGES_BASE_URL={p.get('repo', {}).get('base_url', 'https://<usuario>.github.io/<repo>')}
```
Reserva se o Pages cair: `PAGES_BASE_URL='https://cdn.jsdelivr.net/gh/{p.get('repo', {}).get('github', '<usuario>/<repo>')}@{{sha}}'`.
Se `posts/<hoje>-<serie>/` já existir com slides (e reel.mp4), pule para o passo 8.

## Séries (por dia da semana)
{series}

## Passo a passo
1. **Data e série.** Data de hoje no fuso do perfil; série pelo dia da semana (1 = segunda ... 7 = domingo).
2. **Pesquisar referências** ({rr.get('frequencia', 'diaria')}). Rode `python3 referencias.py . rodada {rr.get('quantidade', 3)}` na raiz do perfil e veja o conteúdo recente de cada fonte sorteada (busca na web, perfil público, canal, artigo). Anote 1 a 3 ideias novas (tema, pergunta, dor do público, notícia) em `ideias.json` com a fonte. Se uma fonte não abrir (login, bloqueio), passe para a próxima e registre isso; não invente o que ela publicou. Escolha a ideia que combina com a série do dia e escreva tudo com palavras próprias.
3. **Não repetir.** Leia `historico.json`; não repita tema, personagem ou citação dos últimos {p.get('nao_repetir_dias', 60)} dias.
4. **Escrever o conteúdo.** Crie `posts/AAAA-MM-DD-<serie>/spec.json` (formato em `exemplos/` da skill ou nos posts anteriores):
   - Layouts: `hero`, `photo`, `text`, `list`, `big`, `verse`, `compare`, `cta`. Carrossel sempre termina em `cta`. Imagem única = 1 slide.
   - Alternar claro/escuro. Títulos até ~70 caracteres, corpo até ~110.
   - 1º slide = gancho que para o scroll. Último = CTA "{p.get('cta', {}).get('botao', 'Siga @' + m['handle'])}".
   - `caption`: {leg.get('estrutura', 'gancho, desenvolvimento, pergunta, CTA, hashtags')}. Hashtags fixas: {' '.join(leg.get('hashtags_fixas', []))}; total {leg.get('hashtags_qtd', [6, 8])[0]} a {leg.get('hashtags_qtd', [6, 8])[1]}.
   {"- `caption_facebook` (opcional): versão sem excesso de hashtags para o Facebook." if 'facebook' in p.get('plataformas', []) else ""}
   - `reel.frames`: {reel.get('cenas', [3, 4])[0]} a {reel.get('cenas', [3, 4])[1]} cenas. {reel.get('regra', '')}
5. **Imagens realistas** (séries com foto): `python3 fetch_photo.py "<busca em inglês>" ../posts/<pasta>/img/foto.jpg`. Estilo: {img.get('estilo', '')}. Evitar: {', '.join(img.get('evitar', []))}. Use a mesma foto em `reel.image`.
6. **Conferir o spec.** `cd engine && python3 checar_spec.py ../posts/<pasta>/spec.json` (corrija todo ERRO).
7. **Renderizar e revisar.** `python3 render_post.py ../posts/<pasta>/spec.json` e `python3 render_reel.py ../posts/<pasta>/spec.json`. Abra 2 ou 3 slides e 2 quadros do Reels: texto cortado, sobreposição com a barra, português. Aplique de novo o checklist das premissas e confirme que nada foi copiado de uma referência.
8. **Publicar.** `python3 publish.py ../posts/<pasta>` (todas as plataformas do perfil; idempotente, pode rodar de novo se falhar no meio).
9. **Registrar.** Acrescente ao `historico.json`: data, série, título, tema, citações, referência que inspirou, links do `resultado.json`. Commit e push.
10. **Token.** Dias 1 e 15: `python3 publish.py --refresh-token` (Instagram). Se `mesmo_token: false` ou validade < 15 dias, avise o dono.
11. **Falhas.** Nunca invente resultado: avise o dono com o erro exato e o que ele precisa fazer.
"""


def main(argv):
    dest = Path(argv[0]).resolve()
    if "--rotina" in argv:
        p = json.loads((dest / "perfil.json").read_text(encoding="utf-8"))
        (dest / "ROTINA.md").write_text(rotina(p), encoding="utf-8")
        print(json.dumps({"rotina": str(dest / "ROTINA.md")}))
        return
    p = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(KIT / "engine", dest / "engine", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    (dest / "posts").mkdir(exist_ok=True)
    (dest / "assets").mkdir(exist_ok=True)
    if len(argv) > 2:
        logo = Path(argv[2])
        target = dest / "assets" / f"logo{logo.suffix.lower()}"
        shutil.copy(logo, target)
        p["marca"]["logo"] = f"assets/{target.name}"
    (dest / "perfil.json").write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")
    if not (dest / "historico.json").exists():
        (dest / "historico.json").write_text("[]")
    if not (dest / "ideias.json").exists():
        (dest / "ideias.json").write_text("[]")
    shutil.copy(KIT / "referencias.py", dest / "referencias.py")
    (dest / "ROTINA.md").write_text(rotina(p), encoding="utf-8")
    (dest / ".gitignore").write_text("__pycache__/\n*.png\npreview.html\nreel.html\n")
    print(json.dumps({"perfil": str(dest), "arquivos": sorted(x.name for x in dest.iterdir())}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])

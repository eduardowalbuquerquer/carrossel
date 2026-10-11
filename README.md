# Forja da Alma · automação diária

Motor que cria e publica 1 post por dia no feed + 1 Reels de chamada em @forjadaalma.oficial.

- `engine/` gerador de slides (`render_post.py`), Reels (`render_reel.py`), fotos Pexels (`fetch_photo.py`) e publicador (`publish.py`)
- `engine/series.json` calendário semanal de séries
- `posts/<data>-<serie>/` cada post (spec.json, slides JPG, reel.mp4). Servidos pelo GitHub Pages para o Instagram baixar.
- `ROTINA.md` procedimento diário seguido pela rotina agendada
- `PASSO-A-PASSO-ACESSO.md` o que o dono da conta precisa liberar

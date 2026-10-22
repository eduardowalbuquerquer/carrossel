# Kit · Fábrica de conteúdo social

Motor genérico (Instagram + Facebook) extraído da automação do Forja da Alma. Tudo que é do perfil fica em `perfil.json`.

```
python3 novo_perfil.py ../meu-perfil perfil.json logo.png   # cria a pasta do perfil
cd ../meu-perfil/engine
python3 checar_spec.py ../posts/<pasta>/spec.json
python3 render_post.py ../posts/<pasta>/spec.json
python3 render_reel.py ../posts/<pasta>/spec.json
python3 publish.py ../posts/<pasta>            # precisa das credenciais (guias/)
```
Exemplo completo: `exemplos/forja-da-alma/`. Procedimento completo: SKILL.md da skill `fabrica-conteudo-social`.

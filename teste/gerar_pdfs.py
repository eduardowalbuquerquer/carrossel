"""Gera teste/pdf/plano-<perfil>.pdf a partir de plano.html + dados.js (fonte única do texto).

Uso: python3 teste/gerar_pdfs.py
(Se o Playwright não achar o navegador: CHROMIUM_PATH=/opt/pw-browsers/chromium python3 teste/gerar_pdfs.py)
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
PERFIS = ["jaco", "pedro", "elias", "davi", "gideao", "jose"]


def main():
    saida = AQUI / "pdf"
    saida.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        pagina = nav.new_page()
        for k in PERFIS:
            pagina.goto(f"{(AQUI / 'plano.html').as_uri()}?p={k}")
            pagina.wait_for_load_state("networkidle")
            pagina.evaluate("document.fonts.ready")
            destino = saida / f"plano-{k}.pdf"
            pagina.pdf(path=str(destino), format="A4", print_background=True, prefer_css_page_size=True)
            print(destino.relative_to(AQUI.parent))
        nav.close()


if __name__ == "__main__":
    main()

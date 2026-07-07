#!/usr/bin/env python3
"""
Exercia — Carousel PNG Exporter
Usage:
  python3 export_carousel.py                         # contenu par défaut
  python3 export_carousel.py --content content.json  # contenu custom
  python3 export_carousel.py --out ./output          # dossier de sortie custom

Format JSON attendu (content.json) :
{
  "slide1": {
    "tag": "CRPE 2026 · MÉTHODE",
    "eyebrow": "Tu travailles dur. Pourtant…",
    "title": "Tu rates les mêmes questions depuis <span class='hook-accent'>3 mois.</span>",
    "sub": "Ce n'est pas un manque de travail. C'est une méthode inadaptée."
  },
  "slide2": { "tag": "ERREUR #1", "title": "Réviser <span class='ct-accent'>sans tester</span> sa mémoire active", "body": "..." },
  "slide3": { "tag": "ERREUR #2", "title": "...", "body": "..." },
  "slide4": { "tag": "ERREUR #3", "title": "...", "body": "..." },
  "slide5": { "cta_label": "Prêt à changer de méthode ?", "title": "Entraîne-toi sur les vraies questions du CRPE.", "btn": "Essayer gratuitement", "sub": "exercia.org · lien en bio" }
}
"""

import json
import argparse
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_CONTENT = {
    "slide1": {
        "tag": "CRPE 2026 · MÉTHODE",
        "eyebrow": "Tu travailles dur. Pourtant…",
        "title": "Tu rates les mêmes questions depuis <span class='hook-accent'>3 mois.</span>",
        "sub": "Ce n'est pas un manque de travail. C'est une méthode inadaptée. Voilà comment corriger ça."
    },
    "slide2": {
        "tag": "ERREUR #1",
        "step": "01",
        "title": "Réviser <span class='ct-accent'>sans tester</span> sa mémoire active",
        "body": "Relire ses fiches donne l'illusion de maîtrise. Le cerveau reconnaît sans retenir. Seul le rappel actif consolide vraiment la mémoire."
    },
    "slide3": {
        "tag": "ERREUR #2",
        "step": "02",
        "title": "Ignorer les <span class='ct-accent'>annales</span> des 3 dernières années",
        "body": "Le jury réutilise les mêmes typologies de questions. Les annales révèlent exactement ce qui tombe."
    },
    "slide4": {
        "tag": "ERREUR #3",
        "step": "03",
        "title": "Bachoter <span class='ct-accent'>sans cibler</span> les notions tombables",
        "body": "Toutes les notions ne se valent pas au CRPE. Certaines reviennent chaque année, d'autres jamais."
    },
    "slide5": {
        "tag": "LA SOLUTION",
        "cta_label": "Prêt à changer de méthode ?",
        "title": "Entraîne-toi sur les vraies questions du CRPE.",
        "btn": "Essayer gratuitement",
        "sub": "exercia.org · lien en bio"
    }
}

# ── HTML template ─────────────────────────────────────────────────────────────

def build_html(content: dict) -> str:
    s = content
    s1 = s["slide1"]
    s2 = s["slide2"]
    s3 = s["slide3"]
    s4 = s["slide4"]
    s5 = s["slide5"]

    logo_white = """<svg width="108" height="33" viewBox="0 0 360 110" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="rW" x1="38" y1="14" x2="94" y2="96" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#FFFEF5"/><stop offset="55%" stop-color="#FFFFFF"/><stop offset="100%" stop-color="#EDF7F8"/></linearGradient></defs>
      <circle cx="70" cy="55" r="34" stroke="url(#rW)" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="180 60" stroke-dashoffset="18"/>
      <path d="M54 55.5L66 67.5L88 43" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <text x="120" y="70" font-family="Inter,sans-serif" font-size="52" font-weight="700" fill="#FFFFFF" letter-spacing="-0.5">Exercia</text>
    </svg>"""

    logo_dark = """<svg width="108" height="33" viewBox="0 0 360 110" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="rD" x1="38" y1="14" x2="94" y2="96" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#63C6A6"/><stop offset="55%" stop-color="#3B8BC6"/><stop offset="100%" stop-color="#2F5BDB"/></linearGradient></defs>
      <circle cx="70" cy="55" r="34" stroke="url(#rD)" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="180 60" stroke-dashoffset="18"/>
      <path d="M54 55.5L66 67.5L88 43" stroke="#3B8BC6" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <text x="120" y="70" font-family="Inter,sans-serif" font-size="52" font-weight="700" fill="#1B1B1B" letter-spacing="-0.5">Exercia</text>
    </svg>"""

    slides_html = f"""
    <!-- SLIDE 1 : Hook -->
    <div id="slide-1" class="slide" style="background:#0F838F; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:0; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:rgba(255,255,255,0.85);">{s1['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(255,255,255,0.6);">01 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-size:24px; font-weight:600; color:#fff; margin-bottom:28px; letter-spacing:0.04em;">{s1['eyebrow']}</div>
        <h1 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:68px; font-weight:800; line-height:1.12; color:#fff; margin-bottom:36px;">{s1['title']}</h1>
        <p style="font-size:30px; line-height:1.6; color:#fff; font-weight:500; max-width:88%;">{s1['sub']}</p>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:flex-end;">
        <div style="font-size:22px; font-weight:500; color:rgba(255,255,255,0.7);">← Swipe →</div>
        {logo_white}
      </div>
    </div>

    <!-- SLIDE 2 -->
    <div id="slide-2" class="slide" style="background:#FFFFFF; border:2px solid #e8e8e8; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:1100px; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:#0F838F;">{s2['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(15,131,143,0.35);">02 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:144px; font-weight:800; color:#EAC435; line-height:1; margin-bottom:16px;">{s2.get('step','01')}</div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:62px; font-weight:800; line-height:1.15; color:#1B1B1B; margin-bottom:32px;">{s2['title']}</h2>
        <p style="font-size:32px; line-height:1.6; color:#333; max-width:90%;">{s2['body']}</p>
      </div>
      <div style="height:6px; background:#f0f0f0; border-radius:4px; overflow:hidden;">
        <div style="width:25%; height:100%; background:#0F838F; border-radius:4px;"></div>
      </div>
    </div>

    <!-- SLIDE 3 -->
    <div id="slide-3" class="slide" style="background:#FFFFFF; border:2px solid #e8e8e8; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:2200px; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:#0F838F;">{s3['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(15,131,143,0.35);">03 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:144px; font-weight:800; color:#EAC435; line-height:1; margin-bottom:16px;">{s3.get('step','02')}</div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:62px; font-weight:800; line-height:1.15; color:#1B1B1B; margin-bottom:32px;">{s3['title']}</h2>
        <p style="font-size:32px; line-height:1.6; color:#333; max-width:90%;">{s3['body']}</p>
      </div>
      <div style="height:6px; background:#f0f0f0; border-radius:4px; overflow:hidden;">
        <div style="width:50%; height:100%; background:#0F838F; border-radius:4px;"></div>
      </div>
    </div>

    <!-- SLIDE 4 -->
    <div id="slide-4" class="slide" style="background:#FFFFFF; border:2px solid #e8e8e8; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:3300px; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:#0F838F;">{s4['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(15,131,143,0.35);">04 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:144px; font-weight:800; color:#EAC435; line-height:1; margin-bottom:16px;">{s4.get('step','03')}</div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:62px; font-weight:800; line-height:1.15; color:#1B1B1B; margin-bottom:32px;">{s4['title']}</h2>
        <p style="font-size:32px; line-height:1.6; color:#333; max-width:90%;">{s4['body']}</p>
      </div>
      <div style="height:6px; background:#f0f0f0; border-radius:4px; overflow:hidden;">
        <div style="width:75%; height:100%; background:#0F838F; border-radius:4px;"></div>
      </div>
    </div>

    <!-- SLIDE 5 : CTA -->
    <div id="slide-5" class="slide" style="background:#EAC435; width:1080px; height:1080px; padding:88px 96px; display:flex; flex-direction:column; justify-content:space-between; position:absolute; top:0; left:4400px; font-family:'Inter',sans-serif;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div style="font-size:20px; font-weight:600; letter-spacing:0.13em; text-transform:uppercase; color:rgba(0,0,0,0.4);">{s5['tag']}</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:22px; font-weight:700; color:rgba(0,0,0,0.25);">05 / 05</div>
      </div>
      <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
        <div style="font-size:28px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:rgba(0,0,0,0.65); margin-bottom:32px;">{s5['cta_label']}</div>
        <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:64px; font-weight:800; line-height:1.15; color:#1B1B1B; margin-bottom:40px;">{s5['title']}</h2>
        <div style="display:inline-flex; align-items:center; gap:16px; background:#0F838F; color:#fff; font-size:26px; font-weight:600; padding:24px 44px; border-radius:16px; width:fit-content;">{s5['btn']} →</div>
        <p style="font-size:28px; font-weight:600; color:rgba(0,0,0,0.6); margin-top:28px;">{s5['sub']}</p>
      </div>
      <div style="display:flex; justify-content:flex-end; align-items:flex-end;">
        <svg width="180" height="55" viewBox="0 0 360 110" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs><linearGradient id="rD2" x1="38" y1="14" x2="94" y2="96" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#63C6A6"/><stop offset="55%" stop-color="#3B8BC6"/><stop offset="100%" stop-color="#2F5BDB"/></linearGradient></defs>
          <circle cx="70" cy="55" r="34" stroke="url(#rD2)" stroke-width="10" stroke-linecap="round" fill="none" stroke-dasharray="180 60" stroke-dashoffset="18"/>
          <path d="M54 55.5L66 67.5L88 43" stroke="#3B8BC6" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          <text x="120" y="70" font-family="Inter,sans-serif" font-size="52" font-weight="700" fill="#1B1B1B" letter-spacing="-0.5">Exercia</text>
        </svg>
      </div>
    </div>
    """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1080px; height: 1080px; overflow: hidden; position: relative; }}
.hook-accent {{ color: #EAC435; }}
.ct-accent {{ color: #0F838F; }}
</style>
</head>
<body>
{slides_html}
</body>
</html>"""

# ── Export ─────────────────────────────────────────────────────────────────────

def export_slides(content: dict, out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    html = build_html(content)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.set_content(html)
        page.wait_for_timeout(1200)  # laisser les polices Google charger

        offsets = [0, 1100, 2200, 3300, 4400]

        for i, offset in enumerate(offsets):
            slide_num = i + 1
            out_path = os.path.join(out_dir, f"slide_{slide_num:02d}.png")

            page.evaluate(f"document.body.style.transform = 'translateX(-{offset}px)'")
            page.wait_for_timeout(100)

            page.screenshot(
                path=out_path,
                clip={"x": 0, "y": 0, "width": 1080, "height": 1080}
            )
            print(f"✓ slide_{slide_num:02d}.png")

        browser.close()

    print(f"\nDone → {out_dir}")

# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export carousel Exercia en PNG")
    parser.add_argument("--content", help="Chemin vers un fichier JSON de contenu", default=None)
    parser.add_argument("--out", help="Dossier de sortie", default="./carousel_output")
    args = parser.parse_args()

    if args.content:
        with open(args.content, "r", encoding="utf-8") as f:
            content = json.load(f)
    else:
        content = DEFAULT_CONTENT

    export_slides(content, args.out)
